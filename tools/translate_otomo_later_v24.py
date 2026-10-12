"""Translate Otomo's contiguous village tutorial and later village dialogue."""

import csv
from pathlib import Path


LINES = {
 ("Otomo_Dialogue.H2O#entry0", "1010"): "或许我们该撤退。",
 ("Otomo_Dialogue.H2O#entry0", "1020"): "丢了。",
 ("Otomo_Dialogue.H2O#entry0", "1030"): "我们试着跟上去……",
 ("Otomo_Dialogue.H2O#entry0", "1040"): "那不是人。你也看见了……",
 ("Otomo_Dialogue.H2O#entry0", "1050"): "你疯了！",
 ("Otomo_Dialogue.H2O#entry0", "1060"): "你还不明白吗？",
 ("Otomo_Dialogue.H2O#entry0", "1070"): "他反过来攻击自己人了！",
 ("Otomo_Dialogue.H2O#entry0", "1080"): "氏族毁灭之前，你还要杀多少人？",
 ("Otomo_Dialogue.H2O#entry0", "1090"): "那是……",
 ("Otomo_Dialogue.H2O#entry0", "1100"): "我效忠氏族。",
 ("Otomo_Dialogue.H2O#entry0", "1110"): "请……让我帮你建起一个村子。",
 ("Otomo_Dialogue.H2O#entry0", "1120"): "这是 Sperri，你在上一个行省救下的农民之一。",
 ("Otomo_Dialogue.H2O#entry0", "1130"): "选中他。",
 ("Otomo_Dialogue.H2O#entry0", "1140"): "屏幕下方显示的是可建造的建筑。",
 ("Otomo_Dialogue.H2O#entry0", "1150"): "现在你只能建农舍。",
 ("Otomo_Dialogue.H2O#entry0", "1170"): "若暂时不想建农舍，左键点击即可取消，也可选中别的东西。",
 ("Otomo_Dialogue.H2O#entry0", "1180"): "只能在较平的地面上建造，所以要好好规划。",
 ("Otomo_Dialogue.H2O#entry0", "1190"): "很好！",
 ("Otomo_Dialogue.H2O#entry0", "1200"): "记住，左键用于取消或选中，右键用于执行动作。",
 ("Otomo_Dialogue.H2O#entry0", "1210"): "看！我们建的农舍里走出了一名新农民。",
 ("Otomo_Dialogue.H2O#entry0", "1220"): "现在你的人民需要食物。",
 ("Otomo_Dialogue.H2O#entry0", "1230"): "让我们从那边的稻田收些稻米。",
 ("Otomo_Dialogue.H2O#entry0", "1240"): "稻米在这里可作交换，也用于一切建造和训练。",
 ("Otomo_Dialogue.H2O#entry0", "1250"): "左键选中一名农民，把画面移到稻田，再右键点击稻田。",
 ("Otomo_Dialogue.H2O#entry0", "1260"): "稻米固然重要，但你还需要水。",
 ("Otomo_Dialogue.H2O#entry0", "1270"): "那边的水池或河流就很好。",
 ("Otomo_Dialogue.H2O#entry0", "1280"): "选中一名农民，把画面移到水池，再右键点击。",
 ("Otomo_Dialogue.H2O#entry0", "1380"): "匪徒一定赶走了这些人。",
 ("Otomo_Dialogue.H2O#entry0", "1390"): "但你看，农舍还立着！",
 ("Otomo_Dialogue.H2O#entry0", "1400"): "我们应该重建这个村子，让它成为我们的家。",
 ("Otomo_Dialogue.H2O#entry0", "1410"): "最后一个也解决了。",
 ("Otomo_Dialogue.H2O#entry0", "1420"): "什么？",
 ("Otomo_Dialogue.H2O#entry0", "1430"): "不，可是……",
 ("Otomo_Dialogue.H2O#entry0", "1440"): "我有亲人住在这个村子。",
 ("Otomo_Dialogue.H2O#entry0", "1450"): "莲花族。",
 ("Otomo_Dialogue.H2O#entry0", "1530"): "看那片森林……真不寻常。",
 ("Otomo_Dialogue.H2O#entry0", "1550"): "你长大了。",
 ("Otomo_Dialogue.H2O#entry0", "1560"): "他残害你父亲的人民。",
 ("Otomo_Dialogue.H2O#entry0", "1570"): "他派来征收的人把能拿走的都拿走了，而且……",
 ("Otomo_Dialogue.H2O#entry0", "1580"): "你父亲死后，氏族就分崩离析了。",
 ("Otomo_Dialogue.H2O#entry0", "1590"): "只是为了救农民脱离……",
 ("Otomo_Dialogue.H2O#entry0", "1600"): "遵命。",
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
        row["status"] = "draft; later Otomo arc; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} later Otomo lines")


if __name__ == "__main__":
    main()
