# CRT Phosphor Dot-Scanline Converter

Rebuilds photos/renders from discrete glowing phosphor dots on horizontal
scanlines, in linear-light with multi-octave bloom. Two modes: `scan`
(static grid) and `rutt` (Rutt-Etra style, lines pushed up by local
luminance).

## Usage

```
python crt_phosphor.py <input file or folder> -o <outdir> [options]
```

Key options: `--mode scan|rutt`, `--tint keep|blue|cyan|green|amber|#hex`,
`--pitch`, `--dot`, `--dotsize`, `--displace`, `--wobble`, `--dropout`,
`--cutoff`, `--gain`, `--gamma`, `--bloom`, `--bg`, `--width`,
`--supersample`, `--seed`, `--frames` (process every frame of an animated
GIF and re-encode as animated GIF).

Example commands used for the acceptance test:

```
python crt_phosphor.py test_input.png -o out_final --mode scan --tint blue --width 1000
python crt_phosphor.py test_input.png -o out_final --mode rutt --tint cyan --width 1000 --displace 40 --pitch 8
python crt_phosphor.py test_input.png -o out_final --mode scan --tint keep --width 1000
```

`test_input.png` is a synthetic dark-background soft-lit sphere with a
specular highlight, generated for the acceptance test (see git history /
`acceptance_strip.png` for the before/after comparison).

## Acceptance checklist (verified)

- Dot grid resolvable at 100% zoom — yes (pitch/dot px individually visible).
- Dropout grain in midtones/shadow edges — yes (stochastic, seeded).
- White hot core with colored halo — yes (ramp overdrive + tinted bloom).
- 3-octave glow (tight/medium/wide, wide tinted) — yes.
- Rutt mode: lines rise continuously over the bright form, no
  stair-stepping (sub-pixel bilinear scatter) — yes.
- Background stays near-black — yes.
- ~1500px image processes in a few seconds (mip-style downsample for wide
  bloom octaves keeps it well under the target).

## Notes on source material

The effect favors a **dark background with a distinctly lit subject** —
that's what produces the signature dropout grain in shadow and a clean
bloom halo around highlights. For flat/bright/low-contrast sources:

- Raise `--cutoff` and lower `--gain` so more of the image counts as
  "background" and gets dropout instead of a solid dot field.
- Lower `--dropout` floor if too much of the midtones vanish.
- Reduce `--bloom` if a bright/high-key source blows out into a
  featureless glow.
