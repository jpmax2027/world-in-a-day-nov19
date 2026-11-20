# world-in-a-day-nov19

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/jpmax2027/world-in-a-day-nov19/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/jpmax2027/world-in-a-day-nov19/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A newspaper front page that sums up one day of world news — Thursday 19 November 2026 — in a single 1024×1024 image: Trump, Xi and Putin's first three-way summit in Shenzhen and their joint "peace declaration" as the lead, Trump saying the US will "see what happens" in the Iran war after Jan. 1, 2027, the UN's top court ruling Myanmar committed genocide against the Rohingya, Ukraine hitting the Crimean Bridge a third time in a week, and Anthropic's record $81.3 billion IPO, plus a strip and ticker of the day's smaller stories.

The image is drawn entirely from code by `main.py`, a dependency-free Python program with its own tiny rasterizer, an embedded bitmap font, and a built-in PNG encoder — no image assets, no network, and every run produces byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` (1024×1024, about 26 KiB) to the directory named by the `MAKEFUN_OUTPUT_DIR` environment variable, or to `/output` when that is not set.

---

<sub>Entered on [make.fun](https://make.fun/?ref=zbqpv30a&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
