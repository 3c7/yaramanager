from typing import Union

import click
import requests
from rich.console import Console

from yaramanager import version as ver


@click.command(help="Displays the current version.")
@click.option("-c", "--check", is_flag=True, help="Checks version via Github API.")
def version(check):
    c = Console(highlight=False)
    github_ver = None
    c.print("YaraManager", end="")

    if check:
        github_ver = get_latest_release_tag()
        if github_ver == ver:
            c.print(f" v{ver}", style="bold green")
        else:
            c.print(f" v{ver} (out of date, most recent version is v.{github_ver})", style="bold yellow")
    else:
        c.print(f" v{ver}")
    c.print(f"https://github.com/3c7/yaramanager/releases/tag/{github_ver or ver}")


def get_latest_release_tag() -> Union[str, None]:
    res = requests.get("https://api.github.com/repos/3c7/yaramanager/releases")
    if res.status_code != 200:
        return None

    return res.json()[0]["tag_name"]
