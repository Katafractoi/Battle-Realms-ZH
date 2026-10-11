"""Read-only comparison of LTE records and LFR advances for render failures.

This checks storage integrity and measures text; it cannot prove which game
widget or line-breaking routine displayed a screenshot.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from patch_lte_h2o import decoder, records


CASES = {
    "WOTW_Goals.lte": [0, 10],
    "Goals.lte": [10],
    "WOTW_Console_Tooltips.lte": [463, 464, 565, 566, 663, 664, 665, 666, 667],
}


def widths_by_size(data):
    version, _, _, count = struct.unpack_from("<IffI", data)
    if version != 1:
        raise ValueError("unsupported LFR")
    pos, result = 16, {}
    for _ in range(count):
        size, _, atlases = struct.unpack_from("<IfI", data, pos)
        pos += 12
        for _ in range(atlases):
            marker, units = struct.unpack_from("<BI", data, pos)
            if marker != 0:
                raise ValueError("bad LFR atlas name")
            pos += 5 + 2 * units
        glyphs, = struct.unpack_from("<I", data, pos)
        pos += 4
        result[size] = {}
        for _ in range(glyphs):
            _, codepoint, width, _, _, _ = struct.unpack_from("<HHffff", data, pos)
            result[size][codepoint] = width
            pos += 20
    if pos != len(data):
        raise ValueError("unexpected LFR tail")
    return result


def entry(data, index, decode):
    f = struct.unpack_from("<10I", data, 513 + 40 * index)
    raw = decode(data[f[6] + 12:f[6] + 12 + f[4]], f[3])
    return list(records(raw))


def metrics(record, widths):
    ident, marker, value, original = record
    units, = struct.unpack_from("<i", original, 5)
    assert units == len(value.encode("utf-16le")) // 2 + 1
    assert original[-2:] == b"\0\0"
    assert "\0" not in value
    return {
        "id": ident, "marker": marker, "utf16_units_including_nul": units,
        "first_character": value[:1], "text": value,
        "ascii_spaces": value.count(" "), "newlines": value.count("\n"),
        "missing_glyphs_21px": sorted({f"U+{ord(c):04X}" for c in value
                                        if ord(c) not in widths[21]}),
        "advance_px": {str(size): round(sum(table.get(ord(c), 0) for c in value), 1)
                       for size, table in widths.items() if size in (11, 21, 26, 36, 42)},
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("official", "tested", "entry-map", "blast-dll", "font", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    source, tested = a.official.read_bytes(), a.tested.read_bytes()
    mapping = json.loads(a.entry_map.read_text(encoding="utf-8"))
    decode = decoder(a.blast_dll)
    widths = widths_by_size(a.font.read_bytes())
    report = {"official_sha256": hashlib.sha256(source).hexdigest(),
              "tested_sha256": hashlib.sha256(tested).hexdigest(), "cases": [],
              "files_checked": 0, "records_checked": 0,
              "native_english_newline_keys": []}
    for path, index in mapping.items():
        if not path.startswith("Text\\ENG\\"):
            continue
        before, after = entry(source, index, decode), entry(tested, index, decode)
        if len(before) != len(after):
            raise ValueError("record count changed: " + path)
        report["files_checked"] += 1
        report["records_checked"] += len(before)
        report["native_english_newline_keys"] += [path + "#" + str(r[0])
                                                    for r in before if "\n" in r[2]]
        for b, c in zip(before, after):
            if b[:2] != c[:2]:
                raise ValueError("ID or marker changed: " + path)
            if Path(path).name in CASES and b[0] in CASES[Path(path).name]:
                report["cases"].append({"source_key": path + "#" + str(b[0]),
                                        "official": metrics(b, widths),
                                        "tested": metrics(c, widths)})
    a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("official_sha256", "tested_sha256", "files_checked",
                       "records_checked", "native_english_newline_keys")}, indent=2))
    print("selected cases:", len(report["cases"]))


if __name__ == "__main__":
    main()
