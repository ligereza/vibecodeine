"""Critical curation over the real corpus without accidental promotion.

The measured field is real material from the artist's archive. The machine may
describe it and propose relations, but it cannot title it or turn a reading
into a public decision. Human authorship still enters through ``curaduria.json``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

import contrato_archivo  # noqa: E402


CAMPO = RAIZ / "iskvw" / "datos" / "campo.json"


def _campo_real() -> dict:
    return json.loads(CAMPO.read_text(encoding="utf-8"))


def test_corpus_real_separa_obra_de_material_operativo():
    piezas = _campo_real()["piezas"]
    obras = [pieza for pieza in piezas if pieza.get("tipo") == "obra"]
    material_operativo = [pieza for pieza in piezas
                          if pieza.get("tipo") in {"flyer_evento", "logo",
                                                    "ficha_sustancia"}]

    assert len(piezas) == 219
    assert len(obras) == 134
    assert material_operativo
    assert all(pieza.get("archivo") for pieza in obras[:10])


def test_lectura_critica_real_no_firma_titulos_ni_publicacion():
    campo = _campo_real()
    seleccion = [pieza for pieza in campo["piezas"]
                 if pieza.get("tipo") == "obra"][:3]
    datos = contrato_archivo.desde_campo({"piezas": seleccion})

    lectura = {
        "reading": [pieza["extra"]["percibido"]
                    for pieza in datos["piezas"]],
        "selection": [pieza["id"] for pieza in datos["piezas"]],
        "relationships": [],
        "public_status": "revision_local",
    }
    assert set(lectura) == {"reading", "selection", "relationships",
                            "public_status"}
    assert lectura["reading"] and lectura["selection"]
    assert isinstance(lectura["relationships"], list)
    assert all(pieza["titulo"] is None for pieza in datos["piezas"])
    assert all("percibido" in pieza["extra"] for pieza in datos["piezas"])
    assert lectura["public_status"] != "publicada"

    curaduria = {
        "piezas": {
            seleccion[0]["id"]: {
                "titulo": "Obra firmada por el artista",
                "nota": "La seleccion aun necesita una lectura critica.",
            },
            seleccion[1]["id"]: {"mostrar": False},
        }
    }
    revisada = contrato_archivo.aplicar_curaduria(
        datos, curaduria, existe=lambda _src: False)
    ids = {pieza["id"] for pieza in revisada["piezas"]}
    firmada = next(pieza for pieza in revisada["piezas"]
                   if pieza["id"] == seleccion[0]["id"])

    assert seleccion[1]["id"] not in ids
    assert firmada["titulo"] == "Obra firmada por el artista"
    assert firmada["extra"]["titulo_firmado"] is True
    assert firmada["extra"]["nota"]
