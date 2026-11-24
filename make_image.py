#!/usr/bin/env python3
"""Draw one front page that sums up Tuesday 24 November 2026.

Every story on the page happened, or was first reported, on
24 November 2026. The page is drawn with Pillow only: no pictures
are downloaded and no network is touched. Each headline, caption
and list item is measured before it is drawn, and the build stops
with an OVERFLOW error instead of printing a clipped page.

Layout (1024 x 1024, cream paper):
  top bar, masthead, red subline, stat strip, region bar,
  three lead stories, ten small leads in two rows, a realistic
  world map with thirteen numbered pins beside a 22-item ALSO
  column, a red DATE CHECK box naming the big stories that
  belong to an earlier day, and a sources line.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
CREAM = (250, 244, 230)
INK = (30, 30, 30)
RED = (178, 34, 34)
TAN = (198, 170, 120)
NAVY = (18, 28, 55)
GREY = (110, 110, 110)
WHITE = (255, 255, 255)
LAND_EDGE = (70, 55, 30)
SOFT = (235, 226, 200)
GOLD = (212, 160, 40)
STEEL = (40, 80, 140)
SLATE = (52, 58, 74)
ORANGE = (214, 110, 30)

# ---------------------------------------------------------------- geometry
W = 1024
H = 1024
MX = 12
RX = 1012
MAP_X0, MAP_X1 = 12, 412
MAP_Y0, MAP_Y1 = 695, 915
HERO_X = [12, 350, 688]
HERO_W = 312
SMALL_X = [12, 214, 416, 618, 820]
SMALL_W = 190
ALSO_COLS = [(420, 280), (712, 298)]

# ---------------------------------------------------------------- fonts
_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/dejavu/",
]


def load_font(name, size):
    for folder in _FONT_DIRS:
        path = os.path.join(folder, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.truetype(name, size)


def text_w(d, text, font):
    return d.textlength(text, font=font)


def one_line(d, text, font, maxw, what):
    got = text_w(d, text, font)
    if got > maxw:
        raise AssertionError(
            "OVERFLOW %s: %.1fpx, max %d" % (what, got, maxw)
        )


def wrap_lines(d, text, font, maxw, maxlines, what):
    words = text.split()
    lines = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(d, trial, font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if len(lines) > maxlines:
        raise AssertionError(
            "OVERFLOW %s: %d lines, max %d" % (what, len(lines), maxlines)
        )
    for line in lines:
        one_line(d, line, font, maxw, what)
    return lines


def italic_layer(text, font, fill, shear=0.22):
    """Render text on its own layer, then slant it geometrically."""
    probe = Image.new("RGBA", (10, 10))
    pd = ImageDraw.Draw(probe)
    tw = int(text_w(pd, text, font)) + 4
    th = font.size + 8
    layer = Image.new("RGBA", (tw + int(shear * th) + 4, th), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((2, 2), text, font=font, fill=fill + (255,))
    layer = layer.transform(
        layer.size,
        Image.AFFINE,
        (1, -shear, shear * th, 0, 1, 0),
        resample=Image.BICUBIC,
    )
    return layer


# ---------------------------------------------------------------- content
TOP_BAR = "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
MASTHEAD = "Tuesday 24 November 2026"
SUBLINE = "Zaporizhzhia hit, 2 killed \u00b7 Three tankers ablaze in Hormuz \u00b7 Estonia defies Moscow"

STATS = [
    ("2", "killed in Zaporizhzhia strike"),
    ("22", "wounded in Zaporizhzhia"),
    ("3", "tankers ablaze in Hormuz"),
    ("181", "Arya's record T20 score"),
    ("+3.9%", "Nikkei rallies on Huang"),
    ("29", "killed in Nigeria boat tragedy"),
]

# (label, count, cell width)
REGIONS = [
    ("EUROPE", 5, 210),
    ("MIDDLE EAST", 6, 105),
    ("AMERICAS", 4, 158),
    ("ASIA-PACIFIC", 10, 262),
    ("AFRICA", 4, 105),
    ("OCEANIA", 3, 80),
    ("WORLD", 3, 80),
]

# (number, region, head, sub, art kind)
HEROES = [
    (1, "EUROPE", "Russian strike kills 2 in Zaporizhzhia",
     "Moscow's attack wounds 22 in the city; Kyiv says it came as peace talks stall.",
     "blast"),
    (2, "MIDDLE EAST", "Three tankers ablaze in Hormuz",
     "Ships hit mines in the strait, Guards say; oil jumps as crews are rescued.",
     "ship"),
    (3, "EUROPE", "Estonia defies Moscow on airspace",
     "Tallinn rejects Russia's claim after its warning; NATO allies back the denial.",
     "shield"),
]

# (number, region, head, sub, art kind)
SMALLS = [
    (4, "MIDDLE EAST", "Netanyahu urges Trump to hit Iran",
     "Israeli PM presses US for fresh strikes amid Gulf strain.", "flag"),
    (5, "ASIA-PACIFIC", "Russian jets breach Korea zone",
     "Seoul scrambles fighters; alert sounded for Ulleung Island.", "jet"),
    (6, "ASIA-PACIFIC", "Nikkei rallies on Huang's return",
     "Tokyo jumps 3.9% as Nvidia chief's comeback revives AI trade.", "bars"),
    (7, "ASIA-PACIFIC", "Arya smashes record 181",
     "India opener's 181 in Indore sets a new T20I benchmark.", "ball"),
    (8, "AMERICAS", "Pentagon rebukes Canada on jets",
     "US slams Ottawa over defence spending and F-35 review.", "shield"),
    (9, "ASIA-PACIFIC", "Hasina seeks return to Dhaka",
     "Ousted PM eyes Dec 16 homecoming, aide tells Reuters.", "flag"),
    (10, "AFRICA", "Nigeria boat toll rises to 29",
     "Bayelsa tragedy deepens as more bodies are recovered.", "boat"),
    (11, "AMERICAS", "California braces for flood threat",
     "King tides and El Ni\u00f1o rains threaten triple flooding.", "waves"),
    (12, "MIDDLE EAST", "Qatar PM pushes Iran diplomacy",
     "Doha seeks to restart US\u2013Iran talks after Rubio meeting.", "doc"),
    (13, "OCEANIA", "Fiji shuts schools for five days",
     "El Ni\u00f1o drought closes every school across the islands.", "house"),
]

# (number, region, brief) — first 11 go in column one, rest in column two
ALSO = [
    (14, "EUROPE", "Two diplomats expelled in spy row"),
    (15, "EUROPE", "Brentford thrash Everton 4-0"),
    (16, "EUROPE", "Woman found stabbed near Blaina"),
    (17, "MIDDLE EAST", "Iran vows wider reply to US"),
    (18, "MIDDLE EAST", "US hits Iran shadow banks"),
    (19, "MIDDLE EAST", "Iran vows to beat US blockade"),
    (20, "AMERICAS", "DNA solves 1968 Ontario murder"),
    (21, "AMERICAS", "Commanders edge Bengals 22-20"),
    (22, "ASIA-PACIFIC", "China sentences spy to death"),
    (23, "ASIA-PACIFIC", "Japan enlists car firms in arms"),
    (24, "ASIA-PACIFIC", "Korea bank to hike rates"),
    (25, "ASIA-PACIFIC", "Bengal beat UP by 93 runs"),
    (26, "ASIA-PACIFIC", "India 3rd in Asia Power Index"),
    (27, "ASIA-PACIFIC", "India\u2013NZ Wellington Test drawn"),
    (28, "AFRICA", "South Africa bowl Bangladesh for 91"),
    (29, "AFRICA", "Ghana backs two-year BECE ban"),
    (30, "AFRICA", "Tullow cuts forecast on Ghana tax"),
    (31, "OCEANIA", "Coalition opposes Vanuatu treaty deal"),
    (32, "OCEANIA", "Kiribati's Kanton Island evacuated"),
    (33, "WORLD", "Ethereum funds see $131M outflows"),
    (34, "WORLD", "Google cuts agent hijacking to 0.9%"),
    (35, "WORLD", "Gemini 4 finds cheaper quantum code"),
]

MAP_CAPTION = "Thirteen stories, pinned where they happened."
DATE_CHECK_TITLE = "DATE CHECK \u2014 NOT TODAY"
DATE_CHECK_ROWS = [
    "Nvidia brings back Huang (23 Nov) \u00b7 Ukraine sinks warship off Libya (23 Nov) \u00b7 COP31 collapses (22 Nov)",
    "Dymer toll hits 11 (23 Nov) \u00b7 Cikande fire toll 24 (22 Nov) \u00b7 Liverpool 4-0 Man Utd (22 Nov)",
]
SOURCES = "Sources: Reuters, Starlit Daily, TBS News, ESPNcricinfo, IANS, AP, AFP, BBC"

# ---------------------------------------------------------------- map data
# Land polygons as (lon, lat) lists; drawn filled tan on a navy ocean.
# Eurasia is a single polygon so no seam shows between Europe and Asia.
NORTH_AMERICA = [(-168, 66), (-160, 59), (-152, 59), (-143, 60), (-134, 57), (-129, 53), (-125, 48), (-124, 42), (-120, 35), (-114, 30), (-109, 24), (-105, 20), (-98, 16), (-92, 14), (-86, 12), (-82, 9), (-79, 8), (-81, 12), (-85, 16), (-88, 20), (-91, 19), (-95, 19), (-97, 25), (-95, 29), (-90, 29), (-84, 30), (-81, 26), (-80, 31), (-77, 34), (-75, 38), (-73, 41), (-69, 43), (-65, 44), (-60, 46), (-56, 49), (-59, 53), (-63, 58), (-67, 59), (-71, 61), (-77, 62), (-83, 65), (-89, 66), (-95, 68), (-102, 68), (-110, 68), (-118, 69), (-126, 70), (-134, 70), (-142, 70), (-150, 70), (-158, 71), (-166, 69), (-168, 66)]
GREENLAND = [(-55, 60), (-48, 60), (-42, 61), (-40, 64), (-32, 68), (-25, 70), (-20, 72), (-20, 76), (-25, 80), (-32, 80), (-40, 79), (-50, 77), (-58, 74), (-60, 70), (-58, 66), (-55, 60)]
SOUTH_AMERICA = [(-79, 9), (-77, 5), (-78, 0), (-81, -4), (-80, -7), (-77, -12), (-73, -16), (-70, -19), (-70, -23), (-70, -28), (-72, -33), (-73, -38), (-73, -44), (-74, -48), (-73, -52), (-69, -54), (-66, -55), (-65, -50), (-63, -45), (-61, -40), (-58, -35), (-54, -34), (-51, -31), (-48, -28), (-44, -23), (-41, -22), (-39, -17), (-37, -13), (-35, -9), (-35, -6), (-38, -4), (-41, -3), (-44, -2), (-47, -1), (-50, 0), (-52, 4), (-55, 6), (-58, 8), (-62, 9), (-66, 10), (-70, 11), (-74, 11), (-77, 10), (-79, 9)]
EURASIA = [(-10, 36), (-9, 43), (-2, 48), (2, 51), (6, 54), (8, 57), (6, 60), (10, 62), (14, 66), (19, 69), (26, 71), (32, 70), (40, 68), (48, 68), (56, 69), (64, 70), (72, 72), (80, 73), (88, 75), (96, 76), (104, 77), (112, 74), (120, 73), (128, 71), (136, 71), (144, 72), (152, 70), (160, 69), (168, 66), (178, 65), (178, 62), (170, 60), (162, 56), (158, 51), (150, 59), (142, 55), (140, 47), (135, 43), (130, 42), (127, 40), (122, 38), (120, 34), (121, 30), (118, 25), (113, 22), (109, 19), (106, 10), (103, 8), (100, 7), (98, 10), (94, 16), (91, 22), (88, 22), (85, 20), (82, 17), (80, 13), (77, 8), (74, 13), (72, 20), (69, 22), (66, 25), (62, 25), (58, 25), (56, 27), (54, 28), (52, 29), (50, 30), (48, 30), (49, 29), (51, 28), (53, 27), (55, 26), (56, 25), (57, 24), (58, 22), (59, 20), (57, 18), (54, 16), (51, 15), (48, 14), (45, 13), (43, 12), (41, 13), (39, 15), (37, 17), (35, 20), (34, 23), (35, 26), (34, 28), (35, 31), (36, 34), (36, 36), (33, 36), (30, 36), (27, 37), (24, 36), (22, 37), (23, 39), (21, 40), (19, 42), (18, 40), (16, 40), (14, 42), (12, 45), (10, 44), (7, 44), (4, 43), (2, 41), (0, 39), (-2, 37), (-5, 36), (-9, 38)]
AFRICA = [(-6, 35), (-10, 31), (-13, 28), (-16, 24), (-17, 20), (-17, 15), (-16, 12), (-13, 8), (-8, 5), (-4, 5), (0, 6), (4, 6), (6, 4), (8, 4), (9, 2), (9, -1), (12, -5), (13, -9), (12, -13), (13, -17), (12, -21), (14, -26), (16, -29), (18, -32), (19, -34), (22, -34), (25, -34), (28, -33), (31, -29), (33, -26), (35, -24), (36, -21), (38, -18), (40, -15), (40, -12), (41, -8), (42, -4), (43, -1), (45, 0), (47, 2), (49, 5), (51, 10), (51, 12), (48, 12), (44, 12), (42, 14), (40, 16), (38, 19), (37, 22), (35, 25), (34, 28), (33, 29), (32, 31), (30, 31), (27, 32), (24, 32), (21, 33), (18, 33), (15, 32), (12, 34), (10, 34), (8, 35), (5, 36), (2, 36), (0, 36), (-3, 35), (-6, 35)]
AUSTRALIA = [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (151, -24), (149, -20), (146, -19), (143, -15), (142, -11), (141, -13), (139, -17), (136, -15), (135, -12), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)]
NEW_GUINEA = [(131, -1), (133, -2), (136, -2), (138, -3), (141, -3), (144, -4), (146, -6), (148, -8), (150, -10), (147, -9), (144, -8), (141, -8), (138, -7), (135, -5), (132, -3), (131, -1)]
BORNEO = [(109, 0), (110, 1), (112, 3), (114, 5), (116, 6), (118, 2), (117, -1), (116, -3), (114, -3), (111, -3), (109, -1), (109, 0)]
SUMATRA = [(95, 5), (97, 4), (99, 1), (101, -1), (103, -3), (105, -5), (106, -6), (104, -5), (102, -3), (100, 0), (98, 2), (96, 4), (95, 5)]
JAVA = [(105, -6), (108, -7), (110, -7), (112, -7), (114, -8), (114, -9), (112, -8), (110, -8), (108, -8), (106, -7), (105, -6)]
MADAGASCAR = [(44, -16), (46, -15), (49, -14), (50, -16), (49, -19), (47, -22), (45, -25), (44, -25), (43, -22), (43, -19), (44, -16)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (0, 50), (-3, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36), (141, 38), (141, 40), (141, 42), (142, 44), (144, 44), (145, 43), (143, 42), (141, 40), (140, 38), (139, 36), (137, 35), (135, 34), (133, 33), (131, 32), (130, 31)]
NZ_NORTH = [(173, -35), (175, -37), (177, -38), (178, -38), (176, -40), (175, -41), (174, -41), (173, -39), (173, -37)]
NZ_SOUTH = [(168, -44), (170, -43), (172, -42), (174, -41), (173, -43), (171, -45), (169, -46), (167, -46), (167, -45)]
ICELAND = [(-22, 64), (-20, 63), (-16, 64), (-14, 64), (-15, 66), (-18, 66), (-22, 65), (-22, 64)]

LAND = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, EURASIA, AFRICA,
        AUSTRALIA, NEW_GUINEA, BORNEO, SUMATRA, JAVA, MADAGASCAR,
        BRITAIN, JAPAN, NZ_NORTH, NZ_SOUTH, ICELAND]

# Inland seas painted navy on top of the land.
CASPIAN = [(47, 47), (49, 47), (51, 46), (52, 44), (53, 42), (52, 40), (51, 38), (50, 37), (48, 37), (47, 39), (46, 42), (47, 45)]
BLACK_SEA = [(28, 41), (31, 41), (34, 42), (37, 43), (39, 44), (41, 46), (41, 47), (39, 46), (36, 45), (33, 44), (30, 43), (28, 42)]

# (story number, lon, lat, display nudge dx, dy in pixels; 0,0 = true spot)
# Pins 1-13 are the three heroes plus the ten small leads, in story order.
PINS = [
    (1, 35.12, 47.85, 0, 0),      # Zaporizhzhia
    (2, 56.5, 26.5, 19, 10),      # Strait of Hormuz
    (3, 24.75, 59.44, 0, 0),      # Tallinn
    (4, 51.39, 35.69, 0, 0),      # Tehran
    (5, 126.98, 37.57, 0, 0),     # Seoul
    (6, 139.69, 35.68, 14, 11),   # Tokyo
    (7, 75.86, 22.72, 0, 0),      # Indore
    (8, -75.70, 45.42, 0, 0),     # Ottawa
    (9, 90.41, 23.81, 15, 10),    # Dhaka
    (10, 6.3, 4.9, 0, 0),         # Bayelsa, Nigeria
    (11, -120.0, 37.0, 0, 0),     # California
    (12, 51.53, 25.29, -18, 15),  # Doha
    (13, 178.0, -17.7, 0, 0),     # Fiji
]


def project(lon, lat):
    """Equirectangular: lon -168..+192 -> x, lat 84..-56 -> y."""
    x = MAP_X0 + (lon + 168) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (84 - lat) / 140.0 * (MAP_Y1 - MAP_Y0)
    return x, y


# ---------------------------------------------------------------- icons
def draw_icon(d, kind, cx, cy, s, color):
    """One simple geometric motif, centred on (cx, cy), size s."""
    h = s / 2.0
    if kind == "flag":
        d.line([(cx - h * 0.6, cy + h), (cx - h * 0.6, cy - h)], fill=color, width=3)
        d.polygon([(cx - h * 0.6, cy - h), (cx + h * 0.8, cy - h * 0.55),
                   (cx - h * 0.6, cy - h * 0.1)], fill=color)
    elif kind == "jet":
        d.polygon([(cx + h, cy), (cx - h * 0.7, cy - h * 0.45),
                   (cx - h * 0.3, cy), (cx - h * 0.7, cy + h * 0.45)], fill=color)
        d.line([(cx - h * 0.7, cy - h * 0.7), (cx - h * 0.2, cy - h * 0.1)], fill=color, width=2)
        d.line([(cx - h * 0.7, cy + h * 0.7), (cx - h * 0.2, cy + h * 0.1)], fill=color, width=2)
    elif kind == "bars":
        for i, f in enumerate((0.45, 0.7, 1.0)):
            bx = cx - h + i * (2 * h / 3.0)
            d.rectangle([bx, cy + h - f * 2 * h, bx + h * 0.45, cy + h], fill=color)
    elif kind == "ball":
        d.ellipse([cx - h, cy - h, cx + h, cy + h], fill=color)
        d.arc([cx - h, cy - h, cx + h, cy + h], 200, 340, fill=WHITE, width=2)
        d.arc([cx - h, cy - h, cx + h, cy + h], 20, 160, fill=WHITE, width=2)
    elif kind == "shield":
        d.polygon([(cx - h * 0.8, cy - h), (cx + h * 0.8, cy - h),
                   (cx + h * 0.8, cy), (cx, cy + h),
                   (cx - h * 0.8, cy)], fill=color)
        r = h * 0.32
        d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=WHITE)
    elif kind == "boat":
        d.polygon([(cx - h, cy + h * 0.2), (cx + h, cy + h * 0.2),
                   (cx + h * 0.6, cy + h * 0.8), (cx - h * 0.6, cy + h * 0.8)], fill=color)
        d.line([(cx, cy + h * 0.2), (cx, cy - h)], fill=color, width=3)
        d.polygon([(cx, cy - h), (cx + h * 0.55, cy - h * 0.6),
                   (cx, cy - h * 0.2)], fill=color)
    elif kind == "waves":
        for j, yy in enumerate((-0.5, 0.0, 0.5)):
            pts = []
            for k in range(9):
                px = cx - h + k * (2 * h / 8.0)
                py = cy + yy * h + (h * 0.18 if k % 2 == 0 else -h * 0.18)
                pts.append((px, py))
            d.line(pts, fill=color, width=3)
    elif kind == "house":
        d.rectangle([cx - h * 0.7, cy - h * 0.1, cx + h * 0.7, cy + h], fill=color)
        d.polygon([(cx - h * 0.9, cy - h * 0.1), (cx + h * 0.9, cy - h * 0.1),
                   (cx, cy - h)], fill=color)
        d.rectangle([cx - h * 0.18, cy + h * 0.3, cx + h * 0.18, cy + h], fill=WHITE)
    elif kind == "doc":
        d.rectangle([cx - h * 0.6, cy - h, cx + h * 0.6, cy + h], outline=color, width=3)
        for j, yy in enumerate((-0.5, 0.0, 0.5)):
            d.line([(cx - h * 0.35, cy + yy * h), (cx + h * 0.35, cy + yy * h)],
                   fill=color, width=2)
    elif kind == "ship":
        d.polygon([(cx - h, cy + h * 0.1), (cx + h, cy + h * 0.1),
                   (cx + h * 0.7, cy + h * 0.7), (cx - h * 0.7, cy + h * 0.7)], fill=color)
        d.rectangle([cx - h * 0.2, cy - h * 0.5, cx + h * 0.1, cy + h * 0.1], fill=color)
        d.polygon([(cx - h * 0.05, cy - h), (cx + h * 0.3, cy - h * 0.4),
                   (cx - h * 0.05, cy - h * 0.3)], fill=ORANGE)
    elif kind == "blast":
        for k in range(8):
            ang = k * 3.14159 / 4.0
            reach = 1.0 if k % 2 == 0 else 0.55
            tipx = cx + h * 0.95 * math.cos(ang) * reach
            tipy = cy + h * 0.95 * math.sin(ang) * reach
            base1 = cx + h * 0.3 * math.cos(ang + 0.5)
            base2 = cy + h * 0.3 * math.sin(ang + 0.5)
            base3 = cx + h * 0.3 * math.cos(ang - 0.5)
            base4 = cy + h * 0.3 * math.sin(ang - 0.5)
            d.polygon([(tipx, tipy), (base1, base2), (base3, base4)], fill=color)
        d.ellipse([cx - h * 0.28, cy - h * 0.28, cx + h * 0.28, cy + h * 0.28], fill=GOLD)

# ---------------------------------------------------------------- sections
def draw_topbar(d):
    f = load_font("DejaVuSans-Bold.ttf", 11)
    one_line(d, TOP_BAR, f, RX - MX, "top bar")
    d.text(((W - text_w(d, TOP_BAR, f)) / 2, 11), TOP_BAR, font=f, fill=INK)


def draw_masthead(d, img):
    f = load_font("DejaVuSerif-Bold.ttf", 56)
    one_line(d, MASTHEAD, f, RX - MX, "masthead")
    d.text(((W - text_w(d, MASTHEAD, f)) / 2, 28), MASTHEAD, font=f, fill=INK)
    f_sub = load_font("DejaVuSerif.ttf", 17)
    cap = italic_layer(SUBLINE, f_sub, RED)
    if cap.width > RX - MX:
        raise AssertionError("OVERFLOW subline")
    img.paste(cap, (int((W - cap.width) / 2), 98), cap)


def draw_stats(d):
    f_num = load_font("DejaVuSans-Bold.ttf", 28)
    f_cap = load_font("DejaVuSans.ttf", 9)
    cell = (RX - MX) / 6.0
    for i, (num, cap) in enumerate(STATS):
        cx = MX + cell * i + cell / 2.0
        one_line(d, num, f_num, cell - 8, "stat number %s" % num)
        one_line(d, cap, f_cap, cell - 8, "stat caption %s" % cap)
        d.text((cx - text_w(d, num, f_num) / 2, 128), num, font=f_num, fill=RED)
        d.text((cx - text_w(d, cap, f_cap) / 2, 160), cap, font=f_cap, fill=GREY)


def draw_regions(d):
    f = load_font("DejaVuSans-Bold.ttf", 11)
    x = MX
    for label, count, cell_w in REGIONS:
        text = "%s %d" % (label, count)
        one_line(d, text, f, cell_w - 8, "region %s" % label)
        d.rectangle([x, 178, x + cell_w, 200], fill=SOFT, outline=(180, 160, 120))
        d.text((x + (cell_w - text_w(d, text, f)) / 2, 183), text, font=f, fill=INK)
        x += cell_w


def draw_hero_art(d, kind, x, y, wdt, hgt):
    if kind == "blast":
        d.rectangle([x, y, x + wdt, y + hgt], fill=SLATE)
        d.rectangle([x + 20, y + hgt - 26, x + 90, y + hgt], fill=INK)
        d.rectangle([x + 100, y + hgt - 38, x + 150, y + hgt], fill=INK)
        d.rectangle([x + 160, y + hgt - 20, x + 230, y + hgt], fill=INK)
        draw_icon(d, "blast", x + wdt - 70, y + 30, 52, GOLD)
    elif kind == "ship":
        d.rectangle([x, y, x + wdt, y + hgt], fill=NAVY)
        for j in range(3):
            yy = y + hgt - 10 - j * 6
            d.line([(x + 10, yy), (x + wdt - 10, yy)], fill=(120, 150, 190), width=2)
        draw_icon(d, "ship", x + wdt / 2, y + hgt / 2 - 4, 64, (200, 80, 60))
    else:  # shield
        d.rectangle([x, y, x + wdt, y + hgt], fill=(226, 232, 240))
        draw_icon(d, "shield", x + wdt / 2, y + hgt / 2, 58, STEEL)


def draw_heroes(d):
    f_kick = load_font("DejaVuSans-Bold.ttf", 9)
    f_head = load_font("DejaVuSerif-Bold.ttf", 19)
    f_sub = load_font("DejaVuSerif.ttf", 11)
    for i, (num, region, head, sub, kind) in enumerate(HEROES):
        x = HERO_X[i]
        draw_hero_art(d, kind, x, 212, HERO_W, 64)
        one_line(d, region, f_kick, HERO_W, "hero %d kicker" % num)
        d.text((x, 280), region, font=f_kick, fill=RED)
        for j, line in enumerate(wrap_lines(d, head, f_head, HERO_W, 2, "hero %d head" % num)):
            d.text((x, 294 + j * 22), line, font=f_head, fill=INK)
        for j, line in enumerate(wrap_lines(d, sub, f_sub, HERO_W, 2, "hero %d sub" % num)):
            d.text((x, 340 + j * 13), line, font=f_sub, fill=INK)


def draw_smalls(d):
    f_kick = load_font("DejaVuSans-Bold.ttf", 9)
    f_head = load_font("DejaVuSerif-Bold.ttf", 15)
    f_sub = load_font("DejaVuSerif.ttf", 9)
    for i, (num, region, head, sub, kind) in enumerate(SMALLS):
        row = 0 if i < 5 else 1
        col = i % 5
        x = SMALL_X[col]
        art_y = 380 if row == 0 else 528
        ky = 457 if row == 0 else 605
        hy = 470 if row == 0 else 618
        sy = 501 if row == 0 else 649
        d.rectangle([x, art_y, x + SMALL_W, art_y + 70], fill=SOFT)
        draw_icon(d, kind, x + SMALL_W / 2, art_y + 35, 44, (90, 90, 100))
        one_line(d, region, f_kick, SMALL_W, "small %d kicker" % num)
        d.text((x, ky), region, font=f_kick, fill=RED)
        for j, line in enumerate(wrap_lines(d, head, f_head, SMALL_W, 2, "small %d head" % num)):
            d.text((x, hy + j * 16), line, font=f_head, fill=INK)
        for j, line in enumerate(wrap_lines(d, sub, f_sub, SMALL_W, 2, "small %d sub" % num)):
            d.text((x, sy + j * 10), line, font=f_sub, fill=INK)


def draw_map(d, img):
    f_head = load_font("DejaVuSans-Bold.ttf", 13)
    f_pin = load_font("DejaVuSans-Bold.ttf", 9)
    one_line(d, "WHERE IT HAPPENED", f_head, MAP_X1 - MAP_X0, "map header")
    d.text((MAP_X0, 674), "WHERE IT HAPPENED", font=f_head, fill=INK)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=NAVY)
    eq_y = int(project(0, 0)[1])
    for xx in range(MAP_X0, MAP_X1, 12):
        d.line([(xx, eq_y), (min(xx + 6, MAP_X1), eq_y)], fill=(120, 150, 190), width=1)
    for poly in LAND:
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=TAN, outline=LAND_EDGE)
    for sea in (CASPIAN, BLACK_SEA):
        pts = [project(lon, lat) for lon, lat in sea]
        d.polygon(pts, fill=NAVY)
    for num, lon, lat, dx, dy in PINS:
        tx, ty = project(lon, lat)
        dx2, dy2 = tx + dx, ty + dy
        if dx or dy:
            d.line([(tx, ty), (dx2, dy2)], fill=(220, 220, 220), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=WHITE)
        d.ellipse([dx2 - 7, dy2 - 7, dx2 + 7, dy2 + 7], fill=RED, outline=WHITE, width=1)
        t = str(num)
        d.text((dx2 - text_w(d, t, f_pin) / 2, dy2 - 6), t, font=f_pin, fill=WHITE)
    cap = italic_layer(MAP_CAPTION, load_font("DejaVuSerif.ttf", 11), GREY)
    if cap.width > MAP_X1 - MAP_X0:
        raise AssertionError("OVERFLOW map caption")
    img.paste(cap, (MX, 915), cap)


def draw_also(d):
    f_head = load_font("DejaVuSans-Bold.ttf", 13)
    head = "ALSO ON TUESDAY 24 NOVEMBER \u2014 22 MORE STORIES"
    one_line(d, head, f_head, RX - 420, "also header")
    d.text((420, 674), head, font=f_head, fill=INK)
    f_bold = load_font("DejaVuSans-Bold.ttf", 11)
    f_reg = load_font("DejaVuSans.ttf", 11)
    for i, (num, region, brief) in enumerate(ALSO):
        col = 0 if i < 11 else 1
        cx, cwid = ALSO_COLS[col]
        y = 695 + (i % 11) * 20
        n = str(num)
        head_txt = region + ": "
        total = (text_w(d, n, f_bold) + 4 + text_w(d, head_txt, f_bold)
                 + text_w(d, brief, f_reg))
        if total > cwid:
            raise AssertionError(
                "OVERFLOW also %d: %.1fpx, max %d" % (num, total, cwid)
            )
        d.text((cx, y), n, font=f_bold, fill=RED)
        x = cx + text_w(d, n, f_bold) + 4
        d.text((x, y), head_txt, font=f_bold, fill=INK)
        x += text_w(d, head_txt, f_bold)
        d.text((x, y), brief, font=f_reg, fill=INK)


def draw_datecheck(d):
    d.rectangle([MX, 930, RX, 975], outline=RED, width=2)
    f_title = load_font("DejaVuSans-Bold.ttf", 10)
    f_item = load_font("DejaVuSans.ttf", 9)
    one_line(d, DATE_CHECK_TITLE, f_title, RX - MX - 16, "date check title")
    d.text((MX + 8, 933), DATE_CHECK_TITLE, font=f_title, fill=RED)
    for i, row in enumerate(DATE_CHECK_ROWS):
        one_line(d, row, f_item, RX - MX - 16, "date check row %d" % (i + 1))
        d.text((MX + 8, 947 + i * 12), row, font=f_item, fill=INK)


def draw_sources(d):
    f = load_font("DejaVuSans.ttf", 9)
    one_line(d, SOURCES, f, RX - MX, "sources")
    d.text((MX, 996), SOURCES, font=f, fill=GREY)


# ---------------------------------------------------------------- build
def build(out_path):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_topbar(d)
    draw_masthead(d, img)
    draw_stats(d)
    draw_regions(d)
    draw_heroes(d)
    draw_smalls(d)
    draw_map(d, img)
    draw_also(d)
    draw_datecheck(d)
    draw_sources(d)
    img.save(out_path, format="PNG")
    print("wrote %s" % out_path)


def main():
    here = Path(__file__).resolve().parent
    build(str(here / "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
