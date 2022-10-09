"""
Add a datacite to your BIDS dataset.

details on the format of datacite for GIN: https://gin.g-node.org/G-Node/Info/wiki/DOIfile
"""
import argparse
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any
from typing import IO
from typing import List
from typing import Optional

import ruamel.yaml
from rich import print
from rich.prompt import Prompt

from . import _version

__version__ = _version.get_versions()["version"]

from bids2cite.authors import update_authors
from bids2cite.license import update_license
from bids2cite.references import update_references
from bids2cite.utils import bids2cite_log, print_unordered_list, prompt_format

bids_dir = Path(__file__).parent.joinpath("tests", "bids")

log = logging.getLogger("bids2datacite")


def update_bidsignore(bids_dir: Path) -> None:
    """Update the .bidsignore file."""
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


def update_description(
    datacite: dict, description: Optional[str] = None, skip_prompt: bool = False
) -> dict:
    """Update the description of the dataset."""
    log.info("update description")
    if description not in [None, ""]:
        datacite["description"] = description
    elif not skip_prompt:
        datacite["description"] = Prompt.ask(
            prompt_format("\nPlease enter a description for the dataset")
        )
        print()
    return datacite


def update_keywords(
    keywords: Optional[List[Any]] = None, skip_prompt: bool = False
) -> list:
    """Update the keywords of the dataset."""
    log.info("updating keywords")

    if keywords is None:
        keywords = []

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
            new_keywords = Prompt.ask(
                prompt_format(
                    """Please enter keywords separated by comma
(for example: 'keyword1, keyword2')"""
                )
            )
            new_keywords = new_keywords.strip().split(",")
            for keyword in new_keywords:
                keywords.append(keyword.strip())

    return keywords


def update_funding(ds_desc: dict, skip_prompt: bool = False) -> List[str]:
    """Update the funding of the dataset."""
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


def bids2cite(argv=sys.argv):
    """Execute the main script for CLI."""

    log = bids2cite_log(name="bids2datacite")

    parser = common_parser()

    args = parser.parse_args(argv[1:])

    skip_prompt = args.skip_prompt == "true"

    log.setLevel(args.verbosity)

    tmp = args.keywords.split(",") if args.keywords else []
    keywords = [x.strip() for x in tmp]

    authors_file = None
    if args.authors_file not in ["", None]:
        authors_file = Path(args.authors_file)
        if not authors_file.exists():
            authors_file = None

    main(
        bids_dir=Path(args.bids_dir).resolve(),
        description=args.description,
        keywords=keywords,
        skip_prompt=skip_prompt,
        authors_file=authors_file,
    )


def main(
    bids_dir: Path,
    description: str = None,
    keywords: list = None,
    skip_prompt: bool = False,
    authors_file: Path = None,
):
    """Create a datacite.yml file for a BIDS dataset."""
    log = bids2cite_log(name="bids2datacite")

    log.info(f"bids_dir: {bids_dir}")

    ds_descr_file = bids_dir.joinpath("dataset_description.json")
    datacite_file = bids_dir.joinpath("datacite.yml")

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    if not ds_descr_file.exists():
        log.error(f"dataset_description.json not found in {bids_dir}")
        sys.exit(1)

    shutil.copyfile(
        ds_descr_file, ds_descr_file.with_name("dataset_description.json.bak")
    )
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

    authors = update_authors(ds_desc, skip_prompt, authors_file)
    datacite["authors"] = authors
    tmp = [f"{x['firstname']} {x['lastname']}" for x in authors]
    ds_desc["Authors"] = tmp

    references = update_references(ds_desc, skip_prompt)
    datacite["references"] = references
    tmp = [x["citation"] for x in references]
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
        "--description", help="Description to add to the dataset.", default=""
    )
    parser.add_argument(
        "--keywords",
        help="List of key words separated by commas to add to the citation file.",
        default="",
    )
    parser.add_argument(
        "--skip-prompt",
        help="Set to 'false' if you want to not use the prompt interface.",
        choices=["true", "false"],
        default="false",
    )
    parser.add_argument(
        "--authors-file",
        help=""".tsv file containing list of potential new authors with the columns:
                    - first_name\n
                    - last_name\n
                    - ORCID (optional)\n
                    - affiliation (optional)""",
        default="",
    )
    parser.add_argument(
        "--verbosity",
        help="One of: DEBUG, INFO, WARNING",
        choices=["DEBUG", "INFO", "WARNING"],
        default="INFO",
    )
    parser.add_argument(
        "--version",
        action="version",
        help="show program's version number and exit",
        version=f"\nbids2cite version {__version__}\n",
    )

    return parser
