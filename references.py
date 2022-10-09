import logging

from utils import prompt_format, print_unordered_list



from rich.prompt import Prompt
from rich import print

import crossref_commons.retrieval
import requests

log = logging.getLogger("bids2datacite")

def get_article_id(reference):
    """Find the article DOI or PMID"""

    article_id = ""

    if "pmid:" in reference:
        pmid = reference.split("pmid:")[1]
        article_id = f"pmid:{pmid}"
    elif "www.ncbi.nlm.nih.gov/pubmed/" in reference:
        pmid = reference.split("www.ncbi.nlm.nih.gov/pubmed/")[1]
        article_id = f"pmid:{pmid}"

    elif "doi:" in reference:
        doi = reference.split("doi:")[1]
        article_id = f"doi:{doi}"
    elif "https://doi.org/:" in reference:
        doi = reference.split("https://doi.org/")[1]
        article_id = f"doi:{doi}"

    else:
        log.warning(f"No PMID or DOI found in:\n{reference}")

    return article_id


def get_reference_details(reference):

    this_reference = {"citation": reference}

    article_info = None

    article_id = get_article_id(reference)
    if article_id.startswith("pmid"):
        article_info = get_article_info_from_pmid(article_id.split("pmid:")[1])
    elif article_id.startswith("doi"):
        article_info = get_article_info_from_doi(article_id.split("doi:")[1])

    if article_info is not None:
        this_reference["id"] = article_id
        this_reference[
            "citation"
        ] = f"{', '.join(article_info['authors'])}; {article_info['title']}; {article_info['journal']}; {article_info['year']}; {article_id}"

    this_reference["reftype"] = "IsSupplementTo"

    return this_reference


def update_references(ds_descr: dict, skip_prompt: bool = False) -> list:

    log.info("update references")

    references = []

    if "ReferencesAndLinks" in ds_descr:
        for reference in ds_descr["ReferencesAndLinks"]:

            this_reference = get_reference_details(reference)

            references.append(this_reference)

    if skip_prompt:
        return references

    items = [x["citation"] for x in references]
    print_unordered_list(msg="Current references:", items=items)

    add_references = "yes"
    while add_references == "yes":

        add_funding = Prompt.ask(
            prompt_format("Do you want to add more references?"),
            default="yes",
            choices=["yes", "no"],
        )
        print()
        if add_funding != "yes":
            break

        reference = Prompt.ask(
            prompt_format(
                """Please enter a references
(for example: 'doi:10.1016/j.neuroimage.2019.116081' or 'pmid:12345678')"""
            )
        )
        this_reference = get_reference_details(reference)
        
        if "id" in this_reference:
            references.append(this_reference)
            items = [x["citation"] for x in references]
            print_unordered_list(msg="Current references:", items=items)

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
        "doi": content["DOI"],
    }


def get_article_info_from_pmid(pmid: str):

    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"

    response = requests.get(url)

    if response.status_code == 200:

        content = response.json()["result"]
        if pmid in content:
            content = content[pmid]
        else:
            print(f"[red]No article matching pmid:{pmid}[/red]")
            return None

        authors = []
        for i, author in enumerate(content["authors"]):
            authors.append(f"{author['name']}")
            if i > 3:
                authors.append("et al.")
                break

        for x in content["articleids"]: 
            if x["idtype"] == "doi":
                doi  = x["value"]  

        return {
            "title": content["title"],
            "journal": content["fulljournalname"],
            "year": content["pubdate"].split(" ")[0],
            "authors": authors,
            "doi": doi,
        }
    else:
        log.warning(f"No article matching pmid:{pmid}")
        return None
