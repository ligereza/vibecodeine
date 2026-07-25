#!/usr/bin/env python3
"""
crtdots.py — CRT phosphor dot-scanline / Rutt-Etra converter.

Re-synthesizes an image as discrete glowing phosphor dots on horizontal
scanlines, with stochastic shadow dropout, multi-scale bloom and an
optional Rutt-Etra luminance displacement mode. All compositing happens
in linear light; output is tonemapped with a soft filmic curve.

Dependencies: numpy, pillow, scipy.

Examples:
    python crtdots.py photo.jpg --mode scan --tint blue -o out
    python crtdots.py renders/ --mode rutt --tint cyan --displace 30 -o out
    python crtdots.py anim.gif --frames --tint amber -o out
    python crtdots.py --maketest test.png
"""

import argparse
import os
import sys
import time

import numpy as np
from PIL import Image, ImageSequence
from scipy.ndimage import gaussian_filter, map_coordinates

# ---------------------------------------------------------------- color

GAMMA = 2.2
REC709 = np.array([0.2126, 0.7152, 0.0722])

NAMED_TINTS = {           # sRGB, normalized later in linear space
    "blue":  (0.30, 0.55, 1.00),
    "cyan":  (0.25, 1.00, 0.95),
    "green": (0.30, 1.00, 0.35),
    "amber": (1.00, 0.62, 0.12),
}


def srgb_to_linear(x):
    return np.clip(x, 0.0, None) ** GAMMA


def linear_to_srgb(x):
    return np.clip(x, 0.0, None) ** (1.0 / GAMMA)


