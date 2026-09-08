#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_motor_semantico_rasterizador.py -- el rasterizador (SVG->PNG,
dos backends) y el critico perceptual que se apoya en el.

El defecto que esto guarda (ver docstring de critico.py): la version original
llamaba sys.exit() al importarse cuando no habia backend, lo que volvia el
modulo INIMPORTABLE y por lo tanto intesteable. `rasterizador.rasterizar()`
debe levantar `RasterizadorNoDisponibleError` -- nunca SystemExit, nunca
ImportError -- y `critico.analizar()` debe devolver un dict con 'error' en vez
de reventar.

Import de ambos modulos con CERO backends instalados debe funcionar siempre;
los tests que necesitan pixeles reales se saltan si esta maquina no tiene
ninguno (`backend_disponible()`).
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cultura" / "mak_codex"))

# el import en si mismo es la primera prueba: si critico.py todavia llamara
# sys.exit() al importarse con dependencias ausentes, esta linea reventaria
# la coleccion entera de pytest.
from motor_semantico import compilador, critico, rasterizador  # noqa: E402

SPEC_SIMPLE = {
    "slug": "raster-test", "composicion": "centro_unico", "tono": "acido",
    "capas": [{"rol": "protagonista", "figura": "disco", "gesto": "girar",
               "ritmo": "rapido"}],
}


def _svg_compilado():
    svg, _avisos = compilador.compilar(SPEC_SIMPLE, "raster-test")
    return svg


requiere_backend = pytest.mark.skipif(
    rasterizador.backend_disponible() is None,
    reason="esta maquina no tiene cairosvg ni navegador")

# Rasterizar y ANIMAR son dos capacidades, y confundirlas costo una matriz de
# CI en rojo: en ubuntu el backend era cairosvg, que dibuja perfecto y no
# ejecuta animaciones CSS, asi que todo cuadro salia igual al primero.
requiere_anima = pytest.mark.skipif(
    rasterizador.backend_disponible(anima=True) is None,
    reason="ningun backend dibuja y anima aca -- %s"
           % rasterizador.por_que_no_hay_navegador(True))


# ---------------------------------------------------------------------------
# sin ningun backend: la excepcion correcta, nunca SystemExit/ImportError
# ---------------------------------------------------------------------------
def test_sin_backends_levanta_error_propio_no_systemexit(monkeypatch):
    monkeypatch.setattr(rasterizador, "_cairosvg", lambda: None)
    monkeypatch.setattr(rasterizador, "_binarios", lambda: [])
    monkeypatch.setattr(rasterizador, "_edge", lambda: None)
    assert rasterizador.backend_disponible() is None
    with pytest.raises(rasterizador.RasterizadorNoDisponibleError):
        rasterizador.rasterizar(_svg_compilado())


def test_sin_backends_no_es_systemexit_ni_importerror(monkeypatch):
    monkeypatch.setattr(rasterizador, "_cairosvg", lambda: None)
    monkeypatch.setattr(rasterizador, "_binarios", lambda: [])
    monkeypatch.setattr(rasterizador, "_edge", lambda: None)
    try:
        rasterizador.rasterizar(_svg_compilado())
        pytest.fail("deberia haber levantado RasterizadorNoDisponibleError")
    except SystemExit:
        pytest.fail("levanto SystemExit: es el defecto original (sys.exit al "
                    "no encontrar backend), que vuelve el modulo intesteable")
    except ImportError:
        pytest.fail("levanto ImportError en vez de RasterizadorNoDisponibleError")
    except rasterizador.RasterizadorNoDisponibleError:
        pass


def test_mutacion_reintroducir_sys_exit_lo_atraparia():
    """Verificacion viva de que el guard de arriba de verdad distingue: si
    rasterizar() volviera a llamar sys.exit() (el bug original), pytest lo
    veria como un SystemExit no capturado por 'except RasterizadorNoDisponible-
    Error' y el test de arriba fallaria. Lo probamos aca en un sandbox
    (una funcion standalone que reproduce el bug), sin tocar el modulo real."""
    def _version_vieja_con_bug():
        sys.exit("ningun rasterizador disponible")

    with pytest.raises(SystemExit):
        _version_vieja_con_bug()
    # y confirmamos que ese SystemExit efectivamente NO es una instancia de
    # RasterizadorNoDisponibleError (si lo fuera, el bug seria invisible)
    try:
        _version_vieja_con_bug()
    except BaseException as e:
        assert not isinstance(e, rasterizador.RasterizadorNoDisponibleError)


