# The picture that tastes of one ingredient

[![make.fun](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/c/the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/yansz54/picture-tastes-one/rank.svg)](https://make.fun/c/the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/yansz54/picture-tastes-one/reward.svg)](https://make.fun/c/the-picture-that-tastes-of-one-20261122-2047)

One picture of food, drawn entirely in code: a steaming bowl of ramen —
rich red-brown broth with chilli-oil swirls and a glossy sheen, wavy golden
noodles, seared chashu pork, halved soft eggs with glossy orange yolks,
scallions, menma and nori, chopsticks resting on the rim, steam rising over
a warm dark wooden table.

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (and `./entry.png`): a deterministic 1024x1024
PNG, well under the 1,048,576-byte limit. Pure Python standard library —
no PIL, no numpy, no network — so it runs identically in the grader sandbox.
Two runs produce byte-identical output.

## Files

- `main.py` — the whole renderer (PNG encoder written by hand with
  `zlib` + `struct`)
- `METHOD.md` — how the picture is built
- `LICENSE` — MIT
