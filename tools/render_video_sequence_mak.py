#!/usr/bin/env python3
"""Render an Instagram reel to a PNG sequence on MAK.

The scene remains a .blend template. Blender receives the reel as a MOVIE
texture, calculates the source frame range, renders Cycles at 128 samples,
and must report a real GPU device. The template is never saved or modified.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_BLEND = Path("/home/mak/RD/AUTOMATIZACION/RD.blend")
DEFAULT_BLENDER = Path("/home/mak/blender/blender")
BLENDER_SCRIPT = Path(__file__).resolve().parents[1] / "src" / "flujo" / "eventos" / "blender_nodes_video_seq.py"
RENDER_TIMEOUT_S = 7200.0
PORTRAIT_9_16_RATIO = 9 / 16
PORTRAIT_9_16_TOLERANCE = 0.03
VIDEO_FLOW_PORTRAIT = "video_portrait_9_16"
VIDEO_FLOW_FRAMED = "video_other_aspect"
VALID_LAYOUTS = {"cover_center", "contain_bars"}


def probe_video(video: Path) -> dict:
    """Read duration/fps/frame count without decoding or changing the video."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=duration,nb_frames,r_frame_rate,width,height",
        "-of", "json", str(video),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"available": False}
    if result.returncode != 0:
        return {"available": False, "error": result.stderr.strip()[-300:]}
    try:
        stream = (json.loads(result.stdout).get("streams") or [{}])[0]
    except (ValueError, TypeError, IndexError):
        return {"available": False, "error": "ffprobe returned invalid JSON"}

    fps_text = str(stream.get("r_frame_rate") or "0/1")
    try:
        numerator, denominator = fps_text.split("/", 1)
        fps = float(numerator) / float(denominator)
    except (ValueError, ZeroDivisionError):
        fps = 0.0
    try:
        duration = float(stream.get("duration") or 0.0)
    except (TypeError, ValueError):
        duration = 0.0
    try:
        nb_frames = int(stream.get("nb_frames") or 0)
    except (TypeError, ValueError):
        nb_frames = 0
    calculated_frames = nb_frames or round(duration * fps)
    return {
        "available": True,
        "fps": fps,
        "duration": duration,
        "source_frames_estimate": calculated_frames,
        "width": stream.get("width"),
        "height": stream.get("height"),
    }


