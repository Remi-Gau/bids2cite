"""
adds a datacite to your BIDS dataset
details on the format of datacite for GIN: https://gin.g-node.org/G-Node/Info/wiki/DOIfile
"""

import json
import logging
from pathlib import Path

import requests
import ruamel.yaml
from rich import print
from rich.logging import RichHandler
from rich.prompt import Prompt
from rich.traceback import install

from references import update_references
from utils import print_unordered_list, prompt_format

description = ""
keywords = ["foo", "bar"]

skip_prompt = False

bids_dir = Path(__file__).parent.joinpath("tests", "bids")


log = logging.getLogger("bids2datacite")


def bids2datacite_log(name=None):
    """Create log.

    :param name: _description_, defaults to None
    :type name: _type_, optional

    :return: _description_
    :rtype: _type_
    """
    # let rich print the traceback
    install(show_locals=True)

    FORMAT = "bids2datacite - %(asctime)s - %(levelname)s - %(message)s"

    log_level = "INFO"

    if not name:
        name = "rich"

    logging.basicConfig(
        level=log_level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    return logging.getLogger(name)


def update_bidsignore(bids_dir: Path) -> None:
    log.info("updating/creating .bidsignore file to ignore datacite.yml")
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


def update_description(datacite: dict, description) -> dict:
    log.info("update description")
    if description not in [None, ""]:
        datacite["description"] = description
    else:
        datacite["description"] = Prompt.ask(
            prompt_format("\nPlease enter a description for the dataset")
        )
        print()
    return datacite


def add_license_file(license_type: str, bids_dir: Path) -> None:

    license_file = bids_dir.joinpath("LICENSE")

    log.info(f"creating {license_file}")

    if license_type == "CC0":
        url = "https://api.github.com/licenses/cc0-1.0"

    license_content = requests.get(url).json()["body"]
    with license_file.open("w") as f:
        f.write(license_content)


def update_keywords(keywords: list) -> list:

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


def update_license(datacite: dict, ds_descr: dict):

    log.info("update license")

    license_file_present = "LICENSE" in bids_dir.glob("LICENSE*")

    if "License" in ds_descr and ds_descr["License"] not in [None, ""]:

        license_name = ds_descr["License"]
        license_url = ""

        if license_name in ["CC0", "cc0-1.0"]:
            license_name = "Creative Commons Zero 1.0 Public Domain Dedication"
            license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
            if not license_file_present:
                add_license_file("CC0", bids_dir)
                license_file_present = True

        elif license_name in ["CC-BY-NC-SA-4.0"]:
            license_name = """
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 Public Domain Dedication
"""
            license_url = "https://creativecommons.org/licenses/by-nc-sa/4.0/"

        datacite["license"]["name"] = license_name
        datacite["license"]["url"] = license_url

        if not license_file_present:
            print(
                """[red]There is no license file in the dataset directory.
Please add a license that matches that of the dataset_description.json file.[/red]
"""
            )

        return datacite, ds_descr

    if not license_file_present:

        if not skip_prompt:

            add_license = Prompt.ask(
                prompt_format("Do you want to add a license?"),
                default="yes",
                choices=["yes", "no"],
            )
            print()
            if add_license == "yes":
                print(
                    """Possible licences:
1. CC0
2. None"""
                )
                license = Prompt.ask(
                    prompt_format("Please choose a license."),
                    choices=["1", "2"],
                    default=1,
                )
                if license == "1":
                    add_license_file("CC0", bids_dir)
                    ds_descr["License"] = "CC0"
                    (datacite, ds_descr) = update_license(datacite, ds_descr)

        return datacite, ds_descr


def update_funding(ds_descr: dict, skip_prompt: bool = False) -> dict:

    log.info("update funding")

    funding = []
    if "Funding" in ds_descr and ds_descr["Funding"] not in [None, []]:
        funding = ds_descr["Funding"]

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


def main(bids_dir, description=None, keywords=None, skip_prompt=False):

    log = bids2datacite_log(name="bids2datacite")

    log.info(f"bids_dir: {bids_dir}")

    ds_descr_file = bids_dir.joinpath("dataset_description.json")
    datacite_file = bids_dir.joinpath("datacite.yml")

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(ds_descr_file, "r") as f:
        ds_descr = json.load(f)

    datacite = {
        "authors": [],
        "title": ds_descr["Name"],
        "description": "",
        "keywords": [],
        "license": {"name": "", "url": ""},
        "funding": [],
        "references": [],
        "resourcetype": "Dataset",
        "templateversion": 1.2,
    }

    datacite = update_description(datacite, description)

    authors = []
    if "Authors" in ds_descr:
        for author in ds_descr["Authors"]:
            firstname = author.split(" ")[0]
            lastname = " ".join(author.split(" ")[1:])
            authors.append({"firstname": firstname, "lastname": lastname})
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

    datacite["authors"] = authors

    references = update_references(ds_descr, skip_prompt)
    datacite["references"] = references
    tmp = [ref["citation"] for ref in references]
    ds_descr["ReferencesAndLinks"] = tmp

    funding = update_funding(ds_descr, skip_prompt)
    datacite["funding"] = funding
    ds_descr["Funding"] = funding

    (datacite, ds_descr) = update_license(datacite, ds_descr)

    keywords = update_keywords(keywords)
    datacite["keywords"] = keywords

    log.info(f"writing {datacite_file}")
    with open(datacite_file, "w") as f:
        yaml.dump(datacite, f)

    log.info(f"updating {ds_descr_file}")
    with open(ds_descr_file, "w") as f:
        json.dump(ds_descr, f, indent=4)

    update_bidsignore(bids_dir)


if __name__ == "__main__":
    main(
        bids_dir=bids_dir,
        description=description,
        keywords=keywords,
        skip_prompt=skip_prompt,
    )
