"""Continue two contiguous Kenji and Otomo Serpentholm dialogue spans."""

import csv
from pathlib import Path


LINES = {
 ("Kenji_Dialogue.H2O#entry0", "1180"): "我在寻找巨蛇宝珠。",
 ("Kenji_Dialogue.H2O#entry0", "1190"): "偷走它的人不是莲花族。",
 ("Kenji_Dialogue.H2O#entry0", "1200"): "Tarrant 曾用宝珠让世界破碎。",
 ("Kenji_Dialogue.H2O#entry0", "1210"): "可是……",
 ("Kenji_Dialogue.H2O#entry0", "1220"): "这片土地必须恢复生机。",
 ("Kenji_Dialogue.H2O#entry0", "1230"): "没有宝珠，我该怎么修复本族造成的伤害？",
 ("Kenji_Dialogue.H2O#entry0", "1240"): "什么邪恶？",
 ("Kenji_Dialogue.H2O#entry0", "1250"): "等等……我该去哪里找你？",
 ("Kenji_Dialogue.H2O#entry0", "1260"): "神龙的时代已经过去了。",
 ("Kenji_Dialogue.H2O#entry0", "1265"): "我们不该去见他。",
 ("Kenji_Dialogue.H2O#entry0", "1280"): "杀了他。",
 ("Kenji_Dialogue.H2O#entry0", "1290"): "他们背叛了我们。",
 ("Kenji_Dialogue.H2O#entry0", "1300"): "不。附近的村子会帮我们。",
 ("Kenji_Dialogue.H2O#entry0", "1310"): "莲花族在这里找不到帮手。",
 ("Kenji_Dialogue.H2O#entry0", "1320"): "我们留下来战斗。",
 ("Kenji_Dialogue.H2O#entry0", "1330"): "抱歉，老朋友。",
 ("Kenji_Dialogue.H2O#entry0", "1340"): "去办吧。",
 ("Kenji_Dialogue.H2O#entry0", "1350"): "Kazan！",
 ("Kenji_Dialogue.H2O#entry0", "1360"): "烧掉 Serpentholm。把它烧成平地。",
 ("Kenji_Dialogue.H2O#entry0", "1370"): "巨蛇已不复存在。",
 ("Kenji_Dialogue.H2O#entry0", "1375"): "只剩神龙。",
 ("Otomo_Dialogue.H2O#entry0", "770"): "不……恶狼族已经败了。",
 ("Otomo_Dialogue.H2O#entry0", "780"): "莲花族的术士才是真正的敌人。",
 ("Otomo_Dialogue.H2O#entry0", "790"): "不能让他们的军队逃回高原。",
 ("Otomo_Dialogue.H2O#entry0", "800"): "趁他们背靠大海时进攻，一举解决他们。",
 ("Otomo_Dialogue.H2O#entry0", "810"): "我会活下去。",
 ("Otomo_Dialogue.H2O#entry0", "820"): "你有话就说……",
 ("Otomo_Dialogue.H2O#entry0", "840"): "放尊重点！",
 ("Otomo_Dialogue.H2O#entry0", "850"): "即使在你父亲死后，艺妓仍被视为不可侵犯……",
 ("Otomo_Dialogue.H2O#entry0", "860"): "宝珠也许还安全。",
 ("Otomo_Dialogue.H2O#entry0", "870"): "大人，别听他的。这条路最安全。",
 ("Otomo_Dialogue.H2O#entry0", "880"): "虽然莲花族在那里建了前哨，但密林能掩护我们通过。",
 ("Otomo_Dialogue.H2O#entry0", "890"): "在救火。",
 ("Otomo_Dialogue.H2O#entry0", "910"): "我们把这些人赶出了家园。",
 ("Otomo_Dialogue.H2O#entry0", "920"): "你说话越来越像你父亲了。",
 ("Otomo_Dialogue.H2O#entry0", "930"): "Serpentholm 已成一片荒地。",
 ("Otomo_Dialogue.H2O#entry0", "940"): "巨蛇死时，莲花族术士拆毁了那里。",
 ("Otomo_Dialogue.H2O#entry0", "960"): "我们的敌人以为它在这里。",
 ("Otomo_Dialogue.H2O#entry0", "970"): "我们可以继续前往 Serpentholm。",
 ("Otomo_Dialogue.H2O#entry0", "980"): "那艺妓怎么办？",
 ("Otomo_Dialogue.H2O#entry0", "990"): "什么？我们不能……",
 ("Otomo_Dialogue.H2O#entry0", "1000"): "可是大人……他们人多，我们人少。",
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
        row["status"] = "draft; Serpentholm arc; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} contiguous Serpentholm lines")


if __name__ == "__main__":
    main()
