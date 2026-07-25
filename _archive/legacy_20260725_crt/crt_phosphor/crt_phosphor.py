#!/usr/bin/env python3
"""CRT Phosphor Dot-Scanline Converter.

Rebuilds an image from discrete glowing phosphor dots arranged on
horizontal scanlines, with optional Rutt-Etra style luminance-driven
line displacement. See tools/crt_phosphor/README.md for usage.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageSequence
from scipy.ndimage import gaussian_filter, zoom as ndi_zoom

# ---------------------------------------------------------------------------
# Color / space helpers
# ---------------------------------------------------------------------------

TINT_PRESETS = {
    "blue": "#3aa9ff",
    "cyan": "#33e6e6",
    "green": "#39ff6a",
    "amber": "#ffb347",
}


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, 1.0)
    a = 0.055
    return np.where(c <= 0.04045, c / 12.92, ((c + a) / (1 + a)) ** 2.4)


def linear_to_srgb(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, None)
    a = 0.055
    low = c * 12.92
    high = (1 + a) * np.power(np.clip(c, 0, None), 1 / 2.4) - a
    return np.where(c <= 0.0031308, low, high)


def hex_to_srgb01(hex_str: str) -> np.ndarray:
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(ch * 2 for ch in hex_str)
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return np.array([r, g, b], dtype=np.float64)


def parse_tint(name: str) -> np.ndarray | None:
    """Return linear-space RGB triple for a tint spec, or None for 'keep'."""
    if name.lower() == "keep":
        return None
    hexval = TINT_PRESETS.get(name.lower(), name)
    return srgb_to_linear(hex_to_srgb01(hexval))


def rec709_luminance(rgb_linear: np.ndarray) -> np.ndarray:
    return (
        0.2126 * rgb_linear[..., 0]
        + 0.7152 * rgb_linear[..., 1]
        + 0.0722 * rgb_linear[..., 2]
    )


def smoothstep(a: float, b: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - a) / max(b - a, 1e-8), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------


def scatter_bilinear(buf: np.ndarray, x: np.ndarray, y: np.ndarray, rgb: np.ndarray) -> None:
    """Splat sub-pixel dots into buf (H,W,3) via bilinear weighted np.add.at."""
    h, w = buf.shape[:2]
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1
    fx = x - x0
    fy = y - y0

    corners = [
        (y0, x0, (1 - fx) * (1 - fy)),
        (y0, x1, fx * (1 - fy)),
        (y1, x0, (1 - fx) * fy),
        (y1, x1, fx * fy),
    ]
    for cy, cx, wgt in corners:
        valid = (cx >= 0) & (cx < w) & (cy >= 0) & (cy < h) & (wgt > 0)
        if not np.any(valid):
            continue
        np.add.at(
            buf,
            (cy[valid], cx[valid]),
            rgb[valid] * wgt[valid][:, None],
        )


def wide_blur(buf: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian blur that downsamples first for large sigma (mip-style bloom)."""
    if sigma <= 6.0:
        return gaussian_filter(buf, sigma=(sigma, sigma, 0))
    factor = max(1, int(sigma / 4.0))
    small = buf[::factor, ::factor]
    small_blurred = gaussian_filter(small, sigma=(sigma / factor, sigma / factor, 0))
    h, w = buf.shape[:2]
    # Upsample via PIL (fast C bilinear resize) instead of scipy.ndimage.zoom.
    up = np.empty((h, w, buf.shape[2]), dtype=np.float32)
    for c in range(buf.shape[2]):
        chan = Image.fromarray(small_blurred[..., c].astype(np.float32), mode="F")
        up[..., c] = np.asarray(chan.resize((w, h), Image.BILINEAR))
    return up


def build_ramp_color(t: np.ndarray, tint_color: np.ndarray) -> np.ndarray:
    """Dark -> saturated tint -> near white ramp, with overdrive for t>1."""
    white = np.array([1.0, 1.0, 1.0], dtype=np.float32)
    t01 = np.clip(t, 0.0, 1.0)
    frac1 = np.clip(t01 / 0.75, 0.0, 1.0)
    c = tint_color[None, :] * frac1[..., None]
    frac2 = np.clip((t01 - 0.75) / 0.25, 0.0, 1.0)
    c = c * (1 - frac2[..., None]) + white[None, :] * frac2[..., None]
    overdrive = np.clip(t - 1.0, 0.0, None)
    c = c + overdrive[..., None] * white[None, :]
    return c


