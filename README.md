# Tuesday 24 November 2026: 35 stories, 6 regions — THE WORLD IN ONE DAY

[![News image 24 Nov](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![Rank](https://make.fun/badge/news-image-20261124/pesertaerdrop/news-image-24nov-entry/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/pesertaerdrop/news-image-24nov-entry/reward.svg)](https://make.fun/bounty/news-image-20261124)

A one-page newspaper front page that sums up the world's news of
Tuesday 24 November 2026 in a single image: 35 stories across 6
regions — 3 heroes, 10 smalls and 22 ALSO items — plus a world map
with 13 numbered pins, a stat strip, a region bar and a DATE CHECK
box listing the big stories that were *not* from 24 November.

## What happened that day

- **Zaporizhzhia hit, 2 killed** — a Russian strike wounds 22,
  including 2 children, in the city.
- **Russian jets breach Korea's zone** — Seoul scrambles fighters
  and warns Ulleung islanders as jets enter the ADIZ.
- **Britain probes nuclear-test veterans** — PM Burnham sets up an
  independent panel on the 45 nuclear tests of 1952–91.
- **Nikkei jumps 3.9%** as Jensen Huang returns to Nvidia;
  **Priyansh Arya smashes a record 181**; **Equinor signs an
  18-year gas deal** with Germany's VNG; **Shenzhou-24's crew** is
  unveiled with Pakistan's Zeeshan Ali aboard; **Senegal are
  reinstated as Africa Cup winners** by CAS; and **Canada courts
  allies for a €100bn global defence bank**.

Every story was checked against its primary source article
(Reuters, AJU Press, IANS, WSJ/AP, Cricinfo, The Standard, eNCA,
TVNZ/PACNEWS, crex) for the event itself happening — or first being
reported — on 24 November 2026, not merely an article timestamp
from that day.

## How it works

`main.py` copies the pre-built `entry.png` (1024×1024, under 1 MiB)
into `MAKEFUN_OUTPUT_DIR`. The image itself is drawn offline by
`make_image.py` (Pillow only, no network): masthead, subline, stat
strip, region bar, three hero panels with drawn scenes, ten small
stories, a filled-continent world map with 13 pins, the ALSO column,
the DATE CHECK box and the sources line. Every text block is
measured before drawing and guarded by a hard overflow assert, so
the build fails loudly instead of producing clipped text.

## Run

```sh
python3 make_image.py   # regenerates entry.png (offline)
python3 main.py         # copies entry.png to $MAKEFUN_OUTPUT_DIR
```

## License

MIT — see LICENSE.
