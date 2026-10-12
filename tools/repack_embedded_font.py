"""Repack existing font glyph pixels into the same TGA entry pool.

Packs by each glyph's actual width, leaving room for exact new translations.
Requires user-supplied game archive, TTF, and blast DLL; writes a fresh local
candidate and backup only. Does not access Steam.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil

from PIL import Image, ImageFont

from extend_embedded_font import (parse_lfr, raw_entry, render, repack,
                                  serialize_lfr, tga_bytes)
from patch_lte_h2o import decoder
from validate_h2o_v7 import inspect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("archive", "entry-map", "translations", "ttf", "blast-dll", "output-dir"):
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error("output directory exists; use a fresh directory")
    source = args.archive.read_bytes()
    mapping = json.loads(args.entry_map.read_text(encoding="utf-8"))
    decode = decoder(args.blast_dll)
    font_index = mapping["Fonts\\KeepTalking6.LFR"]
    original_font = raw_entry(source, font_index, decode)
    version, scale1, scale2, groups, present = parse_lfr(original_font)
    with args.translations.open(encoding="utf-8-sig", newline="") as stream:
        required = {ord(ch) for r in csv.DictReader(stream) for ch in r["chinese"] if r["chinese"]}
    new_codes = sorted(required - present)
    if any(cp > 0xffff for cp in new_codes):
        raise ValueError("font stores BMP codepoints only")
    original_names = [name for g in groups for name in g[2]]
    if len(set(original_names)) != len(original_names):
        raise ValueError("atlas names are not unique across groups")
    image_cache = {}
    for name in original_names:
        raw = raw_entry(source, mapping["Fonts\\" + name], decode)
        image = Image.open(io.BytesIO(raw)).convert("RGBA")
        if image.size != (512, 512):
            raise ValueError(f"unexpected atlas dimensions: {name}")
        image_cache[name] = image
    name_cursor, replacements, details, copied_pixels = 0, {}, [], 0
    for group in groups:
        size, uv_height, old_names, old_glyphs = group
        height = round(uv_height * 512)
        face = ImageFont.truetype(str(args.ttf), size)
        tiles = {}
        for atlas, cp, width, uv_width, x, y in old_glyphs:
            source_image = image_cache[old_names[atlas]]
            px, py = round(x * 512), round(y * 512)
            tile = source_image.crop((px, py, px + max(1, round(width)), py + height))
            if tile.size[0] > 512 or tile.size[1] > 512:
                raise ValueError(f"bad old glyph dimensions U+{cp:04X}")
            tiles[cp] = (width, tile, True)
        for cp in new_codes:
            width = max(1, round(size * .72))
            alpha = render(chr(cp), face, width, height)
            tile = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            tile.putalpha(alpha)
            tiles[cp] = (float(width), tile, False)
        pages, updated, x, y = [], [], 0, 0
        for cp in sorted(tiles):
            width, tile, is_old = tiles[cp]
            if x + tile.width > 512:
                x, y = 0, y + height + 1
            if not pages or y + height > 512:
                if name_cursor >= len(original_names):
                    raise ValueError(f"atlas pool exhausted at size {size}")
                name = original_names[name_cursor]
                name_cursor += 1
                pages.append((name, Image.new("RGBA", (512, 512), (0, 0, 0, 0))))
                x, y = 0, 0
            page_index = len(pages) - 1
            pages[page_index][1].paste(tile, (x, y))
            if is_old and pages[page_index][1].crop((x, y, x + tile.width, y + height)).tobytes() != tile.tobytes():
                raise ValueError(f"old glyph pixels changed: size {size} U+{cp:04X}")
            copied_pixels += int(is_old)
            updated.append((page_index, cp, width, width / 512, x / 512, y / 512))
            x += tile.width + 1
        group[2] = [name for name, _ in pages]
        group[3] = updated
        for name, image in pages:
            replacements[mapping["Fonts\\" + name]] = tga_bytes(image)
        details.append({"size": size, "old_pages": len(old_names), "new_pages": len(pages),
                        "glyphs": len(updated)})
    new_font = serialize_lfr(version, scale1, scale2, groups)
    if len(parse_lfr(new_font)[4]) != len(present) + len(new_codes):
        raise ValueError("LFR readback glyph count drift")
    replacements[font_index] = new_font
    candidate = repack(source, replacements, decode)
    args.output_dir.mkdir(parents=True)
    backup = args.output_dir / "Interface_Text.base.H2O"
    shutil.copyfile(args.archive, backup)
    target = args.output_dir / "Interface_Text.H2O"
    target.write_bytes(candidate)
    _, old = inspect(backup, decode)
    _, new = inspect(target, decode)
    changed = [i for i, (a, b) in enumerate(zip(old, new)) if a[0] != b[0]]
    if set(changed) != set(replacements):
        raise ValueError("changed entries differ from plan")
    for i, raw in replacements.items():
        if new[i][1] != raw:
            raise ValueError(f"archive raw readback failed at {i}")
    report = {"source_sha256": hashlib.sha256(source).hexdigest(),
              "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
              "font_sha256": hashlib.sha256(new_font).hexdigest(),
              "new_characters": "".join(map(chr, new_codes)),
              "new_codepoints": [f"U+{cp:04X}" for cp in new_codes],
              "original_glyph_pixel_copies_verified": copied_pixels,
              "atlas_pages_available": len(original_names),
              "atlas_pages_used": name_cursor,
              "changed_entries": changed,
              "unchanged_compressed_entries": len(old) - len(changed),
              "groups": details}
    (args.output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "groups"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
