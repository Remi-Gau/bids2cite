from __future__ import annotations

from pathlib import Path


def get_test_dir() -> Path:
    return Path(__file__).parent


def license_file() -> Path:
    return get_test_dir().joinpath("bids", "derivatives", "bids2cite", "LICENSE")
