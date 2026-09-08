#!/usr/bin/env python3
"""Deterministic SVG quality and duplicate checks.

This module does not decide whether a metaphor is good. It only answers three
machine questions: can the SVG be rendered, can its animation be rendered, and
is it the same visual artifact as an existing piece. Unknown remains unknown.
"""
import hashlib
import io
import pathlib
import sys

if __name__ == "__main__" and __package__ in (None, ""):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    __package__ = "motor_semantico"

from . import critico, rasterizador  # noqa: E402


def exact_hash(svg_text):
    return hashlib.sha256((svg_text or "").encode("utf-8")).hexdigest()


def _perceptual_signature(svg_text):
    """Return a small grayscale signature, or None when pixels are unavailable."""
    try:
        from PIL import Image
        png = critico.rasterizar(svg_text, tam=32)
        image = Image.open(io.BytesIO(png)).convert("L").resize((16, 16))
    except Exception:  # noqa: BLE001 - unavailable render is an explicit state
        return None
    return tuple(1 if value >= 128 else 0 for value in image.getdata())


def _signature_distance(left, right):
    if left is None or right is None or len(left) != len(right):
        return None
    return sum(a != b for a, b in zip(left, right)) / float(len(left))


def find_duplicate(svg_text, pieces_dir, threshold=0.04):
    """Find an exact or perceptual duplicate without deleting either file."""
    path = pathlib.Path(pieces_dir)
    digest = exact_hash(svg_text)
    signature = _perceptual_signature(svg_text)
    if not path.is_dir():
        return {"status": "unique", "hash": digest, "method": "none"}
    for candidate in sorted(path.glob("*.svg")):
        try:
            candidate_text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if exact_hash(candidate_text) == digest:
            return {"status": "duplicate", "method": "exact",
                    "duplicate_of": str(candidate), "hash": digest}
        if signature is not None:
            distance = _signature_distance(
                signature, _perceptual_signature(candidate_text))
            if distance is not None and distance <= threshold:
                return {"status": "duplicate", "method": "perceptual",
                        "distance": round(distance, 5),
                        "duplicate_of": str(candidate), "hash": digest}
    return {"status": "unique", "hash": digest,
            "method": "perceptual" if signature is not None else "exact_only"}


def validate(svg_text, name="svg"):
    """Require both real rasterization and an animation-capable backend."""
    backend = rasterizador.backend_disponible(anima=True)
    if backend is None:
        return {"ok": False, "status": "unverified", "backend": None,
                "reason": rasterizador.por_que_no_hay_navegador(True)}
    result = critico.analizar(svg_text, nombre=name)
    if result.get("error") or result.get("puntaje") is None:
        return {"ok": False, "status": "unverified", "backend": backend,
                "reason": result.get("error", "no perceptual score"),
                "metrics": result}
    return {"ok": True, "status": "validated", "backend": backend,
            "reason": "rendered and animation-capable backend passed",
            "metrics": result}
