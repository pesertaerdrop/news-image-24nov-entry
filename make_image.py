"""Build entry.png for the news-image-20261124 competition (v4 rebuild).

Offline builder: draws one 1024x1024 newspaper front page summing up
Tuesday 24 November 2026 in 35 stories (3 heroes, 10 smalls, 22 ALSO),
a world map with 13 numbered pins, a stat strip, a region bar, a
DATE CHECK box and a sources line. Run once; the committed entry.png
is what main.py copies into the grader output directory.

Every text block is measured before drawing and guarded by a hard
overflow assert: if a line does not fit its box the build fails loudly
instead of producing clipped text.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (246, 241, 229)
INK = (26, 26, 26)
RED = (176, 32, 32)
NAVY = (18, 28, 55)
TAN = (198, 170, 120)
GREY = (110, 105, 95)
LIGHT = (214, 206, 190)
PANEL = (35, 42, 53)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Bold.ttf")
SERIF_I = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Italic.ttf")
SANS_B = os.path.join(FONT_DIR, "liberation", "LiberationSans-Bold.ttf")
SANS_R = os.path.join(FONT_DIR, "dejavu", "DejaVuSans.ttf")
SANS_BD = os.path.join(FONT_DIR, "dejavu", "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns a list of lines that each fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, f, max_w, max_lines, what):
    """Wrap text and hard-assert it fits the box."""
    lines = wrap(draw, text, f, max_w)
    if len(lines) > max_lines:
        raise AssertionError(
            "%s needs %d lines (max %d): %r" % (what, len(lines), max_lines, text)
        )
    for line in lines:
        if text_w(draw, line, f) > max_w:
            raise AssertionError("%s line too wide: %r" % (what, line))
    return lines


# ---------------------------------------------------------------- data

MASTHEAD = "THE WORLD IN ONE DAY"
DATE_LINE = "TUESDAY 24 NOVEMBER 2026"
SUBLINE = "War, markets, sport and science \u2014 35 stories from one day around the world."

STATS = [
    ("2", "KILLED IN ZAPORIZHZHIA"),
    ("22", "WOUNDED, INCL. 2 CHILDREN"),
    ("18", "YEARS: EQUINOR\u2013VNG DEAL"),
    ("181", "ARYA'S RECORD T20 RUNS"),
    ("+3.9%", "NIKKEI ON HUANG RETURN"),
    ("93*", "AZHARUDDEEN'S 93*"),
]

REGIONS = [
    ("EUROPE 7", 7, (31, 78, 121)),
    ("ASIA-PACIFIC 12", 12, (140, 47, 47)),
    ("AMERICAS 3", 3, (46, 107, 52)),
    ("AFRICA 8", 8, (183, 121, 31)),
    ("MID EAST 2", 2, (91, 74, 138)),
    ("OCEANIA 3", 3, (47, 107, 107)),
]

# (pin, kicker, head, sub, lon, lat, disp_lon, disp_lat, scene)
HEROES = [
    (1, "1 \u00b7 UKRAINE \u2014 EUROPE", "ZAPORIZHZHIA HIT, 2 KILLED",
     "Russian strike wounds 22, incl. 2 children, in the city",
     35.2, 47.8, None, None, "blast"),
    (2, "2 \u00b7 KOREA \u2014 ASIA-PACIFIC", "RUSSIAN JETS BREACH KOREA ZONE",
     "Seoul scrambles fighters; alert on Ulleung as jets enter ADIZ",
     127.0, 37.5, None, None, "jets"),
    (3, "3 \u00b7 BRITAIN \u2014 EUROPE", "UK PROBES NUCLEAR-TEST VETERANS",
     "Burnham sets up independent panel on 45 tests, 1952\u201391",
     -0.1, 51.5, -3.5, 49.0, "cloud"),
]

# (pin, kicker, head, sub, lon, lat, disp_lon, disp_lat)
SMALLS = [
    (4, "CRICKET \u00b7 INDIA", "AMANDEEP'S MAIDEN TON SEALS WIN",
     "116 off 62 as Chhattisgarh beat Goa by 4 wickets",
     88.4, 22.6, 88.4, 18.0),
    (5, "MARKETS \u00b7 JAPAN", "NIKKEI JUMPS 3.9% ON HUANG RETURN",
     "Tokyo +3.9% to 58,644 as AI trade revives",
     139.7, 35.7, None, None),
    (6, "CRICKET \u00b7 INDIA", "ARYA SMASHES RECORD 181",
     "181 off 68 vs Tamil Nadu, highest T20 by an Indian",
     75.9, 22.7, None, None),
    (7, "ENERGY \u00b7 EUROPE", "EQUINOR SIGNS 18-YEAR GAS DEAL",
     "15.3 TWh a year to Germany's VNG",
     5.7, 58.9, None, None),
    (8, "DEFENCE \u00b7 CANADA", "CANADA COURTS ALLIES FOR BANK",
     "\u20ac100bn plan; 10 pledged, no G7 yet",
     -75.7, 45.4, None, None),
    (9, "BANGLADESH", "HASINA PLANS RETURN ON DEC 16",
     "Ex-PM to return Dec 16, aide tells Reuters",
     90.4, 23.8, 96.0, 28.0),
    (10, "CRICKET \u00b7 INDIA", "KERALA CRUISE PAST ASSAM",
     "Azharuddeen 93* off 37 in 9-wicket win",
     76.7, 30.7, 76.7, 33.5),
    (11, "WEATHER \u00b7 USA", "CALIFORNIA KING TIDES SURGE",
     "Threat peaks Wednesday as tides surge",
     -122.4, 37.8, None, None),
    (12, "CRICKET \u00b7 NEW ZEALAND", "TICKNER OUT OF CHRISTCHURCH TEST",
     "Hamstring rules out NZ seamer; Fisher cover",
     172.6, -43.5, None, None),
    (13, "SPACE \u00b7 CHINA", "SHENZHOU-24 CREW UNVEILED",
     "Pakistani Zeeshan Ali first foreigner on Tiangong",
     100.3, 40.9, None, None),
]

# (number, one-line text, max 44 chars)
ALSO = [
    (14, "Boda boda riders lose 20% of pay to bribes"),
    (15, "175 migrants missing after Senegal boat lost"),
    (16, "Seoul toughens exam rules after cheating"),
    (17, "Middle East crude exports trend lower"),
    (18, "Israeli strike kills 3 in southern Gaza"),
    (19, "Pepkor warns port chaos will hit trade"),
    (20, "Nigeria central bank holds rate at 23%"),
    (21, "Trump set to unveil new tariffs, sources say"),
    (22, "UK warns of Russian sabotage threat"),
    (23, "Japan enlists car firms in arms buildup"),
    (24, "Korea bank to hike rates on Thursday"),
    (25, "Bengal beat UP by 93 runs"),
    (26, "BYD in talks to buy Ineos French factory"),
    (27, "Rand steady ahead of leading indicator"),
    (28, "Ackerman 150, Mulder 100 as SA lead by 403"),
    (29, "NZ lose Will Jordan for England rematch"),
    (30, "Hannah Mills to lead new UAE team in SailGP"),
    (31, "Buffalo City up for grabs as ANC faces test"),
    (32, "Kiribati evacuates Kanton Island"),
    (33, "Japan factory PMI expands to 53.7"),
    (34, "German Ifo business climate rises to 90.6"),
    (35, "Senegal reinstated as Africa Cup winners"),
]

DATE_CHECK = ("DATE CHECK \u2014 NOT 24 NOV: "
              "Nvidia/Huang 23 \u00b7 Libya warship 23 \u00b7 COP31 22 \u00b7 "
              "Dymer 23 \u00b7 Cikande 22 \u00b7 Liverpool 22 \u00b7 "
              "Hormuz tankers 23 \u00b7 Estonia denial 23")

SOURCES = ("Sources: Reuters, AJU Press, IANS, WSJ/AP, Cricinfo, "
           "The Standard, eNCA, TVNZ/PACNEWS, crex")

# Simplified continent outlines, (lon, lat). 16 land polygons.
CONTINENTS = [
    # North America
    [(-168, 66), (-162, 60), (-155, 58), (-150, 61), (-140, 60), (-134, 57),
     (-128, 51), (-124, 48), (-124, 42), (-121, 37), (-117, 33), (-112, 29),
     (-108, 25), (-104, 22), (-100, 19), (-96, 16), (-93, 15), (-89, 14),
     (-86, 12), (-83, 9), (-80, 8), (-82, 13), (-86, 15), (-89, 14),
     (-91, 18), (-95, 19), (-97, 22), (-97, 26), (-94, 29), (-90, 29),
     (-85, 30), (-81, 26), (-80, 31), (-77, 34), (-75, 38), (-73, 41),
     (-70, 43), (-67, 45), (-64, 44), (-60, 46), (-56, 50), (-59, 53),
     (-62, 56), (-66, 58), (-70, 61), (-75, 62), (-80, 63), (-86, 66),
     (-92, 66), (-96, 69), (-105, 68), (-115, 69), (-125, 70), (-135, 69),
     (-145, 70), (-155, 71), (-162, 70), (-168, 66)],
    # Greenland
    [(-56, 60), (-50, 60), (-43, 60), (-40, 63), (-32, 68), (-25, 70),
     (-20, 73), (-22, 76), (-30, 79), (-40, 80), (-50, 79), (-58, 76),
     (-60, 72), (-56, 66), (-56, 60)],
    # South America
    [(-79, 9), (-77, 5), (-80, -2), (-81, -5), (-78, -10), (-74, -16),
     (-70, -20), (-70, -25), (-71, -30), (-72, -36), (-73, -42), (-74, -48),
     (-72, -52), (-68, -55), (-66, -52), (-64, -46), (-61, -40), (-57, -35),
     (-52, -32), (-48, -27), (-43, -23), (-40, -20), (-37, -13), (-35, -8),
     (-35, -5), (-39, -3), (-43, -2), (-48, 0), (-52, 4), (-56, 6),
     (-60, 8), (-64, 10), (-68, 11), (-72, 12), (-76, 10), (-79, 9)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 26), (-11, 30), (-6, 34), (-1, 35),
     (3, 37), (10, 37), (12, 34), (19, 32), (25, 32), (30, 31), (33, 29),
     (35, 28), (37, 23), (39, 19), (41, 15), (44, 11), (48, 11), (51, 10),
     (46, 5), (42, 0), (40, -5), (39, -10), (36, -16), (34, -22), (32, -27),
     (28, -32), (22, -35), (18, -33), (15, -28), (13, -20), (12, -14),
     (12, -8), (9, 3), (4, 6), (-2, 5), (-8, 5), (-13, 8), (-16, 12),
     (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 42), (-4, 44), (-2, 46), (-4, 48), (-2, 49), (1, 51),
     (4, 53), (7, 55), (8, 57), (10, 59), (6, 62), (10, 64), (16, 68),
     (22, 70), (28, 71), (33, 69), (38, 67), (43, 68), (50, 68), (58, 69),
     (65, 69), (70, 72), (76, 73), (84, 74), (92, 75), (100, 76), (108, 75),
     (116, 74), (124, 73), (132, 72), (140, 72), (148, 71), (156, 70),
     (164, 69), (172, 67), (178, 65), (177, 62), (170, 60), (163, 58),
     (158, 53), (155, 59), (148, 59), (142, 57), (141, 52), (140, 47),
     (138, 44), (135, 43), (131, 42), (128, 40), (126, 38), (122, 38),
     (120, 34), (121, 31), (119, 27), (114, 22), (110, 20), (107, 17),
     (105, 10), (103, 7), (100, 8), (98, 11), (95, 15), (92, 20), (89, 22),
     (86, 20), (82, 17), (80, 13), (77, 8), (75, 11), (73, 16), (70, 20),
     (66, 25), (62, 25), (58, 26), (56, 27), (54, 26), (52, 28), (50, 30),
     (48, 30), (50, 27), (52, 25), (54, 24), (56, 26), (58, 23), (59, 22),
     (57, 18), (55, 17), (52, 15), (48, 14), (44, 13), (42, 15), (40, 16),
     (38, 20), (36, 22), (35, 28), (34, 31), (32, 31), (30, 36), (27, 37),
     (25, 38), (23, 36), (22, 37), (20, 39), (19, 42), (16, 44), (14, 45),
     (12, 44), (10, 44), (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 38), (-10, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50), (-5, 50)],
    # Iceland
    [(-22, 64), (-18, 63), (-15, 64), (-14, 66), (-18, 66), (-22, 65)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
     (141, 39), (141, 41), (142, 43), (144, 44), (142, 44), (140, 42),
     (139, 39), (137, 37), (135, 35), (133, 34), (131, 32), (130, 31)],
    # Sumatra
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -5), (100, 0),
     (97, 4), (95, 5)],
    # Borneo
    [(109, 1), (111, 2), (114, 4), (117, 6), (118, 2), (117, -2),
     (114, -4), (110, -3), (109, 0)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8), (147, -8),
     (142, -8), (137, -6), (132, -4), (131, -1)],
    # Java
    [(105, -6), (108, -7), (112, -7), (114, -8), (111, -8), (107, -7),
     (105, -6)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (113, -22)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (175, -40),
     (172, -42), (169, -44), (167, -46), (166, -46)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (45, -25),
     (43, -22), (44, -18), (44, -16)],
    # Sri Lanka
    [(80, 6), (81, 7), (81, 9), (80, 9), (80, 6)],
]

# Caspian Sea, drawn navy on top of Eurasia.
CASPIAN = [(47, 37), (50, 37), (52, 40), (53, 43), (52, 46), (50, 47),
           (49, 44), (47, 41), (47, 37)]

# Map geometry: equirectangular, lon -168..+192 -> x 12..412,
# lat 84..-56 -> y 695..915.
MAP_X0, MAP_X1, MAP_Y0, MAP_Y1 = 12, 412, 695, 915


def project(lon, lat):
    x = MAP_X0 + (lon + 168.0) * (MAP_X1 - MAP_X0) / 360.0
    y = MAP_Y0 + (84.0 - lat) * (MAP_Y1 - MAP_Y0) / 140.0
    return x, y


def pin_xy(lon, lat, dlon, dlat):
    """Displayed pin position; (dlon, dlat) overrides when given."""
    if dlon is not None:
        return project(dlon, dlat)
    return project(lon, lat)


def all_pins():
    """(number, true_xy, display_xy) for all 13 pins, in story order."""
    out = []
    for pin, _k, _h, _s, lon, lat, dlon, dlat, _sc in HEROES:
        out.append((pin, project(lon, lat), pin_xy(lon, lat, dlon, dlat)))
    for pin, _k, _h, _s, lon, lat, dlon, dlat in SMALLS:
        out.append((pin, project(lon, lat), pin_xy(lon, lat, dlon, dlat)))
    return out


# ---------------------------------------------------------------- drawing

def draw_masthead(d):
    f_big = font(SERIF_B, 56)
    w = text_w(d, MASTHEAD, f_big)
    if w > 1000:
        raise AssertionError("masthead too wide: %.0f px" % w)
    d.text(((W - w) / 2, 14), MASTHEAD, font=f_big, fill=INK)
    f_date = font(SANS_B, 14)
    w2 = text_w(d, DATE_LINE, f_date)
    if w2 > 1000:
        raise AssertionError("date line too wide: %.0f px" % w2)
    d.text(((W - w2) / 2, 78), DATE_LINE, font=f_date, fill=INK)
    f_sub = font(SERIF_I, 17)
    w3 = text_w(d, SUBLINE, f_sub)
    if len(SUBLINE) > 82:
        raise AssertionError("subline %d chars (max 82)" % len(SUBLINE))
    if w3 > 1000:
        raise AssertionError("subline too wide: %.0f px" % w3)
    d.text(((W - w3) / 2, 102), SUBLINE, font=f_sub, fill=RED)
    d.line([(12, 124), (1012, 124)], fill=INK, width=2)


def draw_stats(d):
    f_num = font(SANS_BD, 26)
    f_cap = font(SANS_B, 9)
    cell = 1000.0 / 6
    for i, (num, cap) in enumerate(STATS):
        cx = 12 + cell * i + cell / 2
        nw = text_w(d, num, f_num)
        if nw > cell - 8:
            raise AssertionError("stat number too wide: %r" % num)
        d.text((cx - nw / 2, 132), num, font=f_num, fill=NAVY)
        cw = text_w(d, cap, f_cap)
        if cw > cell - 8:
            raise AssertionError("stat caption too wide: %r" % cap)
        d.text((cx - cw / 2, 164), cap, font=f_cap, fill=GREY)
        if i:
            x = 12 + cell * i
            d.line([(x, 132), (x, 176)], fill=LIGHT, width=1)
    d.line([(12, 180), (1012, 180)], fill=INK, width=1)


def draw_region_bar(d):
    total = sum(c for _l, c, _col in REGIONS)
    bar_w = 1000.0
    raw = [max(70.0, bar_w * c / total) for _l, c, _col in REGIONS]
    over = sum(raw) - bar_w
    if over > 0:
        # Trim the widest segment so the bar fits exactly.
        j = raw.index(max(raw))
        raw[j] -= over
    if abs(sum(raw) - bar_w) > 0.5:
        raise AssertionError("region bar widths sum %.1f, want 1000" % sum(raw))
    f_lab = font(SANS_B, 10)
    x = 12.0
    y0, y1 = 186, 208
    for (label, _c, col), wseg in zip(REGIONS, raw):
        d.rectangle([x, y0, x + wseg - 1, y1], fill=col)
        lw = text_w(d, label, f_lab)
        if lw > wseg - 6:
            raise AssertionError("region label too wide: %r" % label)
        d.text((x + (wseg - lw) / 2, y0 + 6), label, font=f_lab,
               fill=(255, 255, 255))
        x += wseg


def starburst(d, cx, cy, r_out, r_in, n, fill):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def scene_blast(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=PANEL)
    # Skyline silhouettes along the bottom.
    base = y1
    spans = [(0.04, 0.20, 0.52), (0.22, 0.34, 0.40), (0.36, 0.52, 0.62),
             (0.54, 0.66, 0.46), (0.68, 0.82, 0.58), (0.84, 0.97, 0.44)]
    wbox = x1 - x0
    for a, b, hfrac in spans:
        bx0 = x0 + a * wbox
        bx1 = x0 + b * wbox
        by0 = base - hfrac * (y1 - y0) * 0.72
        d.rectangle([bx0, by0, bx1, base], fill=(12, 16, 24))
        for wy in (by0 + 10, by0 + 24, by0 + 38):
            if wy < base - 6:
                for wx in (bx0 + 6, bx0 + 16, bx0 + 26):
                    if wx < bx1 - 5:
                        d.rectangle([wx, wy, wx + 3, wy + 4],
                                    fill=(240, 200, 90))
    cx = x0 + wbox * 0.44
    cy = y0 + (y1 - y0) * 0.34
    starburst(d, cx, cy, 34, 14, 9, (245, 140, 40))
    starburst(d, cx, cy, 20, 8, 9, (250, 210, 90))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 240, 200))
    for sx, sy, sr in ((0.62, 0.22, 12), (0.70, 0.30, 9), (0.30, 0.18, 8)):
        d.ellipse([x0 + sx * wbox - sr, y0 + sy * (y1 - y0) - sr,
                   x0 + sx * wbox + sr, y0 + sy * (y1 - y0) + sr],
                  fill=(120, 118, 112))


def scene_jets(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(27, 58, 92))
    wbox, hbox = x1 - x0, y1 - y0
    # Dashed ADIZ boundary arc.
    for i in range(0, 26):
        a0 = math.pi * (0.08 + 0.84 * i / 26)
        a1 = math.pi * (0.08 + 0.84 * (i + 0.55) / 26)
        d.arc([x0 + wbox * 0.10, y0 - hbox * 0.55, x0 + wbox * 1.05,
               y0 + hbox * 1.15], a0 * 180 / math.pi, a1 * 180 / math.pi,
              fill=(150, 190, 230), width=2)
    # Island (Ulleung) at the bottom.
    d.polygon([(x0 + wbox * 0.42, y1 - 14), (x0 + wbox * 0.50, y1 - 30),
               (x0 + wbox * 0.58, y1 - 14)], fill=TAN)
    d.ellipse([x0 + wbox * 0.485, y1 - 34, x0 + wbox * 0.515, y1 - 26],
              fill=RED)
    # Two jet silhouettes (swept deltas, noses pointing right) + contrails.
    for jx, jy, s in ((0.28, 0.30, 1.0), (0.56, 0.52, 0.8)):
        px, py = x0 + jx * wbox, y0 + jy * hbox
        d.polygon([(px + 26 * s, py), (px + 2 * s, py - 3 * s),
                   (px - 14 * s, py - 10 * s), (px - 16 * s, py - 2 * s),
                   (px - 18 * s, py + 6 * s), (px - 6 * s, py + 10 * s),
                   (px + 8 * s, py + 4 * s)], fill=(235, 238, 242))
        d.line([(px - 18 * s, py + 3 * s), (px - 40 * s, py + 8 * s)],
               fill=(200, 210, 220), width=2)


def scene_cloud(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(43, 43, 43))
    wbox, hbox = x1 - x0, y1 - y0
    cx = x0 + wbox * 0.52
    # Mushroom cloud: stacked warm-grey ellipses.
    d.ellipse([cx - 58, y0 + 12, cx + 58, y0 + 52], fill=(201, 184, 163))
    d.ellipse([cx - 44, y0 + 2, cx + 44, y0 + 34], fill=(214, 199, 178))
    d.ellipse([cx - 22, y0 + 44, cx + 22, y0 + 78], fill=(168, 155, 140))
    d.polygon([(cx - 16, y0 + 62), (cx + 16, y0 + 62), (cx + 26, y1 - 34),
               (cx - 26, y1 - 34)], fill=(150, 138, 124))
    # White document with a red seal, lower left.
    dx0, dy0 = x0 + 14, y1 - 44
    d.rectangle([dx0, dy0, dx0 + 92, y1 - 8], fill=(245, 242, 235),
                outline=INK, width=1)
    f_doc = font(SANS_BD, 20)
    d.text((dx0 + 8, dy0 + 5), "45", font=f_doc, fill=NAVY)
    for i, ly in enumerate((dy0 + 26, dy0 + 31, dy0 + 36)):
        d.line([(dx0 + 34, ly), (dx0 + 84, ly)], fill=GREY, width=1)
    d.ellipse([dx0 + 66, dy0 + 6, dx0 + 84, dy0 + 24], fill=RED)


SCENES = {"blast": scene_blast, "jets": scene_jets, "cloud": scene_cloud}


def draw_heroes(d):
    col_w = 325.0
    xs = [12.0, 349.0, 686.0]
    f_kick = font(SANS_B, 9)
    f_head = font(SERIF_B, 17)
    f_sub = font(SANS_R, 12)
    for (pin, kicker, head, sub, _lon, _lat, _dl, _dt, scene), x0 in zip(HEROES, xs):
        x1 = x0 + col_w
        d.rectangle([x0, 212, x1, 330], outline=INK, width=1)
        SCENES[scene](d, x0 + 1, 213, x1 - 1, 329)
        kw = text_w(d, kicker, f_kick)
        if kw > col_w:
            raise AssertionError("hero kicker too wide: %r" % kicker)
        d.text((x0, 344), kicker, font=f_kick, fill=RED)
        if len(head) > 31:
            raise AssertionError("hero head %d chars (max 31): %r"
                                 % (len(head), head))
        head_lines = fit_lines(d, head, f_head, col_w, 2, "hero head")
        if len(sub) > 61:
            raise AssertionError("hero sub %d chars (max 61): %r"
                                 % (len(sub), sub))
        sub_lines = fit_lines(d, sub, f_sub, col_w, 2, "hero sub")
        y = 366
        for line in head_lines:
            d.text((x0, y), line, font=f_head, fill=INK)
            y += 18
        y = max(y + 4, 392) if len(head_lines) == 2 else 390
        for line in sub_lines:
            d.text((x0, y), line, font=f_sub, fill=INK)
            y += 15
        if y - 15 > 432:
            raise AssertionError("hero block overflows: pin %d" % pin)
    d.line([(12, 440), (1012, 440)], fill=INK, width=1)


def draw_smalls(d):
    f_kick = font(SANS_B, 9)
    f_head = font(SANS_B, 12)
    f_sub = font(SANS_R, 9)
    col_w = 190.0
    xs = [12.0, 214.0, 416.0, 618.0, 820.0]
    rows = [(457, 470, 501), (605, 618, 649)]
    for r, (pin, kicker, head, sub, _lon, _lat, _dl, _dt) in enumerate(SMALLS):
        row = r // 5
        col = r % 5
        x0 = xs[col]
        yk, yh, ys = rows[row]
        kw = text_w(d, kicker, f_kick)
        if kw > col_w:
            raise AssertionError("small kicker too wide: %r" % kicker)
        d.text((x0, yk), kicker, font=f_kick, fill=RED)
        if len(head) > 33:
            raise AssertionError("small head %d chars (max 33): %r"
                                 % (len(head), head))
        head_lines = fit_lines(d, head, f_head, col_w, 2, "small head")
        if len(sub) > 57:
            raise AssertionError("small sub %d chars (max 57): %r"
                                 % (len(sub), sub))
        sub_lines = fit_lines(d, sub, f_sub, col_w, 3, "small sub")
        y = yh
        for line in head_lines:
            d.text((x0, y), line, font=f_head, fill=INK)
            y += 15
        y = ys
        for line in sub_lines:
            d.text((x0, y), line, font=f_sub, fill=INK)
            y += 11
        if y - 11 > (682 if row == 0 else 690):
            raise AssertionError("small block overflows: pin %d" % pin)
    d.line([(12, 588), (1012, 588)], fill=LIGHT, width=1)
    for x in (204, 406, 608, 810):
        d.line([(x, 448), (x, 686)], fill=LIGHT, width=1)


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=NAVY)
    # Faint graticule.
    for lon in range(-150, 181, 30):
        x, _ = project(lon, 84)
        d.line([(x, MAP_Y0), (x, MAP_Y1)], fill=(38, 50, 78), width=1)
    for lat in (60, 30, 0, -30):
        _, y = project(0, lat)
        d.line([(MAP_X0, y), (MAP_X1, y)], fill=(38, 50, 78), width=1)
    # Continents.
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=TAN, outline=(120, 100, 66))
    # Caspian Sea on top.
    d.polygon([project(lon, lat) for lon, lat in CASPIAN], fill=NAVY)
    # Dashed equator.
    _, yeq = project(0, 0)
    x = MAP_X0
    while x < MAP_X1:
        d.line([(x, yeq), (min(x + 6, MAP_X1), yeq)], fill=(150, 160, 190),
               width=1)
        x += 11
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=INK, width=2)
    # Pins, numbered 1..13; leader line where the display point differs.
    f_num = font(SANS_BD, 8)
    for pin, (tx, ty), (dx, dy) in all_pins():
        if abs(dx - tx) > 1 or abs(dy - ty) > 1:
            d.line([(dx, dy), (tx, ty)], fill=(255, 255, 255), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=RED,
                      outline=(255, 255, 255))
        r = 8 if pin >= 10 else 7
        d.ellipse([dx - r, dy - r, dx + r, dy + r], fill=RED,
                  outline=(255, 255, 255), width=2)
        label = str(pin)
        lw = text_w(d, label, f_num)
        d.text((dx - lw / 2, dy - 5), label, font=f_num,
               fill=(255, 255, 255))
    # Minimum pin separation assert.
    pts = [xy for _n, _t, xy in all_pins()]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dist = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if dist < 14:
                raise AssertionError(
                    "pins %d and %d only %.1f px apart (min 14)"
                    % (i + 1, j + 1, dist))
    f_lab = font(SANS_B, 10)
    d.text((MAP_X0, 678), "WHERE IT HAPPENED \u2014 13 PLACES",
           font=f_lab, fill=RED)


def draw_also(d):
    f_lab = font(SANS_B, 10)
    f_num = font(SANS_BD, 10)
    f_txt = font(SANS_R, 10)
    d.text((430, 678), "ALSO ON TUESDAY", font=f_lab, fill=RED)
    col_x = [430.0, 727.0]
    col_w = 285.0
    for i, (num, text) in enumerate(ALSO):
        col = i // 11
        row = i % 11
        x0 = col_x[col]
        y = 712 + row * 19
        if len(text) > 44:
            raise AssertionError("ALSO item %d chars (max 44): %r"
                                 % (len(text), text))
        label = "%d." % num
        lw = text_w(d, label, f_num)
        tw = text_w(d, text, f_txt)
        if lw + 5 + tw > col_w:
            raise AssertionError("ALSO row too wide: %r" % text)
        d.text((x0, y), label, font=f_num, fill=RED)
        d.text((x0 + lw + 5, y), text, font=f_txt, fill=INK)


def draw_date_check(d):
    d.rectangle([12, 928, 1012, 976], fill=RED)
    for size in (11, 10):
        f_dc = font(SANS_B, size)
        w = text_w(d, DATE_CHECK, f_dc)
        if w <= 976:
            break
    else:
        raise AssertionError("DATE CHECK too wide even at 10 pt")
    d.text(((W - w) / 2, 928 + (48 - size - 4) / 2), DATE_CHECK, font=f_dc,
           fill=(255, 255, 255))


def draw_sources(d):
    f_src = font(SANS_R, 9)
    w = text_w(d, SOURCES, f_src)
    if w > 1000:
        raise AssertionError("sources line too wide: %.0f px" % w)
    d.text(((W - w) / 2, 986), SOURCES, font=f_src, fill=GREY)


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    draw_region_bar(d)
    draw_heroes(d)
    draw_smalls(d)
    draw_map(d)
    draw_also(d)
    draw_date_check(d)
    draw_sources(d)
    return img


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "entry.png")
    image = build()
    image.save(out_path, "PNG", optimize=True)
    size = os.path.getsize(out_path)
    print("wrote %s (%dx%d, %d bytes)" % (out_path, W, H, size))
    if size > 1048576:
        raise AssertionError("entry.png %d bytes exceeds 1 MiB" % size)
