"""Safely extract only Tomato, Potato, and Pepper classes from the source ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE = PROJECT_ROOT / "data" / "raw" / "source_archives" / "plant_village_without_augmentation.zip"
DEFAULT_DESTINATION = PROJECT_ROOT / "data" / "raw" / "PlantVillage"
SOURCE_PREFIX = "Plant_leave_diseases_dataset_without_augmentation/"
SELECTED_CROPS = ("Tomato", "Potato", "Pepper")
LICENSE = "CC0 1.0"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare(archive_path: Path, destination: Path) -> dict:
    if not archive_path.is_file():
        raise FileNotFoundError(f"PlantVillage source archive not found: {archive_path}")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty dataset directory: {destination}")

    selected_counts: Counter[str] = Counter()
    all_counts: Counter[str] = Counter()
    destination.mkdir(parents=True, exist_ok=True)
    expected_root = destination.resolve()
    with ZipFile(archive_path) as archive:
        for member in archive.infolist():
            if member.is_dir() or not member.filename.startswith(SOURCE_PREFIX):
                continue
            relative_name = member.filename[len(SOURCE_PREFIX):]
            relative = PurePosixPath(relative_name)
            if not relative.parts or ".." in relative.parts:
                raise ValueError(f"Unsafe path found in source archive: {member.filename}")
            class_name = relative.parts[0]
            all_counts[class_name] += 1
            if not class_name.split("___", 1)[0].startswith(SELECTED_CROPS):
                continue
            target = (destination / Path(*relative.parts)).resolve()
            if not target.is_relative_to(expected_root):
                raise ValueError(f"Unsafe extraction path: {member.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            selected_counts[class_name] += 1

    if not selected_counts or len(selected_counts) != 15:
        raise ValueError(f"Expected 15 Tomato/Potato/Pepper classes; found {len(selected_counts)}.")
    metadata = {
        "source": "PlantVillage dataset distributed via TensorFlow Datasets",
        "source_url": "https://data.mendeley.com/datasets/tywbtsjrjv/1",
        "source_doi": "10.17632/tywbtsjrjv.1",
        "archive_download_url": "https://data.mendeley.com/public-files/datasets/tywbtsjrjv/files/d5652a28-c1d8-4b76-97f3-72fb80f94efc/file_downloaded",
        "source_archive_name": archive_path.name,
        "source_archive_bytes": archive_path.stat().st_size,
        "source_archive_sha256": _sha256_file(archive_path),
        "license": LICENSE,
        "source_dataset_directory": SOURCE_PREFIX.rstrip("/"),
        "augmentation": "Unaugmented original images only",
        "archive_class_count": len(all_counts),
        "archive_unaugmented_images_across_classes": sum(all_counts.values()),
        "selected_crop_categories": list(SELECTED_CROPS),
        "selected_class_count": len(selected_counts),
        "selected_class_image_counts": dict(sorted(selected_counts.items())),
        "archive_class_image_counts": dict(sorted(all_counts.items())),
        "extraction_root": str(destination.resolve()),
    }
    metadata_path = PROJECT_ROOT / "data" / "raw" / "plantvillage_source.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    prepare(args.archive.resolve(), args.destination.resolve())


if __name__ == "__main__":
    main()
