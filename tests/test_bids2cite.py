from __future__ import annotations

import json
from pathlib import Path

import pytest

from bids2cite.bids2cite import _update_bidsignore, bids2cite


@pytest.fixture
def bidsignore(bids_dir) -> Path:
    return bids_dir / ".bidsignore"


@pytest.fixture
def datacite(bids_dir) -> Path:
    return bids_dir / "derivatives" / "bids2cite" / "datacite.yml"


@pytest.fixture
def citation(bids_dir) -> Path:
    return bids_dir / "derivatives" / "bids2cite" / "CITATION.cff"


@pytest.fixture
def dataset_description(bids_dir) -> Path:
    return bids_dir / "derivatives" / "bids2cite" / "dataset_description.json"


def test_update_bidsignore(bids_dir, bidsignore) -> None:
    _update_bidsignore(bids_dir=bids_dir)
    assert bidsignore.exists()
    with bidsignore.open("r") as f:
        content = f.read()
    assert "datacite.yml" in content


def test_update_bidsignore_2(bids_dir, bidsignore) -> None:
    with bidsignore.open("w") as f:
        f.write("foo")
    _update_bidsignore(bids_dir=bids_dir)
    with bidsignore.open("r") as f:
        content = f.read()
    assert "datacite.yml" in content


def test_bids2cite_datacite(
    bids_dir, license_file, bidsignore, datacite, citation, dataset_description
) -> None:
    bids2cite(
        bids_dir=bids_dir,
        output_format="datacite",
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
        license="PDDL-1.0",
    )

    assert bidsignore.exists()
    assert license_file.exists()
    assert dataset_description.exists()
    assert datacite.exists()
    assert not citation.exists()

    with dataset_description.open("r") as f:
        content = json.load(f)

        assert content.get("authors") is None
        print(content.get("Authors"))
        for x in content.get("Authors"):
            assert x not in ("")
            assert not x.isspace()

        for x in content.get("ReferencesAndLinks"):
            assert x not in ("")
            assert not x.isspace()


def test_bids2cite_citation(
    bids_dir,
    license_file,
    bidsignore,
    dataset_description,
    datacite,
    citation,
) -> None:
    bids2cite(
        bids_dir=bids_dir,
        output_format="citation",
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
        license="PDDL-1.0",
    )

    assert bidsignore.exists()
    assert license_file.exists()
    assert dataset_description.exists()
    assert not datacite.exists()
    assert citation.exists()
