"""
Add a datacite to your BIDS dataset.

details on the format of datacite for GIN: https://gin.g-node.org/G-Node/Info/wiki/DOIfile
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any
from typing import IO

import ruamel.yaml
from cffconvert.cli.create_citation import create_citation
from cffconvert.cli.validate_or_write_output import validate_or_write_output
from rich import print
from rich.prompt import Prompt

from . import _version

__version__ = _version.get_versions()["version"]

from bids2cite.authors import update_authors, authors_for_desc, authors_for_citation
from bids2cite.license import update_license, supported_licenses
from bids2cite.references import (
    update_references,
    references_for_datacite,
    references_for_citation,
)
from bids2cite.utils import (
    bids2cite_log,
    print_unordered_list,
    prompt_format,
    log_levels,
    default_log_level,
)

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


def update_description(description: str | None = None, skip_prompt: bool = False) -> str:
    """Update the description of the dataset."""
    log.info("update description")
    if description not in [None, ""]:
        description = description
    elif not skip_prompt:
        description = Prompt.ask(
            prompt_format("\nPlease enter a description for the dataset")
        )
        print()
    if description is None:
        description = ""
    return description


def update_keywords(
    keywords: list[Any] | None = None, skip_prompt: bool = False
) -> list[str]:
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
            tmp = new_keywords.strip().split(",")
            for keyword in tmp:
                keywords.append(keyword.strip())

    return keywords


def update_funding(ds_desc: dict[str, Any], skip_prompt: bool = False) -> list[str]:
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


def cli(argv: Any = sys.argv) -> None:
    """Execute the main script for CLI."""
    log = bids2cite_log(name="bids2datacite")

    parser = common_parser()

    args = parser.parse_args(argv[1:])

    # https://stackoverflow.com/a/53293042/14223310
    log_level = log_levels().index(default_log_level())
    # For each "-v" flag, adjust the logging verbosity accordingly
    # making sure to clamp off the value from 0 to 4, inclusive of both
    for adjustment in args.log_level or ():
        log_level = min(len(log_levels()) - 1, max(log_level + adjustment, 0))
    log_level_name = log_levels()[log_level]
    log.setLevel(log_level_name)

    tmp = args.keywords.split(",") if args.keywords else []
    keywords = [x.strip() for x in tmp]

    authors_file = None
    if args.authors_file not in ["", None]:
        authors_file = Path(args.authors_file)
        if not authors_file.exists():
            authors_file = None

    licenses = supported_licenses()
    licenses_choices = list(licenses.keys())
    if args.license and args.license not in licenses_choices:
        log.error(
            f"""License '{args.license}' not supported.
        Supported types are {licenses_choices}"""
        )
        sys.exit(1)

    if args.output_format not in ["datacite", "citation"]:
        log.error(
            f"""Format '{args.output_format}' not supported.
        Supported types are 'datacite' and 'citation'"""
        )
        sys.exit(1)

    bids2cite(
        bids_dir=Path(args.bids_dir).resolve(),
        output_format=args.output_format,
        description=args.description,
        keywords=keywords,
        license=args.license,
        skip_prompt=args.skip_prompt,
        authors_file=authors_file,
    )


def bids2cite(
    bids_dir: Path,
    output_format: str,
    description: str | None = None,
    keywords: list[str] | None = None,
    license: str | None = None,
    skip_prompt: bool = False,
    authors_file: Path | None = None,
) -> None:  # sourcery skip: merge-dict-assign
    """Create a datacite.yml file for a BIDS dataset."""
    log = bids2cite_log(name="bids2datacite")

    log.info(f"bids_dir: {bids_dir}")

    output_dir = bids_dir.joinpath("derivatives", "bids2cite")
    output_dir.mkdir(exist_ok=True, parents=True)

    ds_descr_file = bids_dir.joinpath("dataset_description.json")

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    if not ds_descr_file.exists():
        log.error(f"dataset_description.json not found in {bids_dir}")
        sys.exit(1)

    with open(ds_descr_file) as f:
        ds_desc: dict[str, Any] = json.load(f)

    description = update_description(description, skip_prompt)

    authors = update_authors(ds_desc, skip_prompt, authors_file)

    references = update_references(ds_desc, skip_prompt)

    funding = update_funding(ds_desc, skip_prompt)

    if license is not None:
        ds_desc["License"] = license
    (license_name, license_url) = update_license(output_dir, ds_desc, skip_prompt)

    keywords = update_keywords(keywords, skip_prompt)

    update_bidsignore(bids_dir)

    """dataset_description.json"""

    ds_desc["authors"] = authors_for_desc(authors)
    ds_desc["ReferencesAndLinks"] = references_for_datacite(references)
    ds_desc["Funding"] = funding
    ds_desc["License"] = license_name

    output_file = output_dir.joinpath("dataset_description.json")
    log.info(f"updating {output_file}")
    with open(output_file, "w") as f:
        json.dump(ds_desc, f, indent=4)

    """datacite.yml"""
    if output_format == "datacite":
        datacite: dict[str, Any] = {
            "authors": [],
            "title": ds_desc["Name"],
            "description": "",
            "keywords": [],
            "license": {"name": "", "url": ""},
            "resourcetype": "Dataset",
            "references": [],
            "templateversion": 1.2,
            "funding": [],
        }

        datacite["description"] = description
        datacite["authors"] = authors
        datacite["references"] = references
        datacite["funding"] = funding
        datacite["license"]["name"] = license_name
        datacite["license"]["url"] = license_url
        datacite["keywords"] = keywords

        datacite_file = output_dir.joinpath("datacite.yml")
        log.info(f"creating {datacite_file}")
        with open(datacite_file, "w") as f:
            yaml.dump(datacite, f)

    """CITATION.cff"""
    if output_format == "citation":
        citation: dict[str, Any] = {
            "authors": [],
            "title": ds_desc["Name"],
            "message": "",
            "license": "",
            "type": "dataset",
            "identifiers": [],
            "cff-version": "1.2.0",
        }

        if keywords not in [None, []]:
            citation["keywords"] = keywords
        citation["license"] = license_name
        citation["authors"] = authors_for_citation(authors)
        citation["message"] = description
        if description == "":
            citation["message"] = "TODO"
        citation["identifiers"] = references_for_citation(references)

        citation_file = output_dir.joinpath("CITATION.cff")
        log.info(f"creating {citation_file}")
        with open(citation_file, "w") as f:
            yaml.dump(citation, f)

        citation = create_citation(infile=citation_file, url=None)
        validate_or_write_output(
            outfile=None, outputformat=None, validate_only=True, citation=citation
        )


class MuhParser(argparse.ArgumentParser):
    """Parser for the main script."""

    def _print_message(self, message: str, file: IO[str] | None = None) -> None:
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
        "-o",
        "--output-format",
        help="""Choose the output format between 'citation' for CITATION.cff
        and 'datacite' for datacite.yml.""",
        default="datacite",
    )
    parser.add_argument(
        "-d", "--description", help="Description to add to the dataset.", default=""
    )
    parser.add_argument(
        "-k",
        "--keywords",
        help="List of key words separated by commas to add to the citation file.",
        default="",
    )
    licenses = supported_licenses()
    licenses_choices = list(licenses.keys())
    parser.add_argument(
        "-l",
        "--license",
        help=f"License to add to choose from: {licenses_choices}",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--skip-prompt",
        help="If you do not want to use the prompt interface.",
        action="store_true",
    )
    parser.add_argument(
        "--authors-file",
        help=""".tsv file containing list of potential new authors with the columns:
                first_name, last_name, ORCID (optional), affiliation (optional)""",
        default="",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        dest="log_level",
        action="append_const",
        const=-1,
    )
    parser.add_argument(
        "--version",
        action="version",
        help="show program's version number and exit",
        version=f"{__version__}",
    )

    return parser
