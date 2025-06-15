import struct
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple

STBL_TYPE_ID = 0x220557DA

class DBPFEntry(Tuple[int, int, int, int, int]):
    pass


def _read_header(f: BytesIO) -> Tuple[int, int, int, int, int, int]:
    header = f.read(96)
    if len(header) < 96 or header[:4] != b'DBPF':
        raise ValueError('Not a DBPF package')
    values = struct.unpack('<4s17I24s', header)
    major = values[1]
    minor = values[2]
    index_major = values[8]
    index_count = values[9]
    index_off1 = values[10]
    index_size = values[11]
    index_minor = values[15]
    index_off2 = values[16]
    index_offset = index_off2 if major >= 2 else index_off1
    return major, minor, index_major, index_minor, index_offset, index_count


def _read_index(f: BytesIO, index_major: int, index_minor: int, index_offset: int, count: int) -> List[Tuple[int, int, int, int, int, int]]:
    f.seek(index_offset)
    entries = []
    entry_size = 24 if index_minor == 1 else 20
    for _ in range(count):
        data = f.read(entry_size)
        if len(data) < entry_size:
            break
        if entry_size == 20:
            type_id, group, instance, offset, size = struct.unpack('<IIIII', data)
            instance_hi, instance_lo = 0, instance
        else:
            type_id, group, instance_hi, instance_lo, offset, size = struct.unpack('<IIIIII', data)
        entries.append((type_id, group, instance_hi, instance_lo, offset, size))
    return entries


def iter_stbl_from_package(path: Path) -> Iterator[Tuple[int, bytes]]:
    with path.open('rb') as f:
        buf = BytesIO(f.read())
    major, minor, index_major, index_minor, index_offset, count = _read_header(buf)
    entries = _read_index(buf, index_major, index_minor, index_offset, count)
    for type_id, group, inst_hi, inst_lo, offset, size in entries:
        if type_id != STBL_TYPE_ID:
            continue
        buf.seek(offset)
        yield ((inst_hi << 32) | inst_lo), buf.read(size)


def parse_stbl(data: bytes) -> List[Tuple[str, str]]:
    f = BytesIO(data)
    magic = f.read(4)
    if magic != b'STBL':
        raise ValueError('Invalid STBL data')
    version = struct.unpack('<H', f.read(2))[0]
    compressed = f.read(1)
    count = struct.unpack('<Q', f.read(8))[0]
    f.read(2)  # reserved
    string_len = struct.unpack('<I', f.read(4))[0]
    entries: List[Tuple[str, str]] = []
    for _ in range(count):
        key_hash = struct.unpack('<I', f.read(4))[0]
        flags = f.read(1)
        length = struct.unpack('<H', f.read(2))[0]
        text = f.read(length).decode('utf-8', errors='ignore')
        entries.append((f"0x{key_hash:08X}", text))
    return entries


def build_stbl(entries: Iterable[Tuple[str, str]]) -> bytes:
    out = BytesIO()
    out.write(b'STBL')
    out.write(struct.pack('<H', 5))
    out.write(b'\x00')
    entries = list(entries)
    out.write(struct.pack('<Q', len(entries)))
    out.write(b'\x00\x00')
    # placeholder for length
    length_pos = out.tell()
    out.write(b'\x00\x00\x00\x00')
    start = out.tell()
    for key_str, text in entries:
        key = int(key_str, 16)
        encoded = text.encode('utf-8')
        out.write(struct.pack('<IBH', key, 0, len(encoded)))
        out.write(encoded)
    end = out.tell()
    string_len = end - start
    out.seek(length_pos)
    out.write(struct.pack('<I', string_len))
    return out.getvalue()
