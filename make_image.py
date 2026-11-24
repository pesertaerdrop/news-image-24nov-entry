#!/usr/bin/env python3
"""Draw Tuesday 24 November 2026 as one front page.

A single 1024x1024 PNG: masthead, three lead stories, ten small leads,
a realistic world map with thirteen numbered pins, twenty-two more
stories, and a DATE CHECK box. Everything is drawn from code with
Pillow; no picture is downloaded and no network is touched. Every text
block carries a hard size check: if a headline or a caption does not
fit its box, the build stops instead of printing a clipped page.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
CREAM = (250, 246, 238)
INK = (30, 30, 30)
RED = (180, 30, 30)
NAVY = (18, 28, 55)
TAN = (198, 170, 120)
EDGE = (60, 50, 35)
GREY = (100, 100, 100)
WHITE = (255, 255, 255)
GOLD = (240, 210, 70)
MX = 12
RX = 1012

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def text_w(d: ImageDraw.ImageDraw, text: str, font) -> float:
    return d.textlength(text, font=font)


def fit(d, text: str, font, max_w: float, max_lines: int, what: str):
    """Wrap text to at most max_lines lines of at most max_w pixels.

    Stops the build with an OVERFLOW error when the text cannot fit:
    the fix is a shorter text or a wider box, never a silent clip.
    """
    words = text.split()
    lines: list[str] = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(d, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        raise AssertionError(
            "OVERFLOW %s: %d lines, max %d (%r)" % (what, len(lines), max_lines, text)
        )
    return lines


def draw_lines(d, lines, x: int, y: int, font, fill, pitch: int) -> None:
    for i, line in enumerate(lines):
        d.text((x, y + i * pitch), line, font=font, fill=fill)


def one_line(d, text: str, font, max_w: float, what: str) -> None:
    if text_w(d, text, font) > max_w:
        raise AssertionError(
            "OVERFLOW %s: %.1fpx, max %.1f (%r)" % (what, text_w(d, text, font), max_w, text)
        )


def italic_layer(text: str, font, fill, shear: float = 0.22) -> Image.Image:
    """Render text on its own layer, then slant it geometrically."""
    probe = Image.new("RGBA", (10, 10))
    pd = ImageDraw.Draw(probe)
    tw = int(text_w(pd, text, font)) + 4
    th = font.size + 8
    layer = Image.new("RGBA", (tw + int(shear * th) + 4, th), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((2, 2), text, font=font, fill=fill + (255,))
    # x' = x + shear * (height - y): a lean to the right.
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
SUBLINE = "UN demands Libya probe \u00b7 SpaceX sued over Grok images \u00b7 Estonia defies Moscow"

STATS = [
    ("30+", "Hormuz attacks logged"),
    ("17", "killed in Hodeida strike"),
    ("50M", "children in typhoid drive"),
    ("$2B", "SoftBank bets on Intel"),
    ("181", "Arya's record T20 score"),
    ("3", "killed in Gaza strikes"),
]

REGIONS = [
    ("EUROPE", 8, (30, 80, 160), 210),
    ("MIDDLE EAST", 4, (150, 60, 60), 105),
    ("AMERICAS", 6, (180, 140, 40), 158),
    ("ASIA-PACIFIC", 10, (40, 130, 80), 262),
    ("AFRICA", 4, (160, 120, 50), 105),
    ("OCEANIA", 1, (60, 140, 140), 80),
    ("WORLD", 2, (117, 117, 117), 80),
]

# (kicker, head, sub, art kind)
HEROES = [
    (
        "UN demands a probe into Libya attacks",
        "UN mission calls for an inquiry after drones hit a Russian warship and a Maltese vessel off Benghazi. (UN)",
        "probe",
    ),
    (
        "SpaceX sued over Grok abuse images",
        "States say Grok made abuse images and SpaceX hid the risk; suit filed in Portland. (Reuters)",
        "gavel",
    ),
    (
        "Estonia defies Moscow on airspace",
        "Tallinn denies letting Kyiv use its skies; NATO allies rally behind Estonia. (Reuters)",
        "shield",
    ),
]

# (title, kicker, head, sub, art kind)
SMALLS = [
    (
        "HORMUZ LOG",
        "MIDDLE EAST",
        "UK logs record Hormuz attacks",
        "30+ attacks in October, a record; Tehran vows to fight the blockade.",
        "ship",
    ),
    (
        "GAZA STRIKES",
        "MIDDLE EAST",
        "Israeli strikes kill 3 in Gaza",
        "Three dead, including a UNRWA worker, despite the October ceasefire. (Al Jazeera)",
        "blast",
    ),
    (
        "HODEIDA HIT",
        "MIDDLE EAST",
        "Houthis: Saudi strike kills 17",
        "Saudi-led strike on Hodeida kills 17 and hits telecoms, Houthis claim. (Reports)",
        "target",
    ),
    (
        "IRAN WARNING",
        "MIDDLE EAST",
        "Trump warns Iran of 'trauma'",
        "'Very traumatic' if no deal, Trump warns; Tehran vows to fight. (Reuters)",
        "warning",
    ),
    (
        "NIKKEI RALLY",
        "ASIA-PACIFIC",
        "Nikkei rallies on Japan deal",
        "Tokyo stocks jump after Trump announces a Japan trade deal; yen steadies. (Reuters)",
        "chart",
    ),
    (
        "TYPHOID DRIVE",
        "ASIA-PACIFIC",
        "Bangladesh vaccinates 50M kids",
        "Drive targets 50 million children as drug-resistant strains spread. (WHO)",
        "syringe",
    ),
    (
        "SOFTBANK BET",
        "ASIA-PACIFIC",
        "SoftBank to invest $2b in Intel",
        "Japanese giant backs the US chipmaker as Intel rebuilds; shares climb. (Reuters)",
        "chip",
    ),
    (
        "ARYA 181",
        "ASIA-PACIFIC",
        "Arya smashes record 181",
        "Delhi captain hits 19 sixes in a record T20 knock, the best by an Indian. (Cricinfo)",
        "ball",
    ),
    (
        "REVANNA LIFE",
        "ASIA-PACIFIC",
        "Ex-MP Revanna gets life term",
        "Former Indian lawmaker sentenced to life for rape in a landmark verdict. (Reuters)",
        "scales",
    ),
    (
        "EL CHAPO ISIDRO",
        "AMERICAS",
        "Mexico nabs 'El Chapo Isidro'",
        "Drug lord captured; Mexico will prosecute him, defying a US plea. (Reuters)",
        "cuff",
    ),
]

# (number, region, brief) — 22 more stories.
ALSO = [
    (14, "Asia-Pacific", "Thai-Cambodia truce holds"),
    (15, "Asia-Pacific", "Russian jets breach Korea zone"),
    (16, "Asia-Pacific", "Trump seals Indonesia deal"),
    (17, "Asia-Pacific", "India maps landslide risk"),
    (18, "Americas", "US unveils citizenship test changes"),
    (19, "Americas", "Senate to vote on $9.4bn cuts"),
    (20, "Americas", "FAA lifts O'Hare ground stop"),
    (21, "Americas", "California braces for king tides"),
    (22, "Europe", "Arm extends CEO Haas to 2033"),
    (23, "Europe", "14 nations back ICJ Rohingya ruling"),
    (24, "Europe", "Brentford thrash Everton 4-0"),
    (25, "Asia-Pacific", "Hunt for missing in Himalayan flood"),
    (26, "Europe", "Burnham: EU return needs a referendum"),
    (27, "Europe", "Man Utd appeal Yoro red card"),
    (28, "Europe", "Finland summons Russia envoy"),
    (29, "Europe", "Lilly Jones found dead in Blaina"),
    (30, "Africa", "Somalia, Uganda step up Al-Shabaab fight"),
    (31, "Africa", "Ethiopia urges Africa to trade within itself"),
    (32, "Africa", "Uganda general vows to oust minister"),
    (33, "Oceania", "'Job hugging' grips Kiwi workers"),
    (34, "World", "FIFA opens 2030 World Cup media bids"),
    (35, "World", "Ethereum funds see $131M outflows"),
]

DATE_CHECK_TITLE = "DATE CHECK \u2014 NOT TODAY"
DATE_CHECK_ROWS = [
    "Nvidia brings back Huang (23 Nov) \u00b7 Ukraine sinks warship off Libya (23 Nov) \u00b7 COP31 collapses without a deal (22 Nov)",
    "Dymer toll hits 11 (23 Nov) \u00b7 Cikande fire toll 24 (22 Nov) \u00b7 Liverpool 4-0 Man Utd (22 Nov)",
]
SOURCES = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, ESPNcricinfo, UKMTO, WHO, UN"
MAP_CAPTION = "Thirteen stories, pinned where they happened."

# ------------------------------------------------------------------- map
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 12, 695, 412, 915


def project(lon: float, lat: float):
    x = MAP_X0 + (lon + 168.0) * (MAP_X1 - MAP_X0) / 360.0
    y = MAP_Y0 + (84.0 - lat) * (MAP_Y1 - MAP_Y0) / 140.0
    return (x, y)


def project_poly(poly):
    return [project(lon, lat) for lon, lat in poly]


# Coastlines as (lon, lat) points, drawn from world geography. Each list
# is one landmass; Europe and Asia share one polygon so no seam line
# runs through Eurasia. The Black Sea is left as an inlet in the
# coastline, the Persian Gulf as a notch, and the Red Sea as the gap
# between this polygon and Africa.
NORTH_AMERICA = [
    (-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
    (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
    (-105, 20), (-97, 16), (-92, 15), (-86, 12), (-83, 9), (-80, 9),
    (-79, 9), (-83, 15), (-87, 21), (-90, 21), (-97, 26), (-93, 30),
    (-89, 30), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 40),
    (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-65, 50), (-60, 52),
    (-55, 52), (-60, 55), (-65, 60), (-68, 58), (-75, 62), (-80, 66),
    (-85, 66), (-90, 69), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
    (-155, 71), (-165, 68),
]
SOUTH_AMERICA = [
    (-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
    (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
    (-66, -55), (-68, -50), (-65, -45), (-62, -40), (-58, -34), (-52, -32),
    (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
    (-44, -2), (-50, 0), (-52, 5), (-58, 8), (-62, 10), (-68, 11),
    (-72, 12), (-77, 8),
]
GREENLAND = [
    (-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
    (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-62, 72),
]
EURASIA = [
    (-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 49), (2, 51),
    (5, 53), (8, 57), (7, 58), (5, 60), (5, 62), (8, 63), (12, 65),
    (16, 68), (20, 70), (25, 71), (30, 70), (35, 68), (40, 67), (44, 68),
    (50, 68), (55, 68), (60, 69), (68, 70), (72, 72), (75, 73), (80, 73),
    (85, 74), (95, 76), (100, 77), (105, 77), (110, 74), (115, 73),
    (120, 73), (130, 72), (140, 72), (150, 70), (158, 69), (162, 66),
    (170, 66), (178, 65), (170, 60), (162, 56), (156, 52), (150, 55),
    (142, 59), (141, 52), (140, 48), (135, 43), (130, 42), (127, 40),
    (129, 35), (126, 38), (122, 39), (120, 35), (121, 28), (118, 25),
    (110, 20), (108, 18), (105, 9), (103, 2), (100, 6), (98, 10),
    (97, 16), (94, 17), (92, 22), (89, 22), (86, 20), (80, 15), (77, 8),
    (76, 10), (73, 16), (70, 20), (66, 25), (62, 25), (57, 26), (54, 27),
    (52, 28), (50, 29), (48, 30), (48, 29), (44, 29), (40, 31), (36, 36),
    (36, 33), (33, 31), (30, 36), (27, 37), (23, 36), (22, 37), (19, 42),
    (19, 45), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
    (-6, 36), (-9, 37),
]
AFRICA = [
    (-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
    (-13, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (13, 4), (14, 0),
    (12, -5), (13, -10), (12, -17), (14, -22), (16, -28), (19, -34),
    (26, -34), (31, -29), (35, -24), (40, -16), (40, -10), (42, -5),
    (46, -1), (51, 2), (51, 10), (44, 11), (43, 12), (40, 15), (38, 18),
    (36, 22), (34, 28), (32, 31), (30, 31), (25, 32), (20, 32), (15, 32),
    (10, 34), (5, 37), (0, 36), (-6, 35),
]
AUSTRALIA = [
    (114, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
    (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
    (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
    (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
    (118, -20), (114, -22),
]
NEW_ZEALAND_N = [
    (173, -35), (175, -38), (177, -38), (178, -38), (176, -40), (174, -41),
    (173, -35),
]
NEW_ZEALAND_S = [
    (167, -45), (168, -44), (170, -43), (172, -42), (173, -41), (171, -43),
    (168, -46), (167, -45),
]
UNITED_KINGDOM = [
    (-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
    (-5, 50),
]
JAPAN = [
    (130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 38),
    (141, 41), (143, 42), (145, 44), (142, 44), (140, 40), (138, 37),
    (136, 35), (133, 34), (131, 33), (130, 31),
]
MADAGASCAR = [
    (44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (45, -25),
    (43, -22), (44, -16),
]
SUMATRA = [
    (95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -6), (101, -3),
    (98, 2), (95, 5),
]
BORNEO = [
    (109, 1), (111, 2), (114, 4), (117, 6), (119, 1), (117, -3), (114, -4),
    (110, -3), (109, 1),
]
JAVA = [
    (105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (111, -8),
    (108, -8), (105, -7), (105, -6),
]
NEW_GUINEA = [
    (131, -1), (134, -3), (137, -3), (140, -8), (143, -8), (146, -7),
    (150, -10), (147, -9), (143, -8), (140, -8), (137, -6), (134, -4),
    (131, -1),
]
PHILIPPINES = [
    (120, 18), (122, 18), (122, 14), (124, 11), (123, 9), (122, 7),
    (120, 8), (120, 14), (120, 18),
]
LANDMASSES = [
    NORTH_AMERICA, SOUTH_AMERICA, GREENLAND, EURASIA, AFRICA,
    AUSTRALIA, NEW_ZEALAND_N, NEW_ZEALAND_S, UNITED_KINGDOM, JAPAN,
    MADAGASCAR, SUMATRA, BORNEO, JAVA, NEW_GUINEA, PHILIPPINES,
]
# The Caspian is a lake: painted navy on top of the land.
CASPIAN = [
    (47, 47), (50, 46), (53, 44), (54, 42), (52, 40), (50, 39), (49, 41),
    (47, 44), (47, 47),
]

# (number, true lon, true lat, shown lon, shown lat).
# Shown differs from true only where the pin is nudged off a crowded
# coast, with a thin leader line back to the true spot.
PINS = [
    (1, 20.07, 32.12, None, None),      # Benghazi — UN probe
    (2, -122.68, 45.52, None, None),    # Portland — Grok suit
    (3, 24.75, 59.44, None, None),      # Tallinn — Estonia
    (4, 56.5, 26.5, 58.5, 24.0),        # Hormuz — nudged SE
    (5, 34.47, 31.5, 32.0, 33.5),       # Gaza — nudged NW
    (6, 42.95, 14.8, None, None),       # Hodeida
    (7, 51.4, 35.7, None, None),        # Tehran
    (8, 139.7, 35.7, None, None),       # Tokyo — Nikkei
    (9, 90.4, 23.8, None, None),        # Dhaka — typhoid
    (10, -122.0, 37.4, -118.0, 34.0),   # Santa Clara — SoftBank/Intel, nudged SE
    (11, 75.86, 22.72, None, None),     # Indore — Arya 181
    (12, 77.59, 12.97, 79.5, 10.5),     # Bengaluru — Revanna, nudged SE
    (13, -107.39, 24.8, None, None),    # Culiacan — El Chapo Isidro
]


# ------------------------------------------------------------------- art
def art_ship(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 60, 110))
    d.polygon([(x0 + 20, y0 + h - 18), (x0 + w - 20, y0 + h - 18),
               (x0 + w - 35, y0 + h - 6), (x0 + 35, y0 + h - 6)], fill=WHITE)
    d.rectangle([x0 + w // 2 - 14, y0 + 8, x0 + w // 2 + 14, y0 + h - 18], fill=WHITE)
    d.line([x0 + w // 2, y0 + 8, x0 + w // 2, y0 + 2], fill=WHITE, width=2)
    for i in range(3):
        d.arc([x0 + 8 + i * 14, y0 + h - 12, x0 + 20 + i * 14, y0 + h - 2],
              0, 180, fill=GOLD, width=2)


def art_blast(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(60, 20, 20))
    for r, col in [(26, (220, 80, 40)), (18, (240, 160, 40)), (10, (250, 230, 120))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        d.line([cx, cy, cx + int(30 * math.cos(a)), cy + int(30 * math.sin(a))],
               fill=(240, 160, 40), width=2)


def art_target(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(25, 25, 40))
    for r, col in [(24, (200, 40, 40)), (17, WHITE), (10, (200, 40, 40)), (4, WHITE)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def art_warning(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 30, 10))
    d.polygon([(cx, cy - 24), (cx + 26, cy + 18), (cx - 26, cy + 18)], fill=GOLD)
    d.rectangle([cx - 2, cy - 12, cx + 2, cy + 6], fill=(40, 30, 10))
    d.ellipse([cx - 2, cy + 10, cx + 2, cy + 14], fill=(40, 30, 10))


def art_chart(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(15, 45, 30))
    d.line([x0 + 12, y0 + h - 14, x0 + 60, y0 + h - 30, x0 + 110, y0 + h - 22,
            x0 + 160, y0 + 12], fill=(80, 220, 120), width=3)
    d.ellipse([x0 + 154, y0 + 6, x0 + 166, y0 + 18], fill=(80, 220, 120))
    for gx in range(4):
        d.line([x0 + 12 + gx * 48, y0 + h - 10, x0 + 12 + gx * 48, y0 + h - 14],
               fill=GREY, width=1)


def art_syringe(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(230, 240, 245))
    d.rectangle([cx - 22, cy - 6, cx + 10, cy + 6], fill=(120, 180, 220))
    d.rectangle([cx - 28, cy - 10, cx - 22, cy + 10], fill=(60, 90, 130))
    d.line([cx + 10, cy, cx + 34, cy], fill=(60, 90, 130), width=2)
    d.line([cx - 34, cy - 8, cx - 34, cy + 8], fill=(60, 90, 130), width=3)
    for i in range(3):
        d.line([cx - 14 + i * 8, cy - 6, cx - 14 + i * 8, cy + 6], fill=WHITE, width=1)


def art_chip(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(20, 25, 45))
    d.rectangle([cx - 20, cy - 20, cx + 20, cy + 20], fill=(40, 90, 140))
    d.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=(20, 25, 45))
    for i in range(3):
        d.line([cx - 20 + i * 20, cy - 28, cx - 20 + i * 20, cy - 20], fill=GOLD, width=2)
        d.line([cx - 20 + i * 20, cy + 20, cx - 20 + i * 20, cy + 28], fill=GOLD, width=2)
        d.line([cx - 28, cy - 20 + i * 20, cx - 20, cy - 20 + i * 20], fill=GOLD, width=2)
        d.line([cx + 20, cy - 20 + i * 20, cx + 28, cy - 20 + i * 20], fill=GOLD, width=2)


def art_ball(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(25, 70, 35))
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(185, 30, 30))
    d.arc([cx - 24, cy - 24, cx + 24, cy + 24], 300, 60, fill=WHITE, width=2)
    d.arc([cx - 24, cy - 24, cx + 24, cy + 24], 120, 240, fill=WHITE, width=2)
    d.line([x0 + 8, y0 + h - 8, x0 + w - 8, y0 + h - 8], fill=GOLD, width=2)


def art_scales(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(35, 30, 55))
    d.line([cx, cy - 22, cx, cy + 20], fill=GOLD, width=3)
    d.line([cx - 22, cy - 14, cx + 22, cy - 14], fill=GOLD, width=3)
    for sx in (cx - 22, cx + 22):
        d.line([sx, cy - 14, sx, cy + 2], fill=GOLD, width=2)
        d.polygon([(sx - 12, cy + 2), (sx + 12, cy + 2), (sx, cy + 14)], fill=GOLD)
    d.rectangle([cx - 16, cy + 20, cx + 16, cy + 24], fill=GOLD)


def art_cuff(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(25, 25, 30))
    for ox in (cx - 20, cx + 20):
        d.ellipse([ox - 13, cy - 13, ox + 13, cy + 13], outline=(180, 180, 190), width=4)
    d.line([cx - 7, cy, cx + 7, cy], fill=(180, 180, 190), width=3)


def art_drone(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(20, 30, 50))
    d.rectangle([cx - 10, cy - 7, cx + 10, cy + 7], fill=(150, 160, 180))
    for sx, sy in ((-24, -14), (24, -14), (-24, 14), (24, 14)):
        d.line([cx, cy, cx + sx, cy + sy], fill=(150, 160, 180), width=2)
        d.ellipse([cx + sx - 8, cy + sy - 3, cx + sx + 8, cy + sy + 3], fill=(200, 210, 220))


SMALL_ART = {
    "ship": art_ship, "blast": art_blast, "target": art_target,
    "warning": art_warning, "chart": art_chart, "syringe": art_syringe,
    "chip": art_chip, "ball": art_ball, "scales": art_scales,
    "cuff": art_cuff, "drone": art_drone,
}


def art_probe(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(20, 35, 70))
    d.polygon([(x0 + 30, y0 + h - 16), (x0 + 150, y0 + h - 16),
               (x0 + 135, y0 + h - 4), (x0 + 45, y0 + h - 4)], fill=WHITE)
    d.rectangle([x0 + 80, y0 + 14, x0 + 110, y0 + h - 16], fill=WHITE)
    d.ellipse([x0 + 210, y0 + 8, x0 + 250, y0 + 48], outline=GOLD, width=3)
    d.line([x0 + 238, y0 + 40, x0 + 258, y0 + 54], fill=GOLD, width=3)
    d.line([x0 + 10, y0 + h - 6, x0 + w - 10, y0 + h - 6], fill=GOLD, width=2)


def art_gavel(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(45, 30, 25))
    d.rectangle([x0 + 40, y0 + 10, x0 + 170, y0 + 34], fill=(240, 235, 220))
    for i in range(4):
        d.line([x0 + 60 + i * 28, y0 + 12, x0 + 60 + i * 28, y0 + 32], fill=GREY, width=1)
    d.rectangle([x0 + 210, y0 + 8, x0 + 240, y0 + 22], fill=(150, 100, 50))
    d.rectangle([x0 + 222, y0 + 22, x0 + 228, y0 + 50], fill=(150, 100, 50))
    d.rectangle([x0 + 180, y0 + 46, x0 + 270, y0 + 52], fill=(150, 100, 50))


def art_shield(d, x0, y0, w, h):
    cx, cy = x0 + w // 2, y0 + h // 2
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(15, 30, 55))
    d.polygon([(cx, cy - 26), (cx + 24, cy - 16), (cx + 24, cy + 8),
               (cx, cy + 28), (cx - 24, cy + 8), (cx - 24, cy - 16)],
              fill=(40, 90, 160), outline=WHITE)
    d.line([cx, cy - 18, cx, cy + 18], fill=WHITE, width=3)
    d.line([cx - 12, cy - 6, cx + 12, cy - 6], fill=WHITE, width=3)
    d.line([x0 + 16, y0 + h - 8, x0 + 60, y0 + h - 8], fill=GOLD, width=2)
    d.line([x0 + w - 60, y0 + h - 8, x0 + w - 16, y0 + h - 8], fill=GOLD, width=2)


HERO_ART = {"probe": art_probe, "gavel": art_gavel, "shield": art_shield}


# ---------------------------------------------------------------- drawing
def draw_top(d):
    f = load("DejaVuSans-Bold.ttf", 11)
    one_line(d, TOP_BAR, f, RX - MX, "top bar")
    d.text(((W - text_w(d, TOP_BAR, f)) / 2, 11), TOP_BAR, font=f, fill=INK)
    d.line([MX, 28, RX, 28], fill=INK, width=1)


def draw_masthead(d, img):
    f = load("DejaVuSerif-Bold.ttf", 56)
    one_line(d, MASTHEAD, f, RX - MX, "masthead")
    d.text((MX, 34), MASTHEAD, font=f, fill=INK)
    cap = italic_layer(SUBLINE, load("DejaVuSerif.ttf", 17), RED)
    if cap.width > RX - MX:
        raise AssertionError("OVERFLOW subline: %dpx" % cap.width)
    img.paste(cap, (MX, 98), cap)


def draw_stats(d):
    fn = load("DejaVuSans-Bold.ttf", 22)
    fc = load("DejaVuSans.ttf", 10)
    col_w = (RX - MX) // 6
    for i, (num, cap) in enumerate(STATS):
        x = MX + i * col_w
        one_line(d, num, fn, col_w - 8, "stat number %s" % num)
        one_line(d, cap, fc, col_w - 8, "stat caption %s" % cap)
        d.text((x, 126), num, font=fn, fill=RED)
        d.text((x, 152), cap, font=fc, fill=INK)
    d.line([MX, 172, RX, 172], fill=GREY, width=1)


def draw_regions(d):
    f = load("DejaVuSans-Bold.ttf", 11)
    x = MX
    for name, count, colour, seg_w in REGIONS:
        label = "%s %d" % (name, count)
        one_line(d, label, f, seg_w - 8, "region %s" % name)
        d.rectangle([x, 180, x + seg_w, 202], fill=colour)
        d.text((x + 6, 186), label, font=f, fill=WHITE)
        x += seg_w
    if x != RX:
        raise AssertionError("OVERFLOW region bar: ends at %d, expected %d" % (x, RX))


def draw_heroes(d):
    f_head = load("DejaVuSans-Bold.ttf", 24)
    f_sub = load("DejaVuSerif.ttf", 11)
    for i, (head, sub, kind) in enumerate(HEROES):
        x0 = MX + i * 336
        d.line([x0, 212, x0 + 328, 212], fill=RED, width=2)
        lines = fit(d, head, f_head, 328, 2, "hero %d head" % (i + 1))
        draw_lines(d, lines, x0, 220, f_head, INK, 28)
        HERO_ART[kind](d, x0, 280, 328, 55)
        lines = fit(d, sub, f_sub, 328, 2, "hero %d sub" % (i + 1))
        draw_lines(d, lines, x0, 342, f_sub, INK, 13)


def draw_smalls(d):
    f_title = load("DejaVuSans-Bold.ttf", 10)
    f_kick = load("DejaVuSans-Bold.ttf", 9)
    f_head = load("DejaVuSerif-Bold.ttf", 15)
    f_sub = load("DejaVuSerif.ttf", 9)
    cols = [12, 213, 414, 615, 816]
    widths = [195, 195, 195, 195, 195]
    for row in range(2):
        ty = 373 if row == 0 else 521
        ay = 393 if row == 0 else 541
        ky = 457 if row == 0 else 605
        hy = 470 if row == 0 else 618
        sy = 501 if row == 0 else 649
        for col in range(5):
            idx = row * 5 + col
            title, kicker, head, sub, kind = SMALLS[idx]
            x0 = cols[col]
            w = widths[col]
            one_line(d, title, f_title, w - 8, "small %d title" % (idx + 4))
            d.rectangle([x0, ty, x0 + w, ty + 19], fill=RED)
            d.text((x0 + 6, ty + 4), title, font=f_title, fill=WHITE)
            SMALL_ART[kind](d, x0, ay, w, 61)
            one_line(d, kicker, f_kick, w, "small %d kicker" % (idx + 4))
            d.text((x0, ky), kicker, font=f_kick, fill=RED)
            lines = fit(d, head, f_head, w, 2, "small %d head" % (idx + 4))
            draw_lines(d, lines, x0, hy, f_head, INK, 16)
            lines = fit(d, sub, f_sub, w, 2, "small %d sub" % (idx + 4))
            draw_lines(d, lines, x0, sy, f_sub, INK, 10)


def draw_map(d, img):
    f_head = load("DejaVuSans-Bold.ttf", 12)
    d.text((MX, 675), "WHERE IT HAPPENED", font=f_head, fill=INK)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=NAVY)
    # Equator, dashed, drawn before the land so it shows only over sea.
    eq_y = int(round(project(0, 0)[1]))
    x = MAP_X0
    while x < MAP_X1:
        d.line(
            [x, eq_y, min(x + 5, MAP_X1), eq_y],
            fill=(110, 130, 160), width=1,
        )
        x += 10
    for land in LANDMASSES:
        d.polygon(project_poly(land), fill=TAN, outline=EDGE)
    d.polygon(project_poly(CASPIAN), fill=NAVY)
    f_pin = load("DejaVuSans-Bold.ttf", 10)
    for num, tlon, tlat, slon, slat in PINS:
        tx, ty = project(tlon, tlat)
        if slon is None:
            dx, dy = tx, ty
        else:
            dx, dy = project(slon, slat)
            d.line([dx, dy, tx, ty], fill=(220, 220, 220), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=WHITE)
        d.ellipse(
            [dx - 7, dy - 7, dx + 7, dy + 7], fill=RED, outline=WHITE,
            width=1,
        )
        t = str(num)
        d.text(
            (dx - text_w(d, t, f_pin) / 2, dy - 6), t, font=f_pin,
            fill=WHITE,
        )
    cap = italic_layer(MAP_CAPTION, load("DejaVuSerif.ttf", 11), GREY)
    if cap.width > MAP_X1 - MAP_X0:
        raise AssertionError("OVERFLOW map caption")
    img.paste(cap, (MX, 915), cap)


def draw_also(d):
    f_head = load("DejaVuSans-Bold.ttf", 13)
    head = "ALSO ON TUESDAY 24 NOVEMBER \u2014 22 MORE STORIES"
    one_line(d, head, f_head, RX - 420, "also header")
    d.text((420, 675), head, font=f_head, fill=INK)
    f_bold = load("DejaVuSans-Bold.ttf", 11)
    f_reg = load("DejaVuSans.ttf", 11)
    cols = [(420, 280), (712, 298)]
    for i, (num, region, brief) in enumerate(ALSO):
        col = 0 if i < 11 else 1
        cx, cwid = cols[col]
        y = 695 + (i % 11) * 20
        n = str(num)
        head_txt = region + ": "
        total = (
            text_w(d, n, f_bold) + 4 + text_w(d, head_txt, f_bold)
            + text_w(d, brief, f_reg)
        )
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
    f_title = load("DejaVuSans-Bold.ttf", 10)
    f_item = load("DejaVuSans.ttf", 9)
    one_line(d, DATE_CHECK_TITLE, f_title, RX - MX - 16, "date check title")
    d.text((MX + 8, 933), DATE_CHECK_TITLE, font=f_title, fill=RED)
    for i, row in enumerate(DATE_CHECK_ROWS):
        one_line(d, row, f_item, RX - MX - 16, "date check row %d" % (i + 1))
        d.text((MX + 8, 947 + i * 12), row, font=f_item, fill=INK)


def draw_sources(d):
    f = load("DejaVuSans.ttf", 9)
    one_line(d, SOURCES, f, RX - MX, "sources")
    d.text((MX, 996), SOURCES, font=f, fill=GREY)


def build(out_path: str) -> None:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_top(d)
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


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    build(str(here / "entry.png"))
