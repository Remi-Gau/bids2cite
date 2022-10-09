"""
adds a datacite to your BIDS dataset
details on the format of datacite for GIN: https://gin.g-node.org/G-Node/Info/wiki/DOIfile
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import IO, Optional

import ruamel.yaml
from rich import print
from rich.prompt import Prompt

from . import _version

__version__ = _version.get_versions()["version"]

from bids2cite.license import update_license
from bids2cite.references import update_references
from bids2cite.utils import bids2cite_log, print_unordered_list, prompt_format

bids_dir = Path(__file__).parent.joinpath("tests", "bids")

log = logging.getLogger("bids2datacite")


def update_bidsignore(bids_dir: Path) -> None:
    log.info("updating .bidsignore")
    bidsignore = bids_dir.joinpath(".bidsignore")
    if not bidsignore.exists():
        with bidsignore.open("w") as f:
            f.write("datacite.yml")
    else:
        with bidsignore.open("r") as f:
            content = f.read()
        if "datacite.yml" not in content:
            with bidsignore.open("a") as f:
                f.write("datacite.yml")


def update_description(datacite: dict, description, skip_prompt) -> dict:
    log.info("update description")
    if description not in [None, ""]:
        datacite["description"] = description
    elif not skip_prompt:
        datacite["description"] = Prompt.ask(
            prompt_format("\nPlease enter a description for the dataset")
        )
        print()
    return datacite


def update_keywords(keywords: list, skip_prompt) -> list:

    log.info("updating keywords")

    if not skip_prompt:
        add_keyword = "yes"
        while add_keyword == "yes":
            print_unordered_list(msg="Current keywords:", items=keywords)
            add_keyword = Prompt.ask(
                prompt_format("Do you want to add more keywords?"),
                default="yes",
                choices=["yes", "no"],
            )
            if add_keyword != "yes":
                break
            keyword = Prompt.ask(prompt_format("Please enter a keyword"))
            keywords.append(keyword)

    return keywords


def update_funding(ds_desc: dict, skip_prompt: bool = False) -> dict:

    log.info("update funding")

    funding = []
    if "Funding" in ds_desc and ds_desc["Funding"] not in [None, []]:
        funding = ds_desc["Funding"]

    if skip_prompt:
        return funding

    add_funding = "yes"
    while add_funding == "yes":
        print_unordered_list(msg="Current fundings:", items=funding)
        add_funding = Prompt.ask(
            prompt_format("Do you want to add more funding?"),
            default="yes",
            choices=["yes", "no"],
        )
        print()
        if add_funding != "yes":
            break

        grant = Prompt.ask(
            prompt_format("Please enter a funding (for example: 'EU, EU.12345')")
        )
        funding.append(grant)
    return funding


def update_authors(ds_desc, skip_prompt):
    authors = []
    if "Authors" in ds_desc:
        for author in ds_desc["Authors"]:
            firstname = author.split(" ")[0]
            lastname = " ".join(author.split(" ")[1:])
            authors.append({"firstname": firstname, "lastname": lastname})

    if skip_prompt:
        return authors
    print_unordered_list(msg="Current authors:", items=authors)

    add_authors = "yes"
    while add_authors == "yes":

        add_funding = Prompt.ask(
            prompt_format("Do you want to add more authors?"),
            default="yes",
            choices=["yes", "no"],
        )
        print()
        if add_funding != "yes":
            break

        author = Prompt.ask(
            prompt_format(
                """Please enter a new author
(for example: 'firstname surname' or 'ORCID:12345678')"""
            )
        )
        firstname = author.split(" ")[0]
        lastname = " ".join(author.split(" ")[1:])
        authors.append({"firstname": firstname, "lastname": lastname})

    return authors


def bids2cite(argv=sys.argv):

    parser = common_parser()

    args = parser.parse_args(argv[1:])

    main(
        bids_dir=Path(args.bids_dir).resolve(),
        description=args.description,
        keywords=args.keywords,
        skip_prompt=args.skip_prompt,
    )


def main(
    bids_dir: Path,
    description: str = None,
    keywords: list = None,
    skip_prompt: bool = False,
):

    # bids_dir, description=None, keywords=None, skip_prompt=False
    # argv=sys.argv

    log = bids2cite_log(name="bids2datacite")

    log.info(f"bids_dir: {bids_dir}")

    ds_descr_file = bids_dir.joinpath("dataset_description.json")
    datacite_file = bids_dir.joinpath("datacite.yml")

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(ds_descr_file, "r") as f:
        ds_desc = json.load(f)

    datacite = {
        "authors": [],
        "title": ds_desc["Name"],
        "description": "",
        "keywords": [],
        "license": {"name": "", "url": ""},
        "funding": [],
        "references": [],
        "resourcetype": "Dataset",
        "templateversion": 1.2,
    }

    datacite = update_description(datacite, description, skip_prompt)

    authors = update_authors(ds_desc, skip_prompt)
    datacite["authors"] = authors

    references = update_references(ds_desc, skip_prompt)
    datacite["references"] = references
    tmp = [ref["citation"] for ref in references]
    ds_desc["ReferencesAndLinks"] = tmp

    funding = update_funding(ds_desc, skip_prompt)
    datacite["funding"] = funding
    ds_desc["Funding"] = funding

    (datacite, ds_desc) = update_license(bids_dir, datacite, ds_desc, skip_prompt)

    keywords = update_keywords(keywords, skip_prompt)
    datacite["keywords"] = keywords

    log.info(f"creating {datacite_file}")
    with open(datacite_file, "w") as f:
        yaml.dump(datacite, f)

    log.info(f"updating {ds_descr_file}")
    with open(ds_descr_file, "w") as f:
        json.dump(ds_desc, f, indent=4)

    update_bidsignore(bids_dir)


class MuhParser(argparse.ArgumentParser):
    """Parser for the main script."""

    def _print_message(self, message: str, file: Optional[IO[str]] = None) -> None:
        print(message, file=file)


def common_parser() -> MuhParser:
    """Execute the main script."""
    parser = MuhParser(
        description="BIDS app to create citation file for your BIDS dataset.",
        epilog="""
        For a more readable version of this help section,
        see the online ".
        """,
    )

    parser.add_argument(
        "bids_dir",
        help="""
        The directory with the input dataset formatted according to the BIDS standard.
        """,
    )
    parser.add_argument(
        "--description", help="Description to add to the dataset.", default="INFO"
    )
    parser.add_argument(
        "--keywords",
        help="List of key words separated by commas to add to the citation file.",
        default="",
    )
    parser.add_argument(
        "--skip_prompt",
        help="If you want to not use the prompt interface.",
        choices=["true", "false"],
        default="false",
    )
    parser.add_argument(
        "--verbosity", help="INFO, WARNING.", choices=["INFO", "WARNING"], default="INFO"
    )
    parser.add_argument(
        "--debug", help="true or false.", choices=["true", "false"], default="false"
    )
    parser.add_argument(
        "--version",
        action="version",
        help="show program's version number and exit",
        version=f"\nbids2cite version {__version__}\n",
    )

    return parser
