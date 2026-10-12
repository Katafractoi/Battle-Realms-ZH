"""Build and validate the v26 Kenji/Shinja dialogue delta."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kenji-base", type=Path, required=True)
    parser.add_argument("--shinja-base", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    with (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream)
                if row["status"] in ("draft; campaign v26; not game-tested",)]
    if len(rows) != 69:
        raise ValueError(f"v26 row count drift: {len(rows)} != 69")
    full_map = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    report = {}
    for name in ("Kenji", "Shinja"):
        archive_name = f"{name}_Dialogue.H2O"
        base = getattr(args, f"{name.lower()}_base")
        # The patcher selects an entry map by the physical archive basename.
        # A previous stage may use a suffix such as `.final.H2O`.
        if base.name != archive_name:
            normalized = args.output / "base" / archive_name
            normalized.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(base, normalized)
            base = normalized
        subset = [row for row in rows if archive_name in row["source_file"]]
        delta = args.output / f"{archive_name}.delta.csv"
        columns = ("source_file", "string_id", "english", "chinese")
        with delta.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows({key: row[key] for key in columns} for row in subset)
        entry_map = args.output / f"{archive_name}.entry-map.json"
        entry_map.write_text(json.dumps({row["source_file"]: full_map[row["source_file"]]
                                         for row in subset}, indent=2) + "\n", encoding="utf-8")
        candidate = args.output / archive_name
        subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                        "--archive", str(base), "--blast-dll", str(args.blast_dll),
                        "--entry-map", str(entry_map), "--translations", str(delta),
                        "--output", str(candidate)], check=True)
        result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                                 "--source", str(base), "--candidate", str(candidate),
                                 "--blast-dll", str(args.blast_dll)], check=True,
                                capture_output=True, text=True)
        check = json.loads(result.stdout)
        report[archive_name] = {"base_sha256": check["source_sha256"],
                                "candidate_sha256": check["candidate_sha256"],
                                "changed_entries": check["changed_entries"],
                                "translated_lines": len(subset)}
    (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
