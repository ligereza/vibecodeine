"""The per-work animated pieces are deterministic and contract-honest.

The rave essay was the demo; the system exists for the artist's own curated
works. tools/gen_animadas_obras.py derives ONE spec per work from the motor
semantico's closed vocabulary -- semantic where the work's own words allow
it, id-seeded elsewhere -- and the same work must always produce the same
piece (the timecode-as-seed thesis: generative output verifiable as a test).
No rasterizer/browser here on purpose: the WCAG critic needs Edge and that
is flaky in CI; what these tests pin is derivation, validity and contract.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
sys.path.insert(0, str(RAIZ / "cultura" / "mak_codex"))
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

import contrato_archivo  # noqa: E402
from gen_animadas_obras import derivar_spec  # noqa: E402
from motor_semantico.compilador import compilar, validar_spec  # noqa: E402

OBRAS = json.loads((RAIZ / "iskvw" / "datos" / "obras.json").read_text(encoding="utf-8"))


def test_toda_obra_deriva_spec_valida():
    for obra in OBRAS:
        fallos = validar_spec(derivar_spec(obra))
        assert not fallos, f"{obra['id']}: {fallos}"


def test_misma_obra_misma_spec_siempre():
    for obra in OBRAS:
        assert derivar_spec(obra) == derivar_spec(obra), obra["id"]


def test_la_tilde_manda_sobre_lo_generativo():
    # VOLA carries both 'generativo' and 'tilde'; the tilde is the project's
    # signal and must win regardless of tag order.
    vola = next(o for o in OBRAS if o["id"] == "vola")
    spec = derivar_spec(vola)
    assert spec["capas"][0]["gesto"] == "latir"


def test_compila_y_declara_su_animacion():
    vola = next(o for o in OBRAS if o["id"] == "vola")
    svg, _ = compilar(derivar_spec(vola), slug="vola")
    assert "<svg" in svg and "animation" in svg


def test_contrato_excluye_svg_ausente_y_vincula_el_presente():
    manifiesto = {"piezas": [
        {"obra_id": "a", "titulo": "A", "src": "x/a.svg", "declara_animacion": True},
        {"obra_id": "b", "titulo": "B", "src": "x/b.svg", "declara_animacion": True},
    ]}
    r = contrato_archivo.desde_animadas(manifiesto, existe=lambda s: s.endswith("a.svg"))
    assert [p["id"] for p in r["piezas"]] == ["animada-a"]
    assert r["vinculos"] == [{"de": "animada-a", "a": "a", "peso": 1.0,
                              "clase": "manual"}]
    assert r["piezas"][0]["extra"]["declara_animacion"] is True


def test_manifiesto_real_coincide_con_el_disco():
    manif = json.loads((RAIZ / "iskvw" / "datos" / "animadas.json").read_text(encoding="utf-8"))
    assert len(manif["piezas"]) == len(OBRAS)
    for fila in manif["piezas"]:
        assert (RAIZ / fila["src"]).is_file(), fila["src"]
        assert fila["spec"] == derivar_spec(
            next(o for o in OBRAS if o["id"] == fila["obra_id"]))
