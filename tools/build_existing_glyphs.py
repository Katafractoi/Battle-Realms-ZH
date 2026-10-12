"""Layer verified glyph-safe revisions onto the v21 dialogue candidates."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys

from revise_existing_glyphs import REVISIONS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-candidate-dir", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    full_map = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    groups = {}
    for (source_suffix, ident), (old, new) in REVISIONS.items():
        name = source_suffix.split("#")[0]
        row = {"source_file": "Sound\\Dialogue\\" + source_suffix,
               "string_id": ident, "english": old, "chinese": new}
        groups.setdefault(name, []).append(row)
    report = {}
    for name, rows in sorted(groups.items()):
        source, candidate = args.base_candidate_dir / name, args.output / name
        delta = args.output / (name + ".delta.csv")
        with delta.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        mapping = args.output / (name + ".entry-map.json")
        mapping.write_text(json.dumps({r["source_file"]: full_map[r["source_file"]]
                                       for r in rows}, indent=2) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                        "--archive", str(source), "--blast-dll", str(args.blast_dll),
                        "--entry-map", str(mapping), "--translations", str(delta),
                        "--output", str(candidate)], check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                                 "--source", str(source), "--candidate", str(candidate),
                                 "--blast-dll", str(args.blast_dll)], check=True,
                                capture_output=True, text=True)
        validation = json.loads(result.stdout)
        report[name] = {"candidate_sha256": validation["candidate_sha256"],
                        "changed_entries": validation["changed_entries"], "revised_lines": len(rows)}
    (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
