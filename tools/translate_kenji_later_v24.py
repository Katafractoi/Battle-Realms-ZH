"""Translate contiguous later Kenji dialogue, retaining undecided proper names."""

import csv
from pathlib import Path


LINES = {
 ("Kenji_Dialogue.H2O#entry0", "1380"): "恶狼族的难民。",
 ("Kenji_Dialogue.H2O#entry0", "1390"): "给他们食物，让他们住进补给营地。",
 ("Kenji_Dialogue.H2O#entry0", "1400"): "恶狼族已经不是敌人了。",
 ("Kenji_Dialogue.H2O#entry0", "1410"): "即使在我父亲的时代，那些土地也保持独立。",
 ("Kenji_Dialogue.H2O#entry0", "1420"): "东边的高原是圣地，西边的行省则赐给了忍者。",
 ("Kenji_Dialogue.H2O#entry0", "1430"): "僧侣和忍者向来争斗，父亲想把他们隔开。",
 ("Kenji_Dialogue.H2O#entry0", "1440"): "若我们与僧侣结盟，忍者就会与我们为敌。",
 ("Kenji_Dialogue.H2O#entry0", "1450"): "忍者曾为莲花族效力，也许知道他们的秘密。",
 ("Kenji_Dialogue.H2O#entry0", "1460"): "没错……若我们拉拢忍者，僧侣肯定会加入莲花族。",
 ("Kenji_Dialogue.H2O#entry0", "1470"): "别再靠近，Zymeth。",
 ("Kenji_Dialogue.H2O#entry0", "1480"): "早已不在了。",
 ("Kenji_Dialogue.H2O#entry0", "1490"): "我父亲最信任的顾问在哪里？",
 ("Kenji_Dialogue.H2O#entry0", "1500"): "为什么举白旗求和？",
 ("Kenji_Dialogue.H2O#entry0", "1510"): "宝珠已无意义。",
 ("Kenji_Dialogue.H2O#entry0", "1520"): "问你的朋友。",
 ("Kenji_Dialogue.H2O#entry0", "1530"): "我知道：他若不杀你，我也会杀你。",
 ("Kenji_Dialogue.H2O#entry0", "1540"): "你在白费时间。",
 ("Kenji_Dialogue.H2O#entry0", "1550"): "开始了。",
 ("Kenji_Dialogue.H2O#entry0", "1560"): "莲花族正用宝珠清除自身的腐化。",
 ("Kenji_Dialogue.H2O#entry0", "1570"): "神龙说得对。",
 ("Kenji_Dialogue.H2O#entry0", "1580"): "他们的信念给了它力量。",
 ("Kenji_Dialogue.H2O#entry0", "1590"): "我们得快点。",
 ("Kenji_Dialogue.H2O#entry0", "1610"): "多年来，他的后代躲在石壁后，互相憎恨，又惧怕黑暗。",
 ("Kenji_Dialogue.H2O#entry0", "1620"): "他们不明白，即使在 Serpentholm 的中心，阴影也潜伏在每个角落。",
 ("Kenji_Dialogue.H2O#entry0", "1630"): "黑暗永远都在外面，想让我们感到恐惧。",
 ("Kenji_Dialogue.H2O#entry0", "1640"): "但我们不会再躲藏。",
 ("Kenji_Dialogue.H2O#entry0", "1650"): "这片土地将团结一心，迎接未来。",
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    seen = set()
    for row in rows:
        key = (row["source_file"].split("\\")[-1], row["string_id"])
        if key not in LINES:
            continue
        if row["chinese"]:
            raise ValueError(f"already translated: {key}")
        row["chinese"] = LINES[key]
        row["status"] = "draft; later Kenji arc; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} later Kenji lines")


if __name__ == "__main__":
    main()
