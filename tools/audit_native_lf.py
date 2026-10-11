"""Find official hard line breaks in each language's goal/tooltip LTE records."""
import argparse
import json
from pathlib import Path, PureWindowsPath
import struct

from patch_lte_h2o import decoder, records


TARGETS = {"Goals", "WOTW_Goals", "Console_Tooltips", "WOTW_Console_Tooltips"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--blast-dll", type=Path, required=True)
    a = p.parse_args()
    data = a.archive.read_bytes()
    rows = json.loads(a.index.read_text(encoding="utf-8"))["rows"]
    decode = decoder(a.blast_dll)
    found = []
    checked = 0
    for row in rows:
        path = row["path"]
        if PureWindowsPath(path).stem not in TARGETS:
            continue
        i = row["row"]
        f = struct.unpack_from("<10I", data, 513 + 40 * i)
        raw = decode(data[f[6] + 12:f[6] + 12 + f[4]], f[3])
        for ident, _, value, _ in records(raw):
            checked += 1
            if "\n" in value or "\r" in value:
                found.append({"source_key": path + "#" + str(ident),
                              "lf": value.count("\n"), "cr": value.count("\r"),
                              "text": value})
    print(json.dumps({"checked": checked, "native_breaks": found}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
