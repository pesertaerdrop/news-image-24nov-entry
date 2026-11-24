# THE WORLD IN ONE DAY — Tuesday 24 November 2026

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/pesertaerdrop/news-image-24nov-entry/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/pesertaerdrop/news-image-24nov-entry/reward.svg)](https://make.fun/bounty/news-image-20261124)

One front page that sums up **Tuesday 24 November 2026** in a single image:
35 stories from 7 regions, each one dated that day.

## What's on the page

- **Three lead stories**: the UN's call for a probe into attacks off Libya,
  the SpaceX/Grok abuse-images lawsuit, and Estonia's stand against
  Moscow's airspace claim.
- **Ten small leads**: record Hormuz attacks, Gaza strikes, the Hodeida
  strike, Trump's warning to Iran, the Nikkei rally, Bangladesh's typhoid
  drive, SoftBank's Intel bet, Arya's record 181, Revanna's life term,
  and the capture of "El Chapo Isidro".
- **Twenty-two more stories** in the ALSO column, from a Thai-Cambodia
  truce to Ethereum fund outflows.
- **A realistic world map**: navy sea, filled tan continents, a dashed
  equator, and thirteen numbered pins at the places where the stories
  happened — Benghazi, Portland, Tallinn, the Strait of Hormuz, Gaza,
  Hodeida, Tehran, Tokyo, Dhaka, Santa Clara, Indore, Bengaluru,
  Culiacán.
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
