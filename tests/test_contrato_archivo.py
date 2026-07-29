# -*- coding: utf-8 -*-
"""El sustrato: una sola conversion micelio -> piezas+vinculos, dos consumidores.

Lo que estaba mal antes (2026-07-29): la separacion datos/contrato/piel
existia solo para iskvw, y el micelio de MAK tenia sus propios nodos y su
propio dibujo -- el mismo trabajo dos veces. La capa intermedia es
`cultura/mak_plataforma/contrato_archivo.py`, funcion pura compartida por
`tools/gen_archivo_iskvw.py` (lado repo) y `GET /api/archivo` del hub de la
caja (lado MAK, cubierto por el cron de sync).

Se fija:
- la conversion respeta el contrato (titulo vacio para obras, percibido en
  extra, fecha ausente y no cero, vinculos filtrados a ids conocidos)
- los ids pelan la extension (la trampa 1004 piezas / 0 posiciones)
- gen_archivo_iskvw DELEGA aqui: sus _id/_id_pieza son los mismos objetos
- el hub tiene la ruta y arma el sobre con version/fuente/meta
"""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(REPO_ROOT / "tools"))
import gen_archivo_iskvw as G  # noqa: E402

# gen_archivo_iskvw ya importo contrato_archivo (y otro test pudo importarlo
# antes): usar ESA instancia, no recargar una copia -- la prueba de identidad
# de abajo compara objetos funcion.
contrato = sys.modules["contrato_archivo"]


GRAFO = {
    "nodes": [
        {"id": "b7fd4e77b4a2-17926032902806396.md", "dir": "corpus",
         "titulo": "Una mujer sentada bajo una estructura", "chunks": 3},
        {"id": "informe-tapiz.md", "dir": "informes",
         "titulo": "Informe tapiz", "chunks": 2},
        {"id": "util-x.md", "dir": "codex", "titulo": "util x", "chunks": 1},
    ],
    "edges": [
        {"a": "b7fd4e77b4a2-17926032902806396.md", "b": "informe-tapiz.md",
         "w": 0.7123},
        {"a": "informe-tapiz.md", "b": "nodo-fantasma.md", "w": 0.9},
    ],
}


def test_obra_calla_y_percibido_viaja_en_extra():
    salida = contrato.convertir(GRAFO)
    obra = next(p for p in salida["piezas"] if p["clase"] == "obra")
    # silencio antes que voz prestada: la percepcion no es titulo
    assert obra["titulo"] == ""
    assert obra["extra"]["percibido"] == "Una mujer sentada bajo una estructura"
    # lo que escribio MAK si lleva su titulo
    informe = next(p for p in salida["piezas"] if p["clase"] == "informe")
    assert informe["titulo"] == "Informe tapiz"
    codigo = next(p for p in salida["piezas"] if p["clase"] == "codigo")
    assert codigo["id"] == "util-x"
    # fecha ausente, nunca cero
    assert all(p["fecha"] is None for p in salida["piezas"])


def test_ids_pelan_extension_y_vinculos_filtran_fantasmas():
    salida = contrato.convertir(GRAFO)
    ids = {p["id"] for p in salida["piezas"]}
    assert "b7fd4e77b4a2-17926032902806396" in ids  # sin "-md"
    # el vinculo hacia un nodo que no esta en piezas NO sale
    assert len(salida["vinculos"]) == 1
    v = salida["vinculos"][0]
    assert v["clase"] == "semantico"
    assert v["peso"] == 0.712


def test_gen_archivo_delega_en_el_modulo_compartido():
    # mismos objetos funcion: si alguien re-duplica _id_pieza, esto revienta
    assert G._id is contrato._id
    assert G._id_pieza is contrato._id_pieza


def test_hub_sirve_el_contrato(monkeypatch):
    hub = _cargar("hub_mak", REPO_ROOT / "cultura" / "mak_plataforma" / "hub.py")
    monkeypatch.setattr(hub, "_micelio", lambda: GRAFO)

    capturado = {}

    class _Handler:
        _json = lambda self, data, *a, **k: capturado.update(data)  # noqa: E731
        do_GET = hub.H.do_GET
        path = "/api/archivo"

    _Handler().do_GET()
    assert capturado["version"] == 1
    assert capturado["fuente"] == "micelio"
    assert capturado["meta"] == {"piezas": 3, "vinculos": 1}
    assert capturado["piezas"][0]["id"].startswith("b7fd4e77b4a2")
