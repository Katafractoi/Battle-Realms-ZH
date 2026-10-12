"""Patch and validate the contiguous Kenji/Otomo Orb-arc translation."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kenji-base", type=Path, required=True)
    parser.add_argument("--otomo-base", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    with (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["status"] == "draft; Orb arc; not game-tested"]
    if len(rows) != 49:
        raise ValueError("Orb arc row count drift")
    full_map = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    report = {}
    for name, source in (("Kenji_Dialogue.H2O", args.kenji_base),
                         ("Otomo_Dialogue.H2O", args.otomo_base)):
        subset = [r for r in rows if name in r["source_file"]]
        delta = args.output / (name + ".delta.csv")
        with delta.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("source_file", "string_id", "english", "chinese"))
            writer.writeheader()
            writer.writerows({k: r[k] for k in writer.fieldnames} for r in subset)
        mapping = args.output / (name + ".entry-map.json")
        mapping.write_text(json.dumps({r["source_file"]: full_map[r["source_file"]]
                                       for r in subset}, indent=2) + "\n", encoding="utf-8")
        candidate = args.output / name
        subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                        "--archive", str(source), "--blast-dll", str(args.blast_dll),
                        "--entry-map", str(mapping), "--translations", str(delta),
                        "--output", str(candidate)], check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                                 "--source", str(source), "--candidate", str(candidate),
                                 "--blast-dll", str(args.blast_dll)], check=True,
                                capture_output=True, text=True)
        check = json.loads(result.stdout)
        report[name] = {"base_sha256": check["source_sha256"],
                        "candidate_sha256": check["candidate_sha256"],
                        "changed_entries": check["changed_entries"], "translated_lines": len(subset)}
    (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
