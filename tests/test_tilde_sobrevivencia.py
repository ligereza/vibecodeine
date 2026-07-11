"""
Tests del render target sobrevivencia-01 (projects/tilde/sobrevivencia.py)
contra los 9 criterios de aceptacion de projects/tilde/SPEC.md.

Se ejercita el CLI real via subprocess (mismo camino que el usuario:
py projects/tilde/sobrevivencia.py corpus.jsonl --svg salida.svg).
"""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "projects" / "tilde" / "sobrevivencia.py"
SVG_NS = "{http://www.w3.org/2000/svg}"

# Frase centinela plantada en un campo `original` de la fixture: si aparece
# en el SVG, el renderer violo la regla de privacidad del SPEC (criterio 6).
SENTINEL = "CENTINELA_PRIVADO_qz817_esta_frase_jamas_debe_salir_del_corpus"

# Fixture de 3 lineas con per_mark conocidos (criterio 3):
#   banda 1: marks_in=5, marks_out=4  -> 5 ticks, 4 sobrevivientes
#   banda 2: marks_in=3, marks_out=1  -> 3 ticks, 1 sobreviviente
#   banda 3: marks_in=0, survival null -> banda vacia, 0 ticks
FIXTURE_SAMPLES = [
    {
        "ts": "2026-07-11T10:00:00",
        "chars_in": 120,
        "chars_out": 60,
        "marks_in": 5,
        "marks_out": 4,
        "survival": 0.8,
        "per_mark": {"ñ": [3, 2], "á": [2, 2]},
        "degraded": [["año", "ano"]],
        "original": f"el año pasó rápido {SENTINEL}",
        "compressed": "el ano paso rapido",
    },
    {
        "ts": "2026-07-11T10:05:00",
        "chars_in": 80,
        "chars_out": 30,
        "marks_in": 3,
        "marks_out": 1,
        "survival": 0.333,
        "per_mark": {"¿": [2, 0], "é": [1, 1]},
        "degraded": [],
        "original": "¿qué paso? ¿donde?",
        "compressed": "qué paso donde",
    },
    {
        "ts": "2026-07-11T10:10:00",
        "chars_in": 40,
        "chars_out": 20,
        "marks_in": 0,
        "marks_out": 0,
        "survival": None,
        "per_mark": {},
        "degraded": [],
        "original": "linea sin marcas en juego",
        "compressed": "sin marcas",
    },
]

# Paleta esperada: la misma del exportador SVG del tapiz (criterio 8).
sys.path.insert(0, str(REPO_ROOT))
from projects.tapiz.vibecode.svg_export import (  # noqa: E402
    FLUJO_HEX,
    GHOST_COLOR,
)

SURVIVOR_COLOR = FLUJO_HEX["accent"]


