from __future__ import annotations

import json
from pathlib import Path

from .utils import get_test_dir
from .utils import license_file
from bids2cite.bids2cite import _update_bidsignore
from bids2cite.bids2cite import bids2cite


def bids_dir() -> Path:
    return get_test_dir().joinpath("bids")


def bidsignore() -> Path:
    return bids_dir().joinpath(".bidsignore")


def datacite() -> Path:
    return bids_dir().joinpath("derivatives", "bids2cite", "datacite.yml")


def citation() -> Path:
    return bids_dir().joinpath("derivatives", "bids2cite", "CITATION.cff")


def dataset_description() -> Path:
    return bids_dir().joinpath("derivatives", "bids2cite", "dataset_description.json")


def cleanup() -> None:
    bidsignore().unlink(missing_ok=True)
    datacite().unlink(missing_ok=True)
    citation().unlink(missing_ok=True)
    dataset_description().unlink(missing_ok=True)


def test_update_bidsignore() -> None:
    cleanup()

    _update_bidsignore(bids_dir=bids_dir())
    assert bidsignore().exists()
    with bidsignore().open("r") as f:
        content = f.read()
    assert "datacite.yml" in content

    cleanup()
    with bidsignore().open("w") as f:
        f.write("foo")
    _update_bidsignore(bids_dir=bids_dir())
    with bidsignore().open("r") as f:
        content = f.read()
    assert "datacite.yml" in content

    cleanup()


def test_bids2cite_datacite() -> None:
    cleanup()

    bids_dir = get_test_dir().joinpath("bids")

    bids2cite(
        bids_dir=bids_dir,
        output_format="datacite",
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
        license="PDDL-1.0",
    )

    assert bidsignore().exists()
    assert license_file().exists()
    assert dataset_description().exists()
    assert datacite().exists()
    assert not citation().exists()

    with dataset_description().open("r") as f:
        content = json.load(f)

        assert content.get("authors") is None
        print(content.get("Authors"))
        for x in content.get("Authors"):
            assert x not in ("")
            assert not x.isspace()

        for x in content.get("ReferencesAndLinks"):
            assert x not in ("")
            assert not x.isspace()

    cleanup()


def test_bids2cite_citation() -> None:
    bids_dir = get_test_dir().joinpath("bids")

    cleanup()

    bids2cite(
        bids_dir=bids_dir,
        output_format="citation",
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
        license="PDDL-1.0",
    )

    assert bidsignore().exists()
    assert license_file().exists()
    assert dataset_description().exists()
    assert not datacite().exists()
    assert citation().exists()

    cleanup()
