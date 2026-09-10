"""Offline tests for cultura/mak_curatoria/triangular.py -- flyers already
perceived become concrete research questions ("headliner + fecha = productora
encontrable", the user's formula, 2026-07-26).

It builds a queue and dispatches nothing; the tests pin the headliner
heuristic over OCR text, the list-tolerant `_txt`, the dedup by (fuente,
ruta_rel) keeping the LAST record, and the confirm/discover split. All file
paths land in tmp_path.
"""
import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TRIANGULAR_PY = RAIZ / "cultura" / "mak_curatoria" / "triangular.py"


def _cargar():
    spec = importlib.util.spec_from_file_location("triangular_bajo_prueba",
                                                  TRIANGULAR_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


triangular = _cargar()


# ------------------------------------------------------- posibles_headliners

def test_headliners_desde_un_ocr_de_flyer_realista():
    ocr = "\n".join([
        "REDUCIENDO DAÑO PRESENTA",     # noise words -> out
        "DJ NADIE",                     # 'dj' is noise -> out
        "AMELIE LENS",                  # headliner, upper
        "Charlotte de Witte",           # capitalized-ish
        "sabado 12 tickets en puerta",  # noise + lowercase -> out
        "WWW.ENTRADAS.CL",              # noise -> out
        "x" * 60,                       # too long -> out
    ])
    heads = triangular.posibles_headliners(ocr)
    assert "AMELIE LENS" in heads
    assert all("DJ" not in h for h in heads)
    assert all("REDUCIENDO" not in h for h in heads)


def test_headliners_dedup_insensible_a_mayusculas_y_tope_5():
    ocr = "\n".join(["AMELIE LENS", "Amelie Lens"] +
                    ["ARTISTA %s" % chr(65 + i) for i in range(9)])
    heads = triangular.posibles_headliners(ocr)
    assert len([h for h in heads if h.lower() == "amelie lens"]) == 1
    assert len(heads) == 5, "at most 5 candidates per flyer"


def test_headliners_ocr_vacio_o_sin_letras():
    assert triangular.posibles_headliners("") == []
    assert triangular.posibles_headliners(None) == []
    assert triangular.posibles_headliners("12345\n???") == []


def test_una_linea_minuscula_no_es_cartel():
    assert triangular.posibles_headliners("un texto cualquiera en prosa") == []


def test_azure_ner_agrega_candidatos_sin_convertirlos_en_hechos(monkeypatch):
    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({
                "results": {"documents": [{"entities": [
                    {"category": "Person", "text": "Amelie Lens", "confidenceScore": 0.98},
                    {"category": "Location", "text": "Santiago", "confidenceScore": 0.99},
                    {"category": "Product", "text": "TICKETS", "confidenceScore": 0.99},
                ]}]}
            }).encode("utf-8")

    monkeypatch.setenv("AZURE_LANGUAGE_ENDPOINT", "https://language.example")
    monkeypatch.setenv("AZURE_LANGUAGE_KEY", "test-key")
    monkeypatch.setattr(triangular.urllib.request, "urlopen", lambda *_a, **_kw: _Response())

    evidence = triangular._headliner_evidence("AMELIE")

    assert evidence["candidatos"] == ["AMELIE", "Amelie Lens"]
    assert evidence["fuentes"][-1] == {
        "kind": "azure_language_ner", "status": "candidate",
    }
    assert evidence["azure"] == "ok"


def test_azure_ner_falla_abierto_y_conserva_heuristica(monkeypatch):
    monkeypatch.setenv("AZURE_LANGUAGE_ENDPOINT", "https://language.example")
    monkeypatch.setenv("AZURE_LANGUAGE_KEY", "test-key")

    def _fail(*_args, **_kwargs):
        raise OSError("offline")

    monkeypatch.setattr(triangular.urllib.request, "urlopen", _fail)

    assert triangular.posibles_headliners("AMELIE LENS") == ["AMELIE LENS"]
    assert triangular._headliner_evidence("AMELIE LENS")["azure"] == "request_error"


# --------------------------------------------------------------------- _txt

def test_txt_tolera_lista_none_y_string():
    """gemma3 sometimes returns a list where the schema says string."""
    assert triangular._txt(["Club Elipse", "Sala 2"]) == "Club Elipse, Sala 2"
    assert triangular._txt(None) == ""
    assert triangular._txt("  Teatro Caupolicán ") == "Teatro Caupolicán"
    assert triangular._txt(["", None, "x"]) == "x"


# --------------------------------------------------------------------- main

def _ficha(**kw):
    base = {"id": "f1", "fuente": "rd", "ruta_rel": "a.jpg",
            "categoria": "flyer_evento", "datos_evento": {}, "ocr_texto": ""}
    base.update(kw)
    return base


def _correr(monkeypatch, tmp_path, fichas):
    entrada = tmp_path / "fichas.jsonl"
    salida = tmp_path / "triangulacion.jsonl"
    entrada.write_text("no-json\n" + "\n".join(
        json.dumps(f, ensure_ascii=False) for f in fichas) + "\n",
        encoding="utf-8")
    monkeypatch.setattr(triangular, "FICHAS", str(entrada))
    monkeypatch.setattr(triangular, "SALIDA", str(salida))
    triangular.main([])  # argv explicito: no heredar el argv real de pytest
    return [json.loads(l) for l in
            salida.read_text(encoding="utf-8").splitlines()]


def test_main_separa_confirmar_de_descubrir(monkeypatch, tmp_path, capsys):
    filas = _correr(monkeypatch, tmp_path, [
        _ficha(id="conprod", ruta_rel="a.jpg",
               datos_evento={"fecha": "2026-03-14", "productora": "Elipse",
                             "venue": "Club Bizarre"}),
        _ficha(id="sinprod", ruta_rel="b.jpg",
               datos_evento={"fecha": "2026-05-01",
                             "handles": "@fiesta_x"},
               ocr_texto="AMELIE LENS\n"),
    ])
    por_id = {f["id_ficha"]: f for f in filas}
    assert por_id["conprod"]["estado"] == "confirmar"
    assert "Elipse" in por_id["conprod"]["pregunta"]
    assert "Club Bizarre" in por_id["conprod"]["pregunta"]

    assert por_id["sinprod"]["estado"] == "descubrir"
    assert por_id["sinprod"]["handles"] == ["@fiesta_x"], "str handle -> list"
    assert "AMELIE LENS" in por_id["sinprod"]["pregunta"]
    assert "fuente" in por_id["sinprod"]["pregunta"], "always asks for a source"

    out = capsys.readouterr().out
    assert "PREGUNTAS armadas       : 2" in out


def test_main_sin_fecha_o_sin_identificador_no_pregunta(monkeypatch, tmp_path):
    filas = _correr(monkeypatch, tmp_path, [
        _ficha(id="sinfecha", ruta_rel="a.jpg",
               datos_evento={"venue": "Club X"}),
        _ficha(id="soloFecha", ruta_rel="b.jpg",
               datos_evento={"fecha": "2026-01-01"}),
    ])
    assert filas == [], "fecha AND something identifying, or no question"


def test_main_filtra_fuente_ig_y_categorias_no_evento(monkeypatch, tmp_path):
    filas = _correr(monkeypatch, tmp_path, [
        _ficha(id="ig", fuente="ig",
               datos_evento={"fecha": "2026-01-01", "venue": "X"}),
        _ficha(id="retrato", categoria="retrato",
               datos_evento={"fecha": "2026-01-01", "venue": "X"}),
    ])
    assert filas == [], "only rd flyers/fotos de evento enter the queue"


def test_main_la_ultima_ficha_del_mismo_archivo_gana(monkeypatch, tmp_path):
    """fichas.jsonl is append-only: a re-perceived file appears twice and the
    later record must win."""
    filas = _correr(monkeypatch, tmp_path, [
        _ficha(id="vieja", ruta_rel="a.jpg",
               datos_evento={"fecha": "2026-01-01", "venue": "Sala Vieja"}),
        _ficha(id="nueva", ruta_rel="a.jpg",
               datos_evento={"fecha": "2026-02-02", "venue": "Sala Nueva"}),
    ])
    assert len(filas) == 1
    assert filas[0]["id_ficha"] == "nueva"
    assert filas[0]["venue"] == "Sala Nueva"


# --------------------------------------------------------------- despachar
#
# Offline: research_lib/fuentes are monkeypatched with fakes. A test that
# hits the real network depends on the environment (SearXNG in Docker) and
# would not run in CI -- see the test rule in CLAUDE.md.

class _FakeModulos:
    """Fake for _research_lib_module()/_fuentes_module(): records the
    queries it was asked and returns results fixed by the test, without
    touching the real network."""

    def __init__(self, respuesta=None):
        self.respuesta = respuesta or {"results": [], "ciego": True, "motivo": "no configurado"}
        self.queries = []

    def web_search(self, query, max_results=5, errors=None):
        self.queries.append(query)
        return self.respuesta


def _catalogo():
    return [{"canonico": "Creamfields", "variantes": ["Creamfields", "CREAMFIELDSCL"]}]


def test_candidato_legible_rechaza_fragmentos_de_ocr_reales():
    # Real regression (2026-09-09): these 3 fragments came from a real
    # ~/curatoria/triangulacion.jsonl and used to pass a looser "3+ letters
    # in a row" check -- "NES" is exactly 3 letters.
    assert triangular._candidato_legible("NES") is False
    assert triangular._candidato_legible("¡ S") is False
    assert triangular._candidato_legible("7 So 1]") is False
    assert triangular._candidato_legible("ESPACIO RIESCO") is True
    assert triangular._candidato_legible("Carl Cox") is True


def test_senal_suficiente_ignora_venue_generico_y_headliners_ilegibles():
    assert triangular._senal_suficiente({
        "venue": "Santiago de Chile", "headliners_candidatos": ["¡ S", "NES"],
        "productora_declarada": "",
    }) is False
    assert triangular._senal_suficiente({
        "venue": "Blondie", "headliners_candidatos": [], "productora_declarada": "",
    }) is True


def test_despachar_sin_senal_nunca_toca_la_red(monkeypatch):
    fake = _FakeModulos()
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: fake)
    monkeypatch.setattr(triangular, "_source_gate_module", lambda: object())
    row = {"venue": "Santiago de Chile", "headliners_candidatos": ["¡ S"],
           "productora_declarada": "", "fecha": "2025", "pregunta": "?"}
    result = triangular.despachar([row], _catalogo())
    assert result[0]["despacho"]["estado"] == "sin_senal"
    assert fake.queries == [], "a row with no signal must not spend a search"


