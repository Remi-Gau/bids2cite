from __future__ import annotations

from pathlib import Path


def get_test_dir() -> Path:
    return Path(__file__).parent