def test_critico_sin_backend_devuelve_error_sin_reventar(monkeypatch):
    monkeypatch.setattr(rasterizador, "_cairosvg", lambda: None)
    monkeypatch.setattr(rasterizador, "_binarios", lambda: [])
    monkeypatch.setattr(rasterizador, "_edge", lambda: None)
    r = critico.analizar(_svg_compilado(), nombre="raster-test")
    assert "error" in r
    assert r["puntaje"] is None
    assert isinstance(r["error"], str) and r["error"]


def test_mutacion_critico_sin_backend_capturaria_una_excepcion_no_manejada(monkeypatch):
    """Si critico.analizar() dejara de capturar RasterizadorNoDisponibleError
    (por ejemplo si alguien angostara el except a solo SinPillowError),
    analizar() reventaria en vez de devolver {'error': ...}. Simulamos ese
    angostamiento monkeypencheando rasterizador.rasterizar para levantar un
    RuntimeError distinto que el except actual NO atrapa, y confirmamos que
    ESO si revienta -- lo que prueba que el except real (que abajo seguimos
    confiando) es especifico y no un `except Exception` disfrazado."""
    def _explota(*a, **k):
        raise RuntimeError("boom no relacionado")

    monkeypatch.setattr(rasterizador, "rasterizar", _explota)
    with pytest.raises(RuntimeError):
        critico.analizar(_svg_compilado(), nombre="raster-test")


# ---------------------------------------------------------------------------
# con el backend real de esta maquina
# ---------------------------------------------------------------------------
@requiere_backend
def test_rasterizar_produce_png_real():
    datos = rasterizador.rasterizar(_svg_compilado(), tam=96)
    assert datos[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(datos) > 100


@requiere_anima
def test_animar_produce_gif_y_mide_cuadros_distintos(tmp_path):
    salida = tmp_path / "salida.gif"
    ruta, n, distintos = rasterizador.animar(
        _svg_compilado(), salida, cuadros=4, tam=96)
    assert ruta == salida
    assert n == 4
    datos = salida.read_bytes()
    assert datos[:6] == b"GIF89a"
    b = rasterizador.backend_disponible(anima=True)
    sonda_q = rasterizador.rasterizar(rasterizador._SONDA_ANIMA,
                                      tam=rasterizador._TAM_SONDA,
                                      backend=b, anima=True)
    sonda_m = rasterizador.rasterizar(rasterizador._SONDA_ANIMA,
                                      tam=rasterizador._TAM_SONDA,
                                      avance_ms=500, backend=b, anima=True)
    assert distintos > 1, (
        "todos los cuadros iguales. backend=%s (rasteriza: %s); sonda "
        "%d/%d B %s -- si la sonda difiere y el SVG real no, el backend anima "
        "pero no esta dibujando el contenido"
        % (b, rasterizador.backend_disponible(), len(sonda_q), len(sonda_m),
           "IGUALES" if sonda_q == sonda_m else "distintos"))


def test_un_backend_que_dibuja_y_no_anima_lo_dice_en_vez_de_mentir(tmp_path,
                                                                   monkeypatch):
    """LA regresion de la matriz de CI del 2026-07-30.

    ubuntu tenia cairosvg: rasteriza impecable y no ejecuta ni una animacion
    CSS, asi que los 12 cuadros del ciclo salian identicos. `animar()` devolvia
    `distintos=1` y el llamador leia ese 1 como "el icono declara un movimiento
    que no ocurre" -- una acusacion contra 16 archivos sanos. El 1 de "no lo
    medi" y el 1 de "esta muerto" eran el mismo numero.

    Un instrumento incapaz levanta BackendNoAnimaError. Nunca un numero.
    """
    class _Ciego:
        """Dibuja distinto segun el tamano, e ignora el animation-delay: es lo
        que hace un rasterizador estatico de verdad."""
        @staticmethod
        def svg2png(bytestring=None, output_width=None, output_height=None):
            return b"\x89PNG" + bytes([output_width or 0]) * 8

    monkeypatch.setattr(rasterizador, "_cairosvg", lambda: _Ciego)
    monkeypatch.setattr(rasterizador, "_binarios", lambda: [])
    monkeypatch.setattr(rasterizador, "_edge", lambda: None)
    monkeypatch.setattr(rasterizador, "_ANIMADORES", {})
    monkeypatch.setattr(rasterizador, "_SONDEADOS", {})
    monkeypatch.setattr(rasterizador, "_PERFIL_ELEGIDO", {})

    assert rasterizador.backend_disponible() == "cairosvg", (
        "sigue sirviendo para rasterizar: la capacidad que falta es la otra")
    assert rasterizador.backend_disponible(anima=True) is None

    with pytest.raises(rasterizador.BackendNoAnimaError):
        rasterizador.animar(_svg_compilado(), tmp_path / "no.gif", cuadros=4)


@requiere_backend
def test_animar_con_un_cuadro_rechaza(tmp_path):
    with pytest.raises(ValueError):
        rasterizador.animar(_svg_compilado(), tmp_path / "no.gif", cuadros=1)


@requiere_backend
def test_critico_analiza_svg_real_con_metricas_sanas():
    r = critico.analizar(_svg_compilado(), nombre="raster-test")
    assert r.get("error") is None
    assert r["puntaje"] is not None
    assert 0 <= r["puntaje"] <= 100
    assert 0 <= r["tinta"] <= 1
    assert 0 <= r["descentrado"]
    assert r["margen"] >= 0


@requiere_backend
def test_mutacion_lienzo_vacio_da_puntaje_cero():
    """Verificacion viva de que analizar() de verdad mide y no solo devuelve
    un puntaje fijo: un SVG con viewBox correcto pero SIN contenido dibujado
    (fondo=figura, o directamente vacio) debe puntuar 0 y alertar lienzo
    vacio. No es un mock: es un SVG real, rasterizado de verdad."""
    svg_vacio = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">\n'
        '<rect width="120" height="120" fill="#000000"/>\n'
        "</svg>\n")
    r = critico.analizar(svg_vacio, nombre="vacio")
    assert r["puntaje"] == 0
    assert any("VAC" in a.upper() for a in r["alertas"])


