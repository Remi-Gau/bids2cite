"""
details on the format of datacite for GIN: https://gin.g-node.org/G-Node/Info/wiki/DOIfile
"""

import json
from pathlib import Path

import crossref_commons.retrieval
import requests
import ruamel.yaml
from rich import print


description = "Example description."

keywords = ["Neuroscience", "Keyword2", "Keyword3"]

output_dir = Path(__file__).parent

ds_descr_file = Path(__file__).parent.joinpath(
    "test", "data", "dataset_description.json"
)


def get_article_info_from_pmid(pmid):
    print(f"getting info from pubmed for pmid: {pmid}")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["result"][pmid]


def main():

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
        ## Optional Fields
        "funding": [],
        "references": [],
        "resourcetype": "Dataset",
        "templateversion": 1.2,
    }

    if "Authors" in ds_descr:
        for author in ds_descr["Authors"]:
            firstname = author.split(" ")[0]
            lastname = " ".join(author.split(" ")[1:])
            datacite["authors"].append({"firstname": firstname, "lastname": lastname})

    if "License" in ds_descr:

        license_name = ds_descr["License"]
        license_url = ""

        if license_name in ["CC0"]:
            license_name = "Creative Commons CC0 1.0 Public Domain Dedication"
            license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
        elif license_name in ["CC-BY-NC-SA-4.0"]:
            license_name = "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public Domain Dedication"
            license_url = "https://creativecommons.org/licenses/by-nc-sa/4.0/"

        datacite["license"]["name"] = license_name
        datacite["license"]["url"] = license_url

    if "ReferencesAndLinks" in ds_descr:
        for reference in ds_descr["ReferencesAndLinks"]:

            this_reference = {"citation": reference, "reftype": "IsSupplementTo"}

            article_info = None
            pmid = None
            doi = None

            if "www.ncbi.nlm.nih.gov/pubmed/" in reference:
                pmid = reference.split("www.ncbi.nlm.nih.gov/pubmed/")[1]
                this_reference["id"] = f"pmid:{pmid}"
                article_info = get_article_info_from_pmid(pmid)
                title = article_info["title"]
                journal = article_info["source"]
                year = article_info["pubdate"].split(" ")[0]
                authors = []
                for i, author in enumerate(article_info["authors"]):
                    authors.append(f"{author['name']}")
                    if i > 3:
                        authors.append("et al.")
                        break

            elif "doi:" in reference:
                doi = reference.split("doi:")[1]
            elif "https://doi.org/:" in reference:
                doi = reference.split("https://doi.org/")[1]
            if doi is not None:
                this_reference["id"] = f"doi:{doi}"
                article_info = crossref_commons.retrieval.get_publication_as_json(doi)
                title = article_info["title"][0]
                journal = article_info["short-container-title"][0]
                year = article_info["created"]["date-parts"][0][0]
                authors = []
                for i, author in enumerate(article_info["author"]):
                    authors.append(f"{author['given']}, {author['family']}")
                    if i > 3:
                        authors.append("et al.")
                        break

            if article_info is not None:
                print(article_info)                    

            if doi is not None or pmid is not None:
                this_reference[
                    "citation"
                ] = f"{', '.join(authors)}; {title}; {journal}; {year}"

            datacite["references"].append(this_reference)

    if "Funding" in ds_descr:
        for grant in ds_descr["Funding"]:
            datacite["funding"].append(grant)

    if description not in [None, ""]:
        datacite["description"] = description

    if keywords not in [None, []]:
        for word in keywords:
            datacite["keywords"].append(word)

    datacite_file = output_dir.joinpath("datacite.yml")

    with open(datacite_file, "w") as f:
        yaml.dump(datacite, f)


if __name__ == "__main__":
    main()
