"""Build and validate the confirmed-name and adjacent-scene dialogue delta."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


STATUSES = {"draft; confirmed hero name; not game-tested",
            "draft; adjacent scene; not game-tested"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-candidate-dir", type=Path, required=True)
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    with (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["status"] in STATUSES]
    if len(rows) != 59 or any(not r["chinese"] for r in rows):
        raise ValueError("confirmed hero review row count drift")
    full_mapping = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    groups = {}
    for row in rows:
        name = row["source_file"].split("\\")[-1].split("#")[0]
        groups.setdefault(name, []).append(row)
    report = {}
    for name, items in sorted(groups.items()):
        inherited = args.base_candidate_dir / name
        source = inherited if inherited.exists() else args.game / "Sound" / "Dialogue" / name
        delta = args.output / (name + ".delta.csv")
        with delta.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("source_file", "string_id", "english", "chinese"))
            writer.writeheader()
            writer.writerows({k: row[k] for k in writer.fieldnames} for row in items)
        entry_map = args.output / (name + ".entry-map.json")
        entry_map.write_text(json.dumps({r["source_file"]: full_mapping[r["source_file"]]
                                         for r in items}, indent=2) + "\n", encoding="utf-8")
        candidate = args.output / name
        subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                        "--archive", str(source), "--blast-dll", str(args.blast_dll),
                        "--entry-map", str(entry_map), "--translations", str(delta),
                        "--output", str(candidate)], check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                                 "--source", str(source), "--candidate", str(candidate),
                                 "--blast-dll", str(args.blast_dll)], check=True,
                                capture_output=True, text=True)
        validation = json.loads(result.stdout)
        report[name] = {"base_sha256": sha(source), "candidate_sha256": sha(candidate),
                        "changed_entries": validation["changed_entries"], "translated_lines": len(items)}
    for name in ("Lotus_Dialogue.H2O", "Unaligned_Dialogue.H2O"):
        if name not in report:
            report[name] = {"carry_forward_sha256": sha(args.base_candidate_dir / name)}
    (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
