"""Deals with license information."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import requests
from rich import print
from rich.prompt import Prompt

from bids2cite.utils import print_ordered_list
from bids2cite.utils import prompt_format

log = logging.getLogger("bids2datacite")


def supported_licenses() -> dict[str, dict[str, str | list[str | None]]]:
    """Return a list of supported licenses."""
    return {
        "CC0-1.0": {
            "name": "CC0-1.0",
            "values": ["cc0", "cc0-1.0", "creative commons zero"],
            "url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "api_url": "https://api.github.com/licenses/cc0-1.0",
        },
        "CC-BY-NC-SA-4.0": {
            "name": "CC-BY-NC-SA-4.0",
            "values": [
                "cc-by-nc-sa-4.0",
                "attribution-noncommercial-sharealike 4.0",
            ],
            "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        },
        "PDDL-1.0": {
            "name": "PDDL-1.0",
            "values": ["pddl-1.0", "pddl", "public domain dedication and license 1.0"],
            "url": "https://opendatacommons.org/licenses/pddl/1-0/",
            "api_url": "https://opendatacommons.org/licenses/pddl/pddl-10.txt",
        },
        "None": {"name": "", "values": [None, ""], "url": ""},
    }


def add_license_file(license_type: str, output_dir: Path) -> None:
    """Add a license file to the dataset directory."""
    licenses = supported_licenses()

    if license_type not in (licenses_choices := list(licenses.keys())):
        log.warning(f"License {license_type} not recognized.")
        print_ordered_list(msg="Supported licenses are:", items=licenses_choices)

        return

    url = licenses[license_type].get("api_url", "")
    if url in [None, ""]:
        log.warning(f"No available template for license {license_type}")
        return

    response = requests.get(url)  # type: ignore

    if response.status_code == 200:
        license_file = output_dir.joinpath("LICENSE")
        license_file.parent.mkdir(parents=True, exist_ok=True)
        log.info(f"creating {license_file}")
        try:
            license_content = response.json()["body"]
        except Exception:
            license_content = response.content.decode("utf-8")

        with license_file.open("w", encoding="utf-8") as f:
            f.write(license_content)
    else:
        log.warning(f"Could not get license from {url}")


def update_license(
    bids_dir: Path,
    output_dir: Path,
    ds_desc: dict[str, Any],
    skip_prompt: bool = False,
    force: bool = False,
) -> tuple[str, str]:
    """Update the license of the dataset."""
    log.info("update license")

    name, url = identify_license(ds_desc)

    license_file_present = "LICENSE" in [x.name for x in bids_dir.glob("LICENSE*")]
    if force or not license_file_present:
        add_license_file(name, output_dir)

    license_file_present = "LICENSE" in [x.name for x in output_dir.glob("LICENSE*")]
    if name == "":

        if license_file_present:
            log.warning(
                """License found in output folder but not dataset_description.json."""
            )

        if not skip_prompt:
            (name, url) = manually_add_license(
                bids_dir=bids_dir,
                output_dir=output_dir,
                ds_desc=ds_desc,
                skip_prompt=skip_prompt,
            )

    return name, url


def identify_license(ds_desc: dict[str, Any]) -> tuple[str, str]:
    """Identify the license of the dataset."""
    name = ds_desc.get("License", "")
    url = ""

    licenses = supported_licenses()
    licenses_choices = list(licenses.keys())

    for key in licenses_choices:
        if name.lower() in licenses[key]["values"]:
            name = licenses[key]["name"]
            url = licenses[key].get("url", "")  # type: ignore
            break

    if name not in [""]:
        log.debug(f"License {name} found.")

    else:
        log.warning("No license found.")

    return name, url


def manually_add_license(
    bids_dir: Path,
    output_dir: Path,
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

        licenses = list(supported_licenses().keys())
        choices = [str(i + 1) for i, _ in enumerate(licenses)]

        print_ordered_list(msg="Possible licences:", items=licenses)
        license_index = Prompt.ask(
            prompt_format("Please choose a license."),
            choices=choices,
            default=1,
        )

        ds_desc["License"] = licenses[int(license_index) - 1]
        (name, url) = update_license(
            bids_dir=bids_dir,
            output_dir=output_dir,
            ds_desc=ds_desc,
            skip_prompt=skip_prompt,
            force=True,
        )

    return name, url
