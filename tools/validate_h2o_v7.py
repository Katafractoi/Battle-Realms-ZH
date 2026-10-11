"""Independently validate a rebuilt H2O v7 archive against its official source."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

from patch_lte_h2o import decoder, records


def inspect(path, decode):
    data = path.read_bytes()
    if len(data) < 521 or data[480] != 0x1A:
        raise ValueError(f"Invalid H2O header: {path}")
    version, count = struct.unpack_from("<II", data, 481)
    if version != 7:
        raise ValueError(f"Unsupported H2O version {version}")
    second = 513 + 40 * count
    if data[513:second] != data[second:second + 40 * count]:
        raise ValueError("Index copies differ")
    records = []
    cursor = struct.unpack_from("<10I", data, 513)[6]
    if cursor < second + 40 * count or cursor > len(data):
        raise ValueError("Invalid first entry offset")
    for i in range(count):
        fields = struct.unpack_from("<10I", data, 513 + 40 * i)
        raw_size, packed_size, offset, crc = fields[3], fields[4], fields[6], fields[8]
        if offset != cursor:
            raise ValueError(f"Offset mismatch at entry {i}")
        if offset + 12 + packed_size > len(data):
            raise ValueError(f"Out-of-bounds entry {i}")
        header = struct.unpack_from("<III", data, offset)
        if header != (packed_size, raw_size, crc):
            raise ValueError(f"Block header mismatch at entry {i}")
        packed = data[offset + 12:offset + 12 + packed_size]
        try:
            raw = decode(packed, raw_size)
        except ValueError:
            # Dialogue archives also contain non-DCL sound payloads. These
            # must remain compressed-byte-identical to the official source.
            raw = None
        if raw is not None and zlib.crc32(raw) != crc:
            raise ValueError(f"CRC mismatch at entry {i}")
        records.append((packed, raw))
        cursor += 12 + packed_size
    if cursor != len(data):
        raise ValueError("Unexpected archive tail")
    return data, records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--blast-dll", type=Path, required=True)
    args = p.parse_args()
    decode = decoder(args.blast_dll)
    source_data, source = inspect(args.source, decode)
    candidate_data, candidate = inspect(args.candidate, decode)
    if len(source) != len(candidate):
        raise ValueError("Entry count changed")
    changed = [i for i, (old, new) in enumerate(zip(source, candidate))
               if old[0] != new[0]]
    for i, (old, new) in enumerate(zip(source, candidate)):
        if i in changed and (old[1] is None or new[1] is None or old[1] == new[1]):
            raise ValueError(f"Changed entry {i} failed text decode or is identical")
    changed_records = {}
    preserved_records = 0
    for i in changed:
        before, after = list(records(source[i][1])), list(records(candidate[i][1]))
        if len(before) != len(after):
            raise ValueError(f"LTE record count changed at entry {i}")
        altered = []
        for old, new in zip(before, after):
            if old[:2] != new[:2]:
                raise ValueError(f"LTE ID or marker changed at entry {i}")
            if old[3] != new[3]:
                altered.append(old[0])
            else:
                preserved_records += 1
        if not altered:
            raise ValueError(f"Entry {i} has no altered LTE record")
        changed_records[str(i)] = altered
    print(json.dumps({
        "source_sha256": hashlib.sha256(source_data).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate_data).hexdigest(),
        "entries": len(source),
        "changed_entries": changed,
        "changed_lte_record_ids_by_entry": changed_records,
        "unchanged_lte_records_in_changed_entries_preserved": preserved_records,
        "unchanged_compressed_entries_preserved": len(source) - len(changed),
    }, indent=2))


if __name__ == "__main__":
    main()
