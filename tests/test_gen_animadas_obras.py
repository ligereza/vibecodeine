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


def test_the_real_manifest_never_publishes_works_outside_the_field():
    """The direction that had a real incident behind it (#355, 2026-07-27).

    The old assertion was ``len(manifiesto) == len(campo)``, and it went red on
    2026-09-02 when the field legitimately grew from 219 to 871 works: the
    perception reached ``reels`` and more of ``posts``, exactly as the #355
    commit predicted it would. Its author already wrote the rule for this
    case -- "size is not the property worth protecting; a legitimate change of
    scope turning a test red is a bad test".

    What must never happen is the other direction: publishing an animated piece
    for a work the filter excluded. That reverses a decision the user made, and
    it is checked here over EVERY row instead of the first 30. A work in the
    field with no animated piece yet is the honest-missing case the archive
    already accepts elsewhere (``trazo`` measures 208 of 871 and writes no key
    for the rest).
    """
    manif = json.loads((RAIZ / "iskvw" / "datos" / "animadas.json").read_text(encoding="utf-8"))
    por_id = {o["id"]: o for o in OBRAS}

    assert manif["piezas"], "the real manifest is empty: nothing was measured"
    orphans = [f["obra_id"] for f in manif["piezas"]
               if f["obra_id"] not in por_id]
    assert not orphans, (
        "animadas.json publishes pieces for works that are not in the field, "
        "which is published material the filter declares unpublished: %s"
        % ", ".join(orphans[:5]))

    for fila in manif["piezas"][:30]:
        assert (RAIZ / fila["src"]).is_file(), fila["src"]
        assert fila["spec"] == derivar_spec(por_id[fila["obra_id"]])


def test_las_obras_curadas_entran_al_contrato():
    r = contrato_archivo.desde_campo(CAMPO)
    assert len(r["piezas"]) == len(OBRAS)
    p = r["piezas"][0]
    # machine text never as title (VOZ rule); it travels in extra.percibido
    assert p["titulo"] is None
    assert p["clase"] == "obra"
