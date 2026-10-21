"""Verified MobileNetV2 training and evaluation on PlantVillage images."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import time
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np
import tensorflow as tf
from PIL import Image
from scipy.fft import dctn
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = PROJECT_ROOT / "data" / "raw" / "PlantVillage"
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "disease"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports" / "disease"
IMAGE_SIZE = (160, 160)
BATCH_SIZE = 8
SEED = 42
CROPS = ("Tomato", "Potato", "Pepper")
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def set_reproducible_runtime() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    tf.config.threading.set_intra_op_parallelism_threads(3)
    tf.config.threading.set_inter_op_parallelism_threads(2)
    tf.keras.utils.set_random_seed(SEED)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_dataset_root(data_dir: Path) -> Path:
    candidates = [
        data_dir / "Plant_leave_diseases_dataset_without_augmentation",
        data_dir / "PlantVillage" / "Plant_leave_diseases_dataset_without_augmentation",
        data_dir,
    ]
    for candidate in candidates:
        if candidate.is_dir() and any(path.is_dir() for path in candidate.iterdir()):
            return candidate
    raise FileNotFoundError(
        "PlantVillage's Plant_leave_diseases_dataset_without_augmentation folder "
        f"was not found under {data_dir}."
    )


def perceptual_hash(path: Path) -> int:
    with Image.open(path) as source:
        pixels = np.asarray(
            source.convert("L").resize((32, 32), Image.Resampling.LANCZOS),
            dtype=np.float32,
        )
    low_frequency = dctn(pixels, type=2, norm="ortho")[:8, :8]
    values = low_frequency.flatten()[1:]
    median = float(np.median(values))
    bits = values > median
    result = 0
    for bit in bits:
        result = (result << 1) | int(bit)
    return result


class _UnionFind:
    def __init__(self) -> None:
        self.parents: list[int] = []

    def add(self) -> int:
        value = len(self.parents)
        self.parents.append(value)
        return value

    def find(self, value: int) -> int:
        while self.parents[value] != value:
            self.parents[value] = self.parents[self.parents[value]]
            value = self.parents[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parents[right_root] = left_root


class _BKTree:
    def __init__(self) -> None:
        self.root: tuple[int, list] | None = None

    @staticmethod
    def _distance(left: int, right: int) -> int:
        return (left ^ right).bit_count()

    def add(self, value: int, node_id: int) -> None:
        if self.root is None:
            self.root = (value, [(node_id, {})])
            return
        node = self.root
        while True:
            distance = self._distance(value, node[0])
            entries = node[1]
            if distance == 0:
                entries.append((node_id, {}))
                return
            child = entries[0][1].get(distance)
            if child is None:
                entries[0][1][distance] = (value, [(node_id, {})])
                return
            node = child

    def nearby(self, value: int, radius: int) -> list[int]:
        matches: list[int] = []
        if self.root is None:
            return matches
        pending = [self.root]
        while pending:
            node = pending.pop()
            distance = self._distance(value, node[0])
            if distance <= radius:
                matches.extend(node_id for node_id, _ in node[1])
            lower = distance - radius
            upper = distance + radius
            pending.extend(
                child
                for edge, child in node[1][0][1].items()
                if lower <= edge <= upper
            )
        return matches


def _collect_image_records(dataset_root: Path) -> tuple[list[dict], dict]:
    class_dirs = sorted(
        directory
        for directory in dataset_root.iterdir()
        if directory.is_dir() and directory.name.split("___", 1)[0].replace(", bell", "").startswith(CROPS)
    )
    if not class_dirs:
        raise ValueError(f"No Tomato, Potato, or Pepper classes found under {dataset_root}.")

    records: list[dict] = []
    source_counts: dict[str, int] = {}
    for class_dir in class_dirs:
        images = sorted(
            path
            for path in class_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not images:
            continue
        label = class_dir.name
        source_counts[label] = len(images)
        for path in images:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            records.append(
                {
                    "path": path,
                    "label": label,
                    "sha256": digest,
                    "relative_path": path.relative_to(dataset_root).as_posix(),
                }
            )
    if len(source_counts) < 3:
        raise ValueError(f"Expected disease classes for all three crops; found {sorted(source_counts)}.")
    return records, source_counts


def _deduplicate_related_images(records: list[dict], radius: int = 4) -> dict:
    exact_hashes: dict[str, int] = {}
    exact_phashes: dict[str, str] = {}
    phash_nodes: dict[int, int] = {}
    tree = _BKTree()
    groups = _UnionFind()
    for record in records:
        exact_match = exact_hashes.get(record["sha256"])
        if exact_match is not None:
            node_id = exact_match
            record["phash"] = exact_phashes[record["sha256"]]
            record["group_node"] = node_id
            continue

        image_hash = perceptual_hash(record["path"])
        record["phash_value"] = image_hash
        record["phash"] = f"{image_hash:016x}"
        node_id = groups.add()
        exact_hashes[record["sha256"]] = node_id
        exact_phashes[record["sha256"]] = record["phash"]
        record["group_node"] = node_id

        existing_hash_node = phash_nodes.get(image_hash)
        if existing_hash_node is not None:
            groups.union(node_id, existing_hash_node)
            continue
        for nearby_id in tree.nearby(image_hash, radius):
            groups.union(node_id, nearby_id)
        tree.add(image_hash, node_id)
        phash_nodes[image_hash] = node_id

    groups_by_hash: dict[str, int] = {}
    image_group_ids = []
    for record in records:
        if "group_node" not in record:
            node_id = exact_hashes[record["sha256"]]
            record["group_node"] = node_id
        group_id = groups.find(record["group_node"])
        stable_id = groups_by_hash.setdefault(str(group_id), len(groups_by_hash))
        record["group_id"] = stable_id
        image_group_ids.append(stable_id)

    return {
        "image_count": len(records),
        "exact_duplicate_images": len(records) - len(exact_hashes),
        "perceptual_groups": len(groups_by_hash),
        "phash_hamming_radius": radius,
        "images_removed_by_sampling": 0,
    }


def _sample_class_balanced(records: list[dict], max_per_class: int) -> list[dict]:
    by_group: dict[int, list[dict]] = {}
    for record in records:
        by_group.setdefault(record["group_id"], []).append(record)

    groups_by_class: dict[str, list[tuple[int, list[dict]]]] = {}
    for group_id, group_records in by_group.items():
        labels = sorted({record["label"] for record in group_records})
        for label in labels:
            groups_by_class.setdefault(label, []).append((group_id, group_records))

    rng = random.Random(SEED)
    selected_groups: set[int] = set()
    counts: dict[str, int] = {}
    for label, class_groups in groups_by_class.items():
        rng.shuffle(class_groups)
        count = 0
        for group_id, group_records in class_groups:
            if count >= max_per_class:
                break
            if group_id not in selected_groups:
                selected_groups.add(group_id)
            count += sum(record["label"] == label for record in group_records)
        counts[label] = count

    selected = [
        record
        for group_id in selected_groups
        for record in by_group[group_id]
    ]
    selected.sort(key=lambda record: (record["label"], record["relative_path"]))
    too_small = {label: count for label, count in counts.items() if count < 5}
    if too_small:
        raise ValueError(f"Not enough distinct image groups to train these classes: {too_small}")
    return selected


def _grouped_splits(records: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    class_names = sorted({record["label"] for record in records})
    class_to_id = {label: index for index, label in enumerate(class_names)}
    labels = np.asarray([class_to_id[record["label"]] for record in records])
    group_ids = np.asarray([record["group_id"] for record in records])
    indexes = np.arange(len(records))
    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    train_val_idx, test_idx = next(outer.split(indexes, labels, group_ids))
    inner = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED + 1)
    train_sub_idx, val_sub_idx = next(
        inner.split(train_val_idx, labels[train_val_idx], group_ids[train_val_idx])
    )
    train_idx = train_val_idx[train_sub_idx]
    val_idx = train_val_idx[val_sub_idx]

    train_groups = set(group_ids[train_idx])
    val_groups = set(group_ids[val_idx])
    test_groups = set(group_ids[test_idx])
    if train_groups & val_groups or train_groups & test_groups or val_groups & test_groups:
        raise RuntimeError("Duplicate/perceptual image groups crossed a data split.")
    return (
        [records[index] for index in train_idx],
        [records[index] for index in val_idx],
        [records[index] for index in test_idx],
    )


def _make_dataset(records: list[dict], class_to_id: dict[str, int], training: bool) -> tf.data.Dataset:
    paths = [str(record["path"]) for record in records]
    labels = [class_to_id[record["label"]] for record in records]
    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))

    def load_image(path: tf.Tensor, label: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
        contents = tf.io.read_file(path)
        image = tf.io.decode_image(contents, channels=3, expand_animations=False)
        image.set_shape((None, None, 3))
        image = tf.image.resize(image, IMAGE_SIZE, antialias=True)
        return image, label

    dataset = dataset.map(load_image, num_parallel_calls=2, deterministic=True)
    if training:
        dataset = dataset.shuffle(len(records), seed=SEED, reshuffle_each_iteration=True)
    dataset = dataset.batch(BATCH_SIZE).prefetch(1)
    return dataset


def build_model(num_classes: int) -> tf.keras.Model:
    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
            tf.keras.layers.RandomContrast(0.1),
        ],
        name="training_only_augmentation",
    )
    backbone = tf.keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    backbone.trainable = False
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3), name="rgb_image_0_255")
    x = augmentation(inputs)
    x = tf.keras.layers.Rescaling(1.0 / 127.5, offset=-1.0, name="mobilenet_v2_preprocessing")(x)
    x = backbone(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="disease_probabilities")(x)
    model = tf.keras.Model(inputs, outputs, name="AgriVision_MobileNetV2_PlantVillage")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy(name="accuracy")],
    )
    return model


def _save_split_manifest(splits: dict[str, list[dict]], path: Path, dataset_root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=["split", "class_name", "relative_path", "sha256", "phash", "group_id"],
        )
        writer.writeheader()
        for split, records in splits.items():
            for record in records:
                writer.writerow(
                    {
                        "split": split,
                        "class_name": record["label"],
                        "relative_path": record["path"].relative_to(dataset_root).as_posix(),
                        "sha256": record["sha256"],
                        "phash": record["phash"],
                        "group_id": record["group_id"],
                    }
                )


def _evaluate_and_save(model: tf.keras.Model, records: list[dict], class_names: list[str], output_dir: Path) -> dict:
    class_to_id = {label: index for index, label in enumerate(class_names)}
    dataset = _make_dataset(records, class_to_id, training=False)
    true_labels = np.asarray([class_to_id[record["label"]] for record in records])
    start = time.perf_counter()
    probabilities = model.predict(dataset, verbose=0)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    predicted_labels = probabilities.argmax(axis=1)
    confidence = probabilities.max(axis=1)
    matrix = confusion_matrix(true_labels, predicted_labels, labels=list(range(len(class_names))))
    report = classification_report(
        true_labels,
        predicted_labels,
        labels=list(range(len(class_names))),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    accuracy = float(accuracy_score(true_labels, predicted_labels))
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "per_class_metrics.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=["class_name", "precision", "recall", "f1_score", "support"])
        writer.writeheader()
        for class_name in class_names:
            row = report[class_name]
            writer.writerow(
                {
                    "class_name": class_name,
                    "precision": row["precision"],
                    "recall": row["recall"],
                    "f1_score": row["f1-score"],
                    "support": int(row["support"]),
                }
            )

    prediction_path = output_dir / "test_predictions.csv"
    with prediction_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=["relative_path", "true_class", "predicted_class", "confidence", "correct"],
        )
        writer.writeheader()
        for record, predicted, score in zip(records, predicted_labels, confidence):
            writer.writerow(
                {
                    "relative_path": record["relative_path"],
                    "true_class": record["label"],
                    "predicted_class": class_names[int(predicted)],
                    "confidence": float(score),
                    "correct": bool(class_to_id[record["label"]] == int(predicted)),
                }
            )

    metrics = {
        "test_accuracy": accuracy,
        "macro_precision": float(report["macro avg"]["precision"]),
        "macro_recall": float(report["macro avg"]["recall"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "test_images": len(records),
        "inference_ms_per_image": elapsed_ms / len(records),
        "per_class": {name: report[name] for name in class_names},
        "confusion_matrix_labels": class_names,
        "confusion_matrix": matrix.tolist(),
    }
    (output_dir / "evaluation_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(max(11, len(class_names) * 0.8), max(9, len(class_names) * 0.7)))
    image = ax.imshow(matrix, interpolation="nearest", cmap="Blues")
    ax.set_title("PlantVillage test-set confusion matrix")
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("True class")
    ax.set_xticks(range(len(class_names)), labels=class_names, rotation=90, fontsize=7)
    ax.set_yticks(range(len(class_names)), labels=class_names, fontsize=7)
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    fig.savefig(output_dir / "confusion_matrix.png", dpi=180)
    plt.close(fig)
    return metrics


def train(data_dir: Path, model_dir: Path, report_dir: Path, max_per_class: int, epochs: int) -> dict:
    set_reproducible_runtime()
    dataset_root = find_dataset_root(data_dir)
    image_records, source_counts = _collect_image_records(dataset_root)
    duplicate_summary = _deduplicate_related_images(image_records)
    records = _sample_class_balanced(image_records, max_per_class=max_per_class)
    train_records, val_records, test_records = _grouped_splits(records)
    class_names = sorted({record["label"] for record in records})
    class_to_id = {label: index for index, label in enumerate(class_names)}
    splits = {"train": train_records, "validation": val_records, "test": test_records}
    _save_split_manifest(splits, report_dir / "split_manifest.csv", dataset_root)

    model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    model = build_model(len(class_names))
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            model_dir / "best_checkpoint.weights.h5",
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            save_weights_only=True,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            mode="max",
            patience=3,
            restore_best_weights=True,
        ),
        tf.keras.callbacks.CSVLogger(report_dir / "training_history.csv"),
    ]
    model.fit(
        _make_dataset(train_records, class_to_id, training=True),
        validation_data=_make_dataset(val_records, class_to_id, training=False),
        epochs=epochs,
        callbacks=callbacks,
        shuffle=False,
        verbose=2,
    )
    best_weights_path = model_dir / "best_checkpoint.weights.h5"
    model.load_weights(best_weights_path)
    metrics = _evaluate_and_save(model, test_records, class_names, report_dir)
    final_model_path = model_dir / "disease_mobilenetv2.keras"
    model.save(final_model_path)
    model_hash = _sha256_file(final_model_path)
    archive_path = PROJECT_ROOT / "data" / "raw" / "source_archives" / "plant_village_without_augmentation.zip"
    class_mapping = {str(index): name for index, name in enumerate(class_names)}
    metadata = {
        "status": "verified_trained",
        "model_id": "plantvillage-mobilenetv2-tomato-potato-pepper-v1",
        "model_path": str(final_model_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "model_sha256": model_hash,
        "architecture": "MobileNetV2 (ImageNet weights, frozen backbone; global average pooling, dropout 0.3, softmax head)",
        "input_shape": [IMAGE_SIZE[0], IMAGE_SIZE[1], 3],
        "input_dtype": "float32",
        "input_range": "RGB values 0..255; model applies Rescaling(1/127.5, offset=-1)",
        "training_augmentation": ["horizontal flip", "rotation 0.08", "zoom 0.1", "contrast 0.1"],
        "class_mapping": class_mapping,
        "class_names": class_names,
        "dataset_source": "PlantVillage via Mendeley Data DOI 10.17632/tywbtsjrjv.1; archive path selects the unaugmented image directory",
        "dataset_license": "CC0 1.0 (Mendeley Data record)",
        "dataset_archive_sha256": _sha256_file(archive_path) if archive_path.is_file() else None,
        "source_image_counts": source_counts,
        "sampled_class_counts": {
            label: sum(record["label"] == label for record in records)
            for label in class_names
        },
        "split_image_counts": {split: len(part) for split, part in splits.items()},
        "split_strategy": "two-stage StratifiedGroupKFold 5-fold; exact SHA-256 and 64-bit pHash Hamming distance <= 4 grouped before split; fixed seed 42",
        "duplicate_check": duplicate_summary,
        "max_per_class": max_per_class,
        "test_metrics_path": str((report_dir / "evaluation_metrics.json").relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "field_photo_limitation": "PlantVillage test metrics do not establish performance on field photographs.",
        "inference_ms_per_image": metrics["inference_ms_per_image"],
    }
    metadata_path = model_dir / "disease_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (model_dir / "class_names.json").write_text(json.dumps(class_names, indent=2), encoding="utf-8")
    summary = {
        "model_path": str(final_model_path),
        "metadata_path": str(metadata_path),
        "test_accuracy": metrics["test_accuracy"],
        "macro_precision": metrics["macro_precision"],
        "macro_recall": metrics["macro_recall"],
        "macro_f1": metrics["macro_f1"],
        "test_images": metrics["test_images"],
        "inference_ms_per_image": metrics["inference_ms_per_image"],
    }
    (report_dir / "training_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--max-per-class", type=int, default=250)
    parser.add_argument("--epochs", type=int, default=12)
    args = parser.parse_args()
    if args.max_per_class < 20:
        parser.error("--max-per-class must be at least 20 for a grouped train/validation/test split.")
    if args.epochs < 1:
        parser.error("--epochs must be positive.")
    train(args.data_dir.resolve(), args.model_dir.resolve(), args.report_dir.resolve(), args.max_per_class, args.epochs)


if __name__ == "__main__":
    main()
