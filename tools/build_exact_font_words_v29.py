"""Patch and validate restored exact wording atop the latest dialogue packs."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys

from restore_exact_font_words_v29 import REVISIONS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("kenji", "dragon", "shinja"):
        parser.add_argument(f"--{name}-base", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    full_map = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    report = {}
    for name in ("Kenji", "Dragon", "Shinja"):
        archive_name = f"{name}_Dialogue.H2O"
        base = getattr(args, f"{name.lower()}_base")
        if base.name != archive_name:
            raise ValueError(f"base archive must be named {archive_name}")
        rows = [{"source_file": "Sound\\Dialogue\\" + source, "string_id": ident,
                 "english": old, "chinese": new}
                for (source, ident), (old, new) in REVISIONS.items()
                if source.startswith(archive_name + "#")]
        delta = args.output / f"{archive_name}.delta.csv"
        columns = ("source_file", "string_id", "english", "chinese")
        with delta.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        entry_map = args.output / f"{archive_name}.entry-map.json"
        entry_map.write_text(json.dumps({row["source_file"]: full_map[row["source_file"]]
                                         for row in rows}, indent=2) + "\n", encoding="utf-8")
        candidate = args.output / archive_name
        subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                        "--archive", str(base), "--blast-dll", str(args.blast_dll),
                        "--entry-map", str(entry_map), "--translations", str(delta),
                        "--output", str(candidate)], check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                                 "--source", str(base), "--candidate", str(candidate),
                                 "--blast-dll", str(args.blast_dll)], check=True,
                                capture_output=True, text=True)
        check = json.loads(result.stdout)
        if not check["changed_entries"]:
            raise ValueError(f"no changes in {archive_name}")
        report[archive_name] = {"base_sha256": check["source_sha256"],
                                "candidate_sha256": check["candidate_sha256"],
                                "changed_entries": check["changed_entries"],
                                "revised_lines": len(rows)}
    (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