def parse_hex(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"bad hex color: #{s}")
    return np.array([int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def parse_tint(s):
    """Returns None for 'keep', else a linear-light RGB tint (max chan = 1)."""
    s = s.lower()
    if s == "keep":
        return None
    rgb = np.array(NAMED_TINTS[s]) if s in NAMED_TINTS else parse_hex(s)
    lin = srgb_to_linear(rgb)
    return lin / max(lin.max(), 1e-6)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / max(e1 - e0, 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def luminance(rgb):
    return rgb @ REC709


def mean_pool(img, factor):
    h, w = img.shape[:2]
    hp, wp = -(-h // factor) * factor, -(-w // factor) * factor
    pad = np.pad(img, ((0, hp - h), (0, wp - w), (0, 0)), mode="edge")
    small = pad.reshape(hp // factor, factor, wp // factor, factor, 3)
    return small.mean(axis=(1, 3), dtype=np.float32)


def upsample(img, size_wh):
    """Fast bilinear upsample of an HxWx3 float32 array via PIL."""
    return np.stack(
        [np.asarray(Image.fromarray(img[..., c]).resize(size_wh,
                                                        Image.BILINEAR))
         for c in range(3)], axis=-1)

# ---------------------------------------------------------------- core render


def render(src, p, seed):
    """src: HxWx3 float sRGB in [0,1]. Returns HxWx3 uint8 sRGB at 1x scale."""
    rng = np.random.default_rng(seed)
    S = p.supersample

    # 1. working size, supersampled internally
    w1 = p.width
    h1 = max(1, round(src.shape[0] * w1 / src.shape[1]))
    im = Image.fromarray((np.clip(src, 0, 1) * 255).astype(np.uint8))
    im = im.resize((w1 * S, h1 * S), Image.LANCZOS)
    W, H = im.size

    # 2. linear light — every buffer below lives here (LUT: input is uint8)
    lut = srgb_to_linear(np.arange(256, dtype=np.float32) / 255.0)
    lin = lut[np.asarray(im)]

    # 3. luminance shaping: gain, gamma, soft shadow toe
    L = luminance(lin).astype(np.float32)
    Ls = (L * p.gain) ** p.gamma
    if p.cutoff > 0:
        Ls = Ls * smoothstep(p.cutoff * 0.5, p.cutoff * 1.5, Ls)
    samp_field = gaussian_filter(Ls, 0.5 * S)                    # dot sampling
    disp_field = gaussian_filter(Ls, max(1.0, 0.6 * p.pitch) * S)  # rutt relief

    # 4. scanline / dot grid (pitches are given at 1x scale)
    py, px = p.pitch * S, p.dot * S
    ys = np.arange(py * 0.5, H - 0.5, py, dtype=np.float32)
    xs = np.arange(px * 0.5, W - 0.5, px, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)

    # 5. positions: sinusoidal x-wobble (random phase per line) + rutt lift
    if p.wobble > 0:
        ph1 = rng.uniform(0, 2 * np.pi, (len(ys), 1)).astype(np.float32)
        ph2 = rng.uniform(0, 2 * np.pi, (len(ys), 1)).astype(np.float32)
        X = X + p.wobble * S * (
            0.7 * np.sin(2 * np.pi * X / (110.0 * S) + ph1)
            + 0.3 * np.sin(2 * np.pi * X / (41.0 * S) + ph2))
    coords = np.stack([Y.ravel(), X.ravel()])
    I = map_coordinates(samp_field, coords, order=1, mode="nearest")
    if p.mode == "rutt":
        lift = map_coordinates(disp_field, coords, order=1, mode="nearest")
        Yd = Y.ravel() - lift * p.displace * S
    else:
        Yd = Y.ravel().copy()
    Xd = X.ravel()

    # 6. stochastic dropout weighted by darkness (seeded — reproducible)
    keep = I > 1e-4
    if p.dropout > 0:
        prob = np.clip(I / p.dropout, 0.0, 1.0) ** 0.7
        keep &= rng.random(I.shape) < prob
    keep &= (Xd >= 0) & (Xd <= W - 1.001) & (Yd >= 0) & (Yd <= H - 1.001)
    I, Xd, Yd = I[keep], Xd[keep], Yd[keep]

    # per-dot chroma: forced palette tint, or source chromaticity ("keep")
    if p.tint_rgb is None:
        eps = 1e-5
        chroma = np.stack(
            [map_coordinates(lin[..., c], coords, order=1, mode="nearest")
             for c in range(3)], axis=-1)[keep]
        chroma /= luminance(chroma)[:, None] + eps
        chroma /= chroma.max(axis=1, keepdims=True) + eps
        palette = chroma * I[:, None]
        palette = palette.sum(0) / max(I.sum(), eps)   # haze color = mean chroma
        palette /= max(palette.max(), eps)
    else:
        chroma = p.tint_rgb[None, :].astype(np.float32)
        palette = p.tint_rgb

    # 7. scatter bilinear-weighted impulses (sub-pixel accuracy)
    x0, y0 = np.floor(Xd).astype(np.int64), np.floor(Yd).astype(np.int64)
    fx, fy = Xd - x0, Yd - y0
    idx = np.concatenate([(y0 + dy) * W + (x0 + dx)
                          for dy, dx in ((0, 0), (0, 1), (1, 0), (1, 1))])
    wgt = np.concatenate([(1 - fx) * (1 - fy), fx * (1 - fy),
                          (1 - fx) * fy, fx * fy]) * np.tile(I, 4)
    fbuf = np.bincount(idx, wgt, minlength=H * W)
    fbuf = fbuf.reshape(H, W).astype(np.float32)
    if chroma.shape[0] == 1:                       # mono tint: scalar suffices
        buf = fbuf[..., None] * chroma[0]
    else:
        ch4 = np.tile(chroma, (4, 1))
        buf = np.stack([np.bincount(idx, wgt * ch4[:, c], minlength=H * W)
                        for c in range(3)], -1).reshape(H, W, 3)
        buf = buf.astype(np.float32)

    # 8. dot body: small Gaussian, energy renormalized so peak == intensity
    sd = p.dotsize * S
    norm = 2.0 * np.pi * sd * sd
    fb = gaussian_filter(fbuf, sd) * norm
    if chroma.shape[0] == 1:
        body = fb[..., None] * chroma[0]
    else:
        body = gaussian_filter(buf, (sd, sd, 0)) * norm

    # 9. bloom: three octaves, wider ones tinted toward palette + ambient haze
    #    (fill compensates blur energy dilution so halo scales with dot peaks;
    #     octaves run on a mean-pooled level, one bilinear upsample at the end)
    fill = norm / (py * px)
    fac = 4
    small = mean_pool(body, fac)
    glow = np.zeros_like(small)
    wide = None
    for sig, wgt, mix in ((2.0, 0.28, 0.15), (7.0, 0.20, 0.50),
                          (20.0, 0.12, 0.85)):
        B = gaussian_filter(small, (sig * S / fac, sig * S / fac, 0))
        B *= p.bloom * wgt / fill
        lb = luminance(B)
        glow += B * (1.0 - mix) + lb[..., None] * palette[None, None, :] * mix
        wide = lb
    glow += palette[None, None, :] * (float(wide.mean()) * 0.8)  # ambient
    out = body + upsample(glow, (W, H))
    hot = np.clip(fb - 0.60, 0.0, None) ** 1.3 * 4.0             # white-hot core
    out += hot[..., None]
    out += srgb_to_linear(parse_hex(p.bg))[None, None, :]

    # 10. filmic rolloff x/(1+kx) normalized to a whitepoint, then Lanczos
    #     downsample (still linear), then sRGB encode at final resolution
    k, wp = 0.8, 1.6
    out = np.clip(out / (1.0 + k * out) * ((1.0 + k * wp) / wp), 0.0, 1.0)
    out = np.stack(
        [np.asarray(Image.fromarray(out[..., c]).resize((w1, h1),
                                                        Image.LANCZOS))
         for c in range(3)], axis=-1)
    out = linear_to_srgb(np.clip(out, 0.0, 1.0))
    return Image.fromarray((out * 255.0 + 0.5).astype(np.uint8))

# ---------------------------------------------------------------- io / batch


def process_path(path, p, outdir):
    name, ext = os.path.splitext(os.path.basename(path))
    dst = os.path.join(outdir, f"{name}_{p.mode}.png")
    t0 = time.time()
    if ext.lower() == ".gif" and p.frames:
        src = Image.open(path)
        frames, durs = [], []
        for i, fr in enumerate(ImageSequence.Iterator(src)):
            a = np.asarray(fr.convert("RGB"), np.float32) / 255.0
            frames.append(render(a, p, p.seed + i))
            durs.append(fr.info.get("duration", 66))
        dst = os.path.join(outdir, f"{name}_{p.mode}.gif")
        frames[0].save(dst, save_all=True, append_images=frames[1:],
                       duration=durs, loop=src.info.get("loop", 0))
    else:
        a = np.asarray(Image.open(path).convert("RGB"), np.float32) / 255.0
        render(a, p, p.seed).save(dst)
    print(f"  {path} -> {dst}  ({time.time() - t0:.2f}s)")


def make_test(path):
    """Synthetic acceptance image: dark bg, soft-lit sphere, specular spot."""
    w, h = 1024, 768
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    img = np.full((h, w, 3), 0.015, np.float32)
    img[..., 2] += 0.008 * (yy / h)                       # faint floor gradient
    cx, cy, r = w * 0.46, h * 0.52, h * 0.30
    dx, dy = (xx - cx) / r, (yy - cy) / r
    rr = dx * dx + dy * dy
    inside = rr < 1.0
    nz = np.sqrt(np.clip(1.0 - rr, 0.0, 1.0))
    ldir = np.array([-0.55, -0.6, 0.58])
    ldir /= np.linalg.norm(ldir)
    lam = np.clip(dx * ldir[0] + dy * ldir[1] + nz * ldir[2], 0.0, 1.0)
    shade = 0.03 + 0.85 * lam ** 1.4
    col = np.stack([shade * 0.95, shade * 0.82, shade * 0.68], -1)  # warm skin
    img[inside] = col[inside]
    hx, hy = cx - r * 0.38, cy - r * 0.42                 # specular highlight
    spec = np.exp(-(((xx - hx) ** 2 + (yy - hy) ** 2) / (2 * 9.0 ** 2)))
    img += spec[..., None] * 1.2
    img = gaussian_filter(img, (1.5, 1.5, 0))
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path)
    print(f"  wrote synthetic test image: {path}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="CRT phosphor dot-scanline / Rutt-Etra image converter")
    ap.add_argument("input", nargs="?", help="image file or folder of PNG/JPG")
    ap.add_argument("--mode", choices=("scan", "rutt"), default="scan")
    ap.add_argument("--tint", default="blue",
                    help="keep | blue | cyan | green | amber | #hex")
    ap.add_argument("--pitch", type=float, default=6.0,
                    help="vertical scanline pitch in px at 1x (4-8)")
    ap.add_argument("--dot", type=float, default=3.5,
                    help="horizontal dot pitch in px at 1x (3-5)")
    ap.add_argument("--dotsize", type=float, default=0.55,
                    help="dot body Gaussian sigma at 1x scale")
    ap.add_argument("--displace", type=float, default=26.0,
                    help="rutt mode: max upward line displacement in px")
    ap.add_argument("--wobble", type=float, default=1.4,
                    help="horizontal sinusoidal wobble amplitude in px")
    ap.add_argument("--dropout", type=float, default=0.14,
                    help="luminance below which dots start vanishing (0-1)")
    ap.add_argument("--cutoff", type=float, default=0.05,
                    help="soft shadow toe cutoff on shaped luminance")
    ap.add_argument("--gain", type=float, default=1.25)
    ap.add_argument("--gamma", type=float, default=1.1)
    ap.add_argument("--bloom", type=float, default=1.0,
                    help="overall bloom strength multiplier")
    ap.add_argument("--bg", default="#04060d", help="background hex color")
    ap.add_argument("--width", type=int, default=1500, help="output width px")
    ap.add_argument("--supersample", type=int, default=2)
    ap.add_argument("--frames", action="store_true",
                    help="process every frame of an animated GIF")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("-o", "--outdir", default=".")
    ap.add_argument("--maketest", metavar="PATH",
                    help="write a synthetic test image and exit")
    p = ap.parse_args(argv)

    if p.maketest:
        make_test(p.maketest)
        return 0
    if not p.input:
        ap.error("input file/folder required (or use --maketest)")
    p.tint_rgb = parse_tint(p.tint)
    os.makedirs(p.outdir, exist_ok=True)

    if os.path.isdir(p.input):
        exts = (".png", ".jpg", ".jpeg") + ((".gif",) if p.frames else ())
        files = sorted(os.path.join(p.input, f) for f in os.listdir(p.input)
                       if f.lower().endswith(exts))
        if not files:
            print("no images found in folder", file=sys.stderr)
            return 1
    else:
        files = [p.input]
    for f in files:
        process_path(f, p, p.outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