def classify_video_flow(probe: dict) -> dict:
    """Classify real media dimensions into one explicit issue flow."""
    if not probe.get("available"):
        raise ValueError(f"VIDEO_PROBE_UNAVAILABLE: {probe.get('error', 'sin metadata')}")
    try:
        width = int(probe["width"])
        height = int(probe["height"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("VIDEO_DIMENSIONS_REQUIRED") from exc
    if width <= 0 or height <= 0:
        raise ValueError("VIDEO_DIMENSIONS_INVALID")
    aspect = width / height
    if abs(aspect - PORTRAIT_9_16_RATIO) <= PORTRAIT_9_16_TOLERANCE:
        return {
            "flow": VIDEO_FLOW_PORTRAIT,
            "layout": "cover_center",
            "source_aspect_ratio": round(aspect, 6),
        }
    return {
        "flow": VIDEO_FLOW_FRAMED,
        "layout": "contain_bars",
        "source_aspect_ratio": round(aspect, 6),
    }


def build_blender_command(
    blender: Path,
    blend: Path,
    video: Path,
    out_dir: Path,
    manifest: Path,
    frame: Path | None = None,
    color_png: Path | None = None,
    frame_start: int = 1,
    frame_end: int | None = None,
    min_size: int = 20000,
    fps: float | None = None,
    persistent_data: bool = True,
    layout: str = "cover_center",
    issue_flow: str = VIDEO_FLOW_PORTRAIT,
) -> list[str]:
    """Build the foreground Blender invocation used by MAK and CI."""
    cmd = [str(blender), "-b", str(blend), "--python", str(BLENDER_SCRIPT), "--"]
    cmd += ["--input", str(video), "--out-dir", str(out_dir), "--manifest", str(manifest)]
    cmd += ["--frame-start", str(frame_start), "--min-size", str(min_size)]
    cmd += ["--layout", layout, "--issue-flow", issue_flow]
    if fps:
        cmd += ["--fps", str(fps)]
    if frame:
        cmd += ["--frame", str(frame)]
    if color_png:
        cmd += ["--color-png", str(color_png)]
    if frame_end is not None:
        cmd += ["--frame-end", str(frame_end)]
    if not persistent_data:
        cmd += ["--no-persistent-data"]
    return cmd


def _manifest_is_valid(manifest: Path, out_dir: Path) -> tuple[bool, str]:
    if not manifest.is_file():
        return False, "Blender termino sin render_manifest.json"
    try:
        report = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, f"manifest invalido: {exc}"
    if report.get("engine") != "CYCLES":
        return False, f"engine inesperado: {report.get('engine')}"
    if report.get("samples") != 128:
        return False, f"samples inesperados: {report.get('samples')}"
    if (report.get("gpu") or {}).get("device") != "GPU":
        return False, f"GPU no confirmada: {report.get('gpu')}"
    layout = report.get("layout")
    if not isinstance(layout, dict):
        return False, "manifest sin layout audiovisual"
    if layout.get("policy") not in VALID_LAYOUTS:
        return False, f"layout policy inesperada: {layout.get('policy')}"
    for key in ("source_aspect_ratio", "window_aspect_ratio", "crop_axis"):
        if key not in layout:
            return False, f"layout incompleto: falta {key}"
    if report.get("issue_flow") not in {VIDEO_FLOW_PORTRAIT, VIDEO_FLOW_FRAMED}:
        return False, f"issue_flow inesperado: {report.get('issue_flow')}"
    pngs = sorted(out_dir.glob("frame_*.png"))
    if not pngs:
        return False, "no se genero ninguna imagen PNG"
    if report.get("png_count") != len(pngs):
        return False, f"manifest png_count={report.get('png_count')} pero hay {len(pngs)} PNG"
    return True, str(manifest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Instagram reel -> PNG sequence on MAK")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--blend", type=Path, default=DEFAULT_BLEND)
    parser.add_argument("--blender", type=Path, default=DEFAULT_BLENDER)
    parser.add_argument("--frame", type=Path)
    parser.add_argument("--color-png", type=Path)
    parser.add_argument("--frame-start", type=int, default=1)
    parser.add_argument("--frame-end", type=int)
    parser.add_argument("--min-size", type=int, default=20000)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--no-persistent-data",
        action="store_true",
        help="desactivar la cache entre frames (solo diagnostico)",
    )
    parser.add_argument("--layout", choices=("auto", *sorted(VALID_LAYOUTS)), default="auto")
    parser.add_argument("--classify-only", action="store_true")
    args = parser.parse_args(argv)

    video = args.video.resolve()
    blend = args.blend.resolve()
    blender = args.blender.resolve()
    required_paths = [(video, "video")]
    if not args.classify_only:
        if args.out_dir is None:
            parser.error("--out-dir es obligatorio salvo con --classify-only")
        required_paths.extend(((blend, "blend"), (blender, "blender"), (BLENDER_SCRIPT, "Blender script")))
    for path, label in required_paths:
        if not path.exists():
            print(f"RENDER_FALLO: no existe {label}: {path}")
            return 1
    if args.frame_start < 1 or (args.frame_end is not None and args.frame_end < args.frame_start):
        print("RENDER_FALLO: rango de frames invalido")
        return 1

    probe = probe_video(video)
    try:
        profile = classify_video_flow(probe)
    except ValueError as exc:
        print(f"RENDER_FALLO: {exc}")
        return 1
    if args.classify_only:
        print(profile["flow"])
        return 0
    if args.layout != "auto" and args.layout != profile["layout"]:
        print(f"RENDER_FALLO: VIDEO_LAYOUT_PROFILE_MISMATCH requested={args.layout} actual={profile['layout']}")
        return 1
    layout = profile["layout"]
    out_dir = args.out_dir.resolve()
    manifest = out_dir / "render_manifest.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"VIDEO_PROBE: {json.dumps(probe, ensure_ascii=True)}")
    print(f"VIDEO_FLOW: {json.dumps(profile, ensure_ascii=True)}")
    cmd = build_blender_command(
        blender, blend, video, out_dir, manifest, args.frame, args.color_png,
        args.frame_start, args.frame_end, args.min_size,
        probe.get("fps") or None,
        not args.no_persistent_data,
        layout,
        profile["flow"],
    )
    print("BLENDER_CMD: " + " ".join(cmd))
    if args.dry_run:
        return 0

    try:
        completed = subprocess.run(cmd, timeout=RENDER_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print(f"RENDER_FALLO: Blender excedio {RENDER_TIMEOUT_S:.0f}s")
        return 1
    if completed.returncode != 0:
        print(f"RENDER_FALLO: Blender termino con codigo {completed.returncode}")
        return completed.returncode

    ok, detail = _manifest_is_valid(manifest, out_dir)
    if not ok:
        print(f"RENDER_FALLO: {detail}")
        return 1
    print(f"RENDER_OK: {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