def process_array(rgb_srgb: np.ndarray, args: argparse.Namespace, seed: int) -> np.ndarray:
    """rgb_srgb: HxWx3 float64 in [0,1] sRGB. Returns HxWx3 float64 sRGB output."""
    src_h, src_w = rgb_srgb.shape[:2]
    aspect = src_h / src_w
    work_w = int(round(args.width * args.supersample))
    work_h = int(round(work_w * aspect))

    src_img = Image.fromarray((np.clip(rgb_srgb, 0, 1) * 255).astype(np.uint8))
    src_img = src_img.resize((work_w, work_h), Image.LANCZOS)
    srgb = np.asarray(src_img).astype(np.float32) / 255.0

    linear = srgb_to_linear(srgb)  # (Hp, Wp, 3)
    Hp, Wp = linear.shape[:2]

    L_raw = rec709_luminance(linear)
    L_gain = L_raw * args.gain
    L_gamma = np.power(np.clip(L_gain, 0, None), 1.0 / max(args.gamma, 1e-3))
    edge = args.cutoff
    width = max(edge * 0.6, 0.02)
    L_shaped = L_gamma * smoothstep(edge - width, edge + width, L_gamma)

    ss = args.supersample
    pitch_v_px = max(1, int(round(args.pitch * ss)))
    pitch_h_px = max(1, int(round(args.dot * ss)))

    y_idx = np.arange(0, Hp, pitch_v_px)
    x_idx = np.arange(0, Wp, pitch_h_px)
    n_rows, n_cols = len(y_idx), len(x_idx)
    GY, GX = np.meshgrid(y_idx, x_idx, indexing="ij")

    L_grid = L_shaped[GY, GX]
    L_raw_grid = L_raw[GY, GX]
    color_grid = linear[GY, GX, :]

    gy_f = GY.ravel().astype(np.float64)
    gx_f = GX.ravel().astype(np.float64)
    L_f = L_grid.ravel()
    L_raw_f = L_raw_grid.ravel()
    color_f = color_grid.reshape(-1, 3)
    row_idx_f = np.repeat(np.arange(n_rows), n_cols)

    rng = np.random.default_rng(seed)
    phase = rng.uniform(0, 2 * np.pi, n_rows)
    wobble_amp_px = args.wobble * ss
    wobble_freq_px = max(6.0, pitch_h_px * 6.0)
    dx = wobble_amp_px * np.sin(gx_f / wobble_freq_px + phase[row_idx_f])

    if args.mode == "rutt":
        displace_px = args.displace * ss
        dy = -displace_px * L_f
    else:
        dy = np.zeros_like(L_f)

    final_x = gx_f + dx
    final_y = gy_f + dy

    keep_prob = np.clip(L_f / max(args.dropout, 1e-6), 0.0, 1.0) ** 0.6
    drop_rng = rng.random(L_f.shape[0])
    keep_mask = drop_rng < keep_prob

    final_x = final_x[keep_mask]
    final_y = final_y[keep_mask]
    L_kept = L_f[keep_mask]
    L_raw_kept = L_raw_f[keep_mask]
    color_kept = color_f[keep_mask]

    tint_color = parse_tint(args.tint)
    if tint_color is None:
        ratio = L_kept / (L_raw_kept + 1e-4)
        ratio = np.clip(ratio, 0.0, 5.0)
        dot_rgb = color_kept * ratio[:, None]
        halo_tint = np.array([0.5, 0.7, 1.0], dtype=np.float32)  # neutral cool default for bloom tint in keep mode
    else:
        dot_rgb = build_ramp_color(L_kept, tint_color.astype(np.float32))
        halo_tint = tint_color.astype(np.float32)

    impulse = np.zeros((Hp, Wp, 3), dtype=np.float32)
    scatter_bilinear(impulse, final_x, final_y, dot_rgb.astype(np.float32))

    dotsize_px = max(0.35, args.dotsize * ss)
    body = gaussian_filter(impulse, sigma=(dotsize_px, dotsize_px, 0))
    renorm = min(2 * np.pi * dotsize_px * dotsize_px, 60.0)
    body *= renorm

    sigmas = [2.0 * ss, 7.0 * ss, 20.0 * ss]
    weights = [0.18, 0.32, 0.5]
    bloom_buf = np.zeros_like(body)
    for i, (sigma, w) in enumerate(zip(sigmas, weights)):
        blurred = wide_blur(body, sigma)
        if i == 0:
            contrib = blurred * w
        else:
            lum_b = rec709_luminance(blurred)
            colored = lum_b[..., None] * halo_tint[None, None, :]
            contrib = (blurred * 0.35 + colored * 0.65) * w
        bloom_buf += contrib
        if i == len(sigmas) - 1:
            ambient = rec709_luminance(blurred)[..., None] * halo_tint[None, None, :]
            bloom_buf += ambient * 0.06

    bg = srgb_to_linear(hex_to_srgb01(args.bg)).astype(np.float32)
    final_linear = body + bloom_buf * args.bloom + bg[None, None, :]

    k = 1.0
    final_linear = final_linear / (1.0 + k * final_linear)

    out_srgb = linear_to_srgb(final_linear)
    out_srgb = np.clip(out_srgb, 0.0, 1.0)

    out_img = Image.fromarray((out_srgb * 255).astype(np.uint8))
    out_img = out_img.resize((args.width, int(round(args.width * aspect))), Image.LANCZOS)
    return np.asarray(out_img).astype(np.float64) / 255.0


