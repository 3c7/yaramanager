from typing import Optional

from rich.console import Console

from yaramanager.config import load_config


def debug_print(msg: str, c: Optional[Console] = None) -> None:
    debug = load_config().get("debug", False)
    if not debug:
        return
    if not c:
        c = Console()

    c.print("[cyan]DEBUG[reset]: " + msg)
