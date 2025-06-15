from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from rich.console import Console

console = Console()


def load_json(path: Path) -> Dict[str, Any]:
    if path.exists():
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def confirm(question: str, force: bool) -> bool:
    if force:
        return True
    from typer import confirm as typer_confirm

    return typer_confirm(question)
