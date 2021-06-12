import os
from typing import List

import click
import yara
from rich.console import Console, Text
from rich.progress import Progress
from yarabuilder import YaraBuilder

from yaramanager.db.session import get_session
from yaramanager.utils.utils import filter_rules_by_name_and_tag, write_ruleset_to_tmp_file


@click.command(help="Scan files using your rulesets. Please be aware that this program should not be used anywhere "
                    "where performance matters. This is dead slow, single thread scanning. Useful for fast sample "
                    "classifications and checking your rule coverage, but not for scanning large filesets.")
@click.option("-t", "--tag", help="Only use rules with tag.")
@click.option("-n", "--name", help="Only use rules contain [NAME] in name.")
@click.option("-T", "--timeout", default=0, type=int, help="Set timeout in seconds.")
@click.option("-p", "--no-progress", is_flag=True, help="Disable progress bar.")
@click.option("-c", "--csv", is_flag=True, help="CSV like output. Use together with -p!")
@click.option("-r", "--recursive", is_flag=True, help="Scans directories recursively.")
@click.argument("paths", type=click.Path(exists=True, file_okay=True, dir_okay=True), nargs=-1)
def scan(tag: str, name: str, timeout: int, no_progress: bool, csv: bool, recursive: bool, paths: List[str]):
    c, ec = Console(), Console(stderr=True)
    if len(paths) == 0:
        with click.Context(scan) as ctx:
            c.print(scan.get_help(ctx))
            exit(-1)
    session = get_session()
    rules, count = filter_rules_by_name_and_tag(name, tag, session)
    if count == 0:
        ec.print("No rules matching your criteria.")
        exit(-1)

    yb = YaraBuilder()
    for rule in rules:
        rule.add_to_yarabuilder(yb)
    ruleset_path, _ = write_ruleset_to_tmp_file(yb)
    ruleset_compiled = yara.compile(ruleset_path)
    if not no_progress:
        c.print(f"Using ruleset {ruleset_path} for scanning. Check the rule file in case any error shows up.")
    if recursive:
        list_of_files = []
        for path in paths:
            list_of_files.extend(get_dir_recursive(path))
        paths = list_of_files
    with Progress() if not no_progress else c as prog:
        if isinstance(prog, Progress):
            t1 = prog.add_task("Scanning...", total=len(paths))
        for path in paths:
            if isinstance(prog, Progress):
                prog.update(t1, advance=1, description=f"Scanning {path}...")
            if os.path.isdir(path):
                continue
            try:
                matches = ruleset_compiled.match(path, timeout=timeout)
            except yara.TimeoutError:
                prog.print(Text("Timed out!", style="bold red"))
                if isinstance(prog, Progress):
                    prog.update(t1, description="Timed out!")
                exit(-1)
            for match in matches:
                if csv:
                    prog.print(f'"{match.rule}","{",".join(match.tags)}","{path}"')
                else:
                    prog.print(f"{match.rule} ({', '.join(match.tags)}): {path}", highlight=not no_progress)
        if isinstance(prog, Progress):
            prog.update(t1, description="Finished scanning!")
    os.remove(ruleset_path)


def get_dir_recursive(path: str) -> List[str]:
    """Grabbs all files from a given path recursively."""
    files = []
    for dir_entry in os.scandir(path):
        if dir_entry.is_dir(follow_symlinks=True):
            files.extend(get_dir_recursive(dir_entry))
        else:
            files.append(dir_entry.path)
    return files
