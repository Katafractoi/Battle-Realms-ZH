"""Report suspicious spacing in reviewed Chinese and an installed-format interface candidate."""

import argparse
import csv
import json
from pathlib import Path
import re
import struct

from patch_lte_h2o import decoder, records


PATTERNS = {
    "han_space_han": re.compile(r"(?<=[\u3400-\u9fff]) +(?=[\u3400-\u9fff])"),
    "digit_space_han": re.compile(r"(?<=[0-9]) +(?=[\u3400-\u9fff])"),
    "han_space_digit": re.compile(r"(?<=[\u3400-\u9fff]) +(?=[0-9])"),
    "space_by_cjk_punctuation": re.compile(r" +(?=[，。！？；：])|(?<=[，。！？；：]) +"),
    "repeated_line_break": re.compile(r"\n[ \t]*\n"),
    "space_at_line_break": re.compile(r" +\n|\n +"),
    "isolated_han_line": re.compile(r"(?m)^[\u3400-\u9fff]$"),
    "digit_unit_break": re.compile(r"[0-9]\n[点个名座次年月日]"),
}


def findings(text):
    return [name for name, pattern in PATTERNS.items()
            if (name != "isolated_han_line" or "\n" in text) and pattern.search(text)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review", type=Path, required=True)
    p.add_argument("--dialogue", type=Path, required=True)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--entry-map", type=Path, required=True)
    p.add_argument("--blast-dll", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    rows = []
    for path in (args.review, args.dialogue):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                if not row["chinese"]:
                    continue
                issues = findings(row["chinese"])
                if issues:
                    rows.append({"layer": path.name, "source_file": row["source_file"],
                                 "string_id": row["string_id"], "issues": ";".join(issues),
                                 "english": row["english"], "chinese": row["chinese"],
                                 "review_status": "pending field-context review"})
    archive = args.archive.read_bytes()
    mapping = json.loads(args.entry_map.read_text(encoding="utf-8"))
    decode = decoder(args.blast_dll)
    for name, index in mapping.items():
        f = struct.unpack_from("<10I", archive, 513 + 40 * index)
        raw = decode(archive[f[6] + 12:f[6] + 12 + f[4]], f[3])
        for ident, _, text, _ in records(raw):
            if not any("\u3400" <= ch <= "\u9fff" for ch in text):
                continue
            issues = findings(text)
            if issues:
                rows.append({"layer": "candidate_archive", "source_file": name,
                             "string_id": str(ident), "issues": ";".join(issues),
                             "english": "", "chinese": text,
                             "review_status": "pending field-context review"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("layer", "source_file", "string_id",
                                                    "issues", "english", "chinese",
                                                    "review_status"))
        writer.writeheader()
        writer.writerows({**row,
                         "english": row["english"].replace("\n", "\\n"),
                         "chinese": row["chinese"].replace("\n", "\\n")}
                        for row in rows)
    print(json.dumps({"issue_rows": len(rows), "output": str(args.output)}))


if __name__ == "__main__":
    main()
