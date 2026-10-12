"""Translate Kenji's contiguous Serpent-branch dialogue through ID 2100."""

import csv
from pathlib import Path


LINES = {
 ("Kenji_Dialogue.H2O#entry0", "1660"): "该让阴影害怕我们了。",
 ("Kenji_Dialogue.H2O#entry0", "1670"): "不。",
 ("Kenji_Dialogue.H2O#entry0", "1680"): "巨蛇死了。",
 ("Kenji_Dialogue.H2O#entry0", "1690"): "就算我是，又怎样？",
 ("Kenji_Dialogue.H2O#entry0", "1700"): "你就这样轻易背叛你的领主？",
 ("Kenji_Dialogue.H2O#entry0", "1720"): "我父亲的手下为何要争抢他帝国剩下的东西？",
 ("Kenji_Dialogue.H2O#entry0", "1730"): "没错……农民这群人没规矩，得好好教训。",
 ("Kenji_Dialogue.H2O#entry0", "1750"): "臣服，否则我砍下你的头。",
 ("Kenji_Dialogue.H2O#entry0", "1760"): "你知道我是谁。",
 ("Kenji_Dialogue.H2O#entry0", "1770"): "你们为什么一直打下去？",
 ("Kenji_Dialogue.H2O#entry0", "1780"): "你们以前都是灵蛇族的人。",
 ("Kenji_Dialogue.H2O#entry0", "1790"): "现在你们要么归我，要么都得死。",
 ("Kenji_Dialogue.H2O#entry0", "1800"): "你们奉命守护 Tarrant 的宝珠。",
 ("Kenji_Dialogue.H2O#entry0", "1810"): "它在哪里？",
 ("Kenji_Dialogue.H2O#entry0", "1820"): "你们把神圣的宝珠交给了艺妓？",
 ("Kenji_Dialogue.H2O#entry0", "1830"): "该死的老东西！",
 ("Kenji_Dialogue.H2O#entry0", "1840"): "巨蛇太糊涂了。",
 ("Kenji_Dialogue.H2O#entry0", "1850"): "莲花族一直眼红宝珠的力量。",
 ("Kenji_Dialogue.H2O#entry0", "1860"): "旧规矩撑不了多久。",
 ("Kenji_Dialogue.H2O#entry0", "1870"): "我们必须快点行动。",
 ("Kenji_Dialogue.H2O#entry0", "1880"): "天鹅池就在北边。",
 ("Kenji_Dialogue.H2O#entry0", "1890"): "最近的路直穿 Riverside。",
 ("Kenji_Dialogue.H2O#entry0", "1900"): "真是好极了。",
 ("Kenji_Dialogue.H2O#entry0", "1910"): "就像从前……",
 ("Kenji_Dialogue.H2O#entry0", "1920"): "当初就该趁机把他们全杀了。",
 ("Kenji_Dialogue.H2O#entry0", "1930"): "我哥哥说得对。",
 ("Kenji_Dialogue.H2O#entry0", "1940"): "你去哪儿了？",
 ("Kenji_Dialogue.H2O#entry0", "1950"): "我的家园。他们的田地、牲口、女儿和儿子——全都属于我。",
 ("Kenji_Dialogue.H2O#entry0", "1960"): "这是灵蛇族的土地。",
 ("Kenji_Dialogue.H2O#entry0", "1970"): "总还有比我更坏的人。",
 ("Kenji_Dialogue.H2O#entry0", "1980"): "让部队出发。",
 ("Kenji_Dialogue.H2O#entry0", "1990"): "继续赶路，黄昏前就能到天鹅池。",
 ("Kenji_Dialogue.H2O#entry0", "2000"): "把 Tarrant 的宝珠交给我。",
 ("Kenji_Dialogue.H2O#entry0", "2010"): "放在我手里更安全。",
 ("Kenji_Dialogue.H2O#entry0", "2020"): "你疯了吗？",
 ("Kenji_Dialogue.H2O#entry0", "2030"): "这么说你也看见他了。",
 ("Kenji_Dialogue.H2O#entry0", "2040"): "他们难道不明白我是谁？",
 ("Kenji_Dialogue.H2O#entry0", "2050"): "不。",
 ("Kenji_Dialogue.H2O#entry0", "2060"): "打过去，快而狠。",
 ("Kenji_Dialogue.H2O#entry0", "2070"): "处决话最多的那个，把其他人带来。",
 ("Kenji_Dialogue.H2O#entry0", "2080"): "快。",
 ("Kenji_Dialogue.H2O#entry0", "2090"): "好。",
 ("Kenji_Dialogue.H2O#entry0", "2100"): "我们取回本该属于我们的东西，让他们互相残杀。",
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
        row["status"] = "draft; Kenji Serpent branch; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} Kenji Serpent-branch lines")


if __name__ == "__main__":
    main()
