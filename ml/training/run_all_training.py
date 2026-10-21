"""Run both verified local model trainers from the repository root."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = [
    PROJECT_ROOT / "ml" / "disease" / "train_disease_model.py",
    PROJECT_ROOT / "ml" / "yield" / "train_yield_model.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n{'=' * 60}\nRunning: {script.relative_to(PROJECT_ROOT)}\n{'=' * 60}", flush=True)
        subprocess.run([sys.executable, "-u", str(script)], cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()
