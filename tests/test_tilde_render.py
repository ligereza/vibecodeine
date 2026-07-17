"""
Tests del render sobrevivencia-01 (projects/tilde/sobrevivencia.py) a nivel
libreria: importa el modulo directo (no subprocess) y ejercita render_svg()
sobre un corpus SINTETICO generado con el instrumento real
desktop/tilde_meter.py -- no con dicts inventados a mano.

Complementa tests/test_tilde_sobrevivencia.py (que ya cubre los 9 criterios
de aceptacion del SPEC via CLI/subprocess). Este archivo prueba dos cosas
que ese no aisla:

1. Omega11 (declarado por el director): la pieza pierde si necesita datos
   INVENTADOS para verse bien. Aca el fixture no es un dict a mano con
   numeros elegidos por conveniencia -- se produce llamando
   tilde_meter.measure_and_log() sobre pares (original, comprimido) reales
   de espanol, asi el esquema (per_mark, survival, degraded, ...) es
   estructuralmente identico al que emite el instrumento en produccion.
   Sigue siendo SINTETICO (frases de prueba, no prompts reales del usuario)
   y esta etiquetado como tal -- eso es lo que el criterio permite.
2. render_svg()/main() como funciones de libreria: end-to-end sobre el
   fixture, archivo de salida valido (XML parseable), determinista con la
   misma entrada -- sin pasar por el interprete de subprocess.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_DIR = REPO_ROOT / "desktop"
for p in (str(REPO_ROOT), str(DESKTOP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import tilde_meter  # noqa: E402  (desktop/tilde_meter.py, instrumento real)
from projects.tilde import sobrevivencia  # noqa: E402

SVG_NS = "{http://www.w3.org/2000/svg}"

# Pares (original, comprimido) SINTETICOS -- espanol de prueba, no material
# real del usuario -- pasados por el instrumento REAL para que el fixture
# tenga exactamente el esquema que measure_and_log() escribe en produccion
# (mismos campos, mismo redondeo de survival, mismo formato de per_mark).
SYNTHETIC_PAIRS = [
    ("El nino perdio su ano de estudios", "El nino perdio su ano de estudios"),
    ("¿Qué pasó con papá?", "que paso con papa"),
    ("Solo se fue el camión sin ruido", "Solo se fue el camion sin ruido"),
]


def build_synthetic_corpus(tmp_path: Path) -> Path:
    """Genera un corpus con el instrumento real (measure_and_log), no a mano."""
    log_path = tmp_path / "synthetic_tilde_log.jsonl"
    for original, compressed in SYNTHETIC_PAIRS:
        tilde_meter.measure_and_log(original, compressed, path=str(log_path))
    assert log_path.exists(), "measure_and_log() debe escribir el corpus"
    return log_path


def test_synthetic_fixture_matches_real_instrument_schema(tmp_path):
    """Omega11: el fixture no es inventado, sale del instrumento real."""
    log_path = build_synthetic_corpus(tmp_path)
    samples = sobrevivencia.load_corpus(str(log_path))
    assert len(samples) == len(SYNTHETIC_PAIRS)
    expected_fields = {
        "ts", "chars_in", "chars_out", "marks_in", "marks_out",
        "survival", "per_mark", "degraded", "original", "compressed",
    }
    for sample in samples:
        assert expected_fields.issubset(sample.keys())
        # per_mark tiene la forma [count_in, count_out] que produce measure()
        for pair in sample["per_mark"].values():
            assert len(pair) == 2
            assert all(isinstance(n, int) for n in pair)


def test_render_svg_end_to_end_on_synthetic_fixture(tmp_path):
    """render_svg() como funcion de libreria: corre sobre el fixture real."""
    log_path = build_synthetic_corpus(tmp_path)
    samples = sobrevivencia.load_corpus(str(log_path))
    svg_text = sobrevivencia.render_svg(samples)

    # Output valido: parsea como XML bien formado.
    root = ET.fromstring(svg_text)
    assert root.tag == f"{SVG_NS}svg"

    bands = [g for g in root.iter(f"{SVG_NS}g") if g.get("class") == "band"]
    assert len(bands) == len(SYNTHETIC_PAIRS)


def test_render_svg_deterministic_same_input(tmp_path):
    """Criterio 7 del SPEC, verificado a nivel funcion (no solo CLI)."""
    log_path = build_synthetic_corpus(tmp_path)
    samples_a = sobrevivencia.load_corpus(str(log_path))
    samples_b = sobrevivencia.load_corpus(str(log_path))
    assert sobrevivencia.render_svg(samples_a) == sobrevivencia.render_svg(samples_b)


def test_main_cli_writes_valid_svg_file(tmp_path):
    """main() end-to-end: escribe un archivo SVG real, parseable, no vacio."""
    log_path = build_synthetic_corpus(tmp_path)
    out_svg = tmp_path / "sobrevivencia_01.svg"
    exit_code = sobrevivencia.main([str(log_path), "--svg", str(out_svg)])
    assert exit_code == 0
    assert out_svg.is_file()

    svg_text = out_svg.read_text(encoding="utf-8")
    root = ET.fromstring(svg_text)  # bien formado
    assert root.tag == f"{SVG_NS}svg"
    # Ningun texto crudo del par sintetico entra a la pieza (regla de
    # privacidad del SPEC, verificada tambien aca a nivel libreria).
    for original, compressed in SYNTHETIC_PAIRS:
        assert original not in svg_text
        assert compressed not in svg_text


def test_render_placeholder_on_empty_samples():
    """Sin muestras: pieza sobre la ausencia, XML valido, sin crash."""
    svg_text = sobrevivencia.render_svg([])
    root = ET.fromstring(svg_text)
    assert root.tag == f"{SVG_NS}svg"
    assert "no tiene muestras" in svg_text
