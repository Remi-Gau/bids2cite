from __future__ import annotations

import shutil
from pathlib import Path

import pytest


@pytest.fixture
def root_test_dir() -> Path:
    return Path(__file__).parent


@pytest.fixture
def bids_dir(root_test_dir, tmp_path) -> Path:
    # copy the bids directory to a temporary location
    tmp_bids_dir = tmp_path / "bids"
    shutil.copytree(root_test_dir / "bids", tmp_bids_dir)
    return tmp_bids_dir


@pytest.fixture
def license_file(bids_dir) -> Path:
    return bids_dir / "derivatives" / "bids2cite" / "LICENSE"
