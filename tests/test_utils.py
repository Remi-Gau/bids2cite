from __future__ import annotations

from bids2cite._utils import print_ordered_list
from bids2cite._utils import prompt_format


def test_prompt_format():
    assert prompt_format("foo") == "[bold]foo[/bold]"


def test_print_ordered_list():
    print_ordered_list(msg="bar", items=["foo"])
