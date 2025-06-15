from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

PLACEHOLDER_PATTERN = re.compile(r"\{[^\}]+\}|<[^>]+>")


def mask_placeholders(text: str) -> Tuple[str, Dict[str, str]]:
    mapping: Dict[str, str] = {}

    def repl(match: re.Match[str]) -> str:
        placeholder = match.group(0)
        key = f"§§PLH_{len(mapping):03d}§§"
        mapping[key] = placeholder
        return key

    masked = PLACEHOLDER_PATTERN.sub(repl, text)
    return masked, mapping


def unmask_placeholders(text: str, mapping: Dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text


def parse_strings_file(path: Path) -> List[Tuple[str, str]]:
    entries = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            key, _, value = line.partition('=')
            entries.append((key.strip(), value.strip()))
    return entries


def write_strings_file(entries: Iterable[Tuple[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for key, value in entries:
            f.write(f"{key} = {value}\n")
