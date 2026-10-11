"""Prepare a reversible CJK line-break candidate without visible padding spaces.

The source CSV remains natural Chinese. LF insertion is a runtime hypothesis,
so this output must be visually checked before release.
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path, PureWindowsPath
import struct
import subprocess
import sys

from audit_render_cases import widths_by_size
from patch_lte_h2o import decoder, records


LIMITS = {
    "Goals.lte": 160,
    "WOTW_Goals.lte": 160,
    "Console_Tooltips.lte": 96,
    "WOTW_Console_Tooltips.lte": 96,
}
BREAK_AFTER = set("，。；：、！？,.!?;:")
SENTENCE_END = set("。！？.!?")
NO_LINE_START = set("，。；：、！？,.!?;:）】」』")
KEEP_PAIRS = {"执行", "单位", "军事", "训练", "攻击", "目标", "命令", "农民",
              "村民", "建筑", "采集", "修理", "守卫", "跟随", "持续", "有效"}


def advance(text, widths):
    return sum(widths.get(ord(c), 8) for c in text)


def break_paragraph(text, limit, widths, pairs):
    result = []
    remaining = text
    while remaining and advance(remaining, widths) > limit:
        used = 0
        furthest = 0
        for i, char in enumerate(remaining):
            width = widths.get(ord(char), 8)
            if used + width > limit:
                break
            used += width
            furthest = i + 1
        if furthest == 0:
            furthest = 1
        candidates = []
        for i in range(1, furthest + 1):
            prefix = advance(remaining[:i], widths)
            if prefix < limit * 0.55 or i >= len(remaining):
                continue
            left, right = remaining[i - 1], remaining[i]
            if right in NO_LINE_START or left in "（【「『":
                continue
            if left.isascii() and left.isalnum() and right.isascii() and right.isalnum():
                continue
            if left in SENTENCE_END:
                cost = -2000 + (limit - prefix)
            elif left in BREAK_AFTER:
                cost = -1000 + (limit - prefix)
            elif left.isspace():
                cost = -500 + (limit - prefix)
            else:
                cost = pairs[(left, right)] * 4 + (limit - prefix) / 8
                if left + right in KEEP_PAIRS:
                    cost += 500
            candidates.append((cost, -prefix, i))
        boundary = min(candidates)[2] if candidates else furthest
        if boundary < len(remaining) and remaining[boundary] in NO_LINE_START and boundary > 1:
            boundary -= 1
        while (1 < boundary < len(remaining) and
               remaining[boundary - 1].isascii() and remaining[boundary - 1].isalnum() and
               remaining[boundary].isascii() and remaining[boundary].isalnum()):
            boundary -= 1
        if boundary == len(remaining):
            break
        result.append(remaining[:boundary])
        remaining = remaining[boundary:]
    result.append(remaining)
    return "\n".join(result)


def wrap(text, limit, widths, pairs):
    if not any("\u3400" <= char <= "\u9fff" for char in text):
        return text
    return "\n".join(break_paragraph(part, limit, widths, pairs)
                     for part in text.split("\n"))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "translations", "entry-map", "blast-dll", "font", "output-dir"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    mapping = json.loads(a.entry_map.read_text(encoding="utf-8"))
    widths = widths_by_size(a.font.read_bytes())[11]
    source = a.base.read_bytes()
    decode = decoder(a.blast_dll)
    base_records = {}
    for name, i in mapping.items():
        if PureWindowsPath(name).name not in LIMITS:
            continue
        f = struct.unpack_from("<10I", source, 513 + 40 * i)
        raw = decode(source[f[6] + 12:f[6] + 12 + f[4]], f[3])
        base_records[name] = {ident: value for ident, _, value, _ in records(raw)}
    with a.translations.open(encoding="utf-8-sig", newline="") as source_csv:
        rows = list(csv.DictReader(source_csv))
    pairs = Counter((left, right) for row in rows for left, right in
                    zip(row["chinese"], row["chinese"][1:])
                    if "\u3400" <= left <= "\u9fff" and "\u3400" <= right <= "\u9fff")
    delta = []
    stats = {"master_rows_checked": 0, "rows_changed_from_v13": 0,
             "rows_with_new_lf": 0, "new_lf_count": 0,
             "max_line_advance_px": 0, "by_file": {}}
    for row in rows:
        name = row["source_file"]
        if name not in base_records or not row["chinese"]:
            continue
        ident = int(row["string_id"])
        baseline = base_records[name][ident]
        natural = row["chinese"]
        limit = LIMITS[PureWindowsPath(name).name]
        desired = wrap(natural, limit, widths, pairs)
        if desired.replace("\n", "") != natural.replace("\n", ""):
            raise ValueError("Non-newline character changed: " + name + "#" + str(ident))
        if desired.count(" ") != natural.count(" "):
            raise ValueError("ASCII spaces changed: " + name + "#" + str(ident))
        if desired != natural and any(advance(line, widths) > limit for line in desired.split("\n")):
            raise ValueError("Wrapped line exceeds width: " + name + "#" + str(ident))
        stats["master_rows_checked"] += 1
        if desired == baseline:
            continue
        delta.append({"source_file": name, "string_id": ident,
                      "english": baseline, "chinese": desired})
        stats["rows_changed_from_v13"] += 1
        stats["by_file"][name] = stats["by_file"].get(name, 0) + 1
        if desired.count("\n") > natural.count("\n"):
            stats["rows_with_new_lf"] += 1
            stats["new_lf_count"] += desired.count("\n") - natural.count("\n")
        stats["max_line_advance_px"] = max(stats["max_line_advance_px"],
            *(round(advance(line, widths)) for line in desired.split("\n")))
    if not delta:
        raise ValueError("No differences from baseline")
    delta_path = a.output_dir / "interface-v14-wrap-delta.csv"
    with delta_path.open("w", encoding="utf-8-sig", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["source_file", "string_id", "english", "chinese"])
        writer.writeheader()
        writer.writerows(delta)
    archive = a.output_dir / "Interface_Text.H2O"
    subprocess.run([sys.executable, str(Path(__file__).with_name("patch_lte_h2o.py")),
                    "--archive", str(a.base), "--translations", str(delta_path),
                    "--entry-map", str(a.entry_map), "--blast-dll", str(a.blast_dll),
                    "--output", str(archive)], check=True)
    subprocess.run([sys.executable, str(Path(__file__).with_name("validate_h2o_v7.py")),
                    "--source", str(a.base), "--candidate", str(archive),
                    "--blast-dll", str(a.blast_dll)], check=True)
    (a.output_dir / "wrap-stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
