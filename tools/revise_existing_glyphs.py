"""Replace seven older draft lines whose characters are absent from the embedded LFR."""

import csv
from pathlib import Path


REVISIONS = {
 ("Dragon_Dialogue.H2O#entry74", "750"): ("选中几名农民。", "选中数名农民。"),
 ("Dragon_Dialogue.H2O#entry74", "790"): ("按住鼠标右键左右拖动，还能旋转建筑。", "按住右键左右拖动，还能旋转建筑。"),
 ("Dragon_Dialogue.H2O#entry74", "800"): ("松开鼠标右键，就能放置建筑。", "松开右键，就能放置建筑。"),
 ("Dragon_Dialogue.H2O#entry74", "820"): ("选中几名农民，右键点击未完工的道场，完成建造。", "选中数名农民，右键点击未完工的道场，完成建造。"),
 ("Kenji_Dialogue.H2O#entry0", "410"): ("Horde 所到之处尽成废墟，他便率领族人南逃，尽力保住仅存的一切。", "Horde 所到之处尽成荒地，他便率领族人南逃，尽力保住仅存的一切。"),
 ("Kenji_Dialogue.H2O#entry0", "430"): ("Tarrant 至死也不知道，留下来的抉择究竟意味着什么。", "Tarrant 至死也不知道，留下来究竟意味着什么。"),
 ("Kenji_Dialogue.H2O#entry0", "440"): ("他不知道 Horde 只是灵蛇族日后众多祸患中的第一个。", "他不知道 Horde 只是灵蛇族日后众多灾祸中的第一个。"),
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    found = set()
    for row in rows:
        key = (row["source_file"].split("\\")[-1], row["string_id"])
        if key not in REVISIONS:
            continue
        old, new = REVISIONS[key]
        if row["chinese"] != old:
            raise ValueError(f"prior draft drift at {key}")
        row["chinese"] = new
        row["status"] = "draft; embedded-font revision; not game-tested"
        found.add(key)
    if found != REVISIONS.keys():
        raise ValueError(f"missing draft lines: {REVISIONS.keys() - found}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Revised {len(found)} older draft lines")


if __name__ == "__main__":
    main()
