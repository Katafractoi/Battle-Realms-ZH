"""Build two isolated, offline CJK wrapping probes from one tested archive.

Both probes change only WOTW Goals #0 and WOTW tooltip #565. The 12-character
probe tests length; the LF probe tests whether the same widgets honor a hard
line break. Neither is a release translation or an asserted renderer fix.
"""
import argparse
import csv
import json
from pathlib import Path
import struct
import subprocess
import sys

from patch_lte_h2o import decoder, records


TARGETS = [(r"Text\ENG\WOTW_Goals.lte", 0),
           (r"Text\ENG\WOTW_Console_Tooltips.lte", 565)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--entry-map", type=Path, required=True)
    p.add_argument("--blast-dll", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    blob = a.base.read_bytes()
    mapping = json.loads(a.entry_map.read_text(encoding="utf-8"))
    decode = decoder(a.blast_dll)
    texts = {}
    for name, ident in TARGETS:
        i = mapping[name]
        f = struct.unpack_from("<10I", blob, 513 + 40 * i)
        raw = decode(blob[f[6] + 12:f[6] + 12 + f[4]], f[3])
        matching = [text for rid, _, text, _ in records(raw) if rid == ident]
        if len(matching) != 1 or len(matching[0]) < 24:
            raise ValueError("unexpected probe source " + name)
        texts[(name, ident)] = matching[0]
    a.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in ("short12", "lf12"):
        translation = a.output_dir / (variant + ".csv")
        with translation.open("w", encoding="utf-8-sig", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=["source_file", "string_id",
                                                      "english", "chinese"])
            writer.writeheader()
            for (name, ident), value in texts.items():
                replacement = value[:12] if variant == "short12" else value[:12] + "\n" + value[12:]
                writer.writerow({"source_file": name, "string_id": ident,
                                 "english": value, "chinese": replacement})
        candidate = a.output_dir / (variant + ".H2O")
        subprocess.run([sys.executable, str(Path(__file__).with_name("patch_lte_h2o.py")),
                        "--archive", str(a.base), "--entry-map", str(a.entry_map),
                        "--blast-dll", str(a.blast_dll), "--translations", str(translation),
                        "--output", str(candidate)], check=True)
        subprocess.run([sys.executable, str(Path(__file__).with_name("validate_h2o_v7.py")),
                        "--source", str(a.base), "--candidate", str(candidate),
                        "--blast-dll", str(a.blast_dll)], check=True)


if __name__ == "__main__":
    main()
