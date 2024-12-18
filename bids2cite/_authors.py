"""Deal with authors."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from rich.prompt import Prompt

from bids2cite._utils import VALID_RESPONSE, print_ordered_list, prompt_format

log = logging.getLogger("bids2datacite")


def affiliation_from_orcid(orcid_record: dict[str, Any]) -> str | None:
    """Get affiliation the most recent employment (top of the list)."""
    if employer := (
        orcid_record.get("activities-summary", {})
        .get("employments", {})
        .get("employment-summary", [])
    ):
        return str(employer[0].get("organization", {}).get("name"))
    else:
        return None


def first_name_from_orcid(orcid_record: dict[str, Any]) -> str:
    """Return first name from ORCID record."""
    return str(
        orcid_record.get("person", {}).get("name", {}).get("given-names", {}).get("value")
    )


def last_name_from_orcid(orcid_record: dict[str, Any]) -> str:
    """Return last name from ORCID record."""
    return str(
        orcid_record.get("person", {}).get("name", {}).get("family-name", {}).get("value")
    )


def get_author_info_from_orcid(orcid: str) -> dict[str, Any]:
    """Get author info from ORCID."""
    orcid = orcid.strip()

    url = f"https://pub.orcid.org/v3.0/{orcid}/record"

    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
        },
    )
    author_info = {}
    if response.status_code == VALID_RESPONSE:
        record = response.json()
        first_name = first_name_from_orcid(record)
        last_name = last_name_from_orcid(record)
        affiliation = affiliation_from_orcid(record)
        author_info = {
            "firstname": first_name,
            "lastname": last_name,
            "affiliation": affiliation,
            "id": f"ORCID:{orcid}",
        }

    if not author_info:
        log.warning(f"Could not find author info for ORCID: {orcid}")

    return author_info


def parse_author(author: str) -> dict[str, str | None]:
    """Parse author string to get first name, last name, affiliation and ORCID."""
    author = author.strip().replace("  ", " ")

    author_info: dict[str, str | None] = {
        "first_name": None,
        "last_name": None,
        "affiliation": None,
        "id": None,
    }

    if author in (""):
        return {"firstname": None, "lastname": None}
    if "orcid:" in author.lower():
        if author_info := get_author_info_from_orcid(author.split(":")[1]):
            return author_info
    elif "orcid.org/" in author:
        if author_info := get_author_info_from_orcid(author.split("orcid.org/")[1]):
            return author_info
    elif author_info := get_author_info_from_orcid(author):
        return author_info

    if "," in author:
        first_name, last_name = author.split(",")
    elif " " in author:
        first_name = author.split(" ")[0]
        last_name = " ".join(author.split(" ")[1:])

    else:
        first_name = author
        last_name = ""

    first_name = first_name.strip()
    last_name = last_name.strip()

    author_info["firstname"] = first_name
    author_info["lastname"] = last_name
    return author_info


def display_new_authors(authors_file: Path | None = None) -> int:
    """Display new authors from authors file."""
    if authors_file is not None and authors_file.exists():
        tmp = pd.read_csv(authors_file, sep="\t")
        authors_list = [
            {
                "first_name": tmp["first_name"][ind],
                "last_name": tmp["last_name"][ind],
                "affiliation": tmp["affiliation"][ind],
                "ORCID": tmp["ORCID"][ind],
            }
            for ind in tmp.index
        ]

        print_ordered_list(msg="List of potential authors to add:", items=authors_list)

        return len(authors_list)
    else:
        return 0


def rm_empty_authors(authors: list[dict[str, str | None]]) -> list[dict[str, str | None]]:
    """Remove empty authors."""
    return [x for x in authors if x["firstname"] is not None]


def update_authors(
    ds_desc: dict[str, Any], skip_prompt: bool = False, authors_file: Path | None = None
) -> list[dict[str, str | None]]:
    """Update authors."""
    authors: list[dict[str, str | None]] = []
    log.info("update authors")

    if "Authors" in ds_desc:
        desc_authors = [
            x for x in ds_desc["Authors"] if x not in (None, "") or not x.isspace()
        ]
        authors.extend(parse_author(author) for author in desc_authors)

    if skip_prompt:
        return rm_empty_authors(authors)

    add_authors = "yes"

    while add_authors == "yes":
        print_ordered_list(msg="Current authors:", items=authors)

        add_authors = Prompt.ask(
            prompt_format("Do you want to add more authors?"),
            default="yes",
            choices=["yes", "no"],
        )
        print()
        if add_authors != "yes":
            break

        author: Any = None
        if authors_file is not None:
            nb_authors = display_new_authors(authors_file)
            choices = [str(i) for i in range(1, nb_authors + 1)]
            choices.append("0")
            author_idx = Prompt.ask(
                prompt_format(
                    "Select author to add. (0 --> add an author not listed above)"
                ),
                choices=choices,
            )
            if author_idx == "0":
                author = manually_add_author()
                authors.append(parse_author(author))
            else:
                author = choose_from_new_authors(authors_file, int(author_idx) - 1)
                authors.append(author)

        else:
            author = manually_add_author()
            authors.append(parse_author(author))

    return rm_empty_authors(authors)


def choose_from_new_authors(authors_file: Path, author_idx: int) -> dict[str, str | None]:
    """Choose author from new authors file."""
    tmp = pd.read_csv(authors_file, sep="\t")
    author = tmp.iloc[author_idx]
    author_info: dict[str, str | None] = {
        "firstname": author["first_name"],
        "lastname": author["last_name"],
        "affiliation": author["affiliation"],
        "id": f"ORCID:{author['ORCID']}",
    }
    return author_info


def manually_add_author() -> str:
    """Manually add author."""
    author = Prompt.ask(
        prompt_format(
            """Please enter a new author
(for example: 'firstname surname' or 'ORCID:0000-0002-9120-8098')"""
        )
    )
    return str(author)


def authors_for_desc(authors: list[dict[str, str | None]]) -> list[str]:
    """Return authors formatted for dataset_description.json."""
    tmp = []
    for x in authors:
        this_author = f"{x['firstname']} {x['lastname']}"
        if x.get("id"):
            this_author += f", {x['id']}"
        tmp.append(this_author)
    return tmp


def authors_for_citation(
    authors: list[dict[str, str | None]],
) -> list[dict[str, str | None]]:
    """Return authors formatted for citation.cff."""
    tmp = []
    for x in authors:
        this_author = {
            "given-names": x.get("firstname", ""),
            "family-names": x.get("lastname", ""),
        }
        if x.get("id"):
            orcid = x.get("id")
            this_author["orcid"] = f"https://orcid.org/{orcid.replace('ORCID:', '')}"  # type: ignore[union-attr]
        if x.get("affiliation"):
            this_author["affiliation"] = x.get("affiliation", "")
        tmp.append(this_author)
    return tmp
