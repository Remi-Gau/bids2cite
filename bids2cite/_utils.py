"""Misc."""

from __future__ import annotations

import logging
from typing import Any

from rich import print
from rich.logging import RichHandler
from rich.traceback import install


def prompt_format(msg: str) -> str:
    """Format prompt message."""
    return f"[bold]{msg}[/bold]"


def print_ordered_list(msg: str, items: list[Any]) -> None:
    """Print an unordered list."""
    print(f"\n[underline]{msg}[/underline]")
    for i, item in enumerate(items):
        print(f"\t{i+1}. [bold][white]{item}[/white][/bold]")
    print()


def bids2cite_log(name: str | None = None) -> logging.Logger:
    """Create log.

    :param name: _description_, defaults to None
    :type name: _type_, optional

    :return: _description_
    :rtype: _type_
    """
    # let rich print the traceback
    install(show_locals=True)

    FORMAT = "bids2datacite - %(asctime)s - %(levelname)s - %(message)s"

    if not name:
        name = "rich"

    logging.basicConfig(
        level=default_log_level(), format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    return logging.getLogger(name)


def default_log_level() -> str:
    """Return default log level."""
    return "WARNING"


def log_levels() -> list[str]:
    """Return a list of log levels."""
    return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
