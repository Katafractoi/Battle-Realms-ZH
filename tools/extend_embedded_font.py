"""Append missing dialogue glyphs to existing KeepTalking6 atlas free cells.

Requires a legally obtained Interface_Text.H2O, a Unicode TTF, and the local
PKWare blast decoder. Writes a backup and candidate only in a fresh directory.
Existing glyph records and pixels are retained; no atlas is resized.
"""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import struct
import zlib

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from patch_lte_h2o import decoder, literal_dcl
from validate_h2o_v7 import inspect


def parse_lfr(data):
    version, scale1, scale2, count = struct.unpack_from("<IffI", data)
    if version != 1 or not 1 <= count <= 32:
        raise ValueError("unsupported LFR")
    pos, groups = 16, []
    for _ in range(count):
        size, uv_height, atlas_count = struct.unpack_from("<IfI", data, pos)
        pos += 12
        names = []
        for _ in range(atlas_count):
            marker, units = struct.unpack_from("<BI", data, pos)
            pos += 5
            if marker != 0 or not 2 <= units <= 260:
                raise ValueError("bad LFR atlas name")
            raw = data[pos:pos + 2 * units]
            if len(raw) != 2 * units or raw[-2:] != b"\0\0":
                raise ValueError("truncated LFR atlas name")
            names.append(raw[:-2].decode("utf-16le"))
            pos += 2 * units
        glyph_count, = struct.unpack_from("<I", data, pos)
        pos += 4
        glyphs = []
        for _ in range(glyph_count):
            atlas, cp, width, uv_width, x, y = struct.unpack_from("<HHffff", data, pos)
            pos += 20
            if atlas >= len(names) or not math.isclose(uv_width, width / 512, abs_tol=1e-6):
                raise ValueError("bad glyph mapping")
            glyphs.append((atlas, cp, width, uv_width, x, y))
        groups.append([size, uv_height, names, glyphs])
    if pos != len(data):
        raise ValueError("LFR trailing bytes")
    codes = [g[1] for g in groups[0][3]]
    if any([g[1] for g in group[3]] != codes for group in groups[1:]):
        raise ValueError("LFR groups have different codepoint lists")
    return version, scale1, scale2, groups, set(codes)


def serialize_lfr(version, scale1, scale2, groups):
    out = bytearray(struct.pack("<IffI", version, scale1, scale2, len(groups)))
    for size, uv_height, names, glyphs in groups:
        out.extend(struct.pack("<IfI", size, uv_height, len(names)))
        for name in names:
            out.extend(struct.pack("<BI", 0, len(name) + 1))
            out.extend((name + "\0").encode("utf-16le"))
        out.extend(struct.pack("<I", len(glyphs)))
        for glyph in glyphs:
            out.extend(struct.pack("<HHffff", *glyph))
    return bytes(out)


def tga_bytes(image):
    if image.size != (512, 512):
        raise ValueError("atlas is not 512x512")
    header = bytes.fromhex("000002000000000000000000000200022000")
    return header + image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes("raw", "BGRA")


