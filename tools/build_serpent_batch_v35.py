"""Build v34 Serpent and v35 WOTW Serpent dialogue candidates offline."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys


STATUSES = {
    "draft; Serpent campaign v34; font candidate pending; not game-tested",
    "draft; Serpent mines v35; font candidate pending; not game-tested",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serpent-base", type=Path, required=True)
    parser.add_argument("--wotw-serpent-base", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["status"] in STATUSES]
    if len(rows) != 113:
        raise ValueError(f"row count drift: {len(rows)} != 113")
    full_map = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    report = {}
    for name, base, expected in (("Serpent_Dialogue.H2O", args.serpent_base, [0, 10, 26, 47]),
                                 ("WOTW_Serpent_Dialogue.H2O", args.wotw_serpent_base, [0])):
        if base.name != name:
            raise ValueError(f"base filename must be {name}")
        subset = [r for r in rows if r["source_file"].split("\\")[-1].split("#")[0] == name]
        columns = ("source_file", "string_id", "english", "chinese")
        delta = args.output_dir / (name + ".delta.csv")
        with delta.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, columns)
            writer.writeheader()
            writer.writerows({key: row[key] for key in columns} for row in subset)
        entry_map = args.output_dir / (name + ".entry-map.json")
        entry_map.write_text(json.dumps({r["source_file"]: full_map[r["source_file"]]
                                         for r in subset}, indent=2) + "\n", encoding="utf-8")
        candidate = args.output_dir / name
        subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                        "--archive", str(base), "--blast-dll", str(args.blast_dll),
                        "--entry-map", str(entry_map), "--translations", str(delta),
                        "--output", str(candidate)], check=True)
        result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                                 "--source", str(base), "--candidate", str(candidate),
                                 "--blast-dll", str(args.blast_dll)], check=True,
                                capture_output=True, text=True)
        check = json.loads(result.stdout)
        if check["changed_entries"] != expected:
            raise ValueError(f"unexpected changed entries in {name}: {check['changed_entries']}")
        report[name] = {"candidate_sha256": check["candidate_sha256"],
                        "changed_entries": check["changed_entries"],
                        "translated_lines": len(subset)}
    (args.output_dir / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
