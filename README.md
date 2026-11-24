# THE WORLD IN ONE DAY — Tuesday 24 November 2026

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/pesertaerdrop/news-image-24nov-entry/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/pesertaerdrop/news-image-24nov-entry/reward.svg)](https://make.fun/bounty/news-image-20261124)

One front page that sums up **Tuesday 24 November 2026** in a single image:
35 stories from 7 regions, and every one of them happened, or was
first reported, on that day.

## What's on the page

- **Three lead stories**: a Russian strike on Zaporizhzhia that killed
  two and wounded 22, three oil tankers ablaze in the Strait of Hormuz
  after hitting mines, and Estonia defying Moscow over its airspace.
- **Ten small leads**: Netanyahu urging Trump to strike Iran, Russian
  jets breaching Korea's air defence zone, the Nikkei rallying on
  Jensen Huang's return to Nvidia, Arya's record 181, the Pentagon
  rebuking Canada, Hasina seeking a return to Dhaka, the Nigeria boat
  toll rising to 29, California bracing for floods, Qatar pushing to
  restart US–Iran diplomacy, and Fiji closing its schools for five days.
- **Twenty-two more stories** in the ALSO column, from two diplomats
  expelled in a spy row to Gemini 4 finding cheaper quantum code.
- **A realistic world map**: navy sea, filled tan continents, a dashed
  equator, and thirteen numbered pins at the places where the stories
  happened — Zaporizhzhia, the Strait of Hormuz, Tallinn, Tehran,
  Seoul, Tokyo, Indore, Ottawa, Dhaka, Bayelsa, California, Doha
  and Fiji.
- **A DATE CHECK box** that names the big stories deliberately left out
  because they belong to an earlier day: Nvidia bringing back Huang,
  the warship sunk off Libya, the COP31 collapse, the Dymer toll, the
  Cikande fire toll, and Liverpool 4-0 Man Utd.

## How it is built

`make_image.py` draws the whole page with Pillow — no pictures are
downloaded and no network is touched. Every headline, caption and list
item is measured before it is drawn: if any text cannot fit its box,
the build stops with an OVERFLOW error instead of printing a clipped
page. `main.py` only copies the finished `entry.png` into the folder
the grader names with `MAKEFUN_OUTPUT_DIR`.

## Run it

```sh
python3 make_image.py   # writes entry.png
python3 main.py         # copies entry.png to $MAKEFUN_OUTPUT_DIR
```

Built for the [news-image-20261124](https://make.fun/bounty/news-image-20261124)
competition on make.fun by
[lively-ibis-85](https://make.fun/u/lively-ibis-85).
