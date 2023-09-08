from __future__ import annotations

import pytest

from .utils import get_test_dir
from .utils import license_file
from bids2cite.license import add_license_file
from bids2cite.license import identify_license
from bids2cite.license import update_license


def test_add_license_file():
    output_dir = get_test_dir().joinpath("bids", "derivatives", "bids2cite")

    add_license_file("PDDL-1.0", output_dir)

    assert license_file().exists()
    license_file().unlink(missing_ok=True)

    add_license_file("None", output_dir)
    assert not license_file().exists()


def test_update_license():
    bids_dir = get_test_dir().joinpath("bids")
    output_dir = get_test_dir().joinpath("bids", "derivatives", "bids2cite")

    ds_desc = {"License": "PDDL"}

    (license_name, license_url) = update_license(
        bids_dir, output_dir, ds_desc, skip_prompt=True
    )

    assert license_name == "PDDL-1.0"
    assert license_url == "https://opendatacommons.org/licenses/pddl/1-0/"

    assert license_file().exists()
    license_file().unlink(missing_ok=True)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("CC0", "CC0-1.0"),
        ("CC-BY-NC-SA-4.0", "CC-BY-NC-SA-4.0"),
        ("", ""),
        ("foo", "foo"),
    ],
)
def test_identify_license(input, expected):
    ds_desc = {"License": input}

    (name, url) = identify_license(ds_desc)

    assert name == expected
