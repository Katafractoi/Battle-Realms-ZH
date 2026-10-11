"""Apply only reviewed v15 UI text edits to the already tested v14 archive.

Keep v14's existing line breaks and every unrelated compressed entry. Source
archives and the blast DLL are supplied locally; this tool never touches Steam.
"""

import argparse
import csv
from difflib import SequenceMatcher
import json
from pathlib import Path
import struct
import subprocess
import sys

from patch_lte_h2o import decoder, records


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {(row["source_file"], row["string_id"]): row for row in csv.DictReader(stream)}


def boundary(text, visible):
    if visible == 0:
        return 0
    count = 0
    for index, char in enumerate(text):
        count += char != "\n"
        if count == visible:
            return index + 1
    raise ValueError("visible boundary outside string")


def preserve_breaks(base, before, after):
    if base.replace("\n", "") != before:
        raise ValueError("v14 archive and old CSV do not agree")
    edits = [opcode for opcode in SequenceMatcher(None, before, after).get_opcodes()
             if opcode[0] != "equal"]
    if not edits:
        raise ValueError("missing local edit")
    result = base
    for _, i1, i2, j1, j2 in reversed(edits):
        left, right = boundary(base, i1), boundary(base, i2)
        if "\n" in base[left:right]:
            raise ValueError("existing LF inside replacement span; manual layout needed")
        result = result[:left] + after[j1:j2] + result[right:]
    if result.replace("\n", "") != after:
        raise ValueError("new visible text mismatch")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "old-csv", "new-csv", "entry-map", "blast-dll", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    old, new = rows(args.old_csv), rows(args.new_csv)
    if old.keys() != new.keys():
        raise ValueError("CSV source keys changed")
    changed = {key for key in old if old[key]["chinese"] != new[key]["chinese"]}
    if len(changed) != 29:
        raise ValueError(f"expected 29 reviewed keys, found {len(changed)}")
    mapping = json.loads(args.entry_map.read_text(encoding="utf-8"))
    if any(key[0] not in mapping for key in changed):
        raise ValueError("changed source missing from archive map")
    data, decode = args.base.read_bytes(), decoder(args.blast_dll)
    source_records = {}
    for name in {key[0] for key in changed}:
        index = mapping[name]
        fields = struct.unpack_from("<10I", data, 513 + 40 * index)
        raw = decode(data[fields[6] + 12:fields[6] + 12 + fields[4]], fields[3])
        source_records[name] = {str(ident): value for ident, _, value, _ in records(raw)}
    delta = []
    for key in sorted(changed):
        prior, updated = old[key], new[key]
        if prior["english"] != updated["english"]:
            raise ValueError(f"English source changed at {key}")
        existing = source_records[key[0]][key[1]]
        if key == ("Text\\ENG\\Console_Tooltips.lte", "233"):
            assert existing == "扇舞艺妓及其附近友军牺牲\n部分生命值，以提高伤害\n抵抗能力。"
            desired = "扇舞艺妓及其附近友军牺牲\n部分生命值，以提高\n伤害抗性。"
            assert desired.replace("\n", "") == updated["chinese"]
        else:
            try:
                desired = preserve_breaks(existing, prior["chinese"], updated["chinese"])
            except ValueError as error:
                raise ValueError(f"{key}: {error}") from error
        delta.append({"source_file": key[0], "string_id": key[1],
                      "english": existing, "chinese": desired})
    delta_path = args.output_dir / "interface-v15-reviewed-delta.csv"
    with delta_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=delta[0].keys())
        writer.writeheader()
        writer.writerows(delta)
    archive = args.output_dir / "Interface_Text.H2O"
    commands = [
        [sys.executable, str(Path(__file__).with_name("patch_lte_h2o.py")),
         "--archive", str(args.base), "--translations", str(delta_path),
         "--entry-map", str(args.entry_map), "--blast-dll", str(args.blast_dll),
         "--output", str(archive)],
        [sys.executable, str(Path(__file__).with_name("validate_h2o_v7.py")),
         "--source", str(args.base), "--candidate", str(archive),
         "--blast-dll", str(args.blast_dll)],
    ]
    for command, report_name in zip(commands, ("patch-report.json", "validate-report.json")):
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        report = json.loads(result.stdout)
        (args.output_dir / report_name).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reviewed_keys": len(changed),
                      "candidate_sha256": report["candidate_sha256"],
                      "changed_entries": report["changed_entries"],
                      "unchanged_entries": report["unchanged_compressed_entries_preserved"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
