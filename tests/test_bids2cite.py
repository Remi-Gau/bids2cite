from __future__ import annotations

from utils import get_test_dir
from utils import license_file

from bids2cite.bids2cite import bids2cite
from bids2cite.bids2cite import update_bidsignore


def test_update_bidsignore() -> None:

    bids_dir = get_test_dir().joinpath("bids")

    bidsignore = bids_dir.joinpath(".bidsignore")

    bidsignore.unlink(missing_ok=True)
    update_bidsignore(bids_dir=bids_dir)
    assert bidsignore.exists()
    with bidsignore.open("r") as f:
        content = f.read()
    assert "datacite.yml" in content

    bidsignore.unlink(missing_ok=True)
    with bidsignore.open("w") as f:
        f.write("foo")
    update_bidsignore(bids_dir=bids_dir)
    with bidsignore.open("r") as f:
        content = f.read()
    assert "datacite.yml" in content

    bidsignore.unlink(missing_ok=True)


def test_bids2cite_datacite() -> None:

    bids_dir = get_test_dir().joinpath("bids")
    bids2cite(
        bids_dir=bids_dir,
        output_format="datacite",
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
        license="PDDL-1.0",
    )

    bidsignore = bids_dir.joinpath(".bidsignore")
    assert bidsignore.exists()
    bidsignore.unlink(missing_ok=True)

    assert license_file().exists()
    license_file().unlink(missing_ok=True)

    datacite = bids_dir.joinpath("derivatives", "bids2cite", "datacite.yml")
    assert datacite.exists()
    datacite.unlink(missing_ok=True)

    citation = bids_dir.joinpath("derivatives", "bids2cite", "CITATION.cff")
    assert not citation.exists()


def test_bids2cite_citation() -> None:

    bids_dir = get_test_dir().joinpath("bids")
    bids2cite(
        bids_dir=bids_dir,
        output_format="citation",
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
        license="PDDL-1.0",
    )

    bidsignore = bids_dir.joinpath(".bidsignore")
    assert bidsignore.exists()
    bidsignore.unlink(missing_ok=True)

    assert license_file().exists()
    license_file().unlink(missing_ok=True)

    datacite = bids_dir.joinpath("derivatives", "bids2cite", "datacite.yml")
    assert not datacite.exists()

    citation = bids_dir.joinpath("derivatives", "bids2cite", "CITATION.cff")
    assert citation.exists()
    citation.unlink(missing_ok=True)