def test_dispatch_blind_search_does_not_claim_absence_of_sources(monkeypatch):
    """`ciego` (nobody could search) has to be recorded as distinct from
    "searched and found nothing" -- see research_lib.web_search."""
    fake = _FakeModulos({"results": [], "ciego": True, "motivo": "searxng: timeout"})
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: fake)
    monkeypatch.setattr(triangular, "_source_gate_module", lambda: object())
    row = {"venue": "Blondie", "headliners_candidatos": [],
           "productora_declarada": "", "fecha": "2025", "pregunta": "?"}
    result = triangular.despachar([row], _catalogo())
    despacho = result[0]["despacho"]
    assert despacho["estado"] == "sin_busqueda"
    assert "timeout" in despacho["motivo"]


def test_dispatch_confirmed_requires_catalog_match_and_primary_source(monkeypatch):
    import fuentes  # the real module: cl_eventos already knows instagram.com is primary

    fake = _FakeModulos({"ciego": False, "results": [
        {"url": "https://www.instagram.com/creamfields_cl/", "title": "Creamfields Chile",
         "content": "Creamfields organizo el evento en Espacio Riesco"},
    ]})
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: fake)
    monkeypatch.setattr(triangular, "_source_gate_module", lambda: fuentes)
    row = {"venue": "Espacio Riesco", "headliners_candidatos": [],
           "productora_declarada": "Creamfields", "fecha": "2025",
           "pregunta": "Verifica Creamfields"}
    result = triangular.despachar([row], _catalogo())
    despacho = result[0]["despacho"]
    assert despacho["estado"] == "confirmado"
    assert despacho["productora_declarada_confirmada"] == "Creamfields"
    assert despacho["revision_humana"] == "pendiente"
    assert fake.queries, "confirmado still searches (never trusts the declared value alone)"


