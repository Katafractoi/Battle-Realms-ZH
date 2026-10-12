"""Move three CJK punctuation glyphs within their existing font cells.

The only edited archive entries are atlas TGAs containing the target glyphs.
LFR metrics and every other glyph pixel are preserved.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image

from extend_embedded_font import parse_lfr, raw_entry, repack, tga_bytes
from patch_lte_h2o import decoder
from validate_h2o_v7 import inspect


TARGETS = {"，": "bottom", "—": "center", "…": "center"}
REFERENCE = "汉"


def glyph_tile(image, glyph, height):
    _, _, width, _, ux, uy = glyph
    x, y = round(ux * 512), round(uy * 512)
    width = max(1, round(width))
    return (x, y), image.crop((x, y, x + width, y + height))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("archive", "entry-map", "blast-dll", "output-dir"):
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error("output directory exists")
    source = args.archive.read_bytes()
    mapping = json.loads(args.entry_map.read_text(encoding="utf-8"))
    decode = decoder(args.blast_dll)
    groups = parse_lfr(raw_entry(source, mapping["Fonts\\KeepTalking6.LFR"], decode))[3]
    pages = {}
    originals = {}

    def page(name):
        if name not in originals:
            originals[name] = Image.open(io.BytesIO(
                raw_entry(source, mapping["Fonts\\" + name], decode))).convert("RGBA")
            pages[name] = originals[name].copy()
        return pages[name]

    shifts = []
    for size, uv_height, names, glyphs in groups:
        height = round(uv_height * 512)
        by_codepoint = {g[1]: g for g in glyphs}
        ref = by_codepoint[ord(REFERENCE)]
        ref_name = names[ref[0]]
        _, ref_tile = glyph_tile(page(ref_name), ref, height)
        ref_box = ref_tile.getchannel("A").getbbox()
        if not ref_box:
            raise ValueError(f"reference glyph blank at size {size}")
        ref_mid = (ref_box[1] + ref_box[3]) / 2
        for char, placement in TARGETS.items():
            glyph = by_codepoint[ord(char)]
            name = names[glyph[0]]
            image = page(name)
            (x, y), tile = glyph_tile(image, glyph, height)
            box = tile.getchannel("A").getbbox()
            if not box:
                raise ValueError(f"blank {char} at size {size}")
            if placement == "bottom":
                shift = ref_box[3] - box[3]
            else:
                shift = round(ref_mid - (box[1] + box[3]) / 2)
            if box[1] + shift < 0 or box[3] + shift > height:
                raise ValueError(f"out-of-cell move: {char} size {size}")
            target = Image.new("RGBA", tile.size, (0, 0, 0, 0))
            target.paste(tile.crop(box), (box[0], box[1] + shift))
            image.paste(target, (x, y))
            after = target.getchannel("A").getbbox()
            if after != (box[0], box[1] + shift, box[2], box[3] + shift):
                raise ValueError(f"glyph shift readback failed: {char} size {size}")
            shifts.append({"size": size, "char": char, "before": box, "after": after,
                           "vertical_pixels": shift, "atlas": name})
    # Verify that raster pixels for every other glyph remain untouched.
    preserved = 0
    for size, uv_height, names, glyphs in groups:
        height = round(uv_height * 512)
        for glyph in glyphs:
            if glyph[1] in {ord(ch) for ch in TARGETS}:
                continue
            name = names[glyph[0]]
            if name not in pages:
                continue
            _, before = glyph_tile(originals[name], glyph, height)
            _, after = glyph_tile(pages[name], glyph, height)
            if before.tobytes() != after.tobytes():
                raise ValueError(f"unrelated glyph pixels changed: size {size}, U+{glyph[1]:04X}")
            preserved += 1
    replacements = {mapping["Fonts\\" + name]: tga_bytes(image) for name, image in pages.items()}
    candidate = repack(source, replacements, decode)
    args.output_dir.mkdir(parents=True)
    target = args.output_dir / "Interface_Text.H2O"
    target.write_bytes(candidate)
    _, before = inspect(args.archive, decode)
    _, after = inspect(target, decode)
    changed = [i for i, (old, new) in enumerate(zip(before, after))
               if old[0] != new[0]]
    if not changed or not set(changed).issubset(replacements):
        raise ValueError("changed entries outside punctuation atlas set")
    for index, expected in replacements.items():
        if after[index][1] != expected:
            raise ValueError(f"archive readback failed at entry {index}")
    report = {"source_sha256": hashlib.sha256(source).hexdigest(),
              "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
              "shifted_glyphs": len(shifts), "other_glyphs_verified": preserved,
              "changed_entries": changed, "shifts": shifts}
    (args.output_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "shifts"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
