from __future__ import annotations

import pytest

from bids2cite._authors import choose_from_new_authors
from bids2cite._authors import display_new_authors
from bids2cite._authors import get_author_info_from_orcid
from bids2cite._authors import parse_author


def test_display_new_authors(root_test_dir):
    authors_file = root_test_dir.parent / "inputs" / "authors.tsv"
    display_new_authors(authors_file)


def test_choose_from_new_authors(root_test_dir):
    authors_file = root_test_dir.parent / "inputs" / "authors.tsv"
    author_info = choose_from_new_authors(authors_file, author_idx=1)
    assert author_info == {
        "affiliation": "UCLouvain",
        "firstname": "Mohamed",
        "id": "ORCID:0000-0002-1866-8645",
        "lastname": "Rezk",
    }


def test_get_author_info_from_orcid():
    assert get_author_info_from_orcid("0000-0002-9120-8098") == {
        "affiliation": None,
        "firstname": "Melanie",
        "id": "ORCID:0000-0002-9120-8098",
        "lastname": "Ganz",
    }


def test_get_author_info_from_orcid_empty():
    assert get_author_info_from_orcid("8098") == {}


def test_parse_author_orcid():
    assert parse_author("0000-0002-9120-8098") == {
        "affiliation": None,
        "firstname": "Melanie",
        "id": "ORCID:0000-0002-9120-8098",
        "lastname": "Ganz",
    }


@pytest.mark.parametrize(
    "author,firstname,lastname",
    [
        ("  Bob  van der Bob  ", "Bob", "van der Bob"),
        ("   Bob,  van der  Bob  ", "Bob", "van der Bob"),
        ("Bob", "Bob", ""),
        ("Bob  ", "Bob", ""),
        ("", None, None),
    ],
)
def test_parse_author(author, firstname, lastname):
    assert parse_author(author) == {"firstname": firstname, "lastname": lastname}
