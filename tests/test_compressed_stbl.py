import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sims4_auto_translator.dbpf import build_stbl, parse_stbl
import struct, zlib


def test_parse_zlib_wrapped_stbl():
    data = build_stbl([("0x1", "Hello")])
    wrapped = zlib.compress(data)
    result = parse_stbl(wrapped)
    assert result == [("0x00000001", "Hello")]


def test_parse_internal_compressed_stbl():
    data = build_stbl([("0x2", "World")])
    # compress the strings section and set the flag
    header = bytearray(data)
    string_len = struct.unpack("<I", header[17:21])[0]
    strings = bytes(header[21:21 + string_len])
    compressed = zlib.compress(strings)
    header[6] = 1
    header[17:21] = struct.pack("<I", len(compressed))
    header[21:21 + string_len] = compressed
    compressed_stbl = bytes(header[:21 + len(compressed)])
    result = parse_stbl(compressed_stbl)
    assert result == [("0x00000002", "World")]
