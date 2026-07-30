# -*- coding: utf-8 -*-
"""La base de venues: que sembrar de memoria no se disfrace de medicion.

La regla que estos tests fijan es la del §6.4 de la memoria de direccion --
descriptivo, nunca certificante -- aplicada al dato: un venue sembrado desde
tres anios de gira vale, pero vale como `aportado`. `medido` lo escribe quien
estuvo en la sala con instrumento y firma, y ese salto de tier es lo unico que
no es gratis.

Lo que NO se prueba aca: que las cotas sembradas sean correctas. No se midieron,
asi que no se afirma que lo sean; se afirma que el archivo dice de si mismo que
vienen de memoria.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import venue  # noqa: E402

ESQUEMA = json.loads((REPO / "schemas" / "venue.schema.json").read_text(encoding="utf-8"))


def _valida(v: dict) -> list[str]:
    import jsonschema

    val = jsonschema.Draft202012Validator(ESQUEMA)
    return [e.message for e in val.iter_errors(v)]


# ----------------------------------------------------------------- sembrar
def test_sembrar_de_memoria_marca_aportado_nunca_medido():
    v = venue.parsear_semilla("Santiago | Sala Uno | teatro | 10 | 4.5 | 6.2 | 9 | columna")
    assert v["fuente_datos"] == "memoria"
    assert v["escenario"]["ancho"]["confianza"] == "aportado"
    assert v["sala"]["altura_truss"]["confianza"] == "aportado"
    todas = [
        m["confianza"]
        for g in ("escenario", "sala")
        for m in v[g].values()
    ]
    assert "medido" not in todas, "de memoria no es medido"


def test_lo_sembrado_valida_contra_el_esquema():
    v = venue.parsear_semilla("Valparaiso | La Otra | club | 8 | 4 | 5 | 7 | -")
    assert _valida(v) == []


def test_el_id_es_estable_y_sin_tildes():
    v = venue.parsear_semilla("Concepción | Galpón Ñuñoa | galpon | 12 | 6 | - | - | -")
    assert v["id"] == "concepcion-galpon-nunoa"


def test_campos_vacios_no_inventan_medidas():
    v = venue.parsear_semilla("Arica | Sin Datos | otro | - | - | - | - | -")
    assert "escenario" not in v and "sala" not in v
    assert _valida(v) == []


def test_una_semilla_sin_nombre_o_ciudad_se_rechaza():
    with pytest.raises(ValueError):
        venue.parsear_semilla(" | Sin Ciudad | club | 8 | 4 | 5 | 7 | -")


def test_tipo_invalido_se_rechaza():
    with pytest.raises(ValueError):
        venue.parsear_semilla("Santiago | X | discoteque | 8 | 4 | 5 | 7 | -")


def test_comentarios_y_lineas_vacias_se_saltan():
    assert venue.parsear_semilla("# comentario") is None
    assert venue.parsear_semilla("   ") is None


def test_acepta_coma_decimal_y_faltantes_al_final():
    v = venue.parsear_semilla("Osorno | Coma | club | 9,5 | 4")
    assert v["escenario"]["ancho"]["m"] == 9.5
    assert "altura_truss" not in v.get("sala", {})


# ----------------------------------------------------------------- coherencia
def _base(**extra) -> dict:
    v = {
        "id": "x-y",
        "nombre": "Y",
        "ciudad": "X",
        "tipo": "club",
        "publico": True,
        "fecha_captura": "2026-07-30",
        "fuente_datos": "memoria",
    }
    v.update(extra)
    return v


def test_avisa_si_firma_sin_un_solo_dato_medido():
    v = _base(firmado_por="MAK", escenario={"ancho": {"m": 10, "confianza": "aportado"}})
    assert any("firmado pero sin" in a for a in venue.coherencia(v))


def test_avisa_si_dice_medido_pero_la_fuente_es_memoria():
    v = _base(escenario={"ancho": {"m": 10, "confianza": "medido"}})
    assert any("De memoria no es medido" in a for a in venue.coherencia(v))


def test_avisa_si_una_sala_no_publica_lleva_direccion():
    """La geometria es valiosa y anonima; la identidad es peligrosa y no se necesita."""
    v = _base(publico=False, direccion="Calle Falsa 123")
    assert any("publico=false" in a for a in venue.coherencia(v))


def test_avisa_si_la_altura_libre_supera_al_truss():
    v = _base(sala={"altura_truss": {"m": 5, "confianza": "aportado"},
                    "altura_libre": {"m": 6, "confianza": "aportado"}})
    assert any("Imposible" in a for a in venue.coherencia(v))


def test_avisa_si_una_cita_no_trae_fuente():
    v = _base(citas=[{"afirmacion": "truss soporta 500 kg", "fuente": "  "}])
    assert any("sin fuente" in a for a in venue.coherencia(v))


def test_un_venue_limpio_no_genera_avisos():
    v = _base(escenario={"ancho": {"m": 10, "confianza": "aportado"}})
    assert venue.coherencia(v) == []


# ----------------------------------------------------------------- esquema
def test_el_esquema_rechaza_una_confianza_inventada():
    v = _base(escenario={"ancho": {"m": 10, "confianza": "masomenos"}})
    assert _valida(v) != []


def test_el_esquema_exige_confianza_en_cada_medida():
    v = _base(escenario={"ancho": {"m": 10}})
    assert _valida(v) != []


def test_el_esquema_rechaza_medidas_absurdas():
    for malo in (0, -3, 9999):
        v = _base(escenario={"ancho": {"m": malo, "confianza": "aportado"}})
        assert _valida(v) != [], f"acepto {malo} m"


# ----------------------------------------------------------------- sitio
def test_el_sitio_no_publica_las_salas_no_publicas(tmp_path, monkeypatch):
    monkeypatch.setattr(venue, "DIR_VENUES", tmp_path / "v")
    monkeypatch.setattr(venue, "SALIDA_SITIO", tmp_path / "out" / "index.html")
    venue.DIR_VENUES.mkdir(parents=True)
    (venue.DIR_VENUES / "a.json").write_text(
        json.dumps(_base(id="a", nombre="Publica")), encoding="utf-8"
    )
    (venue.DIR_VENUES / "b.json").write_text(
        json.dumps(_base(id="b", nombre="Reservada", publico=False)), encoding="utf-8"
    )
    assert venue.sitio() == 0
    html = venue.SALIDA_SITIO.read_text(encoding="utf-8")
    assert "Publica" in html
    assert "Reservada" not in html, "una sala con publico=false no puede salir en el sitio"


def test_el_sitio_es_un_solo_archivo_sin_red(tmp_path, monkeypatch):
    monkeypatch.setattr(venue, "DIR_VENUES", tmp_path / "v")
    monkeypatch.setattr(venue, "SALIDA_SITIO", tmp_path / "out" / "index.html")
    venue.DIR_VENUES.mkdir(parents=True)
    (venue.DIR_VENUES / "a.json").write_text(json.dumps(_base()), encoding="utf-8")
    venue.sitio()
    html = venue.SALIDA_SITIO.read_text(encoding="utf-8")
    assert "<script src=" not in html and "cdn" not in html.lower()
    assert "localStorage" not in html
