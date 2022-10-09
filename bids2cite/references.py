"""Deal with references."""
import logging

import crossref_commons.retrieval  # type: ignore
import requests  # type: ignore
from rich import print
from rich.prompt import Prompt

from bids2cite.utils import print_unordered_list
from bids2cite.utils import prompt_format

log = logging.getLogger("bids2datacite")


def get_reference_id(reference: str):
    """Find the reference DOI or PMID."""
    ref_id = ""

    if "pmid:" in reference:
        pmid = reference.split("pmid:")[1]
        ref_id = f"pmid:{pmid}"
    elif "ncbi.nlm.nih.gov/pubmed/" in reference:
        pmid = reference.split("ncbi.nlm.nih.gov/pubmed/")[1]
        ref_id = f"pmid:{pmid}"

    elif "doi:" in reference:
        doi = reference.split("doi:")[1]
        ref_id = f"doi:{doi}"
    elif "doi.org/" in reference:
        doi = reference.split("doi.org/")[1]
        ref_id = f"doi:{doi}"

    if ref_id == "":
        log.warning(f"No PMID or DOI found in:\n{reference}")

    ref_id = ref_id.strip()

    return ref_id


def get_reference_details(reference: str):
    """Get reference details."""
    this_reference = {"citation": reference}

    info = None

    ref_id = get_reference_id(reference)
    if ref_id.startswith("pmid"):
        info = get_reference_info_from_pmid(ref_id.split("pmid:")[1])
    elif ref_id.startswith("doi"):
        info = get_reference_info_from_doi(ref_id.split("doi:")[1])

    if info is not None:
        this_reference["id"] = ref_id
        this_reference[
            "citation"
        ] = f"""{', '.join(info['authors'])}; {info['title']}; {info['journal']}; {info['year']}; {ref_id}"""

    this_reference["reftype"] = "IsSupplementTo"

    return this_reference


def update_references(ds_desc: dict, skip_prompt: bool = False) -> list:
    """Update references based on dataset description."""
    log.info("update references")

    references = []

    if "ReferencesAndLinks" in ds_desc:
        for reference in ds_desc["ReferencesAndLinks"]:

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


def get_reference_info_from_doi(doi: str):
    """Get reference info from DOI."""
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


def get_reference_info_from_pmid(pmid: str):
    """Get reference info from PubMed."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    url = f"{base_url}?db=pubmed&id={pmid}&retmode=json"

    response = requests.get(url)

    if response.status_code == 200:

        content = response.json()["result"]
        if pmid in content:
            content = content[pmid]
        else:
            log.warning(f"No reference matching pmid:{pmid} at url {url}")
            return None

        authors = []
        for i, author in enumerate(content["authors"]):
            authors.append(f"{author['name']}")
            if i > 3:
                authors.append("et al.")
                break

        for x in content["articleids"]:
            if x["idtype"] == "doi":
                doi = x["value"]

        return {
            "title": content["title"],
            "journal": content["fulljournalname"],
            "year": content["pubdate"].split(" ")[0],
            "authors": authors,
            "doi": doi,
        }
    else:
        log.warning(f"No reference matching pmid:{pmid}")
        return None
