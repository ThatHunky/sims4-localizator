import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from pathlib import Path

from sims4_auto_translator.parsers import parse_strings_file, write_strings_file


def test_round_trip(tmp_path):
    data = [('key1', 'Hello'), ('key2', 'World')]
    path = tmp_path / 'test.strings'
    write_strings_file(data, path)
    parsed = parse_strings_file(path)
    assert parsed == data
