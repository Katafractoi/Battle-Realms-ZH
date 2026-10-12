"""Translate later Kenji dialogue and adjacent Dragon campaign entries."""

import csv
from pathlib import Path


LINES = {
    ("Kenji_Dialogue.H2O#entry0", "3560"): "从你们镇上过去。",
    ("Kenji_Dialogue.H2O#entry0", "3570"): "山上的房子是谁的？",
    ("Kenji_Dialogue.H2O#entry0", "3580"): "老弱的 Garrin？",
    ("Kenji_Dialogue.H2O#entry0", "3590"): "他如今自称领主了？",
    ("Kenji_Dialogue.H2O#entry0", "3600"): "看起来是。",
    ("Kenji_Dialogue.H2O#entry0", "3610"): "可金子……啊，有了金子才算个人物。",
    ("Kenji_Dialogue.H2O#entry0", "3620"): "也许还能造就更多人物。",
    ("Kenji_Dialogue.H2O#entry0", "3630"): "要是 Garrin 出了什么事，他们或许就不肯再替他作战。",
    ("Kenji_Dialogue.H2O#entry0", "3640"): "这些也很贵重。",
    ("Kenji_Dialogue.H2O#entry0", "3650"): "拿去和同伴分了。",
    ("Kenji_Dialogue.H2O#entry0", "3690"): "灵蛇想去哪里就去哪里。",
    ("Kenji_Dialogue.H2O#entry0", "3700"): "这里曾是灵蛇族的土地。",
    ("Kenji_Dialogue.H2O#entry0", "3710"): "我要把它夺回来。",
    ("Kenji_Dialogue.H2O#entry0", "3720"): "随你。",
    ("Kenji_Dialogue.H2O#entry0", "3730"): "或者你也可以替我作战。",
    ("Kenji_Dialogue.H2O#entry0", "3740"): "等我坐上灵蛇的王座，忠诚的人必得厚礼。",
    ("Kenji_Dialogue.H2O#entry0", "3750"): "说出你想要的。",
    ("Kenji_Dialogue.H2O#entry0", "3760"): "这可以办到。",
    ("Kenji_Dialogue.H2O#entry0", "3870"): "Otomo，今天就是你的死期！",
    ("Kenji_Dialogue.H2O#entry0", "3880"): "等等！",
    ("Kenji_Dialogue.H2O#entry0", "3890"): "我想和你谈谈！",
    ("Kenji_Dialogue.H2O#entry0", "3900"): "Soul Flame？",
    ("Kenji_Dialogue.H2O#entry0", "3910"): "我们会保护你的火焰。",
    ("Kenji_Dialogue.H2O#entry0", "3920"): "很好，因为我有事要你办。",
    ("Kenji_Dialogue.H2O#entry0", "3930"): "这样好多了。",
    ("Kenji_Dialogue.H2O#entry0", "3940"): "来，杀掉剩下的恶狼族，取下他们的皮。",
    ("Kenji_Dialogue.H2O#entry0", "3950"): "这是我的地盘。",
    ("Kenji_Dialogue.H2O#entry0", "3960"): "还是说，你已经忘了灵蛇族？",
    ("Kenji_Dialogue.H2O#entry0", "3970"): "你们这些僧人现在为我效力。",
    ("Kenji_Dialogue.H2O#entry0", "3980"): "但它会的。",
    ("Kenji_Dialogue.H2O#entry0", "3990"): "拿下他们！",
    ("Kenji_Dialogue.H2O#entry0", "4000"): "我没有……",
    ("Kenji_Dialogue.H2O#entry0", "4010"): "你们的圣地现在在哪里？",
    ("Kenji_Dialogue.H2O#entry0", "4020"): "让我来教你明白，兄弟。",
    ("Kenji_Dialogue.H2O#entry0", "4030"): "我走过、休息过的地方，就是你们的圣地。",
    ("Kenji_Dialogue.H2O#entry0", "4040"): "我就是你们的圣地。你们要像爱那边那堆破石头一样爱我。",
    ("Kenji_Dialogue.H2O#entry0", "4050"): "听见了吗？",
    ("Kenji_Dialogue.H2O#entry0", "4060"): "那就把你的兄弟们召集起来。",
    ("Kenji_Dialogue.H2O#entry0", "4070"): "还有很多事要做。",
    ("Kenji_Dialogue.H2O#entry0", "4080"): "去祭台！",
    ("Kenji_Dialogue.H2O#entry0", "4090"): "不惜一切代价夺下宝珠！",
    ("Kenji_Dialogue.H2O#entry0", "4100"): "无知的人，你根本不知道自己做了什么！",
    ("Kenji_Dialogue.H2O#entry0", "4110"): "那就去死！",
    ("Kenji_Dialogue.H2O#entry0", "4120"): "你到底是什么？",
    ("Kenji_Dialogue.H2O#entry0", "4130"): "我不怕黑暗。",
    ("Dragon_Dialogue.H2O#entry36", "210"): "Oja 大人，我们一直在等你。",
    ("Dragon_Dialogue.H2O#entry36", "220"): "我们怎样效力于父亲，也会怎样效力于儿子。",
    ("Dragon_Dialogue.H2O#entry36", "230"): "神龙为我们指路。",
    ("Dragon_Dialogue.H2O#entry36", "240"): "神龙武士必须学会长矛兵和弓箭手的本领。",
    ("Dragon_Dialogue.H2O#entry36", "250"): "把长矛兵派到靶场。",
    ("Dragon_Dialogue.H2O#entry36", "260"): "把弓箭手派到道场。",
    ("Dragon_Dialogue.H2O#entry43", "220"): "随你怎么做。",
    ("Dragon_Dialogue.H2O#entry43", "230"): "他要从那个假灵蛇手里夺回祖先的要塞。",
    ("Dragon_Dialogue.H2O#entry43", "240"): "恶狼族正在进军，与他会合。",
    ("Dragon_Dialogue.H2O#entry43", "250"): "为了 Otomo，死多少次我都愿意！",
    ("Dragon_Dialogue.H2O#entry43", "260"): "求你救救我们！",
    ("Dragon_Dialogue.H2O#entry43", "280"): "没了马匹，冬天一来我们就会饿死！",
    ("Dragon_Dialogue.H2O#entry43", "290"): "交易的地方还要往北走。",
    ("Dragon_Dialogue.H2O#entry43", "300"): "果然。Garrin 一向向着外人，胜过自己人。",
    ("Dragon_Dialogue.H2O#entry43", "310"): "他变了。",
    ("Dragon_Dialogue.H2O#entry43", "320"): "他整天把自己关在那座房子里，让 Vetkin 替他干见不得人的事。",
    ("Dragon_Dialogue.H2O#entry43", "330"): "看！他们在攻打莲花族！",
    ("Dragon_Dialogue.H2O#entry43", "340"): "看那里！Vetkin 正骑马去找恶狼族！",
    ("Dragon_Dialogue.H2O#entry43", "360"): "大人，请下令吧！",
    ("Dragon_Dialogue.H2O#entry43", "370"): "快跑！是屠夫！",
    ("Dragon_Dialogue.H2O#entry43", "380"): "快跑！屠夫打过来了！",
    ("Dragon_Dialogue.H2O#entry43", "390"): "等等……别打！",
    ("Dragon_Dialogue.H2O#entry43", "400"): "只要你保护我们，我们就听你差遣！",
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
        row["status"] = "draft; campaign v28; not game-tested"
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
