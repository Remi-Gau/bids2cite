from __future__ import annotations

from utils import get_test_dir

from bids2cite.bids2cite import bids2cite
from bids2cite.bids2cite import update_bidsignore


def test_update_bidsignore():

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


def test_bids2cite():

    bids_dir = get_test_dir().joinpath("bids")
    bids2cite(
        bids_dir=bids_dir,
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
    )

    bidsignore = bids_dir.joinpath(".bidsignore")
    assert bidsignore.exists()
    bidsignore.unlink(missing_ok=True)

    bids_dir.joinpath("LICENSE").unlink(missing_ok=True)
    bids_dir.joinpath("datacite.yml").unlink(missing_ok=True)
