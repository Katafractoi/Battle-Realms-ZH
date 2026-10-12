"""Translate four contiguous Serpent campaign character scenes."""

import csv
from pathlib import Path


LINES = {
    ("Serpent_Dialogue.H2O#entry0", "0"): "恶狼族矿工有一点值得承认：他们很会逃跑。",
    ("Serpent_Dialogue.H2O#entry0", "10"): "嗯，这点得感谢父亲。",
    ("Serpent_Dialogue.H2O#entry0", "20"): "他们为莲花族效力，莲花族为我们效力。",
    ("Serpent_Dialogue.H2O#entry0", "30"): "只有 Oja 家族有资格做这片土地的领主。",
    ("Serpent_Dialogue.H2O#entry0", "40"): "父亲走后很久，灵蛇族仍会统治。",
    ("Serpent_Dialogue.H2O#entry0", "50"): "当然，我是长子！",
    ("Serpent_Dialogue.H2O#entry0", "60"): "何况你一有空就在后巷酒馆和下等人寻欢。",
    ("Serpent_Dialogue.H2O#entry0", "70"): "你根本没有打仗的胆量。",
    ("Serpent_Dialogue.H2O#entry0", "80"): "是啊，总赢可真是沉重的负担。",
    ("Serpent_Dialogue.H2O#entry10", "210"): "离开我的地！",
    ("Serpent_Dialogue.H2O#entry10", "220"): "这座农庄是我从恶狼族手里买来的！",
    ("Serpent_Dialogue.H2O#entry10", "230"): "蠢货，回去干活！",
    ("Serpent_Dialogue.H2O#entry10", "240"): "我们的‘客人’正要走。",
    ("Serpent_Dialogue.H2O#entry10", "250"): "我说，滚出去！",
    ("Serpent_Dialogue.H2O#entry10", "260"): "你会为此付出代价！",
    ("Serpent_Dialogue.H2O#entry10", "270"): "离开我的地！",
    ("Serpent_Dialogue.H2O#entry10", "280"): "这座农庄是我从恶狼族手里买来的。",
    ("Serpent_Dialogue.H2O#entry10", "290"): "那我就和你打。",
    ("Serpent_Dialogue.H2O#entry10", "300"): "我的价钱可不低。",
    ("Serpent_Dialogue.H2O#entry10", "310"): "我想……尝尝……你的一位艺妓。",
    ("Serpent_Dialogue.H2O#entry10", "320"): "啊……进去吧，美人，快进去。",
    ("Serpent_Dialogue.H2O#entry10", "330"): "真会说服人。",
    ("Serpent_Dialogue.H2O#entry10", "340"): "你让我别无选择。",
    ("Serpent_Dialogue.H2O#entry26", "200"): "眼力不错。",
    ("Serpent_Dialogue.H2O#entry26", "220"): "他在哪里？",
    ("Serpent_Dialogue.H2O#entry26", "230"): "我，就是死灵法师。",
    ("Serpent_Dialogue.H2O#entry26", "240"): "我能帮他。",
    ("Serpent_Dialogue.H2O#entry26", "250"): "蛇人，别对我说教。",
    ("Serpent_Dialogue.H2O#entry26", "260"): "你刺穿那名艺妓时，喜欢听她的惨叫吗？",
    ("Serpent_Dialogue.H2O#entry26", "270"): "时间不多了。",
    ("Serpent_Dialogue.H2O#entry26", "280"): "恶狼族已经拿到宝珠。",
    ("Serpent_Dialogue.H2O#entry26", "290"): "死者会对我说话。",
    ("Serpent_Dialogue.H2O#entry26", "300"): "这么说，他回 Serpentholm 了。",
    ("Serpent_Dialogue.H2O#entry26", "320"): "那真是……太好了。",
    ("Serpent_Dialogue.H2O#entry26", "330"): "那就带路。",
    ("Serpent_Dialogue.H2O#entry26", "340"): "太好了……",
    ("Serpent_Dialogue.H2O#entry26", "350"): "那是谁？",
    ("Serpent_Dialogue.H2O#entry26", "360"): "他们认得你？",
    ("Serpent_Dialogue.H2O#entry26", "370"): "啊……很好……",
    ("Serpent_Dialogue.H2O#entry26", "380"): "又有朋友可以陪我玩了……",
    ("Serpent_Dialogue.H2O#entry26", "390"): "太好了……",
    ("Serpent_Dialogue.H2O#entry47", "210"): "你不是村民。",
    ("Serpent_Dialogue.H2O#entry47", "230"): "喝！",
    ("Serpent_Dialogue.H2O#entry47", "240"): "你打起来像灵蛇本人。",
    ("Serpent_Dialogue.H2O#entry47", "260"): "可你拿着黑暗之刃。",
    ("Serpent_Dialogue.H2O#entry47", "270"): "你也是他的继承人。",
    ("Serpent_Dialogue.H2O#entry47", "280"): "我没有冒犯的意思。",
    ("Serpent_Dialogue.H2O#entry47", "290"): "只要你一声令下，我们就是你的人。",
    ("Serpent_Dialogue.H2O#entry47", "310"): "他把我的人浪费在对付 Otomo 的农民叛军上。",
    ("Serpent_Dialogue.H2O#entry47", "320"): "灵蛇在世时，族人可没落到这种地步。",
    ("Serpent_Dialogue.H2O#entry47", "330"): "他们需要强硬的人带领。",
    ("Serpent_Dialogue.H2O#entry47", "340"): "大人，让我告诉你，夺回这一切有多容易。",
    ("Serpent_Dialogue.H2O#entry47", "360"): "信蛇手下有一支骑兵，控制着 Hilltop Village。",
    ("Serpent_Dialogue.H2O#entry47", "370"): "Otomo 和他雇来的弓箭手在这里扎营。",
    ("Serpent_Dialogue.H2O#entry47", "380"): "他躲在密林深处，不敢进攻。",
    ("Serpent_Dialogue.H2O#entry47", "390"): "现在出手，让大家知道灵蛇回来了！",
    ("Serpent_Dialogue.H2O#entry47", "400"): "村民都去哪里了？",
    ("Serpent_Dialogue.H2O#entry47", "410"): "灵蛇大人！有骑手来了！",
    ("Serpent_Dialogue.H2O#entry47", "420"): "那些下等人是谁？",
    ("Serpent_Dialogue.H2O#entry47", "430"): "别、别杀我……他、他在东南边！",
    ("Serpent_Dialogue.H2O#entry47", "450"): "在、在北边，大人！",
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
        row["status"] = "draft; Serpent campaign v34; font candidate pending; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} Serpent lines")


if __name__ == "__main__":
    main()
