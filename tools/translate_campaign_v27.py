"""Translate the next Kenji, Shinja, and Dragon campaign passages."""

import csv
from pathlib import Path


LINES = {
    ("Kenji_Dialogue.H2O#entry0", "2960"): "Oja 大人是我父亲。",
    ("Kenji_Dialogue.H2O#entry0", "2970"): "你怎么知道我在哪里？",
    ("Kenji_Dialogue.H2O#entry0", "2980"): "我们得穿过镇子。",
    ("Kenji_Dialogue.H2O#entry0", "2990"): "谁住在山上？",
    ("Kenji_Dialogue.H2O#entry0", "3000"): "啊……Garrin 将军。他还好吗？",
    ("Kenji_Dialogue.H2O#entry0", "3010"): "Vetkin 在哪里？",
    ("Kenji_Dialogue.H2O#entry0", "3020"): "他们说莲花族进城时，我们得躲远点。",
    ("Kenji_Dialogue.H2O#entry0", "3030"): "这不像我认识的 Garrin。",
    ("Kenji_Dialogue.H2O#entry0", "3040"): "把那些废物清理了。",
    ("Kenji_Dialogue.H2O#entry0", "3050"): "Garrin。",
    ("Kenji_Dialogue.H2O#entry0", "3060"): "Garrin！",
    ("Kenji_Dialogue.H2O#entry0", "3070"): "你还记得我吗？",
    ("Kenji_Dialogue.H2O#entry0", "3080"): "是谁干的？",
    ("Kenji_Dialogue.H2O#entry0", "3090"): "那莲花族可多了一个敌人。",
    ("Kenji_Dialogue.H2O#entry0", "3110"): "不可能！",
    ("Kenji_Dialogue.H2O#entry0", "3130"): "莲花族知道，在离尖塔这么近的地方建村意味着什么。",
    ("Kenji_Dialogue.H2O#entry0", "3140"): "古老的智者，我来求教。",
    ("Kenji_Dialogue.H2O#entry0", "3150"): "我知道。",
    ("Kenji_Dialogue.H2O#entry0", "3160"): "我和父亲不一样。",
    ("Kenji_Dialogue.H2O#entry0", "3170"): "我想修复家族对这片土地造成的伤害。",
    ("Kenji_Dialogue.H2O#entry0", "3180"): "我想结束这场战争。",
    ("Kenji_Dialogue.H2O#entry0", "3190"): "只要你帮我，我就能做到。",
    ("Kenji_Dialogue.H2O#entry0", "3200"): "你知道那里有忍者？",
    ("Kenji_Dialogue.H2O#entry0", "3210"): "你早该提醒我们！",
    ("Kenji_Dialogue.H2O#entry0", "3220"): "你是他们一伙的？",
    ("Kenji_Dialogue.H2O#entry0", "3230"): "你能带我们去找 Soul Flame 吗？",
    ("Kenji_Dialogue.H2O#entry0", "3240"): "莲花族手里有我家的东西。",
    ("Kenji_Dialogue.H2O#entry0", "3250"): "你得帮我把它拿回来。",
    ("Kenji_Dialogue.H2O#entry0", "3270"): "好兄弟，许久不见了。",
    ("Kenji_Dialogue.H2O#entry0", "3280"): "那我们得快点。",
    ("Kenji_Dialogue.H2O#entry0", "3290"): "召集其他僧人，做好战斗准备。",
    ("Kenji_Dialogue.H2O#entry0", "3300"): "从这里到 High Plateau，还有别的路吗？",
    ("Kenji_Dialogue.H2O#entry0", "3310"): "我知道。",
    ("Kenji_Dialogue.H2O#entry0", "3320"): "他们现在肯定有了防备。",
    ("Kenji_Dialogue.H2O#entry0", "3330"): "你到底是什么？",
    ("Kenji_Dialogue.H2O#entry0", "3340"): "你和你的同类早在数个世纪前就死了！",
    ("Kenji_Dialogue.H2O#entry0", "3350"): "Tarrant 杀了你们！",
    ("Kenji_Dialogue.H2O#entry0", "3360"): "追上他！",
    ("Kenji_Dialogue.H2O#entry0", "3370"): "好久不见了，Otomo。",
    ("Kenji_Dialogue.H2O#entry0", "3390"): "南方各地的农民本该听他的。",
    ("Kenji_Dialogue.H2O#entry0", "3400"): "他是灵蛇族卫队的队长。",
    ("Kenji_Dialogue.H2O#entry0", "3410"): "这么说，你们造反了。",
    ("Kenji_Dialogue.H2O#entry0", "3420"): "你这样子让我作呕。",
    ("Kenji_Dialogue.H2O#entry0", "3450"): "为什么？",
    ("Kenji_Dialogue.H2O#entry0", "3460"): "真不对劲。",
    ("Kenji_Dialogue.H2O#entry0", "3465"): "他还能付得起其他雇佣兵。",
    ("Kenji_Dialogue.H2O#entry0", "3470"): "我在西北方那群劫匪的营地里找到了一箱珠宝。",
    ("Kenji_Dialogue.H2O#entry0", "3480"): "只要替我做事，这些就是你的。",
    ("Kenji_Dialogue.H2O#entry0", "3500"): "说，或者死。",
    ("Kenji_Dialogue.H2O#entry0", "3540"): "不，Arah，我不会再让你跟着我。",
    ("Kenji_Dialogue.H2O#entry0", "3550"): "我还以为终于甩掉你了。",
    ("Shinja_Dialogue.H2O#entry0", "1620"): "恶狼族的矿工烧掉树林，给车子开出道路。",
    ("Shinja_Dialogue.H2O#entry0", "1630"): "到我这里集结！",
    ("Shinja_Dialogue.H2O#entry0", "1640"): "杀了那个假王！",
    ("Shinja_Dialogue.H2O#entry0", "1650"): "为灵蛇族雪恨！",
    ("Shinja_Dialogue.H2O#entry0", "1660"): "这一带已经有人占领。",
    ("Shinja_Dialogue.H2O#entry0", "1670"): "如果你要找我算账，就派你的首领来。",
    ("Shinja_Dialogue.H2O#entry0", "1680"): "他们做了不少事。",
    ("Shinja_Dialogue.H2O#entry0", "1690"): "一路杀到 Serpentholm！",
    ("Shinja_Dialogue.H2O#entry0", "1700"): "谁取下 Otomo 的头，我就给他重金！",
    ("Dragon_Dialogue.H2O#entry0", "210"): "看来我们又碰面了。",
    ("Dragon_Dialogue.H2O#entry0", "220"): "我这条命是你救的。",
    ("Dragon_Dialogue.H2O#entry0", "230"): "不，我一向有恩必报。",
    ("Dragon_Dialogue.H2O#entry0", "240"): "你又救了我一次。",
    ("Dragon_Dialogue.H2O#entry0", "250"): "你知道规矩。",
    ("Dragon_Dialogue.H2O#entry0", "260"): "在我报答你的救命之恩前，你别想甩掉我。",
    ("Dragon_Dialogue.H2O#entry7", "205"): "你做了什么？",
    ("Dragon_Dialogue.H2O#entry7", "220"): "下面来了援军，我们被困住了！",
    ("Dragon_Dialogue.H2O#entry7", "230"): "你，快从那里出来！",
    ("Dragon_Dialogue.H2O#entry7", "231"): "别动！",
    ("Dragon_Dialogue.H2O#entry7", "240"): "谢天谢地！你救了我们！",
    ("Dragon_Dialogue.H2O#entry7", "250"): "救救我们！",
    ("Dragon_Dialogue.H2O#entry7", "260"): "看！恶狼族！",
    ("Dragon_Dialogue.H2O#entry7", "270"): "打开页岩门的第一件信物……",
    ("Dragon_Dialogue.H2O#entry7", "275"): "已经有两把了。",
    ("Dragon_Dialogue.H2O#entry7", "280"): "啊！现在能打开门了！",
    ("Dragon_Dialogue.H2O#entry19", "210"): "要去哪里？",
    ("Dragon_Dialogue.H2O#entry19", "220"): "去也行，但今天由莲花族来交易，他们对外人可不友好。",
    ("Dragon_Dialogue.H2O#entry19", "230"): "要是我，就等明天恶狼族进城时再来。",
    ("Dragon_Dialogue.H2O#entry19", "240"): "Garrin 大人。",
    ("Dragon_Dialogue.H2O#entry19", "250"): "已经很久没人见过他了。",
    ("Dragon_Dialogue.H2O#entry19", "255"): "如今他只通过信使 Vetkin 传话。",
    ("Dragon_Dialogue.H2O#entry19", "260"): "他准是躲在什么地方。",
    ("Dragon_Dialogue.H2O#entry19", "270"): "要去哪里？",
    ("Dragon_Dialogue.H2O#entry19", "280"): "要是我，就不会去。",
    ("Dragon_Dialogue.H2O#entry19", "290"): "今天由恶狼族来交易，他们正兴头上。",
    ("Dragon_Dialogue.H2O#entry19", "300"): "Garrin 大人。",
    ("Dragon_Dialogue.H2O#entry19", "310"): "如今名号可真容易得来。",
    ("Dragon_Dialogue.H2O#entry19", "320"): "我在听。",
    ("Dragon_Dialogue.H2O#entry19", "330"): "这些东西真漂亮。",
    ("Dragon_Dialogue.H2O#entry19", "340"): "救救我们！",
    ("Dragon_Dialogue.H2O#entry19", "350"): "救命！我们需要帮助！",
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
        row["status"] = "draft; campaign v27; not game-tested"
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
