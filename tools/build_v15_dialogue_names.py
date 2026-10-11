"""Patch confirmed Kenji/Shinja names into three translated dialogue archives."""

import argparse
import csv
import json
from pathlib import Path, PureWindowsPath
import struct
import subprocess
import sys

from patch_lte_h2o import decoder, records


def load(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {(row["source_file"], row["string_id"]): row for row in csv.DictReader(stream)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base-dir", "old-csv", "new-csv", "entry-map", "blast-dll", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    old, new = load(args.old_csv), load(args.new_csv)
    if old.keys() != new.keys():
        raise ValueError("source key drift")
    changed = {key for key in old if old[key]["chinese"] != new[key]["chinese"]}
    if len(changed) != 9:
        raise ValueError(f"expected 9 name edits, found {len(changed)}")
    mapping = json.loads(args.entry_map.read_text(encoding="utf-8"))
    decode = decoder(args.blast_dll)
    changes = {}
    for key in sorted(changed):
        source, ident = key
        archive_name = PureWindowsPath(source.split("#entry")[0]).name
        if source not in mapping:
            raise ValueError(f"unmapped source: {source}")
        before, after = old[key]["chinese"], new[key]["chinese"]
        if before.replace("Kenji", "健治").replace("Shinja", "信蛇") != after:
            raise ValueError(f"unexpected text change at {key}")
        changes.setdefault(archive_name, []).append((source, ident, before, after))
    if set(changes) != {"Dragon_Dialogue.H2O", "Kenji_Dialogue.H2O", "Otomo_Dialogue.H2O"}:
        raise ValueError("unexpected archive group")
    reports = {}
    for archive_name, edits in changes.items():
        base = args.base_dir / archive_name
        data = base.read_bytes()
        decoded = {}
        for source in {edit[0] for edit in edits}:
            index = mapping[source]
            fields = struct.unpack_from("<10I", data, 513 + 40 * index)
            raw = decode(data[fields[6] + 12:fields[6] + 12 + fields[4]], fields[3])
            decoded[source] = {str(ident): value for ident, _, value, _ in records(raw)}
        delta = []
        for source, ident, before, after in edits:
            if decoded[source][ident] != before:
                raise ValueError(f"base archive text drift: {source}#{ident}")
            delta.append({"source_file": source, "string_id": ident,
                          "english": before, "chinese": after})
        delta_path = args.output_dir / (archive_name + ".names-delta.csv")
        with delta_path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=delta[0].keys())
            writer.writeheader()
            writer.writerows(delta)
        output = args.output_dir / archive_name
        patch = subprocess.run([
            sys.executable, str(Path(__file__).with_name("patch_lte_h2o.py")),
            "--archive", str(base), "--translations", str(delta_path),
            "--entry-map", str(args.entry_map), "--blast-dll", str(args.blast_dll),
            "--output", str(output)], check=True, capture_output=True, text=True)
        validation = subprocess.run([
            sys.executable, str(Path(__file__).with_name("validate_h2o_v7.py")),
            "--source", str(base), "--candidate", str(output),
            "--blast-dll", str(args.blast_dll)], check=True, capture_output=True, text=True)
        report = json.loads(validation.stdout)
        (args.output_dir / (archive_name + ".validate.json")).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        reports[archive_name] = {"changed_texts": len(edits),
                                 "sha256": report["candidate_sha256"],
                                 "changed_entries": report["changed_entries"]}
    print(json.dumps(reports, ensure_ascii=False))


if __name__ == "__main__":
    main()
