"""Tests de tools/gen_propuestas_rd.py: candidatos digeridos -> borradores.

Fixtures sinteticas en tmp_path; los catalogos de fuzzy-match se pasan como
listas ya construidas (nunca dependen de data/productoras ni knowledge/
reales). Lo que se fija:

- filtros de entrada (fuente, identidad propia, categoria, geografia)
- dudoso (0.70-0.82) se REPORTA y nunca se propone
- umbral de evidencia (MIN_OBRAS_PROPUESTA distintas obras)
- latest-wins por obra_id (re-corridas en el jsonl no inflan evidencia)
- los borradores solo se escriben dentro de outdir y calcan el schema minimo
- regresion: la ONG misma escrita en largo ("Reduciendo Dano Chile") es
  identidad propia (2026-07-29: se escapaba de la deny-list y salia como
  productora candidata)
"""
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


gen = _cargar("gen_propuestas_rd", REPO_ROOT / "tools" / "gen_propuestas_rd.py")
extraccion_db = sys.modules["extraccion_db"]


def _candidato(obra_id="obra_1", fuente="rd", ruta_rel="a.png",
               productora="", venue="", categoria="flyer_evento",
               handles=None, identidad_propia=False):
    return {
        "obra_id": obra_id, "fuente": fuente, "ruta_rel": ruta_rel,
        "miembros_n": 1, "productora_cruda": productora,
        "productora_canonica": None, "match_ratio": 0.0,
        "venue_crudo": venue, "venue_canonico": None, "fecha_cruda": "",
        "handles": handles or [], "categoria": categoria,
        "calidad_senal": "alta", "identidad_propia": identidad_propia,
    }


def _jsonl(tmp_path, filas):
    p = tmp_path / "candidatos_db.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=True) + "\n")
    return p


SIN_CATALOGO = {"catalogo_productoras": [], "catalogo_venues": []}


def test_fila_json_valida_pero_no_objeto_se_salta(tmp_path):
    # gate 2026-07-29: '"just a string"' era JSON valido, llegaba a .get()
    # y abortaba la corrida entera con AttributeError
    p = tmp_path / "candidatos_db.jsonl"
    p.write_text(
        '"just a string"\n[1, 2]\n%s\n' % json.dumps(_candidato(obra_id="ok")),
        encoding="utf-8")
    candidatos = gen.cargar_candidatos(p)
    assert [c["obra_id"] for c in candidatos] == ["ok"]


def test_las_tildes_no_parten_la_evidencia():
    # gate 2026-07-29: _slug no pela acentos, asi que "Nébula Fest" y
    # "Nebula Fest" acumulaban por separado y ninguna llegaba al umbral
    candidatos = [
        _candidato(obra_id="o1", ruta_rel="a.png", productora="Nébula Fest"),
        _candidato(obra_id="o2", ruta_rel="b.png", productora="Nebula Fest"),
    ]
    consolidado, _ = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    assert list(consolidado["productoras_nuevas"]) == ["nebula_fest"]
    assert consolidado["productoras_nuevas"]["nebula_fest"]["evidencia"] == 2


def test_identidad_por_nombre_se_cuenta_no_se_calla():
    # gate 2026-07-29: el descarte por nombre (flag en falso, nombre en la
    # deny-list) no sumaba a ningun contador y el informe no cuadraba
    candidatos = [_candidato(obra_id="o1", productora="Reduciendo Daño Chile")]
    _, informe = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    assert informe["descartes"]["identidad_propia_nombre"] == 1


def test_latest_wins_por_obra_id(tmp_path):
    p = _jsonl(tmp_path, [
        _candidato(obra_id="obra_1", productora="Nebula Fest"),
        _candidato(obra_id="obra_1", productora="Nebula Fest"),
        _candidato(obra_id="obra_1", productora="Nebula Fest"),
    ])
    candidatos = gen.cargar_candidatos(p)
    assert len(candidatos) == 1


def test_filtros_de_entrada():
    candidatos = [
        _candidato(obra_id="o1", fuente="ig", productora="X Fest"),
        _candidato(obra_id="o2", identidad_propia=True, productora="X Fest"),
        _candidato(obra_id="o3", categoria="logo", productora="X Fest"),
        _candidato(obra_id="o4", categoria="ficha_sustancia", productora="X Fest"),
        _candidato(obra_id="o5"),  # sin nombres
    ]
    consolidado, informe = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    assert consolidado == {"productoras_nuevas": {}, "venues_nuevos": {}}
    d = informe["descartes"]
    assert d["fuente_no_rd"] == 1
    assert d["identidad_propia"] == 1
    assert d["categoria_no_evento"] == 2
    assert d["sin_nombres"] == 1


def test_geografia_no_es_venue():
    candidatos = [
        _candidato(obra_id="o%d" % i, venue="Santiago de Chile")
        for i in range(3)
    ]
    consolidado, informe = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    assert consolidado["venues_nuevos"] == {}
    assert informe["descartes"]["venue_geografia"] == 3


def test_dudoso_se_reporta_y_no_se_propone():
    catalogo = [{"canonico": "Espacio Riesco", "variantes": ["Espacio Riesco"]}]
    candidatos = [
        _candidato(obra_id="o%d" % i, venue="Espacio Riesgo, Santiago")
        for i in range(3)
    ]
    consolidado, informe = gen.consolidar_candidatos(
        candidatos, catalogo_productoras=[], catalogo_venues=catalogo)
    assert consolidado["venues_nuevos"] == {}
    assert len(informe["venues"]["dudosos"]) == 3
    assert "Espacio Riesco" in informe["venues"]["dudosos"][0]


