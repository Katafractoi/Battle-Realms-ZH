"""Build and validate all dialogue archives needed to complete Kenji's name."""

import csv
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior", type=Path, required=True, help="Prior validated v16/v19 candidate directory")
    parser.add_argument("--game", type=Path, required=True, help="Official Battle Realms installation, read-only")
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    prior, game, dll, output = args.prior, args.game, args.blast_dll, args.output
    output.mkdir(parents=True, exist_ok=True)
    with (root / "translations/dialogue-all-english.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["status"] == "draft; name confirmed; not game-tested"]
    if len(rows) != 26 or any("Kenji" not in r["english"] or "健治" not in r["chinese"] for r in rows):
        raise ValueError("Kenji translation set drift")
    groups = {}
    full_mapping = json.loads((root / "tools/dialogue-english-entry-map.json").read_text(encoding="utf-8"))
    for row in rows:
        archive = row["source_file"].split("\\")[-1].split("#")[0]
        groups.setdefault(archive, []).append(row)
    report = {}
    for archive, items in sorted(groups.items()):
        if archive == "Kenji_Dialogue.H2O":
            source = prior / "v19-kenji-opening-final" / archive
        elif archive in ("Dragon_Dialogue.H2O", "Otomo_Dialogue.H2O"):
            source = prior / "v16-names-dialogue" / archive
        else:
            source = game / "Sound" / "Dialogue" / archive
        delta = output / (archive + ".delta.csv")
        with delta.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("source_file", "string_id", "english", "chinese"))
            writer.writeheader()
            writer.writerows({k: row[k] for k in writer.fieldnames} for row in items)
        mapping = output / (archive + ".entry-map.json")
        mapping.write_text(json.dumps({r["source_file"]: full_mapping[r["source_file"]]
                                       for r in items}, indent=2) + "\n", encoding="utf-8")
        candidate = output / archive
        subprocess.run([sys.executable, str(root / "tools/patch_lte_h2o.py"),
                        "--archive", str(source), "--blast-dll", str(dll),
                        "--entry-map", str(mapping),
                        "--translations", str(delta), "--output", str(candidate)], check=True)
        validation = subprocess.run([sys.executable, str(root / "tools/validate_h2o_v7.py"),
                                     "--source", str(source), "--candidate", str(candidate),
                                     "--blast-dll", str(dll)], check=True, capture_output=True, text=True)
        detail = json.loads(validation.stdout)
        if not detail["changed_entries"]:
            raise ValueError(f"No changed entries in {archive}")
        report[archive] = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                           "candidate_sha256": detail["candidate_sha256"],
                           "changed_entries": detail["changed_entries"], "name_lines": len(items)}
    report["Interface_Text.H2O"] = {"candidate_sha256": hashlib.sha256(
        (prior / "v16-names-candidate/Interface_Text.H2O").read_bytes()).hexdigest(),
        "note": "Existing name translation; copy separately for live test"}
    (output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
