from typing import Optional

from rich.console import Console

from yaramanager.config import load_config


def debug_print(msg: str, c: Optional[Console] = None) -> None:
    debug = load_config().get("debug", False)
    if not debug:
        return
    if not c:
        # Use stderr so piped output is still valid
        c = Console(stderr=True)

    c.print("[cyan]DEBUG[reset]: " + msg)
