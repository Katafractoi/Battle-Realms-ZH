"""Unchanged LFR/bitmap algorithms from extend_embedded_font.py."""
import math, struct
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
    from PIL import Image
    if image.size != (512, 512):
        raise ValueError("atlas is not 512x512")
    header = bytes.fromhex("000002000000000000000000000200022000")
    return header + image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes("raw", "BGRA")

def render(char, font, width, height):
    from PIL import Image, ImageDraw, ImageEnhance
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
