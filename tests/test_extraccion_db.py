"""Tests de cultura/mak_curatoria/extraccion_db.py.

Fixtures jsonl sinteticas en tmp_path (nunca dependen de datos reales de
data/productoras ni knowledge/); los catalogos de fuzzy-match tambien se
arman en tmp_path via --catalogo-productoras/--catalogo-venues (o se
omiten para probar el camino "sin catalogo -> nuevo?").
"""
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = REPO_ROOT / "cultura" / "mak_curatoria" / "extraccion_db.py"

_spec = importlib.util.spec_from_file_location("extraccion_db", MOD_PATH)
extraccion_db = importlib.util.module_from_spec(_spec)
sys.modules["extraccion_db"] = extraccion_db
_spec.loader.exec_module(extraccion_db)


# ---------------------------------------------------------------------------
# Helpers de fixture
# ---------------------------------------------------------------------------

def _ficha(fuente="rd", ruta_rel="a.png", tipo="imagen", categoria="flyer_evento",
           productora="", venue="", fecha="", handles=None, calidad="alta",
           error=None, descripcion=""):
    return {
        "id": "id_" + ruta_rel.replace("/", "_"),
        "fuente": fuente,
        "ruta_rel": ruta_rel,
        "tipo": tipo,
        "categoria": categoria,
        "bytes": 1000,
        "mtime": "2026-07-20",
        "ocr_texto": "",
        "vision": {"descripcion": descripcion, "estilo": "", "colores": [], "tipo_obra": ""},
        "datos_evento": {
            "productora": productora, "venue": venue, "fecha": fecha,
            "handles": handles or [],
        },
        "calidad_senal": calidad,
        "error": error,
        "seg_proceso": 0.1,
        "ts": "2026-07-20T00:00:00+00:00",
    }


def _escribir_jsonl(ruta: Path, fichas: list[dict]) -> None:
    with ruta.open("w", encoding="utf-8") as f:
        for ficha in fichas:
            f.write(json.dumps(ficha, ensure_ascii=True) + "\n")


def _escribir_catalogo_productora_json(dir_cat: Path, nombre_archivo: str,
                                        name: str, aliases=None, instagram=""):
    dir_cat.mkdir(parents=True, exist_ok=True)
    datos = {"name": name, "aliases": aliases or [], "instagram": instagram}
    (dir_cat / (nombre_archivo + ".json")).write_text(
        json.dumps(datos, ensure_ascii=True), encoding="utf-8")


def _sin_catalogo(tmp_path: Path, nombre: str = "_vacio_catalogo") -> Path:
    """Directorio vacio -- aisla el test de data/productoras y knowledge/
    reales del repo (defaults de cargar_catalogo_*), asi los tests son
    deterministas y no dependen de que catalogos existan hoy en el repo."""
    vacio = tmp_path / nombre
    vacio.mkdir(exist_ok=True)
    return vacio


# ---------------------------------------------------------------------------
# 1. Colapso de secuencia: 5 frames -> 1 obra, representante correcto
# ---------------------------------------------------------------------------

