import logging
from typing import List

import requests  # type: ignore
from rich.prompt import Prompt

from bids2cite.utils import print_unordered_list, prompt_format

log = logging.getLogger("bids2datacite")


def affiliation_from_orcid(orcid_record):
    """Get affiliation the most recent employment (top of the list)"""
    if employer := (
        orcid_record.get("activities-summary", {})
        .get("employments", {})
        .get("employment-summary", [])
    ):
        return employer[0].get("organization", {}).get("name")


def first_name_from_orcid(orcid_record):
    return (
        orcid_record.get("person", {}).get("name", {}).get("given-names", {}).get("value")
    )


def last_name_from_orcid(orcid_record):
    return (
        orcid_record.get("person", {}).get("name", {}).get("family-name", {}).get("value")
    )


def get_author_info_from_orcid(orcid: str) -> dict:
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
    if response.status_code == 200:
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


def parse_author(author: str) -> dict:

    author = author.strip().replace("  ", " ")

    author_info = {
        "first_name": None,
        "last_name": None,
        "affiliation": None,
        "id": None,
    }  # type: ignore

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

    author_info["firstname"] = first_name  # type: ignore
    author_info["lastname"] = last_name  # type: ignore
    return author_info


def update_authors(ds_desc: dict, skip_prompt: bool = False):
    authors: List[str] = []
    if "Authors" in ds_desc:
        authors.extend(parse_author(author) for author in ds_desc["Authors"])  # type: ignore

    if skip_prompt:
        return authors

    add_authors = "yes"
    while add_authors == "yes":

        print_unordered_list(msg="Current authors:", items=authors)

        add_authors = Prompt.ask(
            prompt_format("Do you want to add more authors?"),
            default="yes",
            choices=["yes", "no"],
        )
        print()
        if add_authors != "yes":
            break

        author = Prompt.ask(
            prompt_format(
                """Please enter a new author
(for example: 'firstname surname' or 'ORCID:0000-0002-9120-8098')"""
            )
        )
        authors.append(parse_author(author))  # type: ignore

    return authors
