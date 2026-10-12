"""Translate the next continuous Dragon campaign tutorial segment."""

import csv
from pathlib import Path


LINES = {
    "390": "如您所见，他现在只能建造农舍。",
    "410": "如果暂时不想建农舍，左键点击即可取消，或选中其他目标。",
    "420": "只能在较平坦的地面建造，大人，请仔细规划。",
    "430": "很好，农舍建好了！",
    "440": "记住：左键用于选中，右键用于执行操作。",
    "450": "要继续建造农舍，选中农民，再右键点击已经搭好的框架。",
    "460": "看！一名新农民从我们建好的农舍里出来了。",
    "470": "农民会自动从农舍里出现。",
    "480": "村庄每次能容纳的人数有限，屏幕左下角会显示上限。",
    "490": "现有人口越多，新农民出生的速度就越慢。",
    "500": "看屏幕左下角的进度条，就能知道下一名农民何时到来。",
    "510": "进度条填满时，就会出现一名农民。",
    "520": "您看到界面中央金色的农民按钮了吗？",
    "530": "这是闲置农民按钮。",
    "540": "它能帮您找到没在干活的农民。",
    "550": "左键点击按钮，画面就会移到一名闲置农民身上，并自动选中他。",
    "560": "有机会试试。",
    "570": "大人，要让村庄发展，您的人民需要更多食物。",
    "580": "每建一座建筑、每训练一名士兵，都要消耗食物和水。",
    "590": "去收割这片稻田里的稻米吧。",
    "600": "先选中所有农民。",
    "610": "把光标移到农民附近。",
    "620": "按住鼠标左键。",
    "630": "移动鼠标时，会看到一个方框从光标位置向外展开。",
    "640": "拖动光标，直到方框把所有农民都圈进去。",
    "650": "松开鼠标键，农民就会被选中。",
    "660": "您也可以用这种方法选中其他人。",
    "665": "掌握这个操作，才能有效指挥军队，务必学会。",
    "670": "现在把画面移到稻田，右键点击田里的一株稻苗。",
    "680": "农民就会开始收割；除非收到别的命令，否则他们会一直收下去。",
    "690": "稻米很重要，但我们的人民还需要清水饮用。",
    "700": "这样的池塘或溪流就很合适。",
    "710": "选中农民，把画面移到池塘，再右键点击池塘。",
    "830": "现在来训练第一名战士：长矛兵。",
    "840": "训练长矛兵需要稻米和水。",
    "850": "糟了！稻米用光了！",
    "860": "再看，稻田也干了！",
    "870": "别担心，大人。给稻田灌水，就能收获更多稻米。",
    "880": "像刚才那样选中几名农民。",
    "890": "建造界面的右下角有一个蓝色的灌溉稻田图标。",
    "900": "左键点击灌溉稻田图标，再右键点击一株已经枯竭的稻苗。",
    "910": "稻田很快就能再次收割。现在让农民去收稻米吧。",
    "920": "做得好！田地恢复肥沃，稻米储备也补上了。",
    "930": "不过看来我们还需要更多水。",
    "940": "大人，请选中一名农民，命令他去取水。",
    "950": "现在继续训练那名长矛兵……",
    "960": "选中一名农民，再右键点击道场。",
    "970": "农民就会进入道场，在那里接受训练。",
    "980": "大人，您的第一名士兵很快就能训练完成。",
    "990": "左键点击建筑，观察逐渐变长的蓝线，就能知道训练还要多久。",
    "1000": "恭喜！",
    "1010": "您已经学会发展经济的基本方法，接下来要学习如何组建军队。",
    "1020": "先休息吧，我们明天继续。",
    "1030": "欢迎回来。",
    "1040": "如您所见，New Issen 建设得很顺利。",
    "1050": "要保护新城镇，只靠一名长矛兵可不够。",
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    seen = set()
    for row in rows:
        if not row["source_file"].endswith("Dragon_Dialogue.H2O#entry74"):
            continue
        key = row["string_id"]
        if key not in LINES:
            continue
        if row["chinese"]:
            raise ValueError(f"already translated: {key}")
        row["chinese"] = LINES[key]
        row["status"] = "draft; Dragon tutorial v30; font candidate pending; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} tutorial lines")


if __name__ == "__main__":
    main()
