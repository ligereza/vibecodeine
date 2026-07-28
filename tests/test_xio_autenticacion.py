# -*- coding: utf-8 -*-
"""VCD-01: xio no autenticaba nada, y eso era ejecucion remota de codigo.

Del diagnostico de seguridad del repo (2026-07-27), hallazgo CRITICO. El
servidor escucha en 0.0.0.0 con CORS `*` y lo unico que habia era una denylist
de IP vacia por defecto y un `?confirm=1` que manda el propio solicitante -- un
confirm no identifica a nadie. Con eso, cualquiera en el hotspot podia instalar
un plugin (que el registry ejecuta con exec_module) y de ahi manejar pantalla,
archivos, apps y conectividad del telefono.

El token existente protegia SOLO las rutas del plugin showcontrol.

Estos tests miran el ARCHIVO, no levantan el server: xio corre en Termux con
Flask y sus dependencias no estan en el entorno de CI. Es una comprobacion mas
debil que un test de integracion y por eso se dice: verifica que la puerta
exista y este cerrada, no que nadie sepa forzarla.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
SERVER = _REPO / "xio" / "new" / "server.py"

pytestmark = pytest.mark.skipif(not SERVER.is_file(), reason="xio/new/server.py no esta")


def _src() -> str:
    return SERVER.read_text(encoding="utf-8", errors="replace")


def test_hay_un_guardia_global_y_no_por_plugin():
    s = _src()
    assert "def _exigir_token" in s, "falta la autenticacion global"
    # tiene que colgar de before_request, no de una ruta suelta
    i = s.index("def _exigir_token")
    assert "@app.before_request" in s[max(0, i - 200):i]


def test_el_token_no_puede_quedar_vacio():
    """Fail-closed: si el entorno no trae token, se genera uno. Nunca abierto."""
    s = _src()
    assert "secrets.token_urlsafe" in s
    assert re.search(r"_TOKEN\s*=\s*os\.environ\.get\(\s*[\"']XIO_TOKEN", s)


def test_la_comparacion_es_de_tiempo_constante():
    assert "compare_digest" in _src(), (
        "comparar el token con == filtra el token por tiempo")


def test_el_guardia_no_exime_por_metodo():
    """Un GET tambien lee la pantalla y los archivos del telefono."""
    s = _src()
    i = s.index("def _exigir_token")
    cuerpo = s[i:i + 900]
    assert 'request.method == "OPTIONS"' in cuerpo    # preflight, y nada mas
    assert '"GET"' not in cuerpo


def test_instalar_plugins_esta_apagado_por_defecto():
    """Instalar un plugin es ejecutar su codigo en este proceso."""
    s = _src()
    i = s.index("def api_plugin_install")
    cuerpo = s[i:i + 700]
    assert "XIO_PERMITIR_INSTALAR_PLUGINS" in cuerpo
    assert "403" in cuerpo


def test_ya_no_hay_cors_abierto():
    s = _src()
    assert '"Access-Control-Allow-Origin", "*"' not in s, (
        "CORS * con un servidor que ejecuta acciones deja que cualquier pagina "
        "abierta en el navegador de alguien del hotspot maneje el telefono")
    assert "XIO_ORIGENES" in s


def test_loopback_exento_solo_si_se_pide():
    """El informe avisa que loopback NO es autenticacion: un proceso local
    comprometido tambien llega. Por eso la exencion es opt-in."""
    s = _src()
    assert 'XIO_LOCAL_SIN_TOKEN") == "1"' in s


def test_lo_que_responde_sin_token_no_toca_el_telefono():
    s = _src()
    m = re.search(r"_SIN_TOKEN\s*=\s*\{([^}]*)\}", s)
    assert m, "falta la lista de rutas sin token"
    rutas = re.findall(r'"([^"]+)"', m.group(1))
    assert rutas, "la lista no puede estar vacia sin declararlo"
    for r in rutas:
        assert r.rstrip("/").split("/")[-1] in ("ping", "health"), r