def test_un_edge_que_existe_y_no_rasteriza_cuenta_como_ausente(monkeypatch):
    """El defecto que puso el CI en rojo el 2026-07-30, fijado.

    El runner de ubuntu TIENE `/usr/bin/microsoft-edge` y no produce PNG. Con
    la deteccion por existencia de archivo, `backend_disponible()` respondia
    "edge", los tests que dependen de un rasterizador NO se saltaban, y el
    fallo aparecia en medio de un analisis perceptual en vez de al preguntar
    por la capacidad.

    Se simula con un binario que existe de verdad y no es Edge: el propio
    interprete de Python. Si algun dia la deteccion vuelve a mirar solo si el
    archivo existe, este test se pone rojo.
    """
    rasterizador._SONDEADOS.clear()
    monkeypatch.setattr(rasterizador, "_cairosvg", lambda: None)
    monkeypatch.setattr(rasterizador, "_binarios", lambda: [sys.executable])
    monkeypatch.setattr(rasterizador, "_edge", lambda: sys.executable)

    assert Path(sys.executable).exists(), "el binario falso tiene que existir"
    assert rasterizador.backend_disponible() is None
    with pytest.raises(rasterizador.RasterizadorNoDisponibleError):
        rasterizador.rasterizar("<svg/>")
    rasterizador._SONDEADOS.clear()


def test_la_sonda_no_sobrevive_a_que_cambie_el_binario(monkeypatch):
    """La sonda se recuerda por RUTA, no en un booleano global.

    Con un solo booleano, el resultado del primer sondeo contaminaba cualquier
    consulta posterior: un test que finge "no hay Edge" veia el 'si sirve' de
    la corrida anterior. Indexar por binario es lo que hace que la memoria de
    la medicion no mienta cuando el entorno cambia.
    """
    rasterizador._SONDEADOS.clear()
    monkeypatch.setattr(rasterizador, "_cairosvg", lambda: None)

    monkeypatch.setattr(rasterizador, "_binarios", lambda: [sys.executable])
    monkeypatch.setattr(rasterizador, "_edge", lambda: sys.executable)
    assert rasterizador.backend_disponible() is None
    assert rasterizador._SONDEADOS.get(sys.executable) is False

    monkeypatch.setattr(rasterizador, "_binarios", lambda: [])
    monkeypatch.setattr(rasterizador, "_edge", lambda: None)
    assert rasterizador.backend_disponible() is None
    rasterizador._SONDEADOS.clear()
