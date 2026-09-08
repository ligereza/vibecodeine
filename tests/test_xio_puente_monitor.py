"""Offline tests for cultura/mak_xio_puente/monitor.py -- the READ-ONLY eye
on the xio phone (MAK's only internet).

Rescued 2026-07-30: 172 lines started by a systemd unit that existed on ONE
disk and had never been verified running. Its doctrine is in its own
docstring: GET-only against a hard allowlist, never POST, never touch
network/hotspot/charge endpoints. These tests pin the poll state machine
(reachable / blocked / down / recovered), the defensive summary extraction,
the ntfy antispam window and the history rotation. No network: `_get` and
`ntfy_publish` are faked; every path lands in tmp_path.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PUENTE_DIR = RAIZ / "cultura" / "mak_xio_puente"

# monitor.py hardcodes sys.path.insert("/home/mak/research") for the box; on
# any other machine the repo mirror provides research_lib (vigia does the same).
_RESEARCH = str(RAIZ / "cultura" / "mak_research")
if _RESEARCH not in sys.path:
    sys.path.insert(0, _RESEARCH)


def _cargar():
    spec = importlib.util.spec_from_file_location(
        "monitor_bajo_prueba", PUENTE_DIR / "monitor.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


monitor = _cargar()


def _en_tmp(monkeypatch, tmp_path):
    """Point every state file at tmp and capture ntfy sends."""
    enviados = []
    monkeypatch.setattr(monitor, "ESTADO", str(tmp_path / "estado.json"))
    monkeypatch.setattr(monitor, "HISTORIA", str(tmp_path / "historia.jsonl"))
    monkeypatch.setattr(monitor, "ALERTAS", str(tmp_path / "alertas.json"))
    monkeypatch.setattr(monitor, "ntfy_publish",
                        lambda topic, msg, title="": enviados.append(msg))
    return enviados


def _respuestas(monkeypatch, mapa, registro=None):
    """Fake _get: route -> (code, payload)."""
    def _get(ruta):
        if registro is not None:
            registro.append(ruta)
        return mapa.get(ruta, (0, None))
    monkeypatch.setattr(monitor, "_get", _get)


# ----------------------------------------------------------------- _resumen

def test_resumen_extrae_bateria_en_cualquiera_de_sus_nombres():
    for clave in ("level", "battery", "pct", "percentage"):
        r = monitor._resumen({"/battery/status": {clave: 73.4}})
        assert r["bateria_pct"] == 73, clave


def test_resumen_extrae_cargando_y_clientes_lista_o_numero():
    r = monitor._resumen({
        "/battery/status": {"level": 50, "plugged": 1},
        "/connectivity/status": {"clients": ["mak", "otro"]},
    })
    assert r["cargando"] is True
    assert r["clientes_hotspot"] == 2
    r2 = monitor._resumen({"/connectivity/status": {"n_clients": 3}})
    assert r2["clientes_hotspot"] == 3


def test_resumen_defensivo_ante_formas_raras():
    """The phone's payload shape is not under our control: strings where
    numbers should be, lists where dicts should be -- nothing crashes and
    nothing is invented."""
    r = monitor._resumen({
        "/battery/status": {"level": "73"},          # str: not a number
        "/connectivity/status": ["not", "a", "dict"],
        "/status": {"plugins": 5},                    # len(int) -> TypeError
    })
    assert r == {}


def test_resumen_cuenta_plugins():
    r = monitor._resumen({"/status": {"plugins": ["a", "b", "c"]}})
    assert r["plugins"] == 3


# --------------------------------------------------------------------- poll

def test_poll_sano_escribe_estado_e_historia(monkeypatch, tmp_path):
    enviados = _en_tmp(monkeypatch, tmp_path)
    _respuestas(monkeypatch, {
        "/status": (200, {"plugins": ["x"]}),
        "/obs": (200, {}),
        "/battery/status": (200, {"level": 88, "charging": True}),
        "/connectivity/status": (200, {"clients": ["mak"]}),
    })
    estado, fallos = monitor.poll(fallos_previos=0)

    assert estado["alcanzable"] is True
    assert estado["bloqueado"] is False
    assert estado["http"] == 200
    assert estado["rutas_ok"] == sorted(monitor.RUTAS_LECTURA)
    assert estado["resumen"] == {"bateria_pct": 88, "cargando": True,
                                 "clientes_hotspot": 1, "plugins": 1}
    assert fallos == 0
    assert enviados == [], "a healthy poll must not notify"

    en_disco = json.loads((tmp_path / "estado.json").read_text())
    assert en_disco["resumen"]["bateria_pct"] == 88
    linea = (tmp_path / "historia.jsonl").read_text().strip()
    assert json.loads(linea)["http"] == 200


def test_poll_403_corta_el_barrido_y_alerta_bloqueado(monkeypatch, tmp_path):
    """The deny gate: on the first 403 the monitor stops insisting on the
    remaining routes and raises exactly one 'bloqueado' alert."""
    enviados = _en_tmp(monkeypatch, tmp_path)
    pedidas = []
    _respuestas(monkeypatch, {r: (403, None) for r in monitor.RUTAS_LECTURA},
                registro=pedidas)
    estado, fallos = monitor.poll(fallos_previos=0)

    assert pedidas == [monitor.RUTAS_LECTURA[0]], "403 -> no more requests"
    assert estado["bloqueado"] is True
    assert estado["alcanzable"] is True, "403 means the server is UP"
    assert fallos == 0
    assert len(enviados) == 1 and "403" in enviados[0]


def test_poll_caida_alerta_al_tercer_fallo_exacto(monkeypatch, tmp_path):
    enviados = _en_tmp(monkeypatch, tmp_path)
    _respuestas(monkeypatch, {})  # everything unreachable -> (0, None)

    _, f1 = monitor.poll(fallos_previos=0)
    _, f2 = monitor.poll(fallos_previos=f1)
    assert (f1, f2) == (1, 2) and enviados == [], "quiet until the 3rd miss"

    _, f3 = monitor.poll(fallos_previos=f2)
    assert f3 == 3
    assert len(enviados) == 1 and "inalcanzable" in enviados[0]


def test_poll_recuperacion_notifica_una_vez(monkeypatch, tmp_path):
    enviados = _en_tmp(monkeypatch, tmp_path)
    _respuestas(monkeypatch, {"/status": (200, {})})
    _, fallos = monitor.poll(fallos_previos=3)
    assert fallos == 0, "one good poll resets the failure counter"
    assert len(enviados) == 1 and "DE VUELTA" in enviados[0]


def test_poll_bateria_baja_solo_si_descarga(monkeypatch, tmp_path):
    enviados = _en_tmp(monkeypatch, tmp_path)
    _respuestas(monkeypatch, {
        "/battery/status": (200, {"level": 15, "charging": True})})
    monitor.poll(fallos_previos=0)
    assert enviados == [], "15% but charging: not an emergency"

    # Fresh antispam file, now discharging.
    (tmp_path / "alertas.json").unlink(missing_ok=True)
    _respuestas(monkeypatch, {
        "/battery/status": (200, {"level": 15, "charging": False})})
    monitor.poll(fallos_previos=0)
    assert len(enviados) == 1 and "15%" in enviados[0]


def test_antispam_30_minutos_por_clave(monkeypatch, tmp_path):
    """Two polls inside the window -> one ntfy. Distinct keys do not share
    the window."""
    enviados = _en_tmp(monkeypatch, tmp_path)
    monitor._alerta("caido", "primera")
    monitor._alerta("caido", "repetida")
    monitor._alerta("bateria", "otra clave")
    assert enviados == ["primera", "otra clave"]

    # An old timestamp on record re-arms the key.
    registro = json.loads((tmp_path / "alertas.json").read_text())
    registro["caido"] -= monitor.ANTISPAM_S + 1
    (tmp_path / "alertas.json").write_text(json.dumps(registro))
    monitor._alerta("caido", "pasada la ventana")
    assert enviados[-1] == "pasada la ventana"


def test_historia_rota_al_pasar_5mb(monkeypatch, tmp_path):
    _en_tmp(monkeypatch, tmp_path)
    _respuestas(monkeypatch, {"/status": (200, {})})
    historia = tmp_path / "historia.jsonl"
    with open(historia, "wb") as f:
        f.truncate((5 << 20) + 1)
    monitor.poll(fallos_previos=0)
    assert (tmp_path / "historia.jsonl.1").exists(), "old history rotated away"
    assert os.path.getsize(historia) < 4096, "new history starts near-empty"


def test_estado_se_escribe_atomico(monkeypatch, tmp_path):
    """os.replace from a .tmp: a reader never sees a half-written estado.json."""
    _en_tmp(monkeypatch, tmp_path)
    _respuestas(monkeypatch, {"/status": (200, {})})
    monitor.poll(fallos_previos=0)
    assert not (tmp_path / "estado.json.tmp").exists()
    json.loads((tmp_path / "estado.json").read_text())  # valid JSON on disk
