"""Translate the next Kenji Serpent route passage, preserving uncertain names."""

import csv
from pathlib import Path


LINES = {
    "2110": "别再质疑我。",
    "2120": "胜利的关键。",
    "2130": "我离开期间结识了不少新朋友。",
    "2140": "那宝珠在哪里？",
    "2150": "你真没用。",
    "2160": "那怪物杀了我父亲，你却让它逃了。",
    "2170": "我没时间再浪费了。",
    "2175": "要成为统治者，我必须得到宝珠。",
    "2180": "我们会在 Serpentholm 留下一支守军。",
    "2190": "窃贼往北去了。",
    "2200": "他肯定是想与莲花族或恶狼族结盟。",
    "2210": "我会率主力北上，让他在这些地方只能找到死者作伴。",
    "2220": "这些地方曾效忠灵蛇族。",
    "2230": "必须让它们重新服从。",
    "2250": "他们要是反抗，就把村子烧光。",
    "2260": "Otomo 会跟在后面，清理剩下的乌合之众。",
    "2270": "只要他们忠诚，就不必怕我。",
    "2280": "我杀人是为了让族人更强大。",
    "2290": "我除掉无用之人，留下精兵。",
    "2300": "我不会容忍胆小鬼和不肯出力的人。",
    "2310": "Otomo，你是哪一种？",
    "2320": "那就照我说的做。",
    "2330": "看住他。",
    "2340": "自从莲花族在天鹅池战败，他们就一战接一战地输。",
    "2350": "趁他们还没退回要塞，在这里彻底打败他们。",
    "2360": "恶狼族的主力还在矿区一带。",
    "2370": "正面强攻代价不小，但能夺走他们的兵器库。",
    "2380": "但要是带人穿过沼泽，也许能绕到恶狼族侧翼。",
    "2390": "他们就得派兵应对，其他地方的防线也会变弱。",
    "2400": "用力拉，该死的！",
    "2410": "这已经是第二次了。",
    "2420": "拿他做个例子。",
    "2430": "你是 Otomo 的人。",
    "2440": "Otomo 干的？",
    "2460": "各就各位！",
    "2470": "Otomo，Otomo，Otomo……",
    "2480": "你为什么这么想死？",
    "2490": "我本来还会让你多活一两年。",
    "2500": "还不错。",
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    seen = set()
    for row in rows:
        if not row["source_file"].endswith("Kenji_Dialogue.H2O#entry0"):
            continue
        key = row["string_id"]
        if key not in LINES:
            continue
        if row["chinese"]:
            raise ValueError(f"already translated: {key}")
        row["chinese"] = LINES[key]
        row["status"] = "draft; Kenji campaign v25; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} Kenji lines")


if __name__ == "__main__":
    main()
