from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer
from rich import print

from .deepl_api import DeepLTranslator
from .parsers import (
    mask_placeholders,
    parse_strings_file,
    unmask_placeholders,
    write_strings_file,
)
from .packer import pack_strings_to_package
from .utils import confirm, console
from .gui import run_gui

app = typer.Typer(help="Sims 4 Auto Translator")


@app.command()
def translate(
    infile: Path = typer.Argument(..., help="Input .strings file"),
    apikey: str = typer.Option(None, help="DeepL API key"),
    source_lang: str = typer.Option('EN', help="Source language code"),
    target_lang: str = typer.Option('UK', help="Target language code"),
    yes: bool = typer.Option(False, '--yes', help="Skip confirmation"),
) -> None:
    if not infile.exists():
        print(f"[red]File {infile} not found[/red]")
        raise typer.Exit(code=1)
    key = apikey or os.environ.get('DEEPL_AUTH_KEY')
    if not key:
        print("[red]DeepL API key required[/red]")
        raise typer.Exit(code=1)
    translator = DeepLTranslator(key)
    entries = parse_strings_file(infile)
    masked = []
    maps = []
    for _, text in entries:
        m, mp = mask_placeholders(text)
        masked.append(m)
        maps.append(mp)
    translated = translator.translate(masked, source_lang, target_lang)
    restored = [unmask_placeholders(t, mp) for t, mp in zip(translated, maps)]
    out_dir = Path('output') / f"{source_lang.lower()}-{target_lang.lower()}"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_strings_file(zip([k for k, _ in entries], restored), out_dir / infile.name)
    print(f"[green]Translation saved to {out_dir / infile.name}[/green]")


@app.command()
def verify(infile: Path = typer.Argument(...), yes: bool = typer.Option(False, '--yes')) -> None:
    print(f"Verifying {infile} ... (placeholder)")


@app.command()
def pack(
    infile: Path = typer.Argument(..., help="Input .strings file"),
    out_package: Path = typer.Argument(..., help="Output .package"),
    yes: bool = typer.Option(False, '--yes'),
) -> None:
    if not confirm(f"Pack {infile} into {out_package}?", yes):
        raise typer.Exit()
    entries = parse_strings_file(infile)
    pack_strings_to_package(entries, out_package)
    print(f"[green]Package written to {out_package}[/green]")


@app.command()
def gui() -> None:
    run_gui()


if __name__ == '__main__':
    app()
