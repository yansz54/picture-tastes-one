#!/usr/bin/env python3
"""The picture that tastes of one ingredient — a rich ramen bowl.

Pure Python stdlib only (zlib + struct for PNG). Deterministic: fixed
constants, no time/hash-order randomness. Two runs are byte-identical.

Writes /output/entry.png (creating the dir if needed) and ./entry.png.
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- buffer
buf = bytearray(W * H * 3)


def set_px(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b


def blend_px(x, y, r, g, b, a):
    """Alpha-blend colour over existing pixel (a in 0..1)."""
    if 0 <= x < W and 0 <= y < H and a > 0.0:
        i = (y * W + x) * 3
        if a >= 1.0:
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b
        else:
            buf[i] = int(buf[i] + (r - buf[i]) * a)
            buf[i + 1] = int(buf[i + 1] + (g - buf[i + 1]) * a)
            buf[i + 2] = int(buf[i + 2] + (b - buf[i + 2]) * a)


def det(x, y, s=0):
    """Deterministic pseudo-random in [0,1) from integer coords."""
    n = (x * 374761393 + y * 668265263 + s * 974634211) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    n = (n ^ (n >> 16)) & 0xFFFFFFFF
    return n / 4294967296.0


def clamp(v, lo=0, hi=255):
    return lo if v < lo else hi if v > hi else int(v)


def shade(r, g, b, f):
    return clamp(r * f), clamp(g * f), clamp(b * f)


def fill_ellipse(cx, cy, rx, ry, r, g, b, a=1.0, y0=None, y1=None):
    y0 = int(cy - ry) if y0 is None else y0
    y1 = int(cy + ry) if y1 is None else y1
    for y in range(max(0, y0), min(H, y1 + 1)):
        dy = (y - cy) / ry
        if abs(dy) > 1:
            continue
        dx = rx * math.sqrt(1.0 - dy * dy)
        x0 = int(cx - dx)
        x1 = int(cx + dx)
        for x in range(max(0, x0), min(W, x1 + 1)):
            if a >= 1.0:
                set_px(x, y, r, g, b)
            else:
                blend_px(x, y, r, g, b, a)


def disc(cx, cy, rad, r, g, b, a=1.0):
    fill_ellipse(cx, cy, rad, rad, r, g, b, a)


def thick_point(cx, cy, rad, r, g, b, a=1.0):
    rad = int(rad)
    for y in range(cy - rad, cy + rad + 1):
        for x in range(cx - rad, cx + rad + 1):
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= rad * rad:
                if a >= 1.0:
                    set_px(x, y, r, g, b)
                else:
                    blend_px(x, y, r, g, b, a)


def thick_line(x0, y0, x1, y1, rad, r, g, b, a=1.0):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.4) + 2
    for i in range(steps + 1):
        t = i / steps
        thick_point(int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t),
                    rad, r, g, b, a)


def in_ellipse(x, y, cx, cy, rx, ry):
    dx = (x - cx) / rx
    dy = (y - cy) / ry
    return dx * dx + dy * dy <= 1.0


# ---------------------------------------------------------------- table
# Warm dark wooden table: vertical planks, grain, warm gradient.
for y in range(H):
    for x in range(W):
        plank = (x // 171) % 3
        base = [(58, 34, 20), (66, 38, 22), (52, 31, 18)][plank]
        grain = math.sin(x * 0.011 + plank * 2.1 + math.sin(y * 0.02) * 1.4) * 6
        grain += (det(x // 3, y // 3, 7) - 0.5) * 14
        warm = 1.0 + 0.10 * math.exp(-((x - 300) ** 2 + (y - 260) ** 2) / 300000.0)
        r = clamp(base[0] * warm + grain)
        g = clamp(base[1] * warm + grain * 0.8)
        b = clamp(base[2] * warm + grain * 0.6)
        set_px(x, y, r, g, b)
# Plank seams
for px in (171, 342, 513, 684, 855):
    for y in range(H):
        for dx in (-1, 0, 1):
            blend_px(px + dx, y, 18, 10, 6, 0.55 if dx == 0 else 0.25)
# Soft warm pool of light on the table, upper left
for y in range(0, 620):
    for x in range(0, 700):
        d2 = ((x - 330) ** 2 + (y - 300) ** 2) / 260000.0
        if d2 < 1.0:
            blend_px(x, y, 255, 190, 110, 0.10 * (1 - d2))

# ---------------------------------------------------------------- bowl
BCX, BCY = 512, 580          # bowl centre
BRX, BRY = 448, 368          # bowl outer radii (3/4 view ellipse)
# Bowl shadow on the table
fill_ellipse(BCX + 26, BCY + 40, BRX + 18, 60, 12, 7, 4, 0.55,
             y0=BCY + 168, y1=H - 1)
# Bowl exterior: deep indigo ceramic with warm rim light
for y in range(BCY - BRY, BCY + BRY + 1):
    dy = (y - BCY) / BRY
    if abs(dy) > 1:
        continue
    dx = BRX * math.sqrt(1.0 - dy * dy)
    x0, x1 = int(BCX - dx), int(BCX + dx)
    # lower half of the bowl body is visible below the broth line
    for x in range(max(0, x0), min(W, x1 + 1)):
        # ceramic shading: darker at bottom, warm sheen upper-left
        f = 1.0 - 0.55 * max(0.0, (y - BCY) / BRY)
        sheen = 0.35 * math.exp(-((x - 340) ** 2 + (y - 430) ** 2) / 90000.0)
        r = clamp(38 * f + 200 * sheen + 40 * max(0.0, (x - BCX) / BRX) * 0.2)
        g = clamp(48 * f + 150 * sheen)
        b = clamp(96 * f + 190 * sheen)
        set_px(x, y, r, g, b)
# Decorative band on the bowl body
for y in range(BCY + 134, BCY + 184):
    dy = (y - BCY) / BRY
    if abs(dy) > 1:
        continue
    dx = BRX * math.sqrt(1.0 - dy * dy)
    for x in range(int(BCX - dx), int(BCX + dx) + 1):
        if det(x, y, 11) < 0.5:
            blend_px(x, y, 214, 164, 90, 0.85)
# Bowl rim: thick warm cream ring
for ang in range(0, 360):
    t = math.radians(ang)
    x = int(BCX + math.cos(t) * 418)
    y = int(BCY + math.sin(t) * 342)
    thick_point(x, y, 13, 238, 222, 190)
# Rim inner shadow
for ang in range(0, 360):
    t = math.radians(ang)
    x = int(BCX + math.cos(t) * 396)
    y = int(BCY + math.sin(t) * 322)
    thick_point(x, y, 5, 120, 60, 40, 0.5)

# ---------------------------------------------------------------- broth
BRX2, BRY2 = 392, 316        # broth surface
BCY2 = 572
for y in range(BCY2 - BRY2, BCY2 + BRY2 + 1):
    dy = (y - BCY2) / BRY2
    if abs(dy) > 1:
        continue
    dx = BRX2 * math.sqrt(1.0 - dy * dy)
    for x in range(max(0, int(BCX - dx)), min(W, int(BCX + dx) + 1)):
        # rich red-brown broth, deeper at edges, glowing centre
        edge = ((x - BCX) / BRX2) ** 2 + ((y - BCY2) / BRY2) ** 2
        glow = math.exp(-edge * 2.2)
        n = (det(x // 4, y // 4, 3) - 0.5) * 18
        r = clamp(138 + 78 * glow + n)
        g = clamp(56 + 36 * glow + n * 0.7)
        b = clamp(22 + 12 * glow + n * 0.5)
        set_px(x, y, r, g, b)
# Chilli-oil swirls: glossy red-orange ribbons on the broth
for k in range(5):
    cx0 = BCX - 224 + k * 107
    cy0 = BCY2 - 146 + (k % 2) * 168
    for i in range(90):
        t = i / 90.0
        x = int(cx0 + t * 168 + math.sin(t * 9 + k * 2.0) * 29)
        y = int(cy0 + math.sin(t * 5 + k) * 34 + t * 22)
        if in_ellipse(x, y, BCX, BCY2, BRX2 - 8, BRY2 - 8):
            thick_point(x, y, 7, 198, 62, 18, 0.75)
            thick_point(x, y, 3, 232, 110, 40, 0.8)
# Glossy oil sheen: big soft highlight upper-left of broth
for y in range(BCY2 - BRY2, BCY2 + 40):
    for x in range(BCX - BRX2, BCX + 40):
        d2 = ((x - 386) ** 2) / 27000.0 + ((y - 456) ** 2) / 15000.0
        if d2 < 1.0 and in_ellipse(x, y, BCX, BCY2, BRX2 - 6, BRY2 - 6):
            blend_px(x, y, 255, 205, 140, 0.45 * (1 - d2))
# Second, sharper specular streak across the broth (light catching the oil)
for i in range(120):
    t = i / 120.0
    x = int(308 + t * 290)
    y = int(466 + math.sin(t * 3.1) * 24 - t * 34)
    thick_point(x, y, 6, 255, 225, 165, 0.5)
    thick_point(x, y, 2, 255, 244, 205, 0.7)
# Oil droplets
for (ox, oy, orad) in [(655, 466, 18), (723, 558, 12), (421, 647, 15),
                       (599, 714, 10), (790, 490, 9), (330, 535, 11)]:
    disc(ox, oy, orad, 214, 120, 44, 0.85)
    disc(ox - orad // 3, oy - orad // 3, max(2, orad // 3), 255, 220, 150, 0.9)

# ---------------------------------------------------------------- noodles
# Wavy noodle nests: pale golden strands with shaded undersides.
NOODLE = (233, 196, 110)
NOODLE_D = (176, 128, 52)
for s in range(30):
    seed = s * 37
    y_base = BCY2 - 213 + (s * 53) % 425
    x_start = BCX - 336 + (seed % 100)
    amp = 16 + (seed % 14)
    freq = 0.028 + (seed % 10) * 0.0012
    phase = seed * 0.7
    length = 425 + (seed % 200)
    prev = None
    for i in range(0, length, 7):
        x = x_start + i
        y = int(y_base + math.sin(i * freq + phase) * amp
                + math.sin(i * 0.011 + phase * 2) * 8)
        if not in_ellipse(x, y, BCX, BCY2, BRX2 - 14, BRY2 - 14):
            prev = None
            continue
        if prev is not None:
            thick_line(prev[0], prev[1] + 3, x, y + 3, 5, *NOODLE_D, 0.9)
            thick_line(prev[0], prev[1], x, y, 5, *NOODLE, 0.95)
        prev = (x, y)
# A lifted noodle twirl mound in the centre-left, catching the light:
# tight concentric strands, darker gaps between them so it reads as
# wound noodles rather than a flat blob.
for s in range(8):
    cx0 = 420 + (s % 4) * 27
    cy0 = 518 + (s // 4) * 38
    for i in range(70):
        t = i / 70.0
        ang = t * math.pi * 2.6 + s * 0.9
        rr = 27 - t * 10
        x = int(cx0 + math.cos(ang) * rr * 1.35)
        y = int(cy0 + math.sin(ang) * rr * 0.68 - t * 5)
        thick_point(x, y, 4, *NOODLE_D, 0.9)
        thick_point(x, y - 2, 3, *NOODLE, 0.95)
        thick_point(x, y - 3, 1, 255, 230, 158, 0.7)

# ---------------------------------------------------------------- chashu
def chashu(cx, cy, rad, rot):
    # Seared rolled pork: oval slice, caramelised outer rim, a pale fat
    # ring, roasted rosy meat, a rolled-pork swirl, sear marks, gloss.
    rx, ry = rad, int(rad * 0.82)
    fill_ellipse(cx, cy, rx, ry, 122, 58, 30)                        # caramelised rim
    fill_ellipse(cx, cy, int(rx * 0.90), int(ry * 0.90), 206, 158, 118)  # pale fat ring
    fill_ellipse(cx, cy, int(rx * 0.80), int(ry * 0.80), 176, 86, 58)    # roasted meat
    fill_ellipse(cx, cy, int(rx * 0.62), int(ry * 0.62), 218, 132, 102)  # pale rosy centre
    # rolled-pork swirl: dark spiral arc inside the centre
    for i in range(46):
        t = i / 46.0
        ang = rot + t * math.pi * 3.4
        rr = 0.10 + t * 0.48
        x = int(cx + math.cos(ang) * rx * rr)
        y = int(cy + math.sin(ang) * ry * rr)
        thick_point(x, y, 3, 148, 64, 42, 0.9)
    # fat marbling: thin cream arcs
    for k in range(3):
        a0 = rot + 1.1 + k * 2.1
        for i in range(20):
            t = i / 20.0
            ang = a0 + t * 0.8
            x = int(cx + math.cos(ang) * rad * (0.42 + 0.11 * k))
            y = int(cy + math.sin(ang) * rad * (0.42 + 0.11 * k) * 0.82)
            thick_point(x, y, 2, 246, 228, 208, 0.85)
    # dark sear marks across the top
    for k in range(4):
        ang = rot + 0.6 + k * 0.5
        x0 = int(cx + math.cos(ang) * rad * 0.55)
        y0 = int(cy + math.sin(ang) * rad * 0.55)
        x1 = int(cx + math.cos(ang + 0.35) * rad * 0.55)
        y1 = int(cy + math.sin(ang + 0.35) * rad * 0.55)
        thick_line(x0, y0, x1, y1, 4, 96, 42, 24, 0.85)
    # caramelised edge flecks on the rim
    for k in range(16):
        ang = rot + k * 0.4
        x = int(cx + math.cos(ang) * rx * 0.95)
        y = int(cy + math.sin(ang) * ry * 0.95)
        disc(x, y, 5, 92, 40, 20, 0.85)
    # glossy highlight
    fill_ellipse(cx - rad // 3, cy - rad // 3, rad // 4, int(rad * 0.20),
                 255, 208, 165, 0.55)


chashu(655, 625, 103, 0.4)
chashu(745, 703, 87, 1.8)
chashu(566, 714, 78, 3.0)

# ---------------------------------------------------------------- egg halves
def egg(cx, cy, rx, ry, yolk_r):
    fill_ellipse(cx, cy, rx, ry, 250, 244, 230)
    fill_ellipse(cx, cy, rx - 6, ry - 6, 255, 250, 238)
    disc(cx, cy, yolk_r, 238, 128, 26)
    disc(cx, cy, int(yolk_r * 0.72), 252, 158, 52)
    disc(cx - yolk_r // 3, cy - yolk_r // 3, max(3, yolk_r // 4),
         255, 214, 120, 0.95)
    # soft white shading
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if in_ellipse(x, y, cx, cy, rx, ry) and y > cy + ry * 0.4:
                blend_px(x, y, 210, 200, 185, 0.25)


egg(387, 647, 87, 69, 38)
egg(465, 759, 81, 63, 35)

# ---------------------------------------------------------------- scallions
for (sx, sy, sr) in [(308, 457, 15), (364, 434, 12), (566, 457, 13),
                     (723, 434, 11), (823, 558, 13), (275, 580, 12),
                     (868, 647, 11), (521, 826, 12), (655, 826, 13),
                     (342, 714, 10), (790, 737, 12), (476, 457, 11)]:
    disc(sx, sy, sr, 34, 122, 44)
    disc(sx, sy, int(sr * 0.62), 96, 196, 74)
    disc(sx - 2, sy - 2, int(sr * 0.3), 190, 240, 150, 0.9)

# ---------------------------------------------------------------- menma (bamboo shoots)
for (mx, my, ang) in [(308, 625, 0.5), (342, 670, 0.35), (835, 602, -0.4)]:
    x0 = int(mx - math.cos(ang) * 42)
    y0 = int(my - math.sin(ang) * 42)
    x1 = int(mx + math.cos(ang) * 42)
    y1 = int(my + math.sin(ang) * 42)
    thick_line(x0, y0, x1, y1, 11, 196, 138, 52)
    thick_line(x0, y0 - 3, x1, y1 - 3, 6, 232, 178, 92)

# ---------------------------------------------------------------- nori
# Dark green-black sheet standing at the back-right of the bowl.
nori_pts = [(801, 300), (891, 322), (877, 513), (794, 490)]
for y in range(300, 514):
    t = (y - 300) / 214.0
    xl = int(801 + (794 - 801) * t)
    xr = int(891 + (877 - 891) * t)
    for x in range(xl, xr + 1):
        n = (det(x // 2, y // 2, 5) - 0.5) * 22
        # subtle vertical sheen: nori is glossy, catches light on one side
        sheen = 26 * math.exp(-((x - xl - 12) ** 2) / 90.0)
        blend_px(x, y, clamp(20 + n + sheen), clamp(42 + n + sheen),
                 clamp(24 + n + sheen * 0.7), 0.96)
        if det(x, y, 9) < 0.08:
            blend_px(x, y, 66, 104, 60, 0.55)
# nori edge highlight
thick_line(801, 300, 891, 322, 3, 96, 140, 84, 0.8)
# nori bottom edge dips into the broth: dark wet rim
thick_line(794, 490, 877, 513, 4, 10, 22, 12, 0.7)

# ---------------------------------------------------------------- chopsticks
# Two wooden chopsticks resting diagonally across the bowl rim.
for (ox, oy) in [(0, 0), (0, 26)]:
    x0, y0 = 222 + ox, 378 + oy
    x1, y1 = 834 + ox, 266 + oy
    thick_line(x0, y0, x1, y1, 11, 122, 74, 36)
    thick_line(x0, y0 - 3, x1, y1 - 3, 5, 178, 122, 66)
    thick_line(x0, y0 + 4, x1, y1 + 4, 4, 84, 48, 22, 0.8)

# ---------------------------------------------------------------- steam
# Soft translucent wisps rising above the bowl - strong and tall so the
# heat reads even at small size: more opacity, wider S-curves.
for w in range(9):
    bx = 330 + w * 46
    for y in range(40, 430):
        t = (430 - y) / 390.0
        cx = bx + math.sin(y * 0.016 + w * 1.7) * 42 * t
        width = 34 + 40 * t
        a = 0.45 * (1 - t * 0.4)
        for x in range(int(cx - width), int(cx + width) + 1):
            d = abs(x - cx) / width
            if d < 1.0:
                blend_px(x, y, 255, 250, 244, a * (1 - d) * (0.7 + 0.3 * det(x // 6, y // 6, w)))

# ---------------------------------------------------------------- light & vignette
for y in range(H):
    for x in range(W):
        i = (y * W + x) * 3
        # warm directional light from upper left (stronger, warmer)
        d2 = ((x - 300) ** 2 + (y - 250) ** 2) / 520000.0
        warm = 1.0 + 0.18 * math.exp(-d2)
        # gentle vignette
        dx = (x - 512) / 512.0
        dy = (y - 512) / 512.0
        vig = 1.0 - 0.16 * (dx * dx + dy * dy)
        buf[i] = clamp(buf[i] * warm * vig + 6 * (warm - 1.0))
        buf[i + 1] = clamp(buf[i + 1] * warm * vig)
        buf[i + 2] = clamp(buf[i + 2] * warm * vig * 0.97)


# ---------------------------------------------------------------- PNG write
def write_png(path):
    def chunk(ctype, data):
        c = struct.pack(">I", len(data)) + ctype + data
        c += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        n1 = write_png(os.path.join(out_dir, "entry.png"))
        print("wrote /output/entry.png", n1, "bytes")
    except OSError as e:
        print("cannot write /output:", e)
    n2 = write_png("entry.png")
    print("wrote ./entry.png", n2, "bytes")


if __name__ == "__main__":
    main()
