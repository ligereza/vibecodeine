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
    triangular.main()
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


def test_main_conserva_diacriticos_en_la_pregunta(monkeypatch, tmp_path):
    """The question is read by a researcher: human-read VALUES keep correct
    Spanish (the machine/human cut, 2026-07-29)."""
    filas = _correr(monkeypatch, tmp_path, [
        _ficha(datos_evento={"fecha": "2026-06-06",
                             "venue": "Teatro Caupolicán"})])
    assert "Teatro Caupolicán" in filas[0]["pregunta"]
