"""Translate the next contiguous Otomo tutorial and Shinja campaign passages."""

import csv
from pathlib import Path


LINES = {
    ("Otomo_Dialogue.H2O#entry0", "1620"): "但你看，还有一间农舍完好无损！",
    ("Otomo_Dialogue.H2O#entry0", "1630"): "如果你允许，我会替族人接管它。",
    ("Otomo_Dialogue.H2O#entry0", "1640"): "一名新农民从农舍里出来了。",
    ("Otomo_Dialogue.H2O#entry0", "1650"): "选中他。",
    ("Otomo_Dialogue.H2O#entry0", "1660"): "现在可以看到农民能为你建造的建筑。",
    ("Otomo_Dialogue.H2O#entry0", "1670"): "目前你只能再建一间农舍，或建一座靶场。",
    ("Otomo_Dialogue.H2O#entry0", "1680"): "左键点击靶场图标，再右键点击地面放置新建筑。",
    ("Otomo_Dialogue.H2O#entry0", "1690"): "要建更多建筑、训练军队，还需要更多稻米和水。",
    ("Otomo_Dialogue.H2O#entry0", "1700"): "选中一名农民，再右键点击村西的稻田，让他开始收割。",
    ("Otomo_Dialogue.H2O#entry0", "1710"): "北边还有一条小河，可以取到清水。",
    ("Otomo_Dialogue.H2O#entry0", "1720"): "也派一名农民过去。",
    ("Otomo_Dialogue.H2O#entry0", "1730"): "现在稻米和水都有了，该开始训练弓箭手了。",
    ("Otomo_Dialogue.H2O#entry0", "1740"): "选中农民，再右键点击靶场。",
    ("Otomo_Dialogue.H2O#entry0", "1750"): "很好！",
    ("Otomo_Dialogue.H2O#entry0", "1760"): "我们得小心。",
    ("Otomo_Dialogue.H2O#entry0", "1770"): "大路好走，但肯定会被发现。",
    ("Otomo_Dialogue.H2O#entry0", "1780"): "穿过树林就能掩护我们的行动，直到准备进攻。",
    ("Otomo_Dialogue.H2O#entry0", "1790"): "出来，你这个疯子！",
    ("Otomo_Dialogue.H2O#entry0", "1800"): "来面对我！",
    ("Otomo_Dialogue.H2O#entry0", "1810"): "你真是你父亲的儿子……",
    ("Shinja_Dialogue.H2O#entry0", "710"): "别管宝珠了！",
    ("Shinja_Dialogue.H2O#entry0", "715"): "那不过是块没用的石头！",
    ("Shinja_Dialogue.H2O#entry0", "720"): "看看周围！",
    ("Shinja_Dialogue.H2O#entry0", "730"): "我们已经夺下 Serpentholm，这还不够吗？",
    ("Shinja_Dialogue.H2O#entry0", "740"): "那毫无意义。",
    ("Shinja_Dialogue.H2O#entry0", "750"): "这简直疯了！",
    ("Shinja_Dialogue.H2O#entry0", "760"): "没时间再幻想什么魔法和龙了！",
    ("Shinja_Dialogue.H2O#entry0", "770"): "你必须让灵蛇族再次强大！",
    ("Shinja_Dialogue.H2O#entry0", "780"): "那我就来做。",
    ("Shinja_Dialogue.H2O#entry0", "790"): "趁其他族还弱，我们必须快点行动。",
    ("Shinja_Dialogue.H2O#entry0", "810"): "来，看这里。",
    ("Shinja_Dialogue.H2O#entry0", "820"): "Serpentholm 暂时安全。",
    ("Shinja_Dialogue.H2O#entry0", "830"): "得派人重修城防，以防敌人回来。",
    ("Shinja_Dialogue.H2O#entry0", "840"): "恶狼族的军队退进了山里。",
    ("Shinja_Dialogue.H2O#entry0", "850"): "这会儿他们应该正准备在矿区坚守。",
    ("Shinja_Dialogue.H2O#entry0", "860"): "动作够快，也许能打他们一个措手不及。",
    ("Shinja_Dialogue.H2O#entry0", "870"): "与其正面强攻，不如从侧翼逼近。",
    ("Shinja_Dialogue.H2O#entry0", "880"): "这一带的山谷和沼泽能掩护军队，直到我们发动进攻。",
    ("Shinja_Dialogue.H2O#entry0", "890"): "你受伤了。",
    ("Shinja_Dialogue.H2O#entry0", "900"): "希望你没有太痛苦。",
    ("Shinja_Dialogue.H2O#entry0", "910"): "我们的敌人懂得痛苦，也懂得牺牲。",
    ("Shinja_Dialogue.H2O#entry0", "915"): "他们注定失败，但至少没有躲在村里不敢出来。",
    ("Shinja_Dialogue.H2O#entry0", "920"): "你说什么？",
    ("Shinja_Dialogue.H2O#entry0", "930"): "我没什么可说的。",
    ("Shinja_Dialogue.H2O#entry0", "950"): "灵蛇族需要强者领导，不能交给软弱的人。",
    ("Shinja_Dialogue.H2O#entry0", "960"): "把他带走。",
    ("Shinja_Dialogue.H2O#entry0", "970"): "遵命。",
    ("Shinja_Dialogue.H2O#entry0", "980"): "你竟然把软弱的人收在身边。",
    ("Shinja_Dialogue.H2O#entry0", "990"): "向你屈服？绝不。",
    ("Shinja_Dialogue.H2O#entry0", "1000"): "我怎样侍奉父亲，就怎样侍奉儿子。",
    ("Shinja_Dialogue.H2O#entry0", "1010"): "在天鹅池。",
    ("Shinja_Dialogue.H2O#entry0", "1020"): "不是我……是灵蛇。",
    ("Shinja_Dialogue.H2O#entry0", "1030"): "镇上的人不能信。",
    ("Shinja_Dialogue.H2O#entry0", "1040"): "那群唯利是图的家伙，谁出价高就为谁效力。",
    ("Shinja_Dialogue.H2O#entry0", "1050"): "最好往西走，从这里过河。",
    ("Shinja_Dialogue.H2O#entry0", "1060"): "对岸有个恶狼族的棚户区，派出训练有素的士兵就能轻易清掉那群人。",
    ("Shinja_Dialogue.H2O#entry0", "1070"): "仿佛回到了从前，灵蛇族又能并肩作战了。",
    ("Shinja_Dialogue.H2O#entry0", "1090"): "Riverside 送来了消息！",
    ("Shinja_Dialogue.H2O#entry0", "1100"): "恶狼族正准备反击。",
    ("Shinja_Dialogue.H2O#entry0", "1110"): "必须挡住他们，不然他们会一路打到低地！",
    ("Shinja_Dialogue.H2O#entry0", "1120"): "一支莲花族大军驻扎在术士塔下的山坡上。",
    ("Shinja_Dialogue.H2O#entry0", "1130"): "必须主动出击，否则他们会袭扰南部海岸！",
    ("Shinja_Dialogue.H2O#entry0", "1140"): "我来办。",
    ("Shinja_Dialogue.H2O#entry0", "1150"): "其他各族也来了。",
    ("Shinja_Dialogue.H2O#entry0", "1160"): "那是什么？",
    ("Shinja_Dialogue.H2O#entry0", "1170"): "敌人正在溃逃。",
    ("Shinja_Dialogue.H2O#entry0", "1180"): "够了！",
    ("Shinja_Dialogue.H2O#entry0", "1190"): "一直如此。",
    ("Shinja_Dialogue.H2O#entry0", "1195"): "你打算怎么进攻？",
    ("Shinja_Dialogue.H2O#entry0", "1200"): "这里满是死亡的气息。",
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
        row["status"] = "draft; campaign v25; not game-tested"
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
