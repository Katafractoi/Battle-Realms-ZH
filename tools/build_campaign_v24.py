"""Build and validate the three dialogue archives for the v24 campaign batch."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys


STATUSES = {
    "draft; later Kenji arc; not game-tested",
    "draft; Kenji Serpent branch; not game-tested",
    "draft; later Otomo arc; not game-tested",
    "draft; Shinja campaign arc; not game-tested",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("kenji", "otomo", "shinja"):
        parser.add_argument(f"--{name}-base", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    with (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row["status"] in STATUSES]
    if len(rows) != 156:
        raise ValueError(f"v24 row count drift: {len(rows)} != 156")
    full_map = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    report = {}
    for name in ("kenji", "otomo", "shinja"):
        archive_name = f"{name.capitalize()}_Dialogue.H2O"
        base = getattr(args, f"{name}_base")
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
    # This earlier Kenji line used the obsolete faction term. Apply a second
    # exact-text delta so the v24 output agrees with the reviewed CSV.
    kenji_source = "Sound\\Dialogue\\Kenji_Dialogue.H2O#entry0"
    term_row = next(row for row in csv.DictReader(
        (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline=""))
                    if row["source_file"] == kenji_source and row["string_id"] == "1600")
    term_delta = args.output / "Kenji.termfix.delta.csv"
    with term_delta.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerow({"source_file": kenji_source, "string_id": "1600",
                         "english": "我是龙族领主健治。", "chinese": term_row["chinese"]})
    term_map = args.output / "Kenji.termfix.entry-map.json"
    term_map.write_text(json.dumps({kenji_source: 0}) + "\n", encoding="utf-8")
    kenji = args.output / "Kenji_Dialogue.H2O"
    final = args.output / "Kenji_Dialogue.final.H2O"
    subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                    "--archive", str(kenji), "--blast-dll", str(args.blast_dll),
                    "--entry-map", str(term_map), "--translations", str(term_delta),
                    "--output", str(final)], check=True)
    result = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                             "--source", str(kenji), "--candidate", str(final),
                             "--blast-dll", str(args.blast_dll)], check=True,
                            capture_output=True, text=True)
    report["Kenji_Dialogue.H2O"]["final_sha256"] = json.loads(result.stdout)["candidate_sha256"]
    (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
