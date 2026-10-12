"""Build and validate the next Dragon tutorial dialogue delta."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys


STATUS = "draft; Dragon continuation v33; font candidate pending; not game-tested"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.base.name != "Dragon_Dialogue.H2O":
        raise ValueError("base filename must be Dragon_Dialogue.H2O")
    root = Path(__file__).resolve().parents[1]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["status"] == STATUS]
    if len(rows) != 81:
        raise ValueError(f"row count drift: {len(rows)} != 81")
    columns = ("source_file", "string_id", "english", "chinese")
    delta = args.output_dir / "Dragon.delta.csv"
    with delta.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, columns)
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in rows)
    full_map = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    entry_map = args.output_dir / "Dragon.entry-map.json"
    entry_map.write_text(json.dumps({r["source_file"]: full_map[r["source_file"]]
                                     for r in rows}, indent=2) + "\n", encoding="utf-8")
    candidate = args.output_dir / "Dragon_Dialogue.H2O"
    subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                    "--archive", str(args.base), "--blast-dll", str(args.blast_dll),
                    "--entry-map", str(entry_map), "--translations", str(delta),
                    "--output", str(candidate)], check=True, capture_output=True)
    result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                             "--source", str(args.base), "--candidate", str(candidate),
                             "--blast-dll", str(args.blast_dll)], check=True,
                            capture_output=True, text=True)
    report = json.loads(result.stdout)
    if report["changed_entries"] != [65, 74, 90]:
        raise ValueError(f"wrong changed entries: {report['changed_entries']}")
    (args.output_dir / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"translated_lines": len(rows), "candidate_sha256": report["candidate_sha256"],
                      "changed_entries": report["changed_entries"]}, indent=2))


if __name__ == "__main__":
    main()
