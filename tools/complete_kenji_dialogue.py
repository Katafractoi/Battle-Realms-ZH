"""Fill the remaining dialogue lines that explicitly name Kenji."""

import csv
from pathlib import Path


TRANSLATIONS = {
    ("Dragon_Dialogue.H2O#entry7", "210"): "健治大人！快看！",
    ("Dragon_Dialogue.H2O#entry43", "350"): "看！是健治！",
    ("Dragon_Dialogue.H2O#entry90", "230"): "健治！莲花族士兵来了！",
    ("Kenji_Dialogue.H2O#entry0", "1600"): "我是龙族领主健治。",
    ("Kenji_Dialogue.H2O#entry0", "2760"): "我是灵蛇族领主健治；我的祖先让这个世界分崩离析。",
    ("Lotus_Dialogue.H2O#entry18", "250"): "是次子——健治。",
    ("Lotus_Dialogue.H2O#entry38", "410"): "或许我们都长大了，健治。",
    ("Otomo_Dialogue.H2O#entry0", "760"): "健治说过……",
    ("Otomo_Dialogue.H2O#entry0", "830"): "健治会为此杀了你。",
    ("Otomo_Dialogue.H2O#entry0", "900"): "这太疯狂了，健治。",
    ("Otomo_Dialogue.H2O#entry0", "950"): "健治，那不重要。",
    ("Otomo_Dialogue.H2O#entry0", "1540"): "健治……是你吗？",
    ("Serpent_Dialogue.H2O#entry26", "210"): "我就知道健治会来寻找他族里那条珍贵的龙。",
    ("Serpent_Dialogue.H2O#entry26", "310"): "健治所到之处，总有新添的尸体。",
    ("Serpent_Dialogue.H2O#entry47", "250"): "你就是灵蛇之子健治。",
    ("Serpent_Dialogue.H2O#entry73", "210"): "健治大人……",
    ("Serpent_Dialogue.H2O#entry132", "250"): "健治！我愿效忠于你！",
    ("Shinja_Dialogue.H2O#entry0", "210"): "健治，灵蛇之子。",
    ("Shinja_Dialogue.H2O#entry0", "560"): "健治！",
    ("Shinja_Dialogue.H2O#entry0", "630"): "那只是一块石头，健治！",
    ("Shinja_Dialogue.H2O#entry0", "800"): "健治已不在了，我得建立自己的帝国。",
    ("Shinja_Dialogue.H2O#entry0", "940"): "健治已不在了。",
    ("Shinja_Dialogue.H2O#entry0", "1080"): "健治！",
    ("Shinja_Dialogue.H2O#entry0", "1290"): "你找健治做什么？",
    ("Shinja_Dialogue.H2O#entry0", "1300"): "如果你说的宝珠是真的，健治会需要所有能找到的士兵——连死者也算。",
    ("Unaligned_Dialogue.H2O#entry33", "210"): "健治！谢天谢地！",
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    seen = set()
    for row in rows:
        key = (row["source_file"].split("\\")[-1], row["string_id"])
        if key not in TRANSLATIONS:
            continue
        if row["chinese"] or "Kenji" not in row["english"]:
            raise ValueError(f"unexpected source state: {key}")
        row["chinese"] = TRANSLATIONS[key]
        row["status"] = "draft; name confirmed; not game-tested"
        seen.add(key)
    if seen != TRANSLATIONS.keys():
        raise ValueError(f"missing source rows: {TRANSLATIONS.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {len(seen)} Kenji dialogue rows")


if __name__ == "__main__":
    main()