def test_colapso_secuencia_frames(tmp_path):
    fichas = [
        _ficha(ruta_rel="flyervideo/0001.png", calidad="baja"),
        _ficha(ruta_rel="flyervideo/0002.png", calidad="media"),
        _ficha(ruta_rel="flyervideo/0003.png", calidad="alta", descripcion="frame nitido"),
        _ficha(ruta_rel="flyervideo/0004.png", calidad="baja"),
        _ficha(ruta_rel="flyervideo/0005.png", calidad="media"),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(
        ruta_in, outdir,
        catalogo_productoras_ruta=_sin_catalogo(tmp_path),
        catalogo_venues_ruta=_sin_catalogo(tmp_path, "_vacio_venues"),
    )

    assert resumen["total_obras"] == 1
    (candidato,) = resumen["candidatos"]
    assert candidato["miembros_n"] == 5
    assert candidato["ruta_rel"] == "flyervideo/0003.png"
    assert candidato["calidad_senal"] == "alta"


# ---------------------------------------------------------------------------
# 2. No-colapso de archivos distintos
# ---------------------------------------------------------------------------

def test_no_colapso_archivos_distintos(tmp_path):
    fichas = [
        _ficha(ruta_rel="carpeta/flyer_evento_a.png"),
        _ficha(ruta_rel="carpeta/otro_logo_b.png"),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(ruta_in, outdir)

    assert resumen["total_obras"] == 2
    rutas = {c["ruta_rel"] for c in resumen["candidatos"]}
    assert rutas == {"carpeta/flyer_evento_a.png", "carpeta/otro_logo_b.png"}


# ---------------------------------------------------------------------------
# 3. Fuzzy match canonico (variante con typo)
# ---------------------------------------------------------------------------

def test_fuzzy_match_canonico_con_typo(tmp_path):
    fichas = [_ficha(ruta_rel="a.png", productora="Sundeckk")]  # typo de "Sundeck"
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)

    dir_cat = tmp_path / "catalogo_productoras"
    _escribir_catalogo_productora_json(dir_cat, "sundeck", "Sundeck", aliases=["SUNDECK"])

    outdir = tmp_path / "out"
    resumen = extraccion_db.procesar(ruta_in, outdir, catalogo_productoras_ruta=dir_cat)

    (candidato,) = resumen["candidatos"]
    assert candidato["productora_canonica"] == "Sundeck"
    assert candidato["match_ratio"] >= extraccion_db.RATIO_CANONICO


# ---------------------------------------------------------------------------
# 4. "nuevo?" sin catalogo
# ---------------------------------------------------------------------------

def test_nuevo_sin_catalogo(tmp_path):
    fichas = [_ficha(ruta_rel="a.png", productora="Marca Totalmente Inedita")]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(
        ruta_in, outdir,
        catalogo_productoras_ruta=_sin_catalogo(tmp_path),
        catalogo_venues_ruta=_sin_catalogo(tmp_path, "_vacio_venues"),
    )

    (candidato,) = resumen["candidatos"]
    assert candidato["productora_canonica"] is None
    assert candidato["match_ratio"] == 0.0
    assert extraccion_db.clasificar_ratio(candidato["match_ratio"]) == "nuevo"


# ---------------------------------------------------------------------------
# 5. Separacion: material_rd con productora NO genera candidato
# ---------------------------------------------------------------------------

def test_separacion_material_rd_no_genera_candidato(tmp_path):
    fichas = [
        _ficha(ruta_rel="rd/logo.png", categoria="material_rd",
               productora="REDUCIENDODANO.CL", venue="RD"),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(ruta_in, outdir)

    (candidato,) = resumen["candidatos"]
    assert candidato["productora_cruda"] == ""
    assert candidato["venue_crudo"] == ""
    assert candidato["productora_canonica"] is None
    assert candidato["venue_canonico"] is None


def test_separacion_logo_y_ficha_sustancia_tampoco_aportan(tmp_path):
    fichas = [
        _ficha(ruta_rel="a.png", categoria="logo", productora="Algo"),
        _ficha(ruta_rel="b.png", categoria="ficha_sustancia", venue="Otro"),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(ruta_in, outdir)

    for candidato in resumen["candidatos"]:
        assert candidato["productora_cruda"] == ""
        assert candidato["venue_crudo"] == ""


# ---------------------------------------------------------------------------
# 6. Basura descartada ("e)", "")
# ---------------------------------------------------------------------------

def test_basura_descartada():
    assert extraccion_db.es_basura("e)") is True
    assert extraccion_db.es_basura("") is True
    assert extraccion_db.es_basura("  ") is True
    assert extraccion_db.es_basura("RD") is True  # 2 alfanum, < 3
    assert extraccion_db.es_basura("RGB") is False
    assert extraccion_db.valor_limpio("e)") == ""
    assert extraccion_db.valor_limpio("Sundeck") == "Sundeck"


def test_basura_descartada_en_candidato(tmp_path):
    fichas = [_ficha(ruta_rel="a.png", productora="e)", venue="")]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(ruta_in, outdir)

    (candidato,) = resumen["candidatos"]
    assert candidato["productora_cruda"] == ""
    assert candidato["venue_crudo"] == ""


# ---------------------------------------------------------------------------
# 7. Fichas con error apartadas (no aportan candidato)
# ---------------------------------------------------------------------------

def test_fichas_con_error_apartadas(tmp_path):
    fichas = [
        _ficha(ruta_rel="ok.png", productora="Marca Valida"),
        _ficha(ruta_rel="malo.png", error="ollama_no_disponible: timeout"),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(ruta_in, outdir)

    assert resumen["total_error"] == 1
    assert resumen["total_obras"] == 1
    rutas = {c["ruta_rel"] for c in resumen["candidatos"]}
    assert "malo.png" not in rutas


# ---------------------------------------------------------------------------
# 8. Conteos del informe cuadran
# ---------------------------------------------------------------------------

def test_conteos_del_informe_cuadran(tmp_path):
    fichas = [
        _ficha(ruta_rel="serie/0001.png", calidad="baja"),
        _ficha(ruta_rel="serie/0002.png", calidad="alta"),
        _ficha(ruta_rel="suelto.png", categoria="material_rd"),
        _ficha(ruta_rel="con_error.png", error="excepcion_no_controlada: x"),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(ruta_in, outdir)

    assert resumen["total_fichas"] == 4
    assert resumen["total_error"] == 1
    assert resumen["total_obras"] == 2  # serie colapsa a 1 + suelto.png

    informe = (outdir / "INFORME_CANDIDATOS.md").read_text(encoding="ascii")
    assert "Fichas totales (fuente rd): 4" in informe
    assert "Fichas con error (apartadas, no aportan): 1" in informe
    assert "Fichas validas (sin error): 3" in informe
    assert "Obras tras colapso de secuencias: 2" in informe
    assert "con_error.png" in informe


# ---------------------------------------------------------------------------
# 9. candidatos_db.jsonl bien formado
# ---------------------------------------------------------------------------

def test_candidatos_jsonl_bien_formado(tmp_path):
    fichas = [
        _ficha(ruta_rel="a.png", productora="Marca X", venue="Lugar Y",
               fecha="2026-07-01", handles=["@marcax"]),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    extraccion_db.procesar(ruta_in, outdir)

    ruta_out = outdir / "candidatos_db.jsonl"
    assert ruta_out.exists()
    lineas = ruta_out.read_text(encoding="ascii").strip().splitlines()
    assert len(lineas) == 1

    registro = json.loads(lineas[0])
    assert set(registro.keys()) == set(extraccion_db.CAMPOS_CANDIDATO_JSONL)
    assert registro["obra_id"].startswith("obra_")
    assert registro["ruta_rel"] == "a.png"
    assert registro["productora_cruda"] == "Marca X"
    assert registro["handles"] == ["@marcax"]

    # el archivo entero debe ser ASCII puro (repo ASCII-only).
    ruta_out.read_bytes().decode("ascii")


# ---------------------------------------------------------------------------
# 10. Agrupacion de variantes nuevas entre si (Sundek/sundeck)
# ---------------------------------------------------------------------------

def test_agrupacion_variantes_nuevas_entre_si(tmp_path):
    fichas = [
        _ficha(ruta_rel="uno.png", productora="Sundek"),
        _ficha(ruta_rel="dos.png", productora="sundeck"),
        _ficha(ruta_rel="tres.png", productora="Otra Marca Distinta"),
    ]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(
        ruta_in, outdir,
        catalogo_productoras_ruta=_sin_catalogo(tmp_path),
        catalogo_venues_ruta=_sin_catalogo(tmp_path, "_vacio_venues"),
    )

    clusters = resumen["clusters_nuevos"]
    tamanos = sorted(len(c["obras"]) for c in clusters)
    assert tamanos == [1, 2]

    cluster_grande = next(c for c in clusters if len(c["obras"]) == 2)
    variantes_norm = {extraccion_db.normalizar_texto(v) for v in cluster_grande["variantes"]}
    assert variantes_norm == {"sundek", "sundeck"}

    # con >=2 obras, debe generar una propuesta .md
    assert len(resumen["propuestas"]) == 1
    contenido = resumen["propuestas"][0].read_text(encoding="ascii")
    assert "Sundek" in contenido or "sundeck" in contenido.lower()
    assert "uno.png" in contenido and "dos.png" in contenido


def test_agrupacion_nuevos_con_1_obra_no_genera_propuesta(tmp_path):
    fichas = [_ficha(ruta_rel="unico.png", productora="Marca Solitaria")]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"

    resumen = extraccion_db.procesar(
        ruta_in, outdir,
        catalogo_productoras_ruta=_sin_catalogo(tmp_path),
        catalogo_venues_ruta=_sin_catalogo(tmp_path, "_vacio_venues"),
    )

    assert resumen["propuestas"] == []
    assert not (outdir / "propuestas").exists()


# ---------------------------------------------------------------------------
# Extras: dudosos, venue match, catalogo yaml, cli
# ---------------------------------------------------------------------------

def test_clasificar_ratio_bandas():
    assert extraccion_db.clasificar_ratio(0.95) == "match"
    assert extraccion_db.clasificar_ratio(0.82) == "match"
    assert extraccion_db.clasificar_ratio(0.75) == "dudoso"
    assert extraccion_db.clasificar_ratio(0.70) == "dudoso"
    assert extraccion_db.clasificar_ratio(0.5) == "nuevo"


def test_venue_match_canonico(tmp_path):
    fichas = [_ficha(ruta_rel="a.png", venue="Open Klubb")]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)

    dir_cat = tmp_path / "catalogo_venues"
    dir_cat.mkdir()
    (dir_cat / "openklub.json").write_text(
        json.dumps({"name": "OpenKlub", "aliases": []}), encoding="utf-8")

    outdir = tmp_path / "out"
    resumen = extraccion_db.procesar(ruta_in, outdir, catalogo_venues_ruta=dir_cat)

    (candidato,) = resumen["candidatos"]
    assert candidato["venue_canonico"] == "OpenKlub"


def test_cli_main_ejecuta_end_to_end(tmp_path, capsys):
    fichas = [_ficha(ruta_rel="a.png", productora="Marca Z")]
    ruta_in = tmp_path / "fichas.jsonl"
    _escribir_jsonl(ruta_in, fichas)
    outdir = tmp_path / "out"
    cat_prod = _sin_catalogo(tmp_path)
    cat_venue = _sin_catalogo(tmp_path, "_vacio_venues")

    codigo = extraccion_db.main([
        str(ruta_in), "--outdir", str(outdir),
        "--catalogo-productoras", str(cat_prod),
        "--catalogo-venues", str(cat_venue),
    ])

    assert codigo == 0
    assert (outdir / "candidatos_db.jsonl").exists()
    assert (outdir / "INFORME_CANDIDATOS.md").exists()
    salida = capsys.readouterr().out
    assert "candidatos:" in salida


def test_cli_main_fichas_inexistentes(tmp_path):
    codigo = extraccion_db.main([
        str(tmp_path / "no_existe.jsonl"), "--outdir", str(tmp_path / "out"),
    ])
    assert codigo == 2