def process_pil_image(img: Image.Image, args: argparse.Namespace, seed: int) -> Image.Image:
    img = img.convert("RGB")
    arr = np.asarray(img).astype(np.float64) / 255.0
    out = process_array(arr, args, seed)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------------------
# CLI / batch driving
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CRT Phosphor Dot-Scanline Converter")
    p.add_argument("input", help="Input image file or folder of PNG/JPG (and GIF with --frames)")
    p.add_argument("-o", "--outdir", required=True, help="Output directory")
    p.add_argument("--mode", choices=["scan", "rutt"], default="scan")
    p.add_argument("--tint", default="blue", help="keep|blue|cyan|green|amber|#hex")
    p.add_argument("--pitch", type=float, default=6.0, help="Vertical line pitch (output px)")
    p.add_argument("--dot", type=float, default=4.0, help="Horizontal dot pitch (output px)")
    p.add_argument("--dotsize", type=float, default=1.0, help="Dot body gaussian sigma (output px)")
    p.add_argument("--displace", type=float, default=8.0, help="Rutt-Etra max upward displacement (output px)")
    p.add_argument("--wobble", type=float, default=0.6, help="Horizontal wobble amplitude (output px)")
    p.add_argument("--dropout", type=float, default=0.35, help="Darkness dropout floor (0-1)")
    p.add_argument("--cutoff", type=float, default=0.05, help="Shadow soft-toe cutoff (0-1)")
    p.add_argument("--gain", type=float, default=1.2, help="Luminance gain")
    p.add_argument("--gamma", type=float, default=1.0, help="Luminance gamma shaping")
    p.add_argument("--bloom", type=float, default=1.0, help="Overall bloom intensity multiplier")
    p.add_argument("--bg", default="#02030a", help="Background color hex (sRGB)")
    p.add_argument("--width", type=int, default=1500, help="Final output width in px")
    p.add_argument("--supersample", type=int, default=2, help="Internal supersample factor")
    p.add_argument("--seed", type=int, default=0, help="RNG seed for dropout/wobble reproducibility")
    p.add_argument("--frames", action="store_true", help="Process every frame of an animated GIF")
    return p


def gather_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    exts = {".png", ".jpg", ".jpeg", ".gif"}
    return sorted(f for f in input_path.iterdir() if f.suffix.lower() in exts)


def process_file(path: Path, outdir: Path, args: argparse.Namespace) -> None:
    if path.suffix.lower() == ".gif" and args.frames:
        im = Image.open(path)
        frames = []
        durations = []
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            out_frame = process_pil_image(frame, args, seed=args.seed + i)
            frames.append(out_frame)
            durations.append(frame.info.get("duration", 100))
        out_path = outdir / f"{path.stem}_crt.gif"
        frames[0].save(
            out_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
        )
        print(f"[ok] {path.name} -> {out_path} ({len(frames)} frames)")
        return

    img = Image.open(path)
    out = process_pil_image(img, args, seed=args.seed)
    out_path = outdir / f"{path.stem}_crt.png"
    out.save(out_path)
    print(f"[ok] {path.name} -> {out_path}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    files = gather_inputs(input_path)
    if not files:
        print("No matching PNG/JPG/GIF files found.", file=sys.stderr)
        return 1

    for f in files:
        t0 = time.time()
        process_file(f, outdir, args)
        print(f"    ({time.time() - t0:.2f}s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
