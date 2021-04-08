from typing import Union

import click
import requests
from rich.console import Console

from yaramanager import version as ver

try:
    from yaramanager import commit

    IS_BINARY = True
except ImportError:
    IS_BINARY = False


@click.command(help="Displays the current version.")
@click.option("-c", "--check", is_flag=True, help="Checks version via Github API.")
def version(check):
    c = Console(highlight=False)
    github_ver = None
    if check:
        github_ver = get_latest_release_tag()

    c.print(f"YaraManager v{ver}")
    if IS_BINARY:
        c.print(f"Built from Git commit {commit}.")

    if check:
        if github_ver:
            if ver != github_ver:
                c.print(
                    f"Your version of YaraManager is out of date. Most recent version is {github_ver}.",
                    style="yellow"
                )
            else:
                c.print("Your version of YaraManager is up to date.", style="green")
        else:
            c.print("Could not get most recent version from Github.")

    c.print(f"https://github.com/3c7/yaramanager/releases/tag/{github_ver or ver}")


def get_latest_release_tag() -> Union[str, None]:
    res = requests.get("https://api.github.com/repos/3c7/yaramanager/releases")
    if res.status_code != 200:
        return None

    releases = res.json()
    for release in releases:
        if not release["draft"] and not release["prerelease"]:
            return release["tag_name"]
    return None
