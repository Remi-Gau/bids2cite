from utils import get_test_dir

from bids2cite.bids2cite import main
from bids2cite.bids2cite import update_bidsignore


def test_update_bidsignore():

    bids_dir = get_test_dir().joinpath("bids")
    update_bidsignore(bids_dir=bids_dir)

    bidsignore = bids_dir.joinpath(".bidsignore")
    with bidsignore.open("w") as f:
        f.write("foo")
    update_bidsignore(bids_dir=bids_dir)

    bids_dir.joinpath(".bidsignore").unlink(missing_ok=True)


def test_main():

    bids_dir = get_test_dir().joinpath("bids")
    main(
        bids_dir=bids_dir,
        description="add something",
        keywords=["foo", "bar"],
        skip_prompt=True,
    )

    bids_dir.joinpath(".bidsignore").unlink(missing_ok=True)
    bids_dir.joinpath("LICENSE").unlink(missing_ok=True)
    bids_dir.joinpath("datacite.yml").unlink(missing_ok=True)
