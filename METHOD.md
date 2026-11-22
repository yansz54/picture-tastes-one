# Method

`main.py` renders a 1024x1024 ramen bowl into a pixel buffer and encodes
the PNG by hand (`zlib` + `struct`, filter byte 0 per scanline). No third-party
libraries, no network, no fonts, no text in the image.

## Layers, back to front

1. **Table** — warm dark wooden planks with grain noise (deterministic
   integer hash, fixed seed) and a soft pool of warm light, upper left.
2. **Bowl** — deep indigo ceramic body with a warm sheen, a gold decorative
   band, and a thick cream rim.
3. **Broth** — red-brown radial glow (deep at the rim, glowing at the
   centre), chilli-oil ribbons, oil droplets with specular dots, and a broad
   glossy highlight plus a sharp specular streak to sell the oil sheen.
4. **Noodles** — ~30 wavy golden strands (sine curves with shaded
   undersides) plus a tight wound twirl mound in the centre-left.
5. **Toppings** — three seared chashu slices (caramelised rim, rosy meat,
   subtle fat marbling, browned flecks), two egg halves with glossy orange
   yolks, scallion rings, menma sticks, and a nori sheet with a vertical
   sheen standing at the back of the bowl.
6. **Chopsticks** — two wooden sticks resting diagonally across the rim.
7. **Steam** — seven translucent rising wisps, wider and softer as they
   climb, so the heat reads even at ~300 px.
8. **Light** — warm directional light from the upper left and a gentle
   vignette, applied in a final pass.

## Determinism

Every value comes from fixed constants and a deterministic integer hash of
pixel coordinates. There is no `random`, no time, no dict-order dependence.
Two runs produce byte-identical PNGs (verified with sha256).

## Verification

- `python3 main.py` runs in ~13 s.
- Output: 1024x1024 PNG, 772,661 bytes (limit 1,048,576).
- sha256 identical across two consecutive runs.
- Image inspected visually: bowl fills the frame, dish reads clearly at
  small size, no text, no smears or broken shapes.
