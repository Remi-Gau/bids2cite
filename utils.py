from rich import print


def prompt_format(msg: str) -> str:
    return f"[bold]{msg}[/bold]"


def print_unordered_list(msg: str, items: list) -> None:
    print(f"\n[underline]{msg}[/underline]")
    for i, item in enumerate(items):
        print(f"\t{i+1}. [bold][white]{item}[/white][/bold]")
    print()
