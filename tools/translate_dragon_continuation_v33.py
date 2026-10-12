"""Complete the Dragon tutorial and two adjacent campaign dialogue entries."""

import csv
from pathlib import Path


LINES = {
    ("Dragon_Dialogue.H2O#entry74", "2510"): "气盾生效时，神龙武士把生命力量向外凝聚，保护自己。",
    ("Dragon_Dialogue.H2O#entry74", "2520"): "维持气盾需要全神贯注，他无法移动，但任何攻击都伤不到他。",
    ("Dragon_Dialogue.H2O#entry74", "2530"): "用气盾吸引敌人注意，效果无人能及。",
    ("Dragon_Dialogue.H2O#entry74", "2540"): "看，他的体力正在慢慢减少。",
    ("Dragon_Dialogue.H2O#entry74", "2550"): "您随时可以关闭气盾；体力耗尽时，它也会自动消失。",
    ("Dragon_Dialogue.H2O#entry74", "2555"): "并非所有战技都消耗体力。",
    ("Dragon_Dialogue.H2O#entry74", "2556"): "有些能无限使用，有些限制严格，还有些会消耗使用者的生命。",
    ("Dragon_Dialogue.H2O#entry74", "2557"): "想了解战技的效果，把光标放在按钮上，看屏幕左侧的提示。",
    ("Dragon_Dialogue.H2O#entry74", "2560"): "不同战士在战技建筑里会得到不同能力，多试试各种兵种。",
    ("Dragon_Dialogue.H2O#entry74", "2570"): "接下来是最后一种强化方式。",
    ("Dragon_Dialogue.H2O#entry74", "2580"): "之前的战斗让您得到了一些阳之力。",
    ("Dragon_Dialogue.H2O#entry74", "2590"): "这种灵力会在战斗中获得。",
    ("Dragon_Dialogue.H2O#entry74", "2595"): "我军打得越好，得到得就越快。",
    ("Dragon_Dialogue.H2O#entry74", "2600"): "我们是崇高明理的一族，因此获得的是阳之力。",
    ("Dragon_Dialogue.H2O#entry74", "2605"): "界面中央阴阳图标左侧的白色点数就是阳之力。",
    ("Dragon_Dialogue.H2O#entry74", "2610"): "像来犯的灵蛇族这样较黑暗的族群，积累的是黑色的阴之力。",
    ("Dragon_Dialogue.H2O#entry74", "2620"): "有了阳之力，就能集中它来提高我军战力。",
    ("Dragon_Dialogue.H2O#entry74", "2630"): "左键点击道场，选中它。",
    ("Dragon_Dialogue.H2O#entry74", "2635"): "大人，这是靶场。",
    ("Dragon_Dialogue.H2O#entry74", "2636"): "道场是左边那座建筑。",
    ("Dragon_Dialogue.H2O#entry74", "2637"): "请选中道场，继续学习技法。",
    ("Dragon_Dialogue.H2O#entry74", "2640"): "看界面右侧，有两个图标。",
    ("Dragon_Dialogue.H2O#entry74", "2650"): "每个图标代表一种技法，可以用阴或阳之力购买。",
    ("Dragon_Dialogue.H2O#entry74", "2660"): "战技只强化个别士兵，技法却能强化整类士兵！",
    ("Dragon_Dialogue.H2O#entry74", "2670"): "把鼠标移到图标上，屏幕左侧提示会说明技法效果。",
    ("Dragon_Dialogue.H2O#entry74", "2680"): "左键点击一个技法图标，开始学习。",
    ("Dragon_Dialogue.H2O#entry74", "2681"): "大人，先学靶场的一项技法也无妨。",
    ("Dragon_Dialogue.H2O#entry74", "2690"): "很好。",
    ("Dragon_Dialogue.H2O#entry74", "2700"): "训练建筑的师傅冥想技法期间，无法接收新学员，得事先安排好。",
    ("Dragon_Dialogue.H2O#entry74", "2710"): "太好了！",
    ("Dragon_Dialogue.H2O#entry74", "2720"): "现有长矛兵都变强了，以后训练的长矛兵也会受益。",
    ("Dragon_Dialogue.H2O#entry74", "2730"): "善用技法，就能在战斗中占上风。",
    ("Dragon_Dialogue.H2O#entry74", "2735"): "要让技法配合既定战术，谨慎使用。",
    ("Dragon_Dialogue.H2O#entry74", "2740"): "强化也讲完了，您的训练到此结束。",
    ("Dragon_Dialogue.H2O#entry74", "2750"): "回想一下今天学到的东西。",
    ("Dragon_Dialogue.H2O#entry74", "2760"): "如果忘了什么，想重新上一遍课，我很乐意再陪您回顾。",
    ("Dragon_Dialogue.H2O#entry74", "2770"): "大人？",
    ("Dragon_Dialogue.H2O#entry74", "2780"): "一切都好吗？",
    ("Dragon_Dialogue.H2O#entry74", "2790"): "大人，我们继续训练吧。",
    ("Dragon_Dialogue.H2O#entry74", "2800"): "怕您忘了，我再说一次。",
    ("Dragon_Dialogue.H2O#entry74", "2810"): "大人，我们得快些行动。",
    ("Dragon_Dialogue.H2O#entry74", "2820"): "大人，这里需要那名单位。",
    ("Dragon_Dialogue.H2O#entry65", "210"): "那个该死的 Vetkin 在哪里？",
    ("Dragon_Dialogue.H2O#entry65", "220"): "他把我锁在自家地窖里整整六个月，但现在不会了！",
    ("Dragon_Dialogue.H2O#entry65", "230"): "神龙大人？",
    ("Dragon_Dialogue.H2O#entry65", "240"): "当然！",
    ("Dragon_Dialogue.H2O#entry65", "250"): "等我把这些闯进镇子的外人赶走，就来找你！",
    ("Dragon_Dialogue.H2O#entry65", "260"): "这是什么？",
    ("Dragon_Dialogue.H2O#entry65", "270"): "Vetkin，你这虫子！",
    ("Dragon_Dialogue.H2O#entry65", "280"): "我为你做了那么多，你却反过来对付我！",
    ("Dragon_Dialogue.H2O#entry90", "200"): "你的神龙说话真难懂……",
    ("Dragon_Dialogue.H2O#entry90", "210"): "那是什么？",
    ("Dragon_Dialogue.H2O#entry90", "220"): "Otomo！谁干的？",
    ("Dragon_Dialogue.H2O#entry90", "240"): "他们怎么穿过 Serpentholm 的？",
    ("Dragon_Dialogue.H2O#entry90", "250"): "绕过去就能避开他们。",
    ("Dragon_Dialogue.H2O#entry90", "260"): "我就盼着你这么说。",
    ("Dragon_Dialogue.H2O#entry90", "280"): "可那是灵蛇族祖先的王城……",
    ("Dragon_Dialogue.H2O#entry90", "290"): "他们完了。莲花族打败了他们。",
    ("Dragon_Dialogue.H2O#entry90", "300"): "能信任他们吗？",
    ("Dragon_Dialogue.H2O#entry90", "310"): "还得对付莲花族。看这里。",
    ("Dragon_Dialogue.H2O#entry90", "320"): "莲花族击溃了山里最后的恶狼族抵抗力量。",
    ("Dragon_Dialogue.H2O#entry90", "330"): "他们现在控制了所有高地和最富饶的矿区。",
    ("Dragon_Dialogue.H2O#entry90", "340"): "他们还没向这些地方进军。",
    ("Dragon_Dialogue.H2O#entry90", "350"): "战胜恶狼族，让莲花族更加大胆。",
    ("Dragon_Dialogue.H2O#entry90", "360"): "他们攻打修道院只是迟早的事。",
    ("Dragon_Dialogue.H2O#entry90", "370"): "那些圣兄弟会是可靠的盟友。",
    ("Dragon_Dialogue.H2O#entry90", "380"): "哼！我从来不信任那些刺客。",
    ("Dragon_Dialogue.H2O#entry90", "390"): "金子一用完，他们就会背叛我们。",
    ("Dragon_Dialogue.H2O#entry90", "400"): "那接下来怎么办？",
    ("Dragon_Dialogue.H2O#entry90", "410"): "要过河，就必须拿下那些桥。",
    ("Dragon_Dialogue.H2O#entry90", "420"): "河水不深，可以带人过去。",
    ("Dragon_Dialogue.H2O#entry90", "430"): "那是什么？",
    ("Dragon_Dialogue.H2O#entry90", "440"): "但你说过宝珠不重要。",
    ("Dragon_Dialogue.H2O#entry90", "450"): "神龙万岁！",
    ("Dragon_Dialogue.H2O#entry90", "460"): "<Groan> 呃……？",
    ("Dragon_Dialogue.H2O#entry90", "470"): "这里发生了什么？",
    ("Dragon_Dialogue.H2O#entry90", "480"): "离她远点！",
    ("Dragon_Dialogue.H2O#entry90", "530"): "这一切都是你的神龙做的？",
    ("Dragon_Dialogue.H2O#entry90", "650"): "Soul Flame？",
    ("Dragon_Dialogue.H2O#entry90", "660"): "毁掉另一座桥，把他们困在 High Plateau！",
    ("Dragon_Dialogue.H2O#entry90", "670"): "要不是我们毁了那些桥，莲花族早就夺下修道院了。",
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
        row["status"] = "draft; Dragon continuation v33; font candidate pending; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} Dragon lines")


if __name__ == "__main__":
    main()
