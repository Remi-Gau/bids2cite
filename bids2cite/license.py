"""Deals with license information."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import requests
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

    response = requests.get(url)

    if response.status_code == 200:
        license_content = response.json()["body"]
        with license_file.open("w") as f:
            f.write(license_content)
    else:
        log.warning(f"Could not get license from {url}")


def update_license(
    bids_dir: Path,
    ds_desc: dict[str, Any],
    skip_prompt: bool = False,
) -> tuple[str, str]:
    """Update the license of the dataset."""
    log.info("update license")

    license_file_present = "LICENSE" in bids_dir.glob("LICENSE*")  # type: ignore

    license_name = ds_desc.get("License")
    license_url = ""

    if license_name not in [None, ""]:

        if license_name in ["CC0", "cc0-1.0", "Creative Commons Zero"]:
            license_name = "Creative Commons Zero 1.0 Public Domain Dedication"
            license_url = "https://creativecommons.org/publicdomain/zero/1.0/"

            if not license_file_present:
                add_license_file("CC0", bids_dir)
                return license_name, license_url

        elif license_name in [
            "CC-BY-NC-SA-4.0",
            "Attribution-NonCommercial-ShareAlike 4.0",
        ]:
            license_name = """
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 Public Domain Dedication
"""
            license_url = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
            return license_name, license_url

        if not license_file_present:
            log.warning(
                """There is no license file in the dataset directory.
Please add a license that matches that of the dataset_description.json file.
"""
            )

    else:

        if license_file_present:
            log.warning(
                """License file found in the dataset but not in the dataset_description.json file."""
            )

        if not skip_prompt:
            (license_name, license_url) = manually_add_license(
                bids_dir, ds_desc, skip_prompt
            )

    if license_name is None:
        license_name = ""

    return license_name, license_url


def manually_add_license(
    bids_dir: Path,
    ds_desc: dict[str, Any],
    skip_prompt: bool = False,
) -> tuple[str, str]:
    """Prompt user for what license to add."""
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
            (license_name, license_url) = update_license(bids_dir, ds_desc, skip_prompt)

    return license_name, license_url
