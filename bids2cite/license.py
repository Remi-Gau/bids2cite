"""Deals with license information."""
import logging
from pathlib import Path

import requests  # type: ignore
from rich import print
from rich.prompt import Prompt

from bids2cite.utils import prompt_format

log = logging.getLogger("bids2datacite")


def add_license_file(license_type: str, bids_dir: Path) -> None:
    """Add a license file to the dataset directory."""
    license_file = bids_dir.joinpath("LICENSE")

    log.info(f"creating {license_file}")

    if license_type == "CC0":
        url = "https://api.github.com/licenses/cc0-1.0"

    license_content = requests.get(url).json()["body"]
    with license_file.open("w") as f:
        f.write(license_content)


def update_license(
    bids_dir: Path, datacite: dict, ds_desc: dict, skip_prompt: bool = False
):
    """Update the license of the dataset."""
    log.info("update license")

    license_file_present = "LICENSE" in bids_dir.glob("LICENSE*")  # type: ignore

    if "License" in ds_desc and ds_desc["License"] not in [None, ""]:

        license_name = ds_desc["License"]
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

        return datacite, ds_desc

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
                    ds_desc["License"] = "CC0"
                    (datacite, ds_desc) = update_license(
                        bids_dir, datacite, ds_desc, skip_prompt
                    )

        return datacite, ds_desc
