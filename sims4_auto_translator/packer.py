from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path
from typing import Iterable, Tuple

from .parsers import write_strings_file
from .utils import console


def pack_strings_to_package(strings: Iterable[Tuple[str, str]], output_path: Path) -> None:
    """Write strings to a simple .package (ZIP based) archive."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "language.strings"
        write_strings_file(strings, tmp_path)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(tmp_path, arcname="language.strings")
