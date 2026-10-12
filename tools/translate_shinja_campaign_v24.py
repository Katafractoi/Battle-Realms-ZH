"""Translate Shinja's contiguous campaign briefing and battle dialogue."""

import csv
from pathlib import Path


LINES = {
 ("Shinja_Dialogue.H2O#entry0", "280"): "那老头比我们想的更有远见。",
 ("Shinja_Dialogue.H2O#entry0", "290"): "他知道 Serpentholm 会陷落。",
 ("Shinja_Dialogue.H2O#entry0", "300"): "艺妓仍被视为不可侵犯。",
 ("Shinja_Dialogue.H2O#entry0", "310"): "你父亲死了七年，他的威势已衰，但恶狼族和莲花族仍怕他的名字。",
 ("Shinja_Dialogue.H2O#entry0", "320"): "我怎样服侍父亲，就怎样服侍儿子。",
 ("Shinja_Dialogue.H2O#entry0", "330"): "天鹅池就在这里，走北边的路。",
 ("Shinja_Dialogue.H2O#entry0", "340"): "恶狼族已经来到这里，赶走了原本的农民。",
 ("Shinja_Dialogue.H2O#entry0", "350"): "天气好时，他们破屋的臭味会传到南边。",
 ("Shinja_Dialogue.H2O#entry0", "360"): "和你父亲在世时一样，恶狼族根本挡不住有备而来的军队。",
 ("Shinja_Dialogue.H2O#entry0", "370"): "不过，恶狼族总想找人打一架。",
 ("Shinja_Dialogue.H2O#entry0", "380"): "莲花族的领地远在东边，却在这里建了前哨。",
 ("Shinja_Dialogue.H2O#entry0", "390"): "他们一名邪恶术士用黑暗法术奴役了当地农民。",
 ("Shinja_Dialogue.H2O#entry0", "400"): "村民熟悉土地，会是有用的盟友。",
 ("Shinja_Dialogue.H2O#entry0", "410"): "最近的路穿过 Riverside Town 中心。",
 ("Shinja_Dialogue.H2O#entry0", "415"): "本地人靠与莲花族、恶狼族交易过活，我们肯定会被发现。",
 ("Shinja_Dialogue.H2O#entry0", "420"): "哈！大家又并肩作战，真像从前，不是吗？",
 ("Shinja_Dialogue.H2O#entry0", "430"): "探子报告，恶狼族那些占地者弃屋逃跑，不敢面对你。",
 ("Shinja_Dialogue.H2O#entry0", "440"): "探子报告，商人也从 Riverside 逃走，不敢面对你。",
 ("Shinja_Dialogue.H2O#entry0", "450"): "我已经自作主张，派人占了镇子。",
 ("Shinja_Dialogue.H2O#entry0", "460"): "探子报告，莲花族也弃掉前哨，不敢面对你。",
 ("Shinja_Dialogue.H2O#entry0", "470"): "西边的恶狼族占地者还没走，但一点刀剑与火焰就能让他们……",
 ("Shinja_Dialogue.H2O#entry0", "480"): "东边的莲花族术士还没动，但若烧了他们的塔……",
 ("Shinja_Dialogue.H2O#entry0", "490"): "可我们已拿住他们的要害。",
 ("Shinja_Dialogue.H2O#entry0", "500"): "该死！有他集结的那支大军，我们本可守住低地，重建灵蛇族！",
 ("Shinja_Dialogue.H2O#entry0", "510"): "他到底要宝珠做什么？",
 ("Shinja_Dialogue.H2O#entry0", "520"): "流言，闲话。",
 ("Shinja_Dialogue.H2O#entry0", "530"): "以前我常对着那东西看上数个小时，想找出一点力量的迹象。",
 ("Shinja_Dialogue.H2O#entry0", "540"): "它不过是块好看的石头。",
 ("Shinja_Dialogue.H2O#entry0", "550"): "他疯了。",
 ("Shinja_Dialogue.H2O#entry0", "570"): "Riverside 传来消息！",
 ("Shinja_Dialogue.H2O#entry0", "580"): "恶狼族正在西南方集结大军！",
 ("Shinja_Dialogue.H2O#entry0", "590"): "他们正往营地集合！",
 ("Shinja_Dialogue.H2O#entry0", "595"): "我们必须进攻，否则他们会一路打过低地！",
 ("Shinja_Dialogue.H2O#entry0", "600"): "莲花族正在东边屠杀村民！",
 ("Shinja_Dialogue.H2O#entry0", "610"): "一支刀兵大军驻在术士塔下的山坡上。",
 ("Shinja_Dialogue.H2O#entry0", "615"): "必须在他们南下前进攻！",
 ("Shinja_Dialogue.H2O#entry0", "620"): "敌人伤不了你，就会去伤你的人民。",
 ("Shinja_Dialogue.H2O#entry0", "640"): "农民为你而战，不是为了宝珠！",
 ("Shinja_Dialogue.H2O#entry0", "650"): "他们总算决定留下战斗了。",
 ("Shinja_Dialogue.H2O#entry0", "660"): "换作你会怎么做？",
 ("Shinja_Dialogue.H2O#entry0", "670"): "再躲在破屋里七年，天天闲坐等死吗？",
 ("Shinja_Dialogue.H2O#entry0", "680"): "混账！我要剖开你……",
 ("Shinja_Dialogue.H2O#entry0", "690"): "Serpentholm 是我们的。",
 ("Shinja_Dialogue.H2O#entry0", "700"): "那不是人。你看见它怎么动的了。",
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
        row["status"] = "draft; Shinja campaign arc; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} Shinja campaign lines")


if __name__ == "__main__":
    main()
