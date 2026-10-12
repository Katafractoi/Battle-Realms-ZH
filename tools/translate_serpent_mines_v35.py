"""Translate Budo's contiguous mine, rebellion, and Grayback scenes."""

import csv
from pathlib import Path


LINES = {
    "1010": "谁让你们这些懒狗进我的矿井？",
    "1015": "回去干活！",
    "1020": "哦，狗东西终于饿醒了？",
    "1030": "你，拿镐的，沿右边的坑道往下走。",
    "1040": "那里有一堆页岩，正等着你们敲碎。",
    "1050": "做完回来见我，我就给你们两个分些稻米。",
    "1060": "真贪心，真贪心……我很快派人送去。",
    "1070": "嗯？谁在那里？",
    "1080": "当然！Yvaine 的奴隶活着就是为了服从她。",
    "1090": "你们一粒都别想要。莲花族的地盘上，Yvaine 的心愿就是法令。",
    "1100": "你没完没了地哀求也没用！",
    "1110": "西南边一堆页岩被塌下的洞壁挡住了。",
    "1120": "带上那个拿锤子的同伴，他能敲开塌下来的石头。",
    "1125": "然后把页岩敲碎，赶紧回来。",
    "1130": "多产些页岩，我也许能劝莲花族再给你们点稻米。",
    "1140": "快去干活，不然就尝尝我的鞭子！",
    "1150": "真让我吃惊……我以为会花更久。",
    "1160": "看来饥饿还没把你们弄得太虚弱。",
    "1170": "放在安全的地方。我说话算话，奴隶。",
    "1180": "又来了个传信的？你想要什么？",
    "1190": "请恕罪！这些奴隶怎么敢给女主人送这么可怕的食物！",
    "1200": "请收下我最后的稻米，原谅我的过错。",
    "1210": "恐怕这些肮脏的野人什么都吃得下。",
    "1220": "你把坏掉的稻米送给 Yvaine，真是犯了个大错。",
    "1230": "现在你得加倍干活，才能挣到晚饭。",
    "1240": "一只肮脏的恶狼族小崽子也敢不服从？我的鞭子会教你规矩！",
    "1250": "不服从，还敢威胁我？不可容忍！",
    "1260": "你这张嘴害得朋友要挨三十鞭！",
    "1270": "除非……你愿意补偿我？",
    "1280": "Yvaine 不许我派人去深处的坑道。",
    "1290": "她在那里藏了东西，而我不喜欢秘密，更不喜欢意外。",
    "1300": "偷偷下去替我看看，也许我就不罚你了。",
    "1310": "快动，别等我改变主意！",
    "1320": "退后，狗东西！",
    "3000": "哎呀，我的小探子竟成了叛军。真可爱。",
    "3010": "要是莲花族的废物管得住自己的奴隶，我也不用来了。",
    "3030": "控制你们是我的职责。你们要找的人是我……",
    "3040": "……还有灵蛇族大军！",
    "3050": "Taro 王子派来一队精锐 Enforcer，帮我维持秩序。",
    "3060": "看看一群饿坏的奴隶能不能对付真正的战士！",
    "3070": "我低估你了，奴隶。你没看上去那么蠢。",
    "3080": "没想到你打败了 Taro 王子最喜欢的打手。",
    "3090": "他听了可不会高兴。",
    "3100": "既然你不怕杀灵蛇族的人，那就试试看杀自己人！",
    "3110": "一点稻米就能买到这些，真叫人吃惊，不是吗？",
    "11010": "你确定他们已经到了这里？",
    "11020": "我以为我军会在下面挡住恶狼族。",
    "11030": "这场叛乱威胁着灵蛇族如今的一切。",
    "11040": "Taro 不杀 Grayback，我就亲自动手！",
    "11050": "只要 Grayback 死在我的鞭下，就算 Oja 把我喂狗也无所谓。",
    "11060": "留给 Grayback 吧，我迷人的女杀手。",
    "11070": "眼下该设圈套抓一头狼了。",
}


def main():
    path = Path("translations/dialogue-all-english.csv")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    seen = set()
    for row in rows:
        if not row["source_file"].endswith("Serpent_Dialogue.H2O#entry0"):
            continue
        key = row["string_id"]
        if key not in LINES:
            continue
        if row["chinese"]:
            raise ValueError(f"already translated: {key}")
        row["chinese"] = LINES[key]
        row["status"] = "draft; Serpent mines v35; font candidate pending; not game-tested"
        seen.add(key)
    if seen != LINES.keys():
        raise ValueError(f"missing source rows: {LINES.keys() - seen}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Translated {len(seen)} mine dialogue lines")


if __name__ == "__main__":
    main()