def test_match_conocido_no_se_propone():
    catalogo = [{"canonico": "Piknic", "variantes": ["Piknic", "Piknic Electronik"]}]
    candidatos = [
        _candidato(obra_id="o%d" % i, productora="Piknic Electronik")
        for i in range(3)
    ]
    consolidado, informe = gen.consolidar_candidatos(
        candidatos, catalogo_productoras=catalogo, catalogo_venues=[])
    assert consolidado["productoras_nuevas"] == {}
    assert informe["productoras"]["conocidas"] == 3


def test_umbral_de_evidencia():
    candidatos = [
        _candidato(obra_id="o1", ruta_rel="a.png", productora="Nueva Fest"),
        _candidato(obra_id="o2", ruta_rel="b.png", productora="Nueva Fest",
                   handles=["@nuevafest"]),
        _candidato(obra_id="o3", ruta_rel="c.png", productora="Solo Una Vez"),
    ]
    consolidado, informe = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    assert list(consolidado["productoras_nuevas"]) == ["nueva_fest"]
    entrada = consolidado["productoras_nuevas"]["nueva_fest"]
    assert entrada["evidencia"] == 2
    assert entrada["instagram_handles"] == ["@nuevafest"]
    # la trazabilidad viaja en archivos_fuente: ruta_rel + obra_id
    assert any("a.png" in a and "o1" in a for a in entrada["archivos_fuente"])
    assert informe["productoras"]["evidencia_corta"] == ["Solo Una Vez (1)"]


def test_identidad_propia_en_largo_es_regresion():
    # 2026-07-29: "Reduciendo Dano Chile" pasaba la deny-list (solo cubria
    # "rd" por palabra y los dominios por contains) y salia como candidata.
    assert extraccion_db.es_identidad_propia("Reduciendo Daño Chile")
    assert extraccion_db.es_identidad_propia("REDUCIENDO DANO")
    # y los falsos positivos historicos siguen fuera
    assert not extraccion_db.es_identidad_propia("Hardgroove Records")
    assert not extraccion_db.es_identidad_propia("Panal Records")
    # el filtro por fila tambien re-verifica el nombre aunque el flag venga falso
    candidatos = [
        _candidato(obra_id="o%d" % i, productora="Reduciendo Daño Chile")
        for i in range(3)
    ]
    consolidado, _ = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    assert consolidado["productoras_nuevas"] == {}


def test_borradores_calcan_schema_y_quedan_en_outdir(tmp_path):
    candidatos = [
        _candidato(obra_id="o1", ruta_rel="a.png", productora="Nueva Fest",
                   venue="Club Real", handles=["@nuevafest"]),
        _candidato(obra_id="o2", ruta_rel="b.png", productora="Nueva Fest",
                   venue="Club Real"),
    ]
    consolidado, _ = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    outdir = tmp_path / "propuestas"
    gen.mineria_rd.proponer(consolidado, str(outdir))

    borrador = json.loads((outdir / "productoras" / "nueva_fest.json").read_text(
        encoding="utf-8"))
    # el schema minimo real de data/productoras (nebula.json)
    assert set(borrador) == {
        "name", "aliases", "instagram", "tipos_fecha", "logos", "venues",
        "confirmed", "fuente_datos", "notes",
    }
    assert borrador["name"] == "Nueva Fest"
    assert borrador["instagram"] == "@nuevafest"
    assert borrador["confirmed"] == ""
    assert "sin confirmar" in borrador["fuente_datos"]

    venue_yaml = (outdir / "venues" / "club_real.yaml").read_text(encoding="utf-8")
    assert "status: specs_needed" in venue_yaml
    assert (outdir / "RESUMEN.md").exists()
    # nada se escribio fuera de outdir
    assert set(p.name for p in outdir.iterdir()) == {
        "productoras", "venues", "RESUMEN.md"}


def test_el_nombre_del_venue_conserva_la_tilde(tmp_path):
    # Regla de datos 2026-07-29 (the machine/human cut): el id es clave
    # de maquina (ascii), el name lo lee un humano -- "Teatro Caupolican"
    # sin tilde en el borrador es la misma clase de defecto que
    # "reduciendo ano". Medido en el primer run real.
    candidatos = [
        _candidato(obra_id="o%d" % i, venue="Teatro Caupolicán")
        for i in range(2)
    ]
    consolidado, _ = gen.consolidar_candidatos(candidatos, **SIN_CATALOGO)
    outdir = tmp_path / "propuestas"
    gen.mineria_rd.proponer(consolidado, str(outdir))
    yaml_txt = (outdir / "venues" / "teatro_caupolican.yaml").read_text(
        encoding="utf-8")
    assert 'name: "Teatro Caupolicán"' in yaml_txt
    assert 'id: "teatro_caupolican"' in yaml_txt  # la clave sigue ascii


def test_main_contra_jsonl_real_del_repo(tmp_path, capsys):
    # el espejo versionado existe y el pipeline entero corre sin explotar
    espejo = REPO_ROOT / "docs" / "rd" / "candidatos_curatoria" / "candidatos_db.jsonl"
    assert espejo.exists()
    rc = gen.main(["--candidatos", str(espejo), "--outdir", str(tmp_path / "out")])
    assert rc == 0
    salida = capsys.readouterr().out
    assert "borradores en" in salida
    # la ONG jamas aparece como candidata en ninguna seccion del informe
    assert "Reduciendo" not in salida
