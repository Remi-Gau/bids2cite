"""
adds a datacite to your BIDS dataset
details on the format of datacite for GIN: https://gin.g-node.org/G-Node/Info/wiki/DOIfile
"""

from copy import deepcopy
import json
from pathlib import Path

import crossref_commons.retrieval
import requests
import ruamel.yaml
from rich import print
from rich.prompt import Prompt

description = "test"
keywords = ["foo", "bar"]

skip_prompt = False

bids_dir = Path(__file__).parent.joinpath("test", "bids")


def update_bidsignore(bids_dir: Path) -> None:
    """update bidsignore file to ignore datacite.yml"""
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


def prompt_format(msg: str) -> str:
    return f"[bold]{msg}[/bold]"


def update_description(datacite: dict) -> dict:
    if description not in [None, ""]:
        datacite["description"] = description
    else:
        datacite["description"] = Prompt.ask(
            prompt_format("Please enter a description for the dataset")
        )
    return datacite


def add_license_file(license_type: str, bids_dir: Path) -> None:
    license_file = bids_dir.joinpath("LICENSE")

    if license_type == "CC0":
        url = "https://api.github.com/licenses/cc0-1.0"

    license_content = requests.get(url).json()["body"]
    with license_file.open("w") as f:
        f.write(license_content)


def update_keywords(keywords: list) -> list:

    if not skip_prompt:
        add_keyword = "yes"
        while add_keyword == "yes":
            print(f"Current keywords: {keywords}")
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

    license_file_present = "LICENSE" in bids_dir.glob("LICENSE*")

    if "License" in ds_descr and ds_descr["License"] not in [None, ""]:

        license_name = ds_descr["License"]
        license_url = ""

        if license_name in ["CC0", "cc0-1.0"]:
            license_name = (
                "Creative Commons Zero v1.0 Universal Public Domain Dedication"
            )
            license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
            if not license_file_present:
                add_license_file("CC0", bids_dir)
                license_file_present = True

        elif license_name in ["CC-BY-NC-SA-4.0"]:
            license_name = "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public Domain Dedication"
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

    funding = []
    if "Funding" in ds_descr and ds_descr["Funding"] not in [None, []]:
        funding = ds_descr["Funding"]

    if skip_prompt:
        return funding

    add_funding = "yes"
    while add_funding == "yes":
        print("Current fundings")
        for i, grant in enumerate(funding):
            print(f"{i+1}. {grant}")

        add_funding = Prompt.ask(
            prompt_format("Do you want to add more funding?"),
            default="yes",
            choices=["yes", "no"],
        )
        if add_funding == "yes":
            grant = Prompt.ask(
                prompt_format("Please enter a funding (for exmaple: 'EU, EU.12345')")
            )
        else:
            break

    return funding


def update_references(ds_descr: dict) -> list:

    references = []

    if "ReferencesAndLinks" in ds_descr:
        for reference in ds_descr["ReferencesAndLinks"]:

            this_reference = {"citation": reference}

            pmid = None
            doi = None

            if "pmid:" in reference:
                pmid = reference.split("pmid:")[1]
            elif "www.ncbi.nlm.nih.gov/pubmed/" in reference:
                pmid = reference.split("www.ncbi.nlm.nih.gov/pubmed/")[1]
            if pmid is not None:
                article_info = get_article_info_from_pmid(pmid)

            elif "doi:" in reference:
                doi = reference.split("doi:")[1]
            elif "https://doi.org/:" in reference:
                doi = reference.split("https://doi.org/")[1]
            if doi is not None:
                article_info = get_article_info_from_doi(doi)

            if doi is not None or pmid is not None:
                this_reference["id"] = article_info["id"]
                this_reference[
                    "citation"
                ] = f"""{', '.join(article_info['authors'])}; 
{article_info['title']}; 
{article_info['journal']}; 
{article_info['year']}; 
{article_info['id']}"""

            this_reference["reftype"] = "IsSupplementTo"

            references.append(this_reference)

    return references


def get_article_info_from_doi(doi: str):

    content = crossref_commons.retrieval.get_publication_as_json(doi)

    authors = []
    for i, author in enumerate(content["author"]):
        authors.append(f"{author['given']}, {author['family']}")
        if i > 3:
            authors.append("et al.")
            break

    return {
        "title": content["title"][0],
        "journal": content["short-container-title"][0],
        "year": content["created"]["date-parts"][0][0],
        "authors": authors,
        "id": f"doi:{doi}",
    }


def get_article_info_from_pmid(pmid: str):

    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"

    response = requests.get(url)

    if response.status_code == 200:

        content = response.json()["result"][pmid]

        authors = []
        for i, author in enumerate(content["authors"]):
            authors.append(f"{author['name']}")
            if i > 3:
                authors.append("et al.")
                break

        return {
            "title": content["title"],
            "journal": content["source"],
            "year": content["pubdate"].split(" ")[0],
            "authors": authors,
            "id": f"pmid:{pmid}",
        }


def main(keywords):

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

    datacite = update_description(datacite)

    if "Authors" in ds_descr:
        for author in ds_descr["Authors"]:
            firstname = author.split(" ")[0]
            lastname = " ".join(author.split(" ")[1:])
            datacite["authors"].append({"firstname": firstname, "lastname": lastname})

    references = update_references(ds_descr)
    datacite["references"] = references

    funding = update_funding(ds_descr, skip_prompt)
    datacite["funding"] = funding
    ds_descr["Funding"] = funding

    (datacite, ds_descr) = update_license(datacite, ds_descr)

    keywords = update_keywords(keywords)
    datacite["keywords"] = keywords

    with open(datacite_file, "w") as f:
        yaml.dump(datacite, f)

    with open(ds_descr_file, "w") as f:
        json.dump(ds_descr, f, indent=4)

    update_bidsignore(bids_dir)


if __name__ == "__main__":
    main(keywords)
