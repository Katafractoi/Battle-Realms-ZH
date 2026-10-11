"""Apply narrowly scoped terminology and command punctuation corrections."""

import csv
from pathlib import Path, PureWindowsPath


path = Path("translations/interface-next-review.csv")
with path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
assert fields == ["source_file", "string_id", "english", "chinese", "status", "note"]

clans = ("神龙族", "莲花族", "灵蛇族", "恶狼族")
changes = {}
for name in ("Console_Tooltips.lte", "WOTW_Console_Tooltips.lte"):
    for ident, clan in zip(range(447, 451), clans):
        changes[(name, str(ident))] = (f"{clan}技术", f"{clan}科技")
    for ident in (411, 412, 413, 414, 663, 664, 665, 666):
        changes[(name, str(ident))] = (None, None)
changes[("WOTW_Console_Tooltips.lte", "667")] = (None, None)
changes[("Console_Tooltips.lte", "233")] = (
    "扇舞艺妓及其附近友军牺牲部分生命值，以提高伤害抵抗能力。",
    "扇舞艺妓及其附近友军牺牲部分生命值，以提高伤害抗性。",
)
changes[("WOTW_Console_Tooltips.lte", "2126")] = ("抵抗 ", "抗性 ")
for name in ("Front_End.lte", "WOTW_Front_End.lte"):
    changes[(name, "128")] = ("学会技术数", "已学科技数")

seen = set()
for row in rows:
    key = (PureWindowsPath(row["source_file"]).name, row["string_id"])
    if key not in changes:
        continue
    before, after = changes[key]
    if before is None:
        assert row["english"].find(" - ") >= 0, key
        if "——" not in row["chinese"]:
            assert "：" in row["chinese"], key
            seen.add(key)
            continue
        assert row["chinese"].count("——") == 1, key
        after = row["chinese"].replace("——", "：", 1)
        before = row["chinese"]
    if row["chinese"] == after:
        seen.add(key)
        continue
    assert row["chinese"] == before, (key, row["chinese"])
    row["chinese"] = after
    row["status"] = "显示反馈离线修订，待实机验证"
    row["note"] += " | 2026-10-11 v15：术语或标点校订"
    seen.add(key)
assert seen == set(changes), sorted(set(changes) - seen)

with path.open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print(f"Reviewed {len(changes)} exact source keys")
