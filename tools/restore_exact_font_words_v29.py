"""Restore exact wording where prior drafts avoided missing font glyphs."""

import csv
from pathlib import Path


REVISIONS = {
    ("Kenji_Dialogue.H2O#entry0", "2720"): ("如果他们重造这个世界，就能逃往海对岸。", "如果他们重造这个世界，就能逃往大陆。"),
    ("Shinja_Dialogue.H2O#entry0", "1450"): ("照命令，把它放在大门上方。", "照命令，把它挂在大门上方。"),
    ("Dragon_Dialogue.H2O#entry7", "270"): ("打开页岩门的第一件信物……", "打开页岩门的第一把钥匙……"),
    ("Dragon_Dialogue.H2O#entry19", "250"): ("已经很久没人见过他了。", "已经好几个月没人见过他了。"),
    ("Dragon_Dialogue.H2O#entry0", "220"): ("我这条命是你救的。", "看来我欠你一条命。"),
    ("Dragon_Dialogue.H2O#entry0", "230"): ("不，我一向有恩必报。", "不，我一向有债必还。"),
    ("Dragon_Dialogue.H2O#entry0", "240"): ("你又救了我一次。", "我又欠了你一次。"),
    ("Dragon_Dialogue.H2O#entry0", "260"): ("在我报答你的救命之恩前，你别想甩掉我。", "在我还清欠你的债之前，你别想甩掉我。"),
    ("Dragon_Dialogue.H2O#entry43", "250"): ("为了 Otomo，死多少次我都愿意！", "为了 Otomo，我死一百次也愿意！"),
    ("Dragon_Dialogue.H2O#entry43", "290"): ("交易的地方还要往北走。", "集市还要往北走。"),
    ("Kenji_Dialogue.H2O#entry0", "4030"): ("我走过、休息过的地方，就是你们的圣地。", "我走过、睡过的地方，就是你们的圣地。"),
    ("Kenji_Dialogue.H2O#entry0", "4040"): ("我就是你们的圣地。你们要像爱那边那堆破石头一样爱我。", "我就是你们的圣地。你们要像爱那边的废墟一样爱我。"),
    ("Kenji_Dialogue.H2O#entry0", "4080"): ("去祭台！", "去祭坛！"),
    ("Kenji_Dialogue.H2O#entry0", "4100"): ("无知的人，你根本不知道自己做了什么！", "你这傻子，根本不知道自己做了什么！"),
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    seen = set()
    review = []
    for row in rows:
        key = (row["source_file"].split("\\")[-1], row["string_id"])
        if key not in REVISIONS:
            continue
        old, new = REVISIONS[key]
        if row["chinese"] != old:
            raise ValueError(f"unexpected prior text: {key}: {row['chinese']!r}")
        row["chinese"] = new
        row["status"] = "draft; v29 exact wording; font candidate pending; not game-tested"
        seen.add(key)
        review.append(row)
    if seen != REVISIONS.keys():
        raise ValueError(f"missing source rows: {REVISIONS.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    with Path("translations/exact-font-words-v29-review.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(review)
    print(f"Restored exact wording in {len(review)} lines")


if __name__ == "__main__":
    main()
