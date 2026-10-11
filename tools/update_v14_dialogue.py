"""Apply the v14 opening-cinematic and Dojo tutorial subtitle batch.

Only matching English source lines are changed. The full inventory remains the
single source of truth; this script is idempotent and fails on source drift.
"""
import csv
from pathlib import Path

path = Path("translations/dialogue-all-english.csv")
prefix = "Sound\\Dialogue\\"
edits = {
    ("Kenji_Dialogue.H2O#entry0", 400): "我是灵蛇族的 Kenji。我的祖先曾令世界分崩离析。",
    ("Kenji_Dialogue.H2O#entry0", 410): "Horde 所到之处尽成废墟，他便率领族人南逃，尽力保住仅存的一切。",
    ("Kenji_Dialogue.H2O#entry0", 420): "可当他们抵达高原时，前方已无路可逃。",
    ("Kenji_Dialogue.H2O#entry0", 430): "Tarrant 至死也不知道，留下来的抉择究竟意味着什么。",
    ("Kenji_Dialogue.H2O#entry0", 440): "他不知道 Horde 只是灵蛇族日后众多祸患中的第一个。",
    ("Kenji_Dialogue.H2O#entry0", 450): "他更不可能知道，失去宝珠的指引，后代会变得软弱而邪恶。",
    ("Kenji_Dialogue.H2O#entry0", 460): "他真的有过选择吗？",
    ("Dragon_Dialogue.H2O#entry74", 720): "太好了！",
    ("Dragon_Dialogue.H2O#entry74", 730): "我们很快就能开始组建军队了！",
    ("Dragon_Dialogue.H2O#entry74", 740): "训练战士需要一座道场。",
    ("Dragon_Dialogue.H2O#entry74", 750): "选中几名农民。",
    ("Dragon_Dialogue.H2O#entry74", 760): "看，建造菜单中已经可以选择道场了。",
    ("Dragon_Dialogue.H2O#entry74", 770): "找个合适的位置，像建农舍那样建起道场。",
    ("Dragon_Dialogue.H2O#entry74", 780): "选中的农民越多，道场建成得就越快。",
    ("Dragon_Dialogue.H2O#entry74", 790): "按住鼠标右键左右拖动，还能旋转建筑。",
    ("Dragon_Dialogue.H2O#entry74", 800): "松开鼠标右键，就能放置建筑。",
    ("Dragon_Dialogue.H2O#entry74", 810): "大人，我们得把道场建好。",
    ("Dragon_Dialogue.H2O#entry74", 820): "选中几名农民，右键点击未完工的道场，完成建造。",
    ("Otomo_Dialogue.H2O#entry0", 1290): "很好！我们就快能组建军队了！",
    ("Otomo_Dialogue.H2O#entry0", 1300): "要训练战士，我们需要一座道场。",
    ("Otomo_Dialogue.H2O#entry0", 1310): "选中一名农民。",
    ("Otomo_Dialogue.H2O#entry0", 1320): "看，建造菜单中已经可以选择道场了。",
    ("Otomo_Dialogue.H2O#entry0", 1330): "找个合适的位置，像建农舍那样建起道场。",
    ("Otomo_Dialogue.H2O#entry0", 1340): "现在来训练你的第一名长矛兵。",
    ("Otomo_Dialogue.H2O#entry0", 1350): "选中一名农民，右键点击道场。",
    ("Otomo_Dialogue.H2O#entry0", 1360): "训练长矛兵要消耗稻米和水，记得让一些农民继续采集。",
    ("Otomo_Dialogue.H2O#entry0", 1370): "干得好，我们已经迈出第一步了！",
}

with path.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
assert fields == ["source_file", "string_id", "english", "chinese", "status"]
found = set()
changed = 0
for row in rows:
    source = row["source_file"]
    if not source.startswith(prefix):
        continue
    key = (source[len(prefix):], int(row["string_id"]))
    if key not in edits:
        continue
    assert row["english"], key
    found.add(key)
    if row["chinese"] != edits[key]:
        assert not row["chinese"], f"Existing translation at {key}"
        row["chinese"] = edits[key]
        row["status"] = "draft; not game-tested"
        changed += 1
assert found == set(edits), f"Missing rows: {set(edits) - found}"
with path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print(f"v14 dialogue rows: {len(edits)} targeted, {changed} newly translated")
