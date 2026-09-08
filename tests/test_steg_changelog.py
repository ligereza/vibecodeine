"""Tests de tools/svg/steg_changelog.py (pieza MANIFIESTO #4 ESTEGANOGRAFIA).

Omega11 (declarado por el director): la pieza PIERDE si (a) el roundtrip
embed->extract falla despues de que el SVG pasa svg_lint.py, o (b) el SVG
renderiza distinto con el payload adentro. Este archivo verifica ambas.

Puro stdlib + pytest. Se agrega tools/svg/ al path (mismo patron que
test_mecanismo_residuo.py agrega cultura/ o test_tilde_meter.py agrega desktop/).
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS_SVG_DIR = Path(__file__).resolve().parents[1] / "tools" / "svg"
sys.path.insert(0, str(TOOLS_SVG_DIR))

import steg_changelog  # noqa: E402
import svg_lint  # noqa: E402

from flujo.version import get_version  # noqa: E402

FIXTURE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    'width="2000px" height="2800px" viewBox="0 0 2000 2800">\n'
    '<metadata>fixture / front editable / 2000x2800 px</metadata>\n'
    '<g id="fondo_editable">\n'
    '<rect x="0" y="0" width="2000" height="2800" fill="#0A0A0A"/>\n'
    '<circle cx="255" cy="330" r="340" fill="none" stroke="#FFD21F" stroke-width="34"/>\n'
    "</g>\n"
    '<g id="header_marca">\n'
    '<text x="100" y="100" font-family="Arial, Helvetica" font-size="40">Impulso</text>\n'
    '<path d="M10 10 L50 50 L10 90 Z" fill="#FFFFFF"/>\n'
    "</g>\n"
    "</svg>\n"
)


def _write_fixture(tmp_path: Path) -> Path:
    p = tmp_path / "fixture.svg"
    p.write_text(FIXTURE_SVG, encoding="utf-8")
    return p


def test_extract_returns_none_on_clean_svg(tmp_path: Path) -> None:
    clean = _write_fixture(tmp_path)
    assert steg_changelog.extract(clean) is None


def test_embed_extract_roundtrip(tmp_path: Path) -> None:
    src = _write_fixture(tmp_path)
    out = tmp_path / "embedded.svg"

    embedded_payload = steg_changelog.embed(src, out)
    recovered = steg_changelog.extract(out)

    assert recovered is not None
    assert recovered == embedded_payload
    assert recovered["version"] == get_version()
    assert isinstance(recovered["git_hash"], str) and recovered["git_hash"]
    assert isinstance(recovered["date"], str) and len(recovered["date"]) == 10  # YYYY-MM-DD


def test_embed_is_idempotent_on_reembed(tmp_path: Path) -> None:
    """Re-embeber (ej. nueva version) reemplaza el marcador propio, no lo duplica."""
    src = _write_fixture(tmp_path)
    once = tmp_path / "once.svg"
    twice = tmp_path / "twice.svg"

    steg_changelog.embed(src, once, payload={"version": "0.1.0", "git_hash": "aaa111", "date": "2020-01-01"})
    steg_changelog.embed(once, twice, payload={"version": "0.2.0", "git_hash": "bbb222", "date": "2020-02-02"})

    text = twice.read_text(encoding="utf-8")
    assert text.count(f'id="{steg_changelog.MARKER_ID}"') == 1

    recovered = steg_changelog.extract(twice)
    assert recovered == {"version": "0.2.0", "git_hash": "bbb222", "date": "2020-02-02"}


def test_render_relevant_content_byte_identical_except_carrier(tmp_path: Path) -> None:
    """Omega11(b): probar que el payload no toca ningun byte de render existente.

    embed() solo INSERTA el bloque <metadata id="flujo-steg-changelog">; nunca
    reescribe una linea previa. Se prueba de forma fuerte: el contenido original
    completo debe seguir presente, verbatim y contiguo, dentro del archivo
    embebido (o sea, el diff es una insercion pura, no una edicion).
    """
    src = _write_fixture(tmp_path)
    out = tmp_path / "embedded.svg"

    original = src.read_text(encoding="utf-8")
    steg_changelog.embed(src, out)
    embedded = out.read_text(encoding="utf-8")

    # el bloque insertado es puramente aditivo: partiendo el archivo embebido
    # en el punto donde deberia estar el carrier, los dos lados deben pegar
    # exactamente con el original (insercion, no reemplazo).
    open_tag_end = embedded.index(">", embedded.index("<svg")) + 1
    carrier_end = embedded.index("</metadata>", open_tag_end) + len("</metadata>")
    before = embedded[:open_tag_end]
    after = embedded[carrier_end:]
    assert before + after == original

    # y el numero de elementos de render (todo lo que no es nuestro carrier)
    # es identico: mismo largo de archivo modulo el carrier insertado.
    assert len(embedded) == len(original) + (carrier_end - open_tag_end)


def test_svg_lint_still_passes_after_embed(tmp_path: Path) -> None:
    """Omega11(a): el SVG embebido no debe introducir ningun FAIL nuevo de svg_lint."""
    src = _write_fixture(tmp_path)
    out = tmp_path / "embedded.svg"
    steg_changelog.embed(src, out)

    issues_before = svg_lint.lint(str(src), "flyer")
    issues_after = svg_lint.lint(str(out), "flyer")

    fails_before = [i for i in issues_before if i[0] == "FAIL"]
    fails_after = [i for i in issues_after if i[0] == "FAIL"]

    assert fails_before == []
    assert fails_after == []
    # el carrier no debe generar WARNs nuevos tampoco (mismo set de issues)
    assert issues_after == issues_before


def test_embed_cli_roundtrip(tmp_path: Path) -> None:
    """El CLI (embed/extract via argparse) funciona igual que la API directa."""
    import subprocess

    src = _write_fixture(tmp_path)
    out = tmp_path / "cli_embedded.svg"

    script = TOOLS_SVG_DIR / "steg_changelog.py"
    r_embed = subprocess.run(
        [sys.executable, str(script), "embed", str(src), str(out)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r_embed.returncode == 0, r_embed.stderr
    assert out.exists()

    r_extract = subprocess.run(
        [sys.executable, str(script), "extract", str(out)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r_extract.returncode == 0, r_extract.stderr
    assert get_version() in r_extract.stdout


def test_embed_cleans_duplicate_tampered_markers(tmp_path: Path) -> None:
    """MINOR de review 2026-07-16: un archivo con DOS marcadores propios
    (tampering/merge manual) debe salir de embed() con exactamente UNO."""
    src = tmp_path / "tampered.svg"
    embedded = tmp_path / "step1.svg"
    _write_fixture(tmp_path)
    steg_changelog.embed(tmp_path / "fixture.svg", embedded)

    text = embedded.read_text(encoding="utf-8")
    m = steg_changelog._BLOCK_RE.search(text)
    assert m is not None
    # Duplica el bloque a mano al final del <svg> (tampering simulado).
    tampered = text.replace("</svg>", m.group(0) + "</svg>")
    src.write_text(tampered, encoding="utf-8")
    assert len(steg_changelog._BLOCK_RE.findall(tampered)) == 2

    out = tmp_path / "clean.svg"
    steg_changelog.embed(src, out)
    final = out.read_text(encoding="utf-8")
    assert len(steg_changelog._BLOCK_RE.findall(final)) == 1
    assert steg_changelog.extract(out) is not None