def render(char, font, width, height):
    box = font.getbbox(char)
    if not box:
        raise ValueError(f"no font glyph for U+{ord(char):04X}")
    source = Image.new("L", (box[2] - box[0], box[3] - box[1]), 0)
    ImageDraw.Draw(source).text((-box[0], -box[1]), char, font=font, fill=255)
    if not source.getbbox():
        raise ValueError(f"blank font glyph for U+{ord(char):04X}")
    max_width = max(1, width - 2)
    max_height = max(1, round(height * .72))
    scale = min(1, max_width / source.width, max_height / source.height)
    if scale < 1:
        source = source.resize((max(1, round(source.width * scale)),
                                max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
    alpha = Image.new("L", (width, height), 0)
    alpha.paste(source, ((width - source.width) // 2, (height - source.height) // 2))
    return ImageEnhance.Contrast(alpha).enhance(1.5)


def raw_entry(archive, index, decode):
    f = struct.unpack_from("<10I", archive, 513 + 40 * index)
    return decode(archive[f[6] + 12:f[6] + 12 + f[4]], f[3])


def repack(source, replacements, decode):
    version, count = struct.unpack_from("<II", source, 481)
    if source[480] != 0x1a or version != 7:
        raise ValueError("not H2O v7")
    second = 513 + 40 * count
    if source[513:second] != source[second:second + 40 * count]:
        raise ValueError("index copies differ")
    first_offset = struct.unpack_from("<10I", source, 513)[6]
    result = bytearray(source[:first_offset])
    for i in range(count):
        f = struct.unpack_from("<10I", source, 513 + 40 * i)
        if i in replacements:
            raw = replacements[i]
            packed = literal_dcl(raw)
            if decode(packed, len(raw)) != raw:
                raise ValueError(f"blast readback failed at {i}")
            crc = zlib.crc32(raw)
            size = len(raw)
        else:
            packed = source[f[6] + 12:f[6] + 12 + f[4]]
            crc, size = f[8], f[3]
        offset = len(result)
        for table in (513, second):
            at = table + 40 * i
            for slot, value in ((3, size), (4, len(packed)), (6, offset), (8, crc)):
                struct.pack_into("<I", result, at + 4 * slot, value)
        result.extend(struct.pack("<III", len(packed), size, crc))
        result.extend(packed)
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--entry-map", type=Path, required=True)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--ttf", type=Path, required=True)
    parser.add_argument("--blast-dll", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error("output directory exists; use a fresh directory")
    source = args.archive.read_bytes()
    mapping = json.loads(args.entry_map.read_text(encoding="utf-8"))
    decode = decoder(args.blast_dll)
    font_index = mapping["Fonts\\KeepTalking6.LFR"]
    font_raw = raw_entry(source, font_index, decode)
    version, scale1, scale2, groups, present = parse_lfr(font_raw)
    with args.translations.open(encoding="utf-8-sig", newline="") as stream:
        required = {ord(char) for row in csv.DictReader(stream)
                    for char in row["chinese"] if row["chinese"]}
    missing = sorted(required - present)
    if not missing or any(cp > 0xffff for cp in missing):
        raise ValueError("expected new BMP glyphs")
    replacements = {}
    detail = []
    used_atlases = {name for group in groups for name in group[2]}
    spare_atlases = [path.removeprefix("Fonts\\") for path in mapping
                     if path.startswith("Fonts\\") and path.lower().endswith(".tga")
                     and path.removeprefix("Fonts\\") not in used_atlases]
    for size, uv_height, names, glyphs in groups:
        height = round(uv_height * 512)
        cols, rows = 512 // (size + 1), 512 // (height + 1)
        capacity = cols * rows
        last = len(names) - 1
        used = {(round(g[4] * 512) // (size + 1), round(g[5] * 512) // (height + 1))
                for g in glyphs if g[0] == last}
        path = "Fonts\\" + names[-1]
        index = mapping[path]
        old_image = Image.open(io.BytesIO(raw_entry(source, index, decode))).convert("RGBA")
        if old_image.size != (512, 512):
            raise ValueError(f"bad atlas size: {path}")
        # A cell can contain pixels even when no LFR glyph points to it.
        # Treat the atlas image as the final authority before writing there.
        width = max(1, round(size * .72))
        free = [(col, row) for row in range(rows) for col in range(cols)
                if (col, row) not in used
                and not old_image.crop((col * (size + 1), row * (height + 1),
                                        col * (size + 1) + width,
                                        row * (height + 1) + height)).getbbox()]
        extra_pages = math.ceil(max(0, len(missing) - len(free)) / capacity)
        if extra_pages > len(spare_atlases):
            raise ValueError(f"size {size}: need {extra_pages} more atlas pages, only {len(spare_atlases)} spare")
        images = {last: old_image.copy()}
        slots = [(last, col, row) for col, row in free]
        for _ in range(extra_pages):
            added = spare_atlases.pop(0)
            names.append(added)
            page = len(names) - 1
            images[page] = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            slots.extend((page, col, row) for row in range(rows) for col in range(cols))
        face = ImageFont.truetype(str(args.ttf), size)
        for cp, (page, col, row) in zip(missing, slots):
            width = max(1, round(size * .72))
            alpha = render(chr(cp), face, width, height)
            tile = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            tile.putalpha(alpha)
            x, y = col * (size + 1), row * (height + 1)
            if images[page].crop((x, y, x + width, y + height)).getbbox():
                raise ValueError(f"occupied atlas cell: {names[page]} {(col, row)}")
            images[page].paste(tile, (x, y))
            glyphs.append((page, cp, float(width), width / 512, x / 512, y / 512))
        glyphs.sort(key=lambda glyph: glyph[1])
        for page, image in images.items():
            replacements[mapping["Fonts\\" + names[page]]] = tga_bytes(image)
        detail.append({"size": size, "last_atlas": names[-1], "free_before": len(free),
                       "new_glyphs": len(missing), "capacity": capacity,
                       "added_pages": extra_pages})
    changed_font = serialize_lfr(version, scale1, scale2, groups)
    parsed = parse_lfr(changed_font)
    if len(parsed[4]) != len(present) + len(missing):
        raise ValueError("LFR codepoint count drift")
    replacements[font_index] = changed_font
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
        raise ValueError("changed H2O entries differ from font plan")
    for i in replacements:
        if new[i][1] != replacements[i]:
            raise ValueError(f"candidate raw readback mismatch at {i}")
    report = {"source_sha256": hashlib.sha256(source).hexdigest(),
              "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
              "backup_sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
              "font_sha256": hashlib.sha256(changed_font).hexdigest(),
              "new_codepoints": [f"U+{cp:04X}" for cp in missing],
              "new_characters": "".join(map(chr, missing)),
              "changed_entries": changed,
              "unchanged_compressed_entries": len(old) - len(changed),
              "groups": detail}
    (args.output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "groups"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
