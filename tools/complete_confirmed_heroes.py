"""Add context-preserving Shinja/Budo dialogue translations, keyed by archive and ID."""

import csv
from pathlib import Path


LINES = {
 ("Dragon_Dialogue.H2O#entry43", "210"): "快跑！信蛇的人来了！",
 ("Dragon_Dialogue.H2O#entry43", "270"): "信蛇大人把我们的马全带走了！",
 ("Dragon_Dialogue.H2O#entry90", "270"): "我仿佛已经看见信蛇的头插在长矛上。",
 ("Kenji_Dialogue.H2O#entry0", "1170"): "信蛇若有本事，就让他拖住莲花族和恶狼族。",
 ("Kenji_Dialogue.H2O#entry0", "1270"): "信蛇。",
 ("Kenji_Dialogue.H2O#entry0", "1710"): "信蛇和 Otomo 在互相争斗？",
 ("Kenji_Dialogue.H2O#entry0", "1740"): "信蛇和 Otomo 都是弱者，不配统治。",
 ("Kenji_Dialogue.H2O#entry0", "2240"): "信蛇，带你的人向南前往龙之尖塔，一路平定各村庄。",
 ("Kenji_Dialogue.H2O#entry0", "2450"): "信蛇？信蛇在哪里？",
 ("Kenji_Dialogue.H2O#entry0", "2880"): "你和信蛇，二选一。你自己决定。",
 ("Kenji_Dialogue.H2O#entry0", "2900"): "信蛇在哪里？",
 ("Kenji_Dialogue.H2O#entry0", "2930"): "信蛇会杀自己的人吗？",
 ("Kenji_Dialogue.H2O#entry0", "3380"): "你为什么攻击信蛇的人？",
 ("Kenji_Dialogue.H2O#entry0", "3430"): "带我去找信蛇，我会尽量忘掉这场令人作呕的谈话。",
 ("Kenji_Dialogue.H2O#entry0", "3440"): "信蛇。",
 ("Kenji_Dialogue.H2O#entry0", "3490"): "那么，你得对我比对信蛇更加忠心。",
 ("Kenji_Dialogue.H2O#entry0", "3510"): "你最好开口。我不杀你，信蛇也会杀你。",
 ("Kenji_Dialogue.H2O#entry0", "3520"): "我有事找信蛇。",
 ("Kenji_Dialogue.H2O#entry0", "3530"): "信蛇给你的好处，值得你替他送命吗？",
 ("Otomo_Dialogue.H2O#entry0", "720"): "信蛇……",
 ("Otomo_Dialogue.H2O#entry0", "1610"): "信蛇的匪徒赶走了这些人。",
 ("Serpent_Dialogue.H2O#entry47", "220"): "杀够你那份农民，我就让你加入信蛇的队伍。",
 ("Serpent_Dialogue.H2O#entry47", "300"): "信蛇根本不是领袖。",
 ("Serpent_Dialogue.H2O#entry47", "350"): "你父亲死后，信蛇一直统治着这三个行省。",
 ("Serpent_Dialogue.H2O#entry47", "440"): "信蛇在东边，混账。",
 ("Serpent_Dialogue.H2O#entry73", "260"): "看着像信蛇大人雇来的匪徒。",
 ("Serpent_Dialogue.H2O#entry122", "240"): "我……我们替信蛇做事。",
 ("WOTW_Lotus_Dialogue.H2O#entry35", "1030"): "武堂大人的命令对我没用！我们的女主人会知道这件事！",
 ("WOTW_Serpent_Dialogue.H2O#entry0", "3020"): "双膝着地！没人敢违抗武堂！",
 ("WOTW_Serpent_Dialogue.H2O#entry54", "10000"): "看来武堂和 Utara 说的是真的……",
 ("WOTW_Serpent_Dialogue.H2O#entry73", "11040"): "啊……武堂，你我有相同的爱好。",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1080"): "没有米，我们就干不了活，武堂。",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1100"): "还是回去找武堂领我们的米吧……",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1130"): "武堂派的活越来越难了……回去吧。",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1160"): "武堂命令我们到这些地道里寻找可开采的新页岩……",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "1220"): "我只是按武堂的命令办事……有什么不对吗？",
 ("WOTW_Wolf_Dialogue.H2O#entry37", "3160"): "武堂，你这恶徒！你会付出代价的！",
 ("WOTW_Wolf_Dialogue.H2O#entry349", "3010"): "你给我们的只有死路……武堂至少给我们米。",
 ("WOTW_Wolf_Dialogue.H2O#entry364", "1020"): "武堂开始使唤我们以后，我都没能好好进食！",
 ("WOTW_Wolf_Dialogue.H2O#entry364", "1120"): "别伤害我们！武堂说这里有页岩！",
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
        if row["chinese"] or not any(name in row["english"] for name in ("Shinja", "Budo")):
            raise ValueError(f"source drift at {key}")
        row["chinese"] = LINES[key]
        row["status"] = "draft; confirmed hero name; not game-tested"
        found.add(key)
    if found != LINES.keys():
        raise ValueError(f"missing rows: {LINES.keys() - found}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {len(found)} confirmed-hero dialogue lines")


if __name__ == "__main__":
    main()
