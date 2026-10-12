"""Translate contiguous Kenji/Otomo dialogue around the Orb and Serpentholm."""

import csv
from pathlib import Path


LINES = {
 ("Kenji_Dialogue.H2O#entry0", "830"): "我不想与其他氏族交战。",
 ("Kenji_Dialogue.H2O#entry0", "840"): "你见过宝珠。它是真的。",
 ("Kenji_Dialogue.H2O#entry0", "850"): "既然要做，就快点动手。",
 ("Kenji_Dialogue.H2O#entry0", "860"): "给这个新起的氏族一点教训。",
 ("Kenji_Dialogue.H2O#entry0", "870"): "我看见了。",
 ("Kenji_Dialogue.H2O#entry0", "880"): "不是莲花族。",
 ("Kenji_Dialogue.H2O#entry0", "890"): "宝珠醒来，神龙也会醒来。",
 ("Kenji_Dialogue.H2O#entry0", "900"): "他要我们快走。",
 ("Kenji_Dialogue.H2O#entry0", "910"): "龙之尖塔可不是白叫这个名字的。",
 ("Kenji_Dialogue.H2O#entry0", "920"): "让大家继续前进。",
 ("Kenji_Dialogue.H2O#entry0", "930"): "今夜我们不再停下。",
 ("Kenji_Dialogue.H2O#entry0", "940"): "Serpentholm。",
 ("Kenji_Dialogue.H2O#entry0", "950"): "他们要的是宝珠，不是我。",
 ("Kenji_Dialogue.H2O#entry0", "960"): "通往 Serpentholm 的关键。",
 ("Kenji_Dialogue.H2O#entry0", "970"): "我离开时结识了新朋友。",
 ("Kenji_Dialogue.H2O#entry0", "980"): "巨蛇，你在哪里？",
 ("Kenji_Dialogue.H2O#entry0", "990"): "现身吧，老头！",
 ("Kenji_Dialogue.H2O#entry0", "1000"): "今夜你别想躲在艺妓身后！",
 ("Kenji_Dialogue.H2O#entry0", "1010"): "不管我是次子还是第十子，你都得听我说！",
 ("Kenji_Dialogue.H2O#entry0", "1020"): "醒醒！",
 ("Kenji_Dialogue.H2O#entry0", "1030"): "（倒吸一口气）",
 ("Kenji_Dialogue.H2O#entry0", "1040"): "偷走宝珠的人在哪里？",
 ("Kenji_Dialogue.H2O#entry0", "1050"): "可你把他跟丢了。",
 ("Kenji_Dialogue.H2O#entry0", "1060"): "我知道。",
 ("Kenji_Dialogue.H2O#entry0", "1070"): "就是它害死了巨蛇。",
 ("Kenji_Dialogue.H2O#entry0", "1080"): "现在已经无所谓了。",
 ("Kenji_Dialogue.H2O#entry0", "1090"): "看。",
 ("Kenji_Dialogue.H2O#entry0", "1100"): "神龙与宝珠本为一体。",
 ("Kenji_Dialogue.H2O#entry0", "1110"): "你从来没有认真看过。",
 ("Kenji_Dialogue.H2O#entry0", "1120"): "并非如此。",
 ("Kenji_Dialogue.H2O#entry0", "1130"): "宝珠只承载了 Tarrant 一半的力量。",
 ("Kenji_Dialogue.H2O#entry0", "1140"): "不。",
 ("Kenji_Dialogue.H2O#entry0", "1150"): "我得去龙之尖塔。",
 ("Kenji_Dialogue.H2O#entry0", "1160"): "不。我需要你留在这里。",
 ("Otomo_Dialogue.H2O#entry0", "600"): "什么？",
 ("Otomo_Dialogue.H2O#entry0", "610"): "神龙要我们快走。",
 ("Otomo_Dialogue.H2O#entry0", "620"): "其他氏族来了。",
 ("Otomo_Dialogue.H2O#entry0", "630"): "他们人很多。",
 ("Otomo_Dialogue.H2O#entry0", "640"): "一周前，这些人还只是种田的农民。",
 ("Otomo_Dialogue.H2O#entry0", "650"): "你把他们练成了战士，可莲花族和恶狼族的兵都是老手。",
 ("Otomo_Dialogue.H2O#entry0", "660"): "总好过七年来一直抢那些信任我们保护他们的农民！",
 ("Otomo_Dialogue.H2O#entry0", "670"): "那……那是什么？",
 ("Otomo_Dialogue.H2O#entry0", "680"): "不见了。",
 ("Otomo_Dialogue.H2O#entry0", "690"): "我们试着跟上去……",
 ("Otomo_Dialogue.H2O#entry0", "700"): "你确定？",
 ("Otomo_Dialogue.H2O#entry0", "710"): "他为什么想要宝珠？",
 ("Otomo_Dialogue.H2O#entry0", "730"): "我以前怎么没看出来？",
 ("Otomo_Dialogue.H2O#entry0", "740"): "大人，他会想明白的。",
 ("Otomo_Dialogue.H2O#entry0", "750"): "让我和你一起去。",
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
        row["status"] = "draft; Orb arc; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} contiguous Orb-arc lines")


if __name__ == "__main__":
    main()
