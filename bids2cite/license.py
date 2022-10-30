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
    if license_type not in ["CC0-1.0", "CC0"]:
        return

    url = "https://api.github.com/licenses/cc0-1.0"
    response = requests.get(url)

    if response.status_code == 200:
        license_file = bids_dir.joinpath("LICENSE")
        log.info(f"creating {license_file}")
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

    name, url = identify_license(ds_desc)

    if name == "CC0-1.0" and not license_file_present:
        add_license_file("CC0-1.0", bids_dir)
        return name, url

    if not license_file_present:
        log.warning(
            """There is no license file in the dataset directory.
Please add a license that matches that of the dataset_description.json file.
"""
        )

    if name == "":

        if license_file_present:
            log.warning(
                """License file found in the dataset but not in the dataset_description.json file."""
            )

        if not skip_prompt:
            (name, url) = manually_add_license(bids_dir, ds_desc, skip_prompt)

    return name, url


def identify_license(ds_desc: dict[str, Any]) -> tuple[str, str]:
    """Identify the license of the dataset."""
    name = ds_desc.get("License", "")
    url = ""

    if name not in [""]:

        if name.lower() in ["cc0", "cc0-1.0", "creative commons zero"]:
            name = "CC0-1.0"
            url = "https://creativecommons.org/publicdomain/zero/1.0/"
            log.info(f"License {name} found.")

        elif name in [
            "CC-BY-NC-SA-4.0",
            "Attribution-NonCommercial-ShareAlike 4.0",
        ]:
            name = "CC-BY-NC-SA-4.0"
            url = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
            log.info(f"License {name} found.")

        else:
            log.warning(f"License {name} not recognized.")

    return name, url


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
1. CC0-1.0
2. None"""
        )
        license = Prompt.ask(
            prompt_format("Please choose a license."),
            choices=["1", "2"],
            default=1,
        )
        if license == "1":
            add_license_file("CC0-1.0", bids_dir)
            ds_desc["License"] = "CC0-1.0"
            (name, url) = update_license(bids_dir, ds_desc, skip_prompt)

    return name, url