def write_corpus(path: Path, samples) -> Path:
    with open(path, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    return path


def run_cli(corpus: Path, svg: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(corpus), "--svg", str(svg)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )


def render_fixture(tmp_path: Path, name: str = "pieza.svg") -> str:
    corpus = write_corpus(tmp_path / "corpus.jsonl", FIXTURE_SAMPLES)
    svg = tmp_path / name
    proc = run_cli(corpus, svg)
    assert proc.returncode == 0, proc.stderr
    return svg.read_text(encoding="utf-8")


def bands(svg_text: str):
    root = ET.fromstring(svg_text)
    return [g for g in root.iter(f"{SVG_NS}g") if g.get("class") == "band"]


def ticks(band):
    return [r for r in band.iter(f"{SVG_NS}rect") if r.get("class") == "tick"]


def test_svg_well_formed_and_one_band_per_line(tmp_path):
    """Criterios 1 y 2: SVG standalone parseable, band count == sample count."""
    svg_text = render_fixture(tmp_path)
    found = bands(svg_text)  # ET.fromstring ya valida que el XML es well-formed
    assert len(found) == len(FIXTURE_SAMPLES) == 3


def test_tick_counts_and_survivor_colors(tmp_path):
    """Criterio 3: marks_in ticks por banda, marks_out en color sobreviviente."""
    svg_text = render_fixture(tmp_path)
    found = bands(svg_text)
    expected = [(5, 4), (3, 1), (0, 0)]
    for band, (marks_in, marks_out) in zip(found, expected):
        band_ticks = ticks(band)
        assert len(band_ticks) == marks_in
        survivors = [t for t in band_ticks if t.get("fill") == SURVIVOR_COLOR]
        assert len(survivors) == marks_out
        lost = [t for t in band_ticks if t.get("fill") == GHOST_COLOR]
        assert len(lost) == marks_in - marks_out


def test_null_survival_renders_empty_band(tmp_path):
    """Criterio 4: survival null -> banda vacia (sin ticks ni label), sin crash."""
    svg_text = render_fixture(tmp_path)
    empty_band = bands(svg_text)[2]
    assert ticks(empty_band) == []
    assert [t for t in empty_band.iter(f"{SVG_NS}text")] == []
    # el lecho de la banda si existe: erosion legible, no ausencia
    bg = [r for r in empty_band.iter(f"{SVG_NS}rect") if r.get("class") == "band-bg"]
    assert len(bg) == 1


def test_survival_labels_and_footer_aggregate(tmp_path):
    """Ratio numerico por banda + linea agregada del pie (SPEC seccion 1)."""
    svg_text = render_fixture(tmp_path)
    assert "0.800" in svg_text
    assert "0.333" in svg_text
    assert "3 muestras" in svg_text
    # media de (0.8, 0.333) redondeada como summarize(): 0.567
    assert "sobrevivencia media 0.567" in svg_text
    # ranking de marcas mas perdidas: ¿ pierde 2, ñ pierde 1
    assert "¿:2" in svg_text
    assert "ñ:1" in svg_text


def test_minimal_pairs_caption(tmp_path):
    """SPEC seccion 1: pares minimos canonicos verbatim del dossier."""
    svg_text = render_fixture(tmp_path)
    for pair in ("año / ano", "papá / papa", "él / el", "sólo / solo"):
        assert pair in svg_text


def test_privacy_sentinel_absent(tmp_path):
    """Criterio 6: texto crudo de original/compressed jamas entra al SVG."""
    svg_text = render_fixture(tmp_path)
    assert SENTINEL not in svg_text
    for sample in FIXTURE_SAMPLES:
        assert sample["original"] not in svg_text
        assert sample["compressed"] not in svg_text


def test_deterministic_byte_identical(tmp_path):
    """Criterio 7: dos corridas sobre el mismo corpus -> bytes identicos."""
    corpus = write_corpus(tmp_path / "corpus.jsonl", FIXTURE_SAMPLES)
    svg_a = tmp_path / "a.svg"
    svg_b = tmp_path / "b.svg"
    assert run_cli(corpus, svg_a).returncode == 0
    assert run_cli(corpus, svg_b).returncode == 0
    assert svg_a.read_bytes() == svg_b.read_bytes()


def test_empty_corpus_placeholder(tmp_path):
    """Criterio 5: corpus vacio -> exit 0 y SVG placeholder sobre la ausencia."""
    corpus = tmp_path / "vacio.jsonl"
    corpus.write_text("", encoding="utf-8")
    svg = tmp_path / "placeholder.svg"
    proc = run_cli(corpus, svg)
    assert proc.returncode == 0, proc.stderr
    svg_text = svg.read_text(encoding="utf-8")
    ET.fromstring(svg_text)
    assert "no tiene muestras" in svg_text
    assert bands(svg_text) == []


def test_missing_corpus_placeholder(tmp_path):
    """Criterio 5: corpus inexistente -> exit 0 y el mismo placeholder."""
    svg = tmp_path / "ausente.svg"
    proc = run_cli(tmp_path / "no_existe.jsonl", svg)
    assert proc.returncode == 0, proc.stderr
    svg_text = svg.read_text(encoding="utf-8")
    ET.fromstring(svg_text)
    assert "no tiene muestras" in svg_text


def test_palette_is_flujo_not_adhoc(tmp_path):
    """Criterio 8: los colores usados salen de la paleta del tapiz."""
    svg_text = render_fixture(tmp_path)
    assert FLUJO_HEX["ink"] in svg_text        # fondo
    assert SURVIVOR_COLOR in svg_text          # ticks sobrevivientes
    assert GHOST_COLOR in svg_text             # ticks perdidos
    assert FLUJO_HEX["paper"] in svg_text      # labels
