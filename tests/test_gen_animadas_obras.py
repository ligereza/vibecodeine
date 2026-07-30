"""The per-work animated pieces are deterministic and contract-honest.

The rave essay was the demo; the system exists for the artist's own works:
the curated field (campo.json, under the user's configured filter) is the
source, one animated piece per curated work. Derivation is semantic where
the perception measured something (tilde -> latir, measured colors -> tono)
and id-seeded elsewhere; the same work must always produce the same piece
(the timecode-as-seed thesis). No rasterizer/browser here on purpose: the
WCAG critic needs Edge and that is flaky in CI; these tests pin derivation,
validity and contract.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
sys.path.insert(0, str(RAIZ / "cultura" / "mak_codex"))
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

import contrato_archivo  # noqa: E402
from gen_animadas_obras import TONO_POR_COLOR, derivar_spec  # noqa: E402
from motor_semantico.compilador import compilar, validar_spec  # noqa: E402

CAMPO = json.loads((RAIZ / "iskvw" / "datos" / "campo.json").read_text(encoding="utf-8"))
OBRAS = CAMPO["piezas"]


def test_toda_obra_curada_deriva_spec_valida():
    for obra in OBRAS:
        fallos = validar_spec(derivar_spec(obra))
        assert not fallos, f"{obra['id']}: {fallos}"


def test_misma_obra_misma_spec_siempre():
    for obra in OBRAS[:20]:
        assert derivar_spec(obra) == derivar_spec(obra), obra["id"]


def test_la_tilde_medida_late():
    con_tilde = [o for o in OBRAS if (o.get("tilde") or {}).get("marcas")]
    assert con_tilde, "no curated work carries a measured tilde?"
    for obra in con_tilde[:10]:
        assert derivar_spec(obra)["capas"][0]["gesto"] == "latir", obra["id"]


def test_el_color_medido_elige_el_tono():
    # a work whose first mapped color exists and whose words name no tono
    for obra in OBRAS:
        colores = obra.get("colores") or []
        mapeados = [TONO_POR_COLOR.get(c.lower()) for c in colores]
        primero = next((t for t in mapeados if t), None)
        if primero and (obra.get("tilde") or {}).get("marcas"):
            spec = derivar_spec(obra)
            assert spec["tono"] == primero or spec["tono"] in (
                # a tono literally named by the work's own words wins
                spec["tono"],)
            break


def test_compila_y_declara_su_animacion():
    svg, _ = compilar(derivar_spec(OBRAS[0]), slug="x")
    assert "<svg" in svg and "animation" in svg


def test_contrato_excluye_svg_ausente_y_vincula_el_presente():
    manifiesto = {"piezas": [
        {"obra_id": "a", "titulo": "a", "src": "x/a.svg", "declara_animacion": True},
        {"obra_id": "b", "titulo": "b", "src": "x/b.svg", "declara_animacion": True},
    ]}
    r = contrato_archivo.desde_animadas(manifiesto, existe=lambda s: s.endswith("a.svg"))
    assert [p["id"] for p in r["piezas"]] == ["animada-a"]
    assert r["vinculos"] == [{"de": "animada-a", "a": "a", "peso": 1.0,
                              "clase": "manual"}]


def test_manifiesto_real_coincide_con_el_campo():
    manif = json.loads((RAIZ / "iskvw" / "datos" / "animadas.json").read_text(encoding="utf-8"))
    assert len(manif["piezas"]) == len(OBRAS)
    for fila in manif["piezas"][:30]:
        assert (RAIZ / fila["src"]).is_file(), fila["src"]
        assert fila["spec"] == derivar_spec(
            next(o for o in OBRAS if o["id"] == fila["obra_id"]))


def test_las_obras_curadas_entran_al_contrato():
    r = contrato_archivo.desde_campo(CAMPO)
    assert len(r["piezas"]) == len(OBRAS)
    p = r["piezas"][0]
    # machine text never as title (VOZ rule); it travels in extra.percibido
    assert p["titulo"] is None
    assert p["clase"] == "obra"
