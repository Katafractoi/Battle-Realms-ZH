"""Translate contiguous Kenji and Shinja late-campaign dialogue."""

import csv
from pathlib import Path


LINES = {
    ("Shinja_Dialogue.H2O#entry0", "1210"): "保持警惕。",
    ("Shinja_Dialogue.H2O#entry0", "1220"): "有什么东西带走了他们。",
    ("Shinja_Dialogue.H2O#entry0", "1230"): "是你，你带走了村民。",
    ("Shinja_Dialogue.H2O#entry0", "1240"): "谁在问？",
    ("Shinja_Dialogue.H2O#entry0", "1250"): "怎么会？",
    ("Shinja_Dialogue.H2O#entry0", "1260"): "靠杀掉他的士兵？",
    ("Shinja_Dialogue.H2O#entry0", "1270"): "我们不需要你的死灵法术。",
    ("Shinja_Dialogue.H2O#entry0", "1280"): "你怎么知道？",
    ("Shinja_Dialogue.H2O#entry0", "1310"): "不对劲。",
    ("Shinja_Dialogue.H2O#entry0", "1320"): "Otomo 早该到了。",
    ("Shinja_Dialogue.H2O#entry0", "1330"): "他的军队在哪里？",
    ("Shinja_Dialogue.H2O#entry0", "1340"): "叛军。",
    ("Shinja_Dialogue.H2O#entry0", "1350"): "他们认得我。",
    ("Shinja_Dialogue.H2O#entry0", "1360"): "他们是 Otomo 的人。",
    ("Shinja_Dialogue.H2O#entry0", "1370"): "我们被背叛了。",
    ("Shinja_Dialogue.H2O#entry0", "1380"): "Otomo 在哪里？",
    ("Shinja_Dialogue.H2O#entry0", "1390"): "他抛下了你们。",
    ("Shinja_Dialogue.H2O#entry0", "1400"): "他把你们留在这里等死。",
    ("Shinja_Dialogue.H2O#entry0", "1410"): "一个就够。",
    ("Shinja_Dialogue.H2O#entry0", "1420"): "让他们的尸体留在那里腐化。",
    ("Shinja_Dialogue.H2O#entry0", "1430"): "我们得走了。",
    ("Shinja_Dialogue.H2O#entry0", "1440"): "我们效忠灵蛇族。",
    ("Shinja_Dialogue.H2O#entry0", "1450"): "照命令，把它放在大门上方。",
    ("Shinja_Dialogue.H2O#entry0", "1460"): "只要还能继续杀人。",
    ("Shinja_Dialogue.H2O#entry0", "1470"): "可这些地方仍然无人占领。",
    ("Shinja_Dialogue.H2O#entry0", "1480"): "不过……那些圣兄弟倒很适合派去前线送死。",
    ("Shinja_Dialogue.H2O#entry0", "1490"): "如果放任他们自由，他们可能会投靠恶狼族。",
    ("Shinja_Dialogue.H2O#entry0", "1500"): "休战旗。",
    ("Shinja_Dialogue.H2O#entry0", "1510"): "也许我们该再等等……",
    ("Shinja_Dialogue.H2O#entry0", "1520"): "看，雪崩截断了河道。",
    ("Shinja_Dialogue.H2O#entry0", "1530"): "可以从那里过河，绕到他们背后。",
    ("Shinja_Dialogue.H2O#entry0", "1540"): "河上的通道和浅水处都有重兵把守。",
    ("Shinja_Dialogue.H2O#entry0", "1550"): "一群无知的人。",
    ("Shinja_Dialogue.H2O#entry0", "1560"): "他们在想什么？",
    ("Shinja_Dialogue.H2O#entry0", "1570"): "这一带已经有人占领。",
    ("Shinja_Dialogue.H2O#entry0", "1580"): "在我杀你之前，快滚！",
    ("Shinja_Dialogue.H2O#entry0", "1590"): "他们干活真勤快，不是吗？",
    ("Shinja_Dialogue.H2O#entry0", "1600"): "他们发现我们了！",
    ("Shinja_Dialogue.H2O#entry0", "1610"): "我们离矿区不远了。",
    ("Kenji_Dialogue.H2O#entry0", "2510"): "Otomo 的头在哪里？",
    ("Kenji_Dialogue.H2O#entry0", "2520"): "很好。",
    ("Kenji_Dialogue.H2O#entry0", "2530"): "你找到的那个死灵法师……能信吗？",
    ("Kenji_Dialogue.H2O#entry0", "2540"): "那他暂时还会忠诚。",
    ("Kenji_Dialogue.H2O#entry0", "2550"): "看这里。",
    ("Kenji_Dialogue.H2O#entry0", "2560"): "探子回报，恶狼族把莲花族要塞烧光了。",
    ("Kenji_Dialogue.H2O#entry0", "2570"): "他们仍控制着所有高地和矿区。",
    ("Kenji_Dialogue.H2O#entry0", "2580"): "那些僧人在东边高地待了多年。",
    ("Kenji_Dialogue.H2O#entry0", "2590"): "我父亲把西边沼泽交给忍者，就是为了让他们远离圣地。",
    ("Kenji_Dialogue.H2O#entry0", "2600"): "忍者曾效力于莲花族，恶狼族一直记着这事。",
    ("Kenji_Dialogue.H2O#entry0", "2610"): "他们的农民很迷信，怕那些刺客怕得要命。",
    ("Kenji_Dialogue.H2O#entry0", "2620"): "如果忍者加入我们，谁也挡不住我们。",
    ("Kenji_Dialogue.H2O#entry0", "2630"): "也许吧。",
    ("Kenji_Dialogue.H2O#entry0", "2640"): "他们一向独来独往，也不怎么喜欢我父亲。",
    ("Kenji_Dialogue.H2O#entry0", "2650"): "等等。",
    ("Kenji_Dialogue.H2O#entry0", "2660"): "就是现在。",
    ("Kenji_Dialogue.H2O#entry0", "2670"): "不，看那里。",
    ("Kenji_Dialogue.H2O#entry0", "2680"): "恶狼族在保护杀我父亲的人。",
    ("Kenji_Dialogue.H2O#entry0", "2690"): "不休战，也不留活口。",
    ("Kenji_Dialogue.H2O#entry0", "2700"): "他们想使用宝珠。",
    ("Kenji_Dialogue.H2O#entry0", "2710"): "他们想回家。",
    ("Kenji_Dialogue.H2O#entry0", "2720"): "如果他们重造这个世界，就能逃往海对岸。",
    ("Kenji_Dialogue.H2O#entry0", "2730"): "今夜就让你尽兴，死者。",
    ("Kenji_Dialogue.H2O#entry0", "2740"): "你的时代过去了。",
    ("Kenji_Dialogue.H2O#entry0", "2750"): "这里不属于你。",
    ("Kenji_Dialogue.H2O#entry0", "2770"): "两个世纪以来，我的族人一直藏身，求神龙保护。",
    ("Kenji_Dialogue.H2O#entry0", "2780"): "但神龙只是传说。",
    ("Kenji_Dialogue.H2O#entry0", "2790"): "软弱无用的人都不在了。",
    ("Kenji_Dialogue.H2O#entry0", "2800"): "最后的胆小鬼和叛徒 Otomo 一同死了。",
    ("Kenji_Dialogue.H2O#entry0", "2810"): "我们终于得到净化。",
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
        row["status"] = "draft; campaign v26; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} campaign lines")


if __name__ == "__main__":
    main()
