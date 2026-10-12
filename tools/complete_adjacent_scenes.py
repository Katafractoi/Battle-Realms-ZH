"""Translate short neighboring lines so confirmed-name dialogue is not isolated."""

import csv
from pathlib import Path


LINES = {
 ("Kenji_Dialogue.H2O#entry0", "2820"): "该让阴影害怕我们了。",
 ("Kenji_Dialogue.H2O#entry0", "2870"): "追上他！",
 ("Kenji_Dialogue.H2O#entry0", "2890"): "别让我再问。",
 ("Kenji_Dialogue.H2O#entry0", "2910"): "你真认为他的命比你自己的更重要？",
 ("Kenji_Dialogue.H2O#entry0", "2920"): "把他们尸体上的装束取下来。",
 ("Kenji_Dialogue.H2O#entry0", "2940"): "那就去拿他们的装束。",
 ("Kenji_Dialogue.H2O#entry0", "2950"): "算了。",
 ("Shinja_Dialogue.H2O#entry0", "200"): "当然。",
 ("Shinja_Dialogue.H2O#entry0", "220"): "我曾认识一个受人质问就吓得逃跑的男孩。",
 ("Shinja_Dialogue.H2O#entry0", "230"): "我得知道他是否还是当年的那个男孩。",
 ("Shinja_Dialogue.H2O#entry0", "240"): "你回来统治灵蛇族了？",
 ("Shinja_Dialogue.H2O#entry0", "250"): "那么，你要毁掉这个世界吗？",
 ("Shinja_Dialogue.H2O#entry0", "260"): "如你所愿，Otomo。",
 ("Shinja_Dialogue.H2O#entry0", "270"): "在天鹅池。",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1090"): "这听起来并不难。",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1110"): "页岩坏了。我们的米在哪里？",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1120"): "但光靠法规也无法让我们活下去。",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1140"): "恶狼族越饿越有力气，而非越弱。我们的米在哪里？",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1150"): "你若把 Yvaine 的奴隶打死，她可不会高兴。",
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    found = set()
    for row in rows:
        key = (row["source_file"].split("\\")[-1], row["string_id"])
        if key not in LINES:
            continue
        if row["chinese"]:
            raise ValueError(f"already translated: {key}")
        row["chinese"] = LINES[key]
        row["status"] = "draft; adjacent scene; not game-tested"
        found.add(key)
    if found != LINES.keys():
        raise ValueError(f"missing rows: {LINES.keys() - found}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {len(found)} adjacent lines")


if __name__ == "__main__":
    main()
