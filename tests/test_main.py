from utils import get_test_dir

from bids2cite.bids2cite import main
from bids2cite.utils import print_unordered_list, prompt_format


def test_prompt_format():

    assert prompt_format("foo") == "[bold]foo[/bold]"


def test_prompt_format():

    assert prompt_format("foo") == "[bold]foo[/bold]"


def test_main():

    bids_dir = get_test_dir().joinpath("bids")
    main(bids_dir=bids_dir, skip_prompt=True)
