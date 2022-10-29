from __future__ import annotations

from utils import get_test_dir

from bids2cite.license import add_license_file
from bids2cite.license import update_license


def test_add_license_file():

    bids_dir = get_test_dir().joinpath("bids")

    add_license_file("CC0", bids_dir)

    assert bids_dir.joinpath("LICENSE").exists()
    bids_dir.joinpath("LICENSE").unlink(missing_ok=True)


def test_update_license():

    bids_dir = get_test_dir().joinpath("bids")

    ds_desc = {"License": "CC0"}

    (license_name, license_url) = update_license(bids_dir, ds_desc, skip_prompt=True)

    assert license_name == "Creative Commons Zero 1.0 Public Domain Dedication"
    assert license_url == "https://creativecommons.org/publicdomain/zero/1.0/"

    assert bids_dir.joinpath("LICENSE").exists()
    bids_dir.joinpath("LICENSE").unlink(missing_ok=True)
