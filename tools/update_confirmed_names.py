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
    if any(count != 0 for count in counts.values()) and counts != expected:
        raise ValueError(f"partially updated source: {name}: {counts}")
    changed = 0
    for row in rows:
        original = row["chinese"]
        for english, chinese in NAMES.items():
            row["chinese"] = row["chinese"].replace(english, chinese)
            row["chinese"] = row["chinese"].replace(" " + chinese, chinese).replace(chinese + " ", chinese)
        if row["chinese"] != original:
            changed += 1
            row["status"] = "已确认专名离线修订，待实机验证"
            if "note" in row:
                marker = "2026-10-11 确认健治/信蛇"
                if marker not in row["note"]:
                    row["note"] += " | " + marker
    if not changed:
        print(f"Already updated {name}")
        continue
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {name}: {changed} rows; old names {counts}")
