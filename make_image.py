"""Build entry.png for news-image-20261124 (v3).

One-day world news front page, 1024x1024. Drawn fresh with Pillow
only; no network, no randomness, no timestamps, so repeated runs
produce identical bytes. Run: python3 make_image.py (writes
entry.png next to this file). The graded entry point main.py only
copies that committed image; it never runs this builder.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (252, 248, 238)
INK = (22, 22, 22)
RED = (176, 32, 32)
NAVY = (18, 28, 55)
TAN = (198, 170, 120)
LAND_LINE = (74, 62, 40)
GREY = (110, 108, 100)
DARK_BAR = (28, 34, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_w(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0]


def wrap_lines(draw, s, f, max_w, max_lines, label):
    """Wrap s to fit max_w; fail loudly if it needs more than max_lines."""
    words = s.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        raise AssertionError(
            "OVERFLOW %s: %d lines > %d allowed: %r" % (label, len(lines), max_lines, s)
        )
    return lines


def draw_lines(draw, lines, x, y, f, fill, pitch):
    for i, line in enumerate(lines):
        draw.text((x, y + i * pitch), line, font=f, fill=fill)


# ---------------------------------------------------------------- map
# Equirectangular: lon -168..+192 -> x 12..412, lat 84..-56 -> y 695..915.
MAP_X0, MAP_X1 = 12, 412
MAP_Y0, MAP_Y1 = 695, 915


def proj(lon, lat):
    x = MAP_X0 + (lon + 168.0) * (MAP_X1 - MAP_X0) / 360.0
    y = MAP_Y0 + (84.0 - lat) * (MAP_Y1 - MAP_Y0) / 140.0
    return (x, y)


# Simplified continent outlines as (lon, lat) loops. Deliberately
# coarse: at 400 px wide the shapes read as continents, which is
# what the front page needs.
LAND = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 73), (-95, 80), (-80, 73),
     (-65, 62), (-55, 47), (-65, 44), (-70, 42), (-76, 35), (-80, 32),
     (-84, 30), (-90, 29), (-97, 26), (-104, 22), (-97, 16), (-88, 13),
     (-82, 9), (-86, 14), (-94, 17), (-102, 20), (-110, 24), (-117, 30),
     (-124, 40), (-124, 48), (-132, 56), (-148, 60), (-162, 58),
     (-168, 66)],
    # Greenland
    [(-55, 60), (-42, 60), (-32, 66), (-22, 70), (-28, 76), (-48, 76),
     (-58, 72), (-55, 60)],
    # South America
    [(-80, 9), (-76, 4), (-71, 0), (-64, -4), (-52, -4), (-42, -8),
     (-36, -13), (-39, -22), (-47, -28), (-54, -35), (-62, -41),
     (-68, -50), (-70, -55), (-74, -48), (-73, -36), (-72, -24),
     (-78, -16), (-80, -8), (-80, 9)],
    # Europe
    [(-10, 36), (-2, 37), (4, 38), (10, 38), (18, 40), (26, 38),
     (30, 36), (28, 41), (24, 45), (19, 45), (14, 45), (10, 44),
     (6, 43), (2, 43), (-2, 46), (-4, 48), (-8, 50), (-4, 54),
     (-1, 57), (3, 59), (6, 61), (10, 63), (16, 66), (24, 69),
     (30, 70), (36, 68), (30, 65), (26, 62), (21, 58), (18, 55),
     (12, 54), (8, 57), (4, 58), (0, 54), (-4, 51), (-8, 47),
     (-10, 43), (-10, 36)],
    # Africa
    [(-10, 35), (-2, 35), (6, 37), (12, 34), (20, 32), (28, 31),
     (32, 28), (36, 24), (40, 20), (43, 12), (50, 11), (46, 6),
     (41, 0), (38, -6), (34, -12), (30, -18), (26, -26), (20, -32),
     (16, -35), (12, -30), (8, -26), (4, -20), (0, -14), (-4, -6),
     (-8, 2), (-13, 8), (-16, 12), (-12, 20), (-10, 28), (-10, 35)],
    # Asia (mainland)
    [(30, 70), (38, 68), (46, 70), (56, 71), (66, 72), (76, 73),
     (86, 74), (96, 76), (106, 76), (116, 73), (126, 72), (136, 72),
     (146, 71), (156, 70), (166, 67), (178, 65), (178, 60), (168, 60),
     (158, 58), (150, 59), (142, 55), (138, 50), (132, 44), (127, 39),
     (122, 37), (120, 31), (116, 24), (111, 20), (108, 13), (104, 9),
     (100, 7), (96, 10), (91, 15), (87, 20), (82, 16), (77, 9),
     (73, 16), (71, 22), (66, 25), (61, 25), (56, 26), (51, 28),
     (47, 30), (42, 34), (37, 36), (33, 38), (30, 42), (30, 50),
     (30, 60), (30, 70)],
    # Australia
    [(113, -22), (118, -16), (126, -13), (132, -12), (138, -12),
     (142, -11), (146, -16), (150, -21), (153, -26), (150, -31),
     (146, -36), (141, -38), (136, -35), (131, -32), (126, -32),
     (121, -34), (116, -35), (113, -28), (113, -22)],
    # Borneo
    [(109, 1), (113, 4), (117, 6), (119, 2), (117, -2), (113, -3),
     (110, -1), (109, 1)],
    # Sumatra
    [(95, 5), (99, 2), (103, -2), (106, -5), (103, -5), (99, -1),
     (96, 2), (95, 5)],
    # Java
    [(105, -6), (110, -7), (114, -8), (114, -9), (108, -8), (105, -7),
     (105, -6)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
     (141, -7), (136, -4), (131, -2), (131, -1)],
    # Japan
    [(130, 31), (133, 34), (136, 35), (139, 37), (141, 40), (143, 43),
     (145, 44), (142, 42), (140, 38), (137, 35), (133, 33), (130, 31)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 56), (1, 52),
     (-1, 51), (-4, 50), (-5, 50)],
    # New Zealand
    [(167, -45), (169, -42), (172, -40), (175, -38), (178, -37),
     (176, -39), (173, -41), (170, -44), (167, -46), (167, -45)],
    # Madagascar
    [(44, -16), (47, -15), (50, -17), (49, -21), (46, -25), (44, -22),
     (43, -18), (44, -16)],
    # Philippines
    [(120, 18), (122, 16), (122, 12), (121, 9), (120, 12), (119, 16),
     (120, 18)],
    # Sri Lanka
    [(80, 9), (81, 7), (80, 6), (79, 8), (80, 9)],
]

# Caspian Sea, painted navy on top of the Asian landmass.
CASPIAN = [(47, 47), (51, 47), (54, 44), (53, 40), (50, 37), (47, 39),
           (46, 43), (47, 47)]


def draw_map(img, draw, pins):
    """Realistic filled-continent map with numbered pins."""
    draw.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=NAVY)
    for poly in LAND:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=TAN, outline=LAND_LINE)
    # Caspian Sea back to navy.
    draw.polygon([proj(lon, lat) for lon, lat in CASPIAN], fill=NAVY)
    # Persian Gulf notch: small navy wedge into the Arabian coast.
    gulf = [(48, 30), (52, 29), (56, 27), (54, 25), (50, 26), (48, 28)]
    draw.polygon([proj(lon, lat) for lon, lat in gulf], fill=NAVY)
    # Dashed equator.
    eq_y = proj(0, 0)[1]
    x = MAP_X0
    while x < MAP_X1:
        draw.line([(x, eq_y), (min(x + 6, MAP_X1), eq_y)], fill=(150, 160, 190), width=1)
        x += 12
    draw.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=INK, width=2)
    # Pins: red disc, white number, leader line when display != true.
    pin_f = font("DejaVuSans-Bold.ttf", 9)
    for num, (tlon, tlat, dlon, dlat) in pins:
        dx, dy = proj(dlon, dlat)
        tx, ty = proj(tlon, tlat)
        if abs(dx - tx) > 1 or abs(dy - ty) > 1:
            draw.line([(dx, dy), (tx, ty)], fill=RED, width=1)
            draw.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=RED)
        r = 7
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=RED, outline=(255, 255, 255))
        label = str(num)
        tw = text_w(draw, label, pin_f)
        draw.text((dx - tw / 2, dy - 6), label, font=pin_f, fill=(255, 255, 255))

# ---------------------------------------------------------------- content
# Every story below was checked against its own primary-source
# article for a Tuesday 24 November 2026 publication or event date.
# Aggregator timestamps were NOT trusted (see the build report).

MASTHEAD = "Tuesday 24 November 2026"
SUBLINE = ("Zaporizhzhia hit, 2 killed \u00b7 Russian jets breach Korea zone "
           "\u00b7 Estonia defies Moscow")

STATS = [
    ("2", "killed in Zaporizhzhia"),
    ("22", "wounded in Zaporizhzhia"),
    ("18", "years, Equinor\u2013VNG deal"),
    ("181", "Arya runs"),
    ("+3.9%", "Nikkei rise"),
    ("93", "Azharuddeen 93*"),
]

REGIONS = [
    ("EUROPE", 5),
    ("MIDDLE EAST", 2),
    ("AMERICAS", 4),
    ("ASIA-PACIFIC", 13),
    ("AFRICA", 6),
    ("OCEANIA", 4),
    ("WORLD", 1),
]

# Heroes: (kicker, head, sub, art kind, pin true lon/lat, pin display lon/lat)
HEROES = [
    ("UKRAINE \u00b7 EUROPE",
     "Zaporizhzhia hit, 2 killed",
     "Russian strike wounds 22, incl. 2 children, in city centre",
     "burst", (35.2, 47.8), (35.2, 47.8)),
    ("KOREA \u00b7 ASIA-PACIFIC",
     "Russian jets breach Korea zone",
     "Seoul scrambles fighters; alert on Ulleung as jets enter ADIZ",
     "contrail", (127.0, 37.5), (127.0, 37.5)),
    ("ESTONIA \u00b7 EUROPE",
     "Estonia defies Moscow",
     "Tallinn rejects Moscow\u2019s airspace claim",
     "stripes", (24.7, 59.4), (24.7, 59.4)),
]

# Smalls: (kicker, head, sub, pin true lon/lat, pin display lon/lat)
SMALLS = [
    ("INDIA \u00b7 CRICKET",
     "Amandeep\u2019s maiden ton seals win",
     "Khare\u2019s first T20 century powers chase past Goa",
     (88.4, 22.6), (88.4, 18.0)),
    ("JAPAN \u00b7 MARKETS",
     "Nikkei jumps 3.9% on Huang return",
     "Tokyo surges as Nvidia chief\u2019s comeback revives AI trade",
     (139.7, 35.7), (139.7, 35.7)),
    ("INDIA \u00b7 CRICKET",
     "Arya smashes record 181",
     "Delhi skipper\u2019s 181 is the most by an Indian in T20s",
     (75.9, 22.7), (75.9, 22.7)),
    ("NORWAY \u00b7 ENERGY",
     "Equinor signs 18-year gas deal",
     "Norway to send 15.3 TWh a year to Germany\u2019s VNG",
     (5.7, 58.9), (5.7, 58.9)),
    ("US \u00b7 DEFENCE",
     "Pentagon rebukes Canada on jets",
     "US faults Ottawa on defence spending and F-35 review",
     (-75.7, 45.4), (-75.7, 45.4)),
    ("BANGLADESH \u00b7 POLITICS",
     "Hasina plans return on Dec 16",
     "Ex-PM in exile says she will return to Dhaka next month",
     (90.4, 23.8), (96.0, 28.0)),
    ("INDIA \u00b7 CRICKET",
     "Kerala cruise past Assam",
     "Azharuddeen\u2019s 93* off 37 seals 9-wicket win",
     (76.7, 30.7), (76.7, 33.5)),
    ("US \u00b7 WEATHER",
     "California braces for king tides",
     "Coastal flood threat peaks as tides surge on Tuesday",
     (-122.4, 37.8), (-122.4, 37.8)),
    ("NEW ZEALAND \u00b7 CRICKET",
     "Tickner out of Christchurch Test",
     "Hamstring rules out seamer; Fisher called in as cover",
     (172.6, -43.5), (172.6, -43.5)),
    ("CHINA \u00b7 SPACE",
     "China unveils Shenzhou-24 crew",
     "Pakistani to be first foreigner aboard Tiangong station",
     (100.3, 40.9), (100.3, 40.9)),
]

# ALSO items 14-35, one line each.
ALSO = [
    "Boda boda riders lose 20% of pay to bribes",
    "Brentford hit Everton for four",
    "Seoul toughens exam rules after cheating",
    "Middle East crude exports trend lower",
    "Israeli strike kills 3 in southern Gaza",
    "Pepkor warns port chaos will hit trade",
    "Ghana pledges bonus after amputee Cup win",
    "Commanders edge Bengals 22-20",
    "S&P slashes Philippine growth outlook",
    "Japan enlists car firms in arms buildup",
    "Korea bank to hike rates on Thursday",
    "Bengal beat UP by 93 runs",
    "Trump to meet NATO chief Rutte Wednesday",
    "Rand steady ahead of leading indicator",
    "South Africa bowl Bangladesh for 91",
    "Australia rotate for league Cup final",
    "NATO chief vows defence on space threat",
    "Buffalo City up for grabs as ANC faces test",
    "Kiribati evacuates Kanton Island",
    "US futures climb as Asian shares mixed",
    "De Villiers: tampering \u2018started in Durban\u2019",
    "Gold Fields eyes $7.5bn for Tarkwa mine",
]

DATE_CHECK_ITEMS = [
    "Huang returns 23 Nov",
    "Libya warship 23 Nov",
    "COP31 22 Nov",
    "Dymer 23 Nov",
    "Cikande 22 Nov",
    "Liverpool 22 Nov",
    "Hormuz tankers 23 Nov",
]

SOURCES = ("Sources: Reuters \u00b7 AJU Press \u00b7 IANS \u00b7 Cricinfo \u00b7 crex "
           "\u00b7 The Standard \u00b7 Manila Times \u00b7 BBC \u00b7 AP \u00b7 eNCA "
           "\u00b7 MyJoyOnline")

MAP_CAPTION = "Thirteen stories, pinned where they happened."


def hero_art(draw, x, y, w, h, kind):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    if kind == "burst":
        cx, cy = x + w // 2, y + h // 2
        draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(198, 90, 40))
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(240, 200, 90))
        for dx, dy in ((-52, -18), (52, -18), (-52, 18), (52, 18), (0, -30), (0, 30)):
            draw.line([(cx, cy), (cx + dx, cy + dy)], fill=(240, 200, 90), width=2)
    elif kind == "contrail":
        draw.line([(x + 8, y + h - 12), (x + w - 30, y + 12)], fill=(240, 200, 90), width=3)
        draw.line([(x + 8, y + h - 12), (x + w - 70, y + h - 12)], fill=(150, 160, 190), width=2)
        draw.ellipse([x + w - 44, y + 4, x + w - 20, y + 28], fill=RED)
    else:  # stripes
        third = h // 3
        draw.rectangle([x, y, x + w, y + third], fill=(38, 70, 140))
        draw.rectangle([x, y + third, x + w, y + 2 * third], fill=(20, 20, 20))
        draw.rectangle([x, y + 2 * third, x + w, y + h], fill=(235, 235, 235))


def build():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Top bar.
    draw.rectangle([12, 11, 1012, 14], fill=RED)

    # Masthead.
    f_mast = font("DejaVuSerif-Bold.ttf", 56)
    mw = text_w(draw, MASTHEAD, f_mast)
    if mw > 1000:
        raise AssertionError("OVERFLOW masthead: %d px > 1000" % mw)
    draw.text(((W - mw) / 2, 14), MASTHEAD, font=f_mast, fill=INK)

    # Red italic subline (sheared 0.22), centred, y=98.
    f_sub = font("DejaVuSerif.ttf", 17)
    sw = text_w(draw, SUBLINE, f_sub)
    if sw > 1000:
        raise AssertionError("OVERFLOW subline: %d px > 1000" % sw)
    layer = Image.new("RGBA", (W, 34), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text(((W - sw) / 2, 2), SUBLINE, font=f_sub, fill=RED + (255,))
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0.22, 0, 0, 1, 0))
    img.paste(layer, (0, 96), layer)

    # Stat strip: six numbers with captions.
    f_stat = font("DejaVuSerif-Bold.ttf", 20)
    f_statcap = font("DejaVuSans.ttf", 8)
    col_w = 1000 / 6
    for i, (num, cap) in enumerate(STATS):
        cx = 12 + col_w * i + col_w / 2
        nw = text_w(draw, num, f_stat)
        draw.text((cx - nw / 2, 126), num, font=f_stat, fill=INK)
        cw = text_w(draw, cap, f_statcap)
        if cw > col_w - 8:
            raise AssertionError("OVERFLOW stat caption: %r" % cap)
        draw.text((cx - cw / 2, 150), cap, font=f_statcap, fill=GREY)

    # Region bar: segments sized by story count (min 70 px each).
    total = sum(c for _, c in REGIONS)
    base = 70
    rest = 1000 - base * len(REGIONS)
    widths = [base + round(rest * c / total) for _, c in REGIONS]
    widths[-1] += 1000 - sum(widths)
    f_reg = font("DejaVuSans-Bold.ttf", 9)
    x = 12
    for (name, count), seg_w in zip(REGIONS, widths):
        draw.rectangle([x, 168, x + seg_w, 188], fill=DARK_BAR)
        label = "%s %d" % (name, count)
        lw = text_w(draw, label, f_reg)
        if lw > seg_w - 6:
            raise AssertionError("OVERFLOW region label: %r" % label)
        draw.text((x + (seg_w - lw) / 2, 173), label, font=f_reg, fill=(255, 255, 255))
        x += seg_w

    # Heroes: three columns.
    f_hkick = font("DejaVuSans-Bold.ttf", 9)
    f_hhead = font("DejaVuSerif-Bold.ttf", 26)
    f_hsub = font("DejaVuSerif.ttf", 11)
    hero_xs = [12, 352, 692]
    hero_w = 320
    for (kicker, head, sub, kind, _t, _d), hx in zip(HEROES, hero_xs):
        draw.line([(hx, 200), (hx + hero_w, 200)], fill=RED, width=2)
        draw.text((hx, 208), kicker, font=f_hkick, fill=RED)
        head_lines = wrap_lines(draw, head, f_hhead, hero_w, 3, "hero head")
        draw_lines(draw, head_lines, hx, 226, f_hhead, INK, 30)
        sub_y = 226 + len(head_lines) * 30 + 8
        sub_lines = wrap_lines(draw, sub, f_hsub, hero_w, 2, "hero sub")
        draw_lines(draw, sub_lines, hx, sub_y, f_hsub, INK, 14)
        art_y = sub_y + len(sub_lines) * 14 + 12
        art_h = 445 - art_y
        if art_h < 40:
            raise AssertionError("OVERFLOW hero art too short: %d px" % art_h)
        hero_art(draw, hx, art_y, hero_w, art_h, kind)
        draw.line([(hx, 448), (hx + hero_w, 448)], fill=GREY, width=1)

    # Smalls: two rows x five columns.
    f_skick = font("DejaVuSans-Bold.ttf", 8)
    f_shead = font("DejaVuSerif-Bold.ttf", 15)
    f_ssub = font("DejaVuSerif.ttf", 9)
    col_xs = [12, 214, 416, 618, 820]
    col_w = 192
    row_ys = [(457, 470, 501), (605, 618, 649)]
    for row_i, (ky, hy, sy) in enumerate(row_ys):
        for col_i, cx in enumerate(col_xs):
            idx = row_i * 5 + col_i
            kicker, head, sub, _t, _d = SMALLS[idx]
            draw.text((cx, ky), kicker, font=f_skick, fill=RED)
            head_lines = wrap_lines(draw, head, f_shead, col_w, 2, "small head")
            draw_lines(draw, head_lines, cx, hy, f_shead, INK, 16)
            sub_lines = wrap_lines(draw, sub, f_ssub, col_w, 3, "small sub")
            draw_lines(draw, sub_lines, cx, sy, f_ssub, INK, 10)

    # Map (left) with the 13 pins: 3 heroes + 10 smalls.
    pins = []
    for i, (_k, _h, _s, _kind, t, d) in enumerate(HEROES, start=1):
        pins.append((i, (t[0], t[1], d[0], d[1])))
    for j, (_k, _h, _s, t, d) in enumerate(SMALLS, start=4):
        pins.append((j, (t[0], t[1], d[0], d[1])))
    draw_map(img, draw, pins)
    f_cap = font("DejaVuSerif.ttf", 10)
    # Italic caption via the same shear trick, small factor.
    cap_w = text_w(draw, MAP_CAPTION, f_cap)
    cap_layer = Image.new("RGBA", (MAP_X1 - MAP_X0 + 40, 22), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cap_layer)
    cd.text(((cap_layer.width - cap_w) / 2, 1), MAP_CAPTION, font=f_cap, fill=INK + (255,))
    cap_layer = cap_layer.transform(cap_layer.size, Image.AFFINE, (1, 0.15, 0, 0, 1, 0))
    img.paste(cap_layer, (MAP_X0 - 20, 915), cap_layer)

    # ALSO: 22 one-liners in two columns beside the map.
    f_also_h = font("DejaVuSans-Bold.ttf", 10)
    f_also_n = font("DejaVuSans-Bold.ttf", 10)
    f_also = font("DejaVuSerif.ttf", 10)
    draw.text((430, 695), "ALSO", font=f_also_h, fill=INK)
    draw.line([(430, 712), (1012, 712)], fill=GREY, width=1)
    also_cols = [(430, 285), (730, 282)]
    for half in range(2):
        cx, cw = also_cols[half]
        for r in range(11):
            idx = half * 11 + r
            num = 14 + idx
            item = ALSO[idx]
            y = 720 + r * 18
            nlabel = "%d." % num
            nw = text_w(draw, nlabel, f_also_n)
            draw.text((cx, y), nlabel, font=f_also_n, fill=RED)
            lines = wrap_lines(draw, item, f_also, cw - nw - 6, 1, "also %d" % num)
            draw.text((cx + nw + 4, y), lines[0], font=f_also, fill=INK)

    # DATE CHECK box, y=930..975.
    draw.rectangle([12, 930, 1012, 975], outline=RED, width=2)
    f_dc_h = font("DejaVuSans-Bold.ttf", 10)
    f_dc = font("DejaVuSerif.ttf", 9)
    draw.text((22, 937), "DATE CHECK \u2014 NOT 24 NOVEMBER NEWS:", font=f_dc_h, fill=RED)
    dc_line = " \u00b7 ".join(DATE_CHECK_ITEMS)
    dc_lines = wrap_lines(draw, dc_line, f_dc, 980, 1, "date check")
    draw.text((22, 954), dc_lines[0], font=f_dc, fill=INK)

    # Sources line.
    f_src = font("DejaVuSans.ttf", 8)
    sw = text_w(draw, SOURCES, f_src)
    if sw > 1000:
        raise AssertionError("OVERFLOW sources: %d px > 1000" % sw)
    draw.text(((W - sw) / 2, 996), SOURCES, font=f_src, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    return out


if __name__ == "__main__":
    print(build())
