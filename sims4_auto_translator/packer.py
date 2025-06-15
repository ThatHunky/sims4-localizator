from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable, Tuple

from .parsers import write_strings_file
from .utils import console


def pack_strings_to_package(strings: Iterable[Tuple[str, str]], output_path: Path) -> None:
    temp_dir = output_path.parent / 'temp_strings'
    write_strings_file(strings, temp_dir / 'language.strings')
    # Placeholder for real packaging logic
    try:
        subprocess.run(['S4Studio', '-batchfix', str(temp_dir)], check=True)
    except FileNotFoundError:
        console.print('[yellow]S4Studio not found, skipping package packing[/yellow]')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    (temp_dir / 'language.strings').replace(output_path.with_suffix('.strings'))