def test_despachar_un_solo_dominio_primario_es_confianza_media(monkeypatch):
    import fuentes

    fake = _FakeModulos({"ciego": False, "results": [
        {"url": "https://www.instagram.com/creamfields_cl/", "title": "x",
         "content": "Creamfields en el line up"},
    ]})
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: fake)
    monkeypatch.setattr(triangular, "_source_gate_module", lambda: fuentes)
    row = {"venue": "Espacio Riesco", "headliners_candidatos": [],
           "productora_declarada": "", "fecha": "2025", "pregunta": "?"}
    result = triangular.despachar([row], _catalogo())
    assert result[0]["despacho"]["estado"] == "candidata_media_confianza"


def test_despachar_dos_dominios_independientes_es_alta_confianza(monkeypatch):
    import fuentes

    fake = _FakeModulos({"ciego": False, "results": [
        {"url": "https://www.instagram.com/creamfields_cl/", "title": "x", "content": "Creamfields"},
        {"url": "https://www.puntoticket.com/creamfields-2026", "title": "y", "content": "Creamfields"},
    ]})
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: fake)
    monkeypatch.setattr(triangular, "_source_gate_module", lambda: fuentes)
    row = {"venue": "Espacio Riesco", "headliners_candidatos": [],
           "productora_declarada": "", "fecha": "2025", "pregunta": "?"}
    result = triangular.despachar([row], _catalogo())
    assert result[0]["despacho"]["estado"] == "candidata_alta_confianza"


