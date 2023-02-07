from __future__ import annotations

import pytest

from bids2cite.references import get_reference_id
from bids2cite.references import references_for_datacite


@pytest.mark.parametrize(
    "reference,expected",
    [
        ("pmid:1245  ", "pmid:1245"),
        ("  doi:1245", "doi:1245"),
        ("ncbi.nlm.nih.gov/pubmed/568", "pmid:568"),
        ("https://doi.org/10.666 ", "doi:10.666"),
        ("", ""),
    ],
)
def test_get_reference_id(reference, expected):
    assert get_reference_id(reference) == expected


def test_references_for_datacite():
    tmp = references_for_datacite(
        references=[{"citation": "foobarbaz"}, {"citation": ""}, {"citation": " "}]
    )

    assert tmp == ["foobarbaz"]
