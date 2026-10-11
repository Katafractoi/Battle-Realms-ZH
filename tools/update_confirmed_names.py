"""Apply only user-confirmed Kenji/Shinja names to draft Chinese text."""

import csv
from pathlib import Path


EXPECTED = {
    "translations/interface-next-review.csv": {"Kenji": 16, "Shinja": 44},
    "translations/dialogue-all-english.csv": {"Kenji": 6, "Shinja": 3},
}
NAMES = {"Kenji": "健治", "Shinja": "信蛇"}

for name, expected in EXPECTED.items():
    path = Path(name)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    counts = {key: sum(key in row["chinese"] for row in rows) for key in NAMES}
    if any(counts[key] not in (0, expected[key]) for key in NAMES):
        raise ValueError(f"unexpected source count in {name}: {counts}")
    if all(count == 0 for count in counts.values()):
        print(f"Already updated {name}")
        continue
    if counts != expected:
        raise ValueError(f"partially updated source: {name}: {counts}")
    for row in rows:
        original = row["chinese"]
        for english, chinese in NAMES.items():
            row["chinese"] = row["chinese"].replace(english, chinese)
        if row["chinese"] != original:
            row["status"] = "已确认专名离线修订，待实机验证"
            if "note" in row:
                row["note"] += " | 2026-10-11 确认健治/信蛇"
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {name}: {counts}")
