"""Verified Random Forest training on actual FAOSTAT crop-yield observations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE = PROJECT_ROOT / "data" / "raw" / "source_archives" / "faostat_crops_livestock_normalized.zip"
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "yield"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports" / "yield"
REQUIRED_COLUMNS = ("Area", "Item", "Element", "Year", "Unit", "Value")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_faostat_yields(archive_path: Path) -> tuple[pd.DataFrame, dict]:
    if not archive_path.is_file():
        raise FileNotFoundError(f"FAOSTAT archive not found: {archive_path}")
    with ZipFile(archive_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        source_name = next(
            (name for name in csv_names if name.endswith("All_Data_(Normalized).csv")),
            None,
        )
        if source_name is None:
            raise ValueError(
                f"Normalized FAOSTAT observations CSV not found in {archive_path}; found {csv_names}."
            )
        chunks: list[pd.DataFrame] = []
        source_rows = 0
        for chunk in pd.read_csv(
            archive.open(source_name),
            usecols=lambda column: column in REQUIRED_COLUMNS,
            chunksize=250_000,
            low_memory=False,
        ):
            source_rows += len(chunk)
            chunk["Element"] = chunk["Element"].astype("string").str.strip()
            selected = chunk.loc[chunk["Element"].str.casefold().eq("yield")].copy()
            if not selected.empty:
                chunks.append(selected)
    if not chunks:
        raise ValueError("The FAOSTAT file contains no rows with Element='Yield'.")

    frame = pd.concat(chunks, ignore_index=True)
    frame["Year"] = pd.to_numeric(frame["Year"], errors="coerce")
    frame["Value"] = pd.to_numeric(frame["Value"], errors="coerce")
    frame["Unit"] = frame["Unit"].astype("string").str.strip()
    frame["Area"] = frame["Area"].astype("string").str.strip()
    frame["Item"] = frame["Item"].astype("string").str.strip()
    conversion = {
        "hg/ha": 0.1,
        "kg/ha": 1.0,
        "t/ha": 1000.0,
    }
    frame = frame.dropna(subset=["Area", "Item", "Year", "Value", "Unit"])
    frame = frame.loc[frame["Value"] > 0].copy()
    unit_counts = {
        str(unit): int(count)
        for unit, count in frame["Unit"].value_counts().items()
    }
    total_yield_rows = len(frame)
    frame = frame.loc[frame["Unit"].isin(conversion)].copy()
    if frame.empty:
        raise ValueError("FAOSTAT Yield rows did not contain supported area-based units.")
    units = sorted(frame["Unit"].unique().tolist())
    frame["yield_kg_per_hectare"] = [
        value * conversion[unit] for value, unit in zip(frame["Value"], frame["Unit"])
    ]
    frame["year"] = frame["Year"].astype(int)
    frame = frame.rename(columns={"Area": "country", "Item": "crop"})
    frame = frame[["country", "crop", "year", "yield_kg_per_hectare", "Unit", "Value"]]

    key_columns = ["country", "crop", "year"]
    duplicate_rows = int(frame.duplicated(key_columns, keep=False).sum())
    if duplicate_rows:
        frame = (
            frame.groupby(key_columns, as_index=False)
            .agg(
                yield_kg_per_hectare=("yield_kg_per_hectare", "median"),
                source_unit=("Unit", "first"),
                source_value=("Value", "median"),
            )
        )
    else:
        frame = frame.rename(columns={"Unit": "source_unit", "Value": "source_value"})
    frame = frame.sort_values(key_columns).reset_index(drop=True)
    info = {
        "archive_path": str(archive_path),
        "archive_sha256": _sha256_file(archive_path),
        "csv_member": source_name,
        "selected_element": "Yield",
        "source_rows_scanned": source_rows,
        "yield_rows_before_deduplication": total_yield_rows,
        "unit_counts_before_filtering": unit_counts,
        "unsupported_unit_rows_excluded": total_yield_rows - len(frame),
        "duplicate_key_rows_collapsed": duplicate_rows,
        "source_units": units,
        "rows_after_filtering": len(frame),
        "years": [int(frame["year"].min()), int(frame["year"].max())],
        "countries_or_regions": int(frame["country"].nunique()),
        "crops": int(frame["crop"].nunique()),
    }
    return frame, info


def _make_pipeline(categorical: list[str], numeric: list[str], estimator) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("numeric", StandardScaler(), numeric),
        ],
        remainder="drop",
    )
    return Pipeline([("preprocessor", preprocessor), ("regressor", estimator)])


def _metrics(actual: pd.Series, predicted: np.ndarray) -> dict:
    return {
        "mae_kg_per_hectare": float(mean_absolute_error(actual, predicted)),
        "rmse_kg_per_hectare": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
    }


def train(archive_path: Path, model_dir: Path, report_dir: Path) -> dict:
    frame, source_info = load_faostat_yields(archive_path)
    years = sorted(frame["year"].unique())
    if len(years) < 10:
        raise ValueError(f"Need at least 10 distinct years for a time holdout; found {len(years)}.")
    split_index = min(max(int(len(years) * 0.8), 1), len(years) - 1)
    test_start_year = int(years[split_index])
    train_frame = frame.loc[frame["year"] < test_start_year].copy()
    test_frame = frame.loc[frame["year"] >= test_start_year].copy()
    if train_frame.empty or test_frame.empty:
        raise ValueError("FAOSTAT time split produced an empty train or test partition.")

    categorical = ["country", "crop"]
    numeric = ["year"]
    feature_columns = categorical + numeric
    x_train = train_frame[feature_columns]
    y_train = train_frame["yield_kg_per_hectare"]
    x_test = test_frame[feature_columns]
    y_test = test_frame["yield_kg_per_hectare"]

    baseline = _make_pipeline(categorical, numeric, LinearRegression())
    random_forest = _make_pipeline(
        categorical,
        numeric,
        RandomForestRegressor(
            n_estimators=100,
            max_depth=18,
            min_samples_leaf=5,
            max_features=0.8,
            random_state=42,
            n_jobs=2,
        ),
    )
    baseline.fit(x_train, y_train)
    random_forest.fit(x_train, y_train)
    baseline_prediction = baseline.predict(x_test)
    forest_prediction = random_forest.predict(x_test)
    metrics = {
        "target": "FAOSTAT Element=Yield converted to kg/hectare",
        "test_split_start_year": test_start_year,
        "train_rows": len(train_frame),
        "test_rows": len(test_frame),
        "baseline_linear_regression": _metrics(y_test, baseline_prediction),
        "random_forest_regressor": _metrics(y_test, forest_prediction),
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    prediction_path = report_dir / "test_predictions.csv"
    predictions = test_frame[["country", "crop", "year", "yield_kg_per_hectare"]].copy()
    predictions = predictions.rename(columns={"yield_kg_per_hectare": "actual_yield_kg_per_hectare"})
    predictions["baseline_prediction_kg_per_hectare"] = baseline_prediction
    predictions["random_forest_prediction_kg_per_hectare"] = forest_prediction
    predictions.to_csv(prediction_path, index=False)

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.scatter(y_test, forest_prediction, alpha=0.28, s=12, label="Random Forest")
    lower = float(min(y_test.min(), forest_prediction.min()))
    upper = float(max(y_test.max(), forest_prediction.max()))
    ax.plot([lower, upper], [lower, upper], color="black", linestyle="--", linewidth=1, label="Ideal")
    ax.set_xlabel("Actual yield (kg/hectare)")
    ax.set_ylabel("Predicted yield (kg/hectare)")
    ax.set_title("FAOSTAT future-year test set: actual vs predicted")
    ax.legend()
    fig.tight_layout()
    fig.savefig(report_dir / "actual_vs_predicted.png", dpi=180)
    plt.close(fig)

    model_path = model_dir / "faostat_random_forest_yield.joblib"
    joblib.dump(random_forest, model_path, compress=3)
    metadata = {
        "status": "verified_trained",
        "model_id": "faostat-country-crop-year-random-forest-v1",
        "model_path": str(model_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "model_sha256": _sha256_file(model_path),
        "algorithm": "RandomForestRegressor(n_estimators=100, max_depth=18, min_samples_leaf=5, max_features=0.8, random_state=42, n_jobs=2)",
        "baseline": "LinearRegression with the same training-only preprocessing",
        "dataset_source": "FAOSTAT Production: Crops and livestock products, normalized bulk dataset",
        "dataset_url": "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip",
        "dataset_license": "CC BY 4.0, subject to FAOSTAT Statistical Database Terms of Use and third-party exceptions",
        "dataset_attribution": "FAO. 2025. FAOSTAT: Production: Crops and livestock products. Accessed 7 October 2026. Licence: CC-BY-4.0.",
        "dataset_info": source_info,
        "target_column": "yield_kg_per_hectare",
        "target_units": "kg/hectare",
        "input_columns": feature_columns,
        "source_column_definitions": {
            "Area": "FAOSTAT country or regional aggregate name; used as the country input",
            "Item": "FAOSTAT agricultural product/crop name; used as the crop input",
            "Element": "Selected only when equal to Yield",
            "Year": "Observation calendar year",
            "Unit": "Official measurement unit; only area-based kg/ha, hg/ha, or t/ha rows retained",
            "Value": "Published yield value, converted to kg/hectare",
        },
        "input_schema": {
            "country": "FAOSTAT Area (country or region) label",
            "crop": "FAOSTAT Item label",
            "year": "target year; integer",
        },
        "features_not_used": ["production", "area", "soil", "rainfall", "temperature"],
        "split_strategy": f"Time-based holdout: train years < {test_start_year}; test years >= {test_start_year}. Later years are the intended future-period evaluation.",
        "test_year_range": [int(test_frame["year"].min()), int(test_frame["year"].max())],
        "train_year_range": [int(train_frame["year"].min()), int(train_frame["year"].max())],
        "supported_crops": sorted(frame["crop"].unique().tolist()),
        "supported_countries": sorted(frame["country"].unique().tolist()),
        "max_training_year": int(train_frame["year"].max()),
        "recommended_prediction_year_range": [
            int(train_frame["year"].max()) + 1,
            int(train_frame["year"].max()) + 5,
        ],
        "metrics_path": str((report_dir / "evaluation_metrics.json").relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "predictions_path": str(prediction_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }
    metadata_path = model_dir / "yield_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (report_dir / "evaluation_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    summary = {
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
        "test_split_start_year": test_start_year,
        "train_rows": len(train_frame),
        "test_rows": len(test_frame),
        **metrics,
    }
    (report_dir / "training_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args()
    train(args.data_archive.resolve(), args.model_dir.resolve(), args.report_dir.resolve())


if __name__ == "__main__":
    main()