def test_dispatch_never_confirms_without_any_primary_source(monkeypatch):
    import fuentes

    fake = _FakeModulos({"ciego": False, "results": [
        {"url": "https://www.eldinamo.cl/nota-x", "title": "x",
         "content": "Creamfields se realizo el fin de semana"},
    ]})
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: fake)
    monkeypatch.setattr(triangular, "_source_gate_module", lambda: fuentes)
    row = {"venue": "Espacio Riesco", "headliners_candidatos": [],
           "productora_declarada": "Creamfields", "fecha": "2025", "pregunta": "?"}
    result = triangular.despachar([row], _catalogo())
    despacho = result[0]["despacho"]
    assert despacho["estado"] == "candidata_sin_fuente_primaria"
    assert despacho["estado"] != "confirmado"


def test_despachar_respeta_el_limite(monkeypatch):
    fake = _FakeModulos({"ciego": True, "motivo": "no importa"})
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: fake)
    monkeypatch.setattr(triangular, "_source_gate_module", lambda: object())
    filas = [{"venue": "Blondie", "headliners_candidatos": [],
              "productora_declarada": "", "fecha": "2025", "pregunta": "?"}
             for _ in range(5)]
    result = triangular.despachar(filas, _catalogo(), limite=2)
    assert len(result) == 2


def test_despachar_sin_modulos_no_crashea(monkeypatch):
    monkeypatch.setattr(triangular, "_research_lib_module", lambda: None)
    row = {"venue": "Blondie", "headliners_candidatos": [],
           "productora_declarada": "", "fecha": "2025", "pregunta": "?"}
    result = triangular.despachar([row], _catalogo())
    assert result[0]["despacho"]["estado"] == "sin_despacho"


def test_main_dispatch_writes_result_and_never_touches_rd_db(monkeypatch, tmp_path):
    """At the CLI level: --despachar must write DISPATCH_RESULTS_PATH using
    whatever catalog module _catalog_db_module() returns -- a fake here, so
    this test does not depend on data/rd.db."""
    entrada = tmp_path / "fichas.jsonl"
    salida = tmp_path / "triangulacion.jsonl"
    result_path = tmp_path / "triangulacion_resultado.jsonl"
    entrada.write_text(json.dumps(_ficha(
        datos_evento={"fecha": "2026-06-06", "venue": "Blondie"})) + "\n",
        encoding="utf-8")
    monkeypatch.setattr(triangular, "FICHAS", str(entrada))
    monkeypatch.setattr(triangular, "SALIDA", str(salida))
    monkeypatch.setattr(triangular, "DISPATCH_RESULTS_PATH", str(result_path))

    llamadas = []

    def _fake_despachar(filas, catalogo, limite=None):
        llamadas.append((len(filas), len(catalogo), limite))
        return [dict(f, despacho={"estado": "sin_busqueda", "motivo": "test"}) for f in filas]

    monkeypatch.setattr(triangular, "despachar", _fake_despachar)
    monkeypatch.setattr(triangular, "_catalog_db_module",
                        lambda: type("M", (), {"cargar_catalogo_productoras": staticmethod(lambda: [])})())

    triangular.main(["--despachar", "--limite", "3"])
    assert llamadas and llamadas[0][2] == 3
    result_rows = [json.loads(l) for l in result_path.read_text(encoding="utf-8").splitlines()]
    assert result_rows[0]["despacho"]["estado"] == "sin_busqueda"


def test_main_conserva_diacriticos_en_la_pregunta(monkeypatch, tmp_path):
    """The question is read by a researcher: human-read VALUES keep correct
    Spanish (the machine/human cut, 2026-07-29)."""
    filas = _correr(monkeypatch, tmp_path, [
        _ficha(datos_evento={"fecha": "2026-06-06",
                             "venue": "Teatro Caupolicán"})])
    assert "Teatro Caupolicán" in filas[0]["pregunta"]
