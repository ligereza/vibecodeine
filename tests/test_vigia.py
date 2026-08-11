# -*- coding: utf-8 -*-
"""Tests for cultura/mak_vigia/vigia.py -- the watch department.

The department is a diff, so the tests are about the diff: a new item must be
detected exactly once, a source that goes quiet must SCREAM instead of
returning a tidy empty list, and the conditional-GET headers must actually
leave the machine. No network is touched: every fetch is a fake opener.
"""
import importlib.util
import json
import sys
import threading
import time
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
VIGIA_DIR = RAIZ / "cultura" / "mak_vigia"


def _cargar():
    spec = importlib.util.spec_from_file_location(
        "vigia_bajo_prueba", VIGIA_DIR / "vigia.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


vigia = _cargar()


# --------------------------------------------------------------- utilidades

class RespuestaFalsa:
    def __init__(self, cuerpo=b"", headers=None, status=200):
        self._cuerpo = cuerpo
        self.headers = headers or {}
        self.status = status

    def read(self):
        return self._cuerpo

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_run_is_atomic_across_concurrent_crons(monkeypatch, tmp_path):
    state_dir = tmp_path / "estado"
    state = {"active": 0, "max_active": 0}
    state_lock = threading.Lock()

    def slow_review(source, previous, seen, now, **_kwargs):
        with state_lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.05)
        is_new = "hash-demo" not in seen
        with state_lock:
            state["active"] -= 1
        return {
            "nombre": "demo", "error": "", "alerta": "",
            "nuevos": ([{"h": "hash-demo", "titulo": "Aviso nuevo",
                          "ts": now}] if is_new else []),
            "estado": {"hashes": ["hash-demo"], "n_items": 1},
        }

    monkeypatch.setattr(vigia, "revisar_fuente", slow_review)
    source = {"id": "demo", "nombre": "demo"}
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        vigia.correr([source], str(state_dir), notificar=False,
                     ahora=1000, max_vistos=5000))) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    seen_lines = (state_dir / "vistos.jsonl").read_text(encoding="utf-8").splitlines()
    assert state["max_active"] == 1
    assert len(seen_lines) == 1
    assert sum(len(result[0]["nuevos"]) for result in results) == 1


def test_save_last_replace_failure_leaves_no_temp(monkeypatch, tmp_path):
    state_dir = tmp_path / "estado"
    state_dir.mkdir()
    path = state_dir / vigia.ULTIMO
    path.write_text('{"old": true}', encoding="utf-8")
    original_replace = vigia.os.replace

    def fail_install(source, destination):
        if destination == str(path):
            raise OSError("simulated replace failure")
        return original_replace(source, destination)

    monkeypatch.setattr(vigia.os, "replace", fail_install)
    with pytest.raises(OSError, match="simulated replace failure"):
        vigia.guardar_ultimo(str(state_dir), {"new": True})

    assert path.read_text(encoding="utf-8") == '{"old": true}'
    assert not list(state_dir.glob(".*.tmp"))


def abridor(paginas, registro=None):
    """Fake urlopen. paginas: url -> bytes | (bytes, headers) | Exception."""
    def _abrir(req, timeout=None):
        if registro is not None:
            registro.append(req)
        r = paginas[req.full_url]
        if isinstance(r, Exception):
            raise r
        if isinstance(r, tuple):
            return RespuestaFalsa(r[0], r[1])
        return RespuestaFalsa(r)
    return _abrir


def _pagina(titulos, prefijo="/aviso/"):
    filas = "".join(
        '<li><a href="%s%d">%s</a></li>' % (prefijo, i, t)
        for i, t in enumerate(titulos))
    return ("<html><body><ul>%s</ul></body></html>" % filas).encode("utf-8")


FUENTE = {"id": "demo", "nombre": "Demo", "tipo": "general",
          "url": "https://ejemplo.cl/lista", "formato": "html"}


# ------------------------------------------------------- diff por hash

def test_hash_diff_detecta_lo_nuevo_y_solo_una_vez(tmp_path):
    estado = tmp_path / "estado"
    paginas = {FUENTE["url"]: _pagina(["Convocatoria de residencia en Valparaiso",
                                       "Beca de movilidad para artistas"])}

    r1 = vigia.correr([FUENTE], str(estado), abrir=abridor(paginas),
                      notificar=False, ahora=1000.0)[0]
    assert r1["n_items"] == 2
    assert len(r1["nuevos"]) == 2, "la primera corrida ve todo como nuevo"

    # Misma pagina, segunda corrida: nada nuevo.
    r2 = vigia.correr([FUENTE], str(estado), abrir=abridor(paginas),
                      notificar=False, ahora=2000.0)[0]
    assert r2["n_items"] == 2
    assert r2["nuevos"] == [], "un item ya visto no se vuelve a notificar"

    # Aparece uno mas: solo ese es nuevo.
    paginas[FUENTE["url"]] = _pagina([
        "Convocatoria de residencia en Valparaiso",
        "Beca de movilidad para artistas",
        "Residencia de invierno en Chiloe"])
    r3 = vigia.correr([FUENTE], str(estado), abrir=abridor(paginas),
                      notificar=False, ahora=3000.0)[0]
    assert len(r3["nuevos"]) == 1
    assert r3["nuevos"][0]["titulo"] == "Residencia de invierno en Chiloe"


def test_hash_ignora_mayusculas_y_tildes_del_mismo_aviso(tmp_path):
    """Un portal que re-acentua su propio titulo no genera un aviso falso."""
    estado = tmp_path / "estado"
    url = FUENTE["url"]
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: _pagina(["Concurso de Composicion Musical"])}),
                 notificar=False, ahora=1000.0)
    r = vigia.correr([FUENTE], str(estado),
                     abrir=abridor({url: _pagina(["CONCURSO DE COMPOSICIÓN MUSICAL"])}),
                     notificar=False, ahora=2000.0)[0]
    assert r["nuevos"] == []


def test_el_titulo_conserva_las_tildes_aunque_el_hash_las_pliegue(tmp_path):
    """El hash es clave de maquina y se pliega a ASCII; el titulo que lee una
    persona conserva el espanol correcto (el corte maquina/humano)."""
    estado = tmp_path / "estado"
    pagina = _pagina(["Técnico en Enfermería para el Hospital de Ñuñoa"])
    r = vigia.correr([FUENTE], str(estado), abrir=abridor({FUENTE["url"]: pagina}),
                     notificar=False, ahora=1000.0)[0]
    assert r["nuevos"][0]["titulo"] == "Técnico en Enfermería para el Hospital de Ñuñoa"
    linea = (estado / vigia.VISTOS).read_text(encoding="utf-8").strip()
    assert json.loads(linea)["titulo"].startswith("Técnico en Enfermería")


# ----------------------------------------------------------- REGLA DE ORO

def test_regla_de_oro_cero_despues_de_no_cero_es_ERROR(tmp_path):
    """La linea que decide si el departamento sirve: una pagina que sigue
    respondiendo 200 pero ahora parsea CERO items no puede devolver silencio."""
    estado = tmp_path / "estado"
    url = FUENTE["url"]
    r1 = vigia.correr([FUENTE], str(estado),
                      abrir=abridor({url: _pagina(["Residencia de verano en Antofagasta",
                                                   "Beca de creacion literaria"])}),
                      notificar=False, ahora=1000.0)[0]
    assert r1["n_items"] == 2 and r1["alerta"] == ""

    # El sitio cambia su HTML: responde 200 y no parsea nada.
    r2 = vigia.correr([FUENTE], str(estado),
                      abrir=abridor({url: b"<html><body><div>rediseno</div></body></html>"}),
                      notificar=False, ahora=2000.0)[0]
    assert r2["n_items"] == 0
    assert r2["alerta"], "cero tras no-cero DEBE gritar, no callar"
    assert "0 items" in r2["alerta"]


def test_regla_de_oro_n_dias_sin_novedades_es_ERROR():
    """La otra forma de morir callado: la fuente responde y parsea bien, pero
    lleva N dias sin un solo item nuevo."""
    dia = 86400.0
    previo = {"n_items": 5, "ultimo_nuevo_ts": 0.0}

    # Dentro del umbral: silencio legitimo.
    assert vigia.regla_de_oro(previo, 5, 0, 3 * dia, dias=4) == ""
    # Cruzado el umbral: error.
    alerta = vigia.regla_de_oro(previo, 5, 0, 4 * dia, dias=4)
    assert alerta and "nuevo" in alerta

    # Con algo nuevo, no hay alerta por mas dias que hayan pasado.
    assert vigia.regla_de_oro(previo, 5, 1, 40 * dia, dias=4) == ""


def test_regla_de_oro_no_castiga_un_304():
    """304 es el servidor diciendo 'no cambio': no es una fuente rota."""
    fuente = dict(FUENTE)
    import urllib.error
    err = urllib.error.HTTPError(fuente["url"], 304, "Not Modified", {}, None)
    previo = {"n_items": 7, "etag": 'W/"abc"', "ultimo_nuevo_ts": 0.0}
    r = vigia.revisar_fuente(fuente, previo, set(), 90 * 86400.0,
                             abrir=abridor({fuente["url"]: err}))
    assert r["codigo"] == 304
    assert r["alerta"] == "", "un 304 no puede disparar la regla de oro"
    assert r["n_items"] == 7, "conserva el conteo previo"


def test_primera_corrida_no_dispara_la_regla_de_oro(tmp_path):
    """Sin estado previo, cero items es 'todavia no sabemos', no una rotura."""
    r = vigia.correr([FUENTE], str(tmp_path / "estado"),
                     abrir=abridor({FUENTE["url"]: b"<html></html>"}),
                     notificar=False, ahora=1000.0)[0]
    assert r["n_items"] == 0 and r["alerta"] == ""


# ------------------------------------------------------ REGLA DE AVALANCHA

def _titulos(n, sello=""):
    return ["Convocatoria numero %d de la temporada %s" % (i, sello)
            for i in range(n)]


def test_avalancha_un_cambio_de_urls_alerta_y_no_notifica_item_a_item(
        monkeypatch, tmp_path):
    """El otro lado de la regla de oro: si el sitio cambia la forma de sus
    URLs, TODO re-hashea como nuevo. Eso es una alerta, no 299 avisos."""
    enviados = []
    monkeypatch.setattr(vigia, "ntfy_publish",
                        lambda t, m, title="", priority="default", errors=None:
                        enviados.append((t, m, title, priority)) or True)
    monkeypatch.setenv("VIGIA_NTFY_TOPIC", "general")
    monkeypatch.delenv("VIGIA_NTFY_TOPIC_ENFERMERIA", raising=False)

    estado = tmp_path / "estado"
    url = FUENTE["url"]
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: _pagina(_titulos(20), "/aviso/")}),
                 notificar=False, ahora=1000.0)

    # Mismos titulos, permalinks nuevos: el diff ve 20 items "nuevos".
    enviados.clear()
    r = vigia.correr([FUENTE], str(estado),
                     abrir=abridor({url: _pagina(_titulos(20), "/v2/aviso/")}),
                     notificar=True, ahora=2000.0)[0]
    assert r["suprimido"] == 20
    assert "de golpe" in r["alerta"]
    assert any(p == "high" for _, _, _, p in enviados), "la avalancha alerta"
    cuerpos = [m for _, m, titulo, _ in enviados if "ROTO" not in titulo]
    assert not any("Convocatoria numero" in c for c in cuerpos), (
        "los items de la avalancha no se notifican uno a uno")

    # Tercera corrida, misma pagina: los hashes quedaron registrados y todo
    # vuelve a la calma -- la avalancha grita UNA vez.
    enviados.clear()
    r3 = vigia.correr([FUENTE], str(estado),
                      abrir=abridor({url: _pagina(_titulos(20), "/v2/aviso/")}),
                      notificar=True, ahora=3000.0)[0]
    assert r3["nuevos"] == [] and r3["alerta"] == ""
    assert enviados == []


def test_avalancha_primera_corrida_no_es_avalancha(tmp_path):
    """Sin historia, todo-nuevo es lo esperado: la primera corrida de una
    fuente con 300 items no puede gritar."""
    r = vigia.correr([FUENTE], str(tmp_path / "estado"),
                     abrir=abridor({FUENTE["url"]: _pagina(_titulos(300))}),
                     notificar=False, ahora=1000.0)[0]
    assert r["alerta"] == ""
    assert len(r["nuevos"]) == 300


def test_avalancha_fuente_chica_no_grita():
    """Una fuente de 5 items que rota entera es churn normal, no avalancha:
    el minimo absoluto existe para eso."""
    previo = {"n_items": 5, "ultimo_nuevo_ts": 900.0}
    assert vigia.regla_de_avalancha(previo, 5, 5) == ""


def test_avalancha_es_configurable_por_fuente(tmp_path):
    """avalancha_minimo=0 en fuentes.json desactiva la regla para esa fuente;
    la aesthetica del umbral no esta cableada en el codigo."""
    fuente = dict(FUENTE, avalancha_minimo=0)
    estado = tmp_path / "estado"
    url = fuente["url"]
    vigia.correr([fuente], str(estado),
                 abrir=abridor({url: _pagina(_titulos(20), "/aviso/")}),
                 notificar=False, ahora=1000.0)
    r = vigia.correr([fuente], str(estado),
                     abrir=abridor({url: _pagina(_titulos(20), "/v2/")}),
                     notificar=False, ahora=2000.0)[0]
    assert r["alerta"] == "" and "suprimido" not in r
    assert len(r["nuevos"]) == 20


def test_avalancha_bajo_umbral_notifica_normal(tmp_path):
    """4 items nuevos sobre 20 es un dia bueno, no una rotura."""
    estado = tmp_path / "estado"
    url = FUENTE["url"]
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: _pagina(_titulos(20), "/aviso/")}),
                 notificar=False, ahora=1000.0)
    pagina = _pagina(_titulos(20), "/aviso/") + _pagina(_titulos(4, "extra"),
                                                        "/aviso/x")
    r = vigia.correr([FUENTE], str(estado), abrir=abridor({url: pagina}),
                     notificar=False, ahora=2000.0)[0]
    assert len(r["nuevos"]) == 4
    assert r["alerta"] == "" and "suprimido" not in r


def test_avalancha_no_pisa_la_regla_de_oro():
    """Cero tras no-cero sigue siendo la alerta de oro, nunca una avalancha."""
    previo = {"n_items": 20, "ultimo_nuevo_ts": 900.0}
    assert vigia.regla_de_avalancha(previo, 0, 0) == ""
    assert "0 items" in vigia.regla_de_oro(previo, 0, 0, 2000.0)


# --------------------------------------------------------- conditional GET

def test_cabeceras_condicionales_se_envian():
    previo = {"etag": 'W/"v3"', "last_modified": "Mon, 28 Jul 2026 10:00:00 GMT"}
    h = vigia.cabeceras_condicionales(previo)
    assert h["If-None-Match"] == 'W/"v3"'
    assert h["If-Modified-Since"] == "Mon, 28 Jul 2026 10:00:00 GMT"
    assert h["User-Agent"]


def test_sin_estado_previo_no_hay_cabeceras_condicionales():
    h = vigia.cabeceras_condicionales({})
    assert "If-None-Match" not in h and "If-Modified-Since" not in h


def test_validadores_se_guardan_y_se_reenvian(tmp_path):
    """Ida y vuelta real: la respuesta trae ETag/Last-Modified, quedan en el
    estado, y la corrida siguiente los manda de vuelta."""
    estado = tmp_path / "estado"
    url = FUENTE["url"]
    headers = {"ETag": 'W/"v1"',
               "Last-Modified": "Mon, 28 Jul 2026 10:00:00 GMT"}
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: (_pagina(["Residencia de otono en Chillan"]),
                                      headers)}),
                 notificar=False, ahora=1000.0)

    guardado = json.loads((estado / vigia.ULTIMO).read_text(encoding="utf-8"))
    assert guardado["demo"]["etag"] == 'W/"v1"'
    assert guardado["demo"]["last_modified"] == "Mon, 28 Jul 2026 10:00:00 GMT"

    peticiones = []
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: (b"<html></html>", {})}, peticiones),
                 notificar=False, ahora=2000.0)
    enviadas = peticiones[0].headers
    # urllib normaliza los nombres de cabecera a Capitalizado.
    assert enviadas.get("If-none-match") == 'W/"v1"'
    assert enviadas.get("If-modified-since") == "Mon, 28 Jul 2026 10:00:00 GMT"


# ----------------------------------------------------------------- estado

def test_el_estado_vive_bajo_estado_y_esta_gitignorado(tmp_path):
    estado = tmp_path / "estado"
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({FUENTE["url"]: _pagina(["Beca de residencia en Punta Arenas"])}),
                 notificar=False, ahora=1000.0)
    assert (estado / vigia.VISTOS).exists()
    assert (estado / vigia.ULTIMO).exists()

    gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    assert "cultura/mak_vigia/estado/" in gitignore, (
        "el estado del vigia es local de la caja y no entra al repo")
    assert vigia.ESTADO_DIR.endswith(("estado", "estado/"))


# ------------------------------------------------- retencion del estado

def _pagina_enlaces(pares):
    filas = "".join('<li><a href="%s">%s</a></li>' % (href, t)
                    for t, href in pares)
    return ("<html><body><ul>%s</ul></body></html>" % filas).encode("utf-8")


DIA = 86400.0


def test_compactar_mueve_lo_viejo_a_archive_y_nunca_borra(monkeypatch, tmp_path):
    """La politica de retencion que el repo ya decidio (retencion.py,
    2026-07-17): conservar lo que el diff necesita, MOVER el resto a archive/,
    jamas borrar. Un hash que sigue en la pagina NUNCA se archiva, porque
    resurgiria como 'nuevo'."""
    firmas = []
    monkeypatch.setattr(vigia, "registrar_mutacion",
                        lambda accion, detalle="", origen=None, ruta=None:
                        firmas.append((accion, detalle)) or True)
    estado = tmp_path / "estado"
    url = FUENTE["url"]
    viejas = [("Antigua residencia en La Serena todavia listada", "/aviso/a"),
              ("Antigua beca de teatro ya cerrada", "/aviso/b"),
              ("Antiguo concurso de danza ya cerrado", "/aviso/c")]
    vigia.correr([FUENTE], str(estado), abrir=abridor({url: _pagina_enlaces(viejas)}),
                 notificar=False, ahora=1000.0)
    originales = (estado / vigia.VISTOS).read_text(encoding="utf-8")
    assert len(originales.strip().splitlines()) == 3

    # 200 dias despues: 'a' sigue listada, 'b' y 'c' ya no, aparece 'd'.
    despues = 1000.0 + 200 * DIA
    pagina2 = _pagina_enlaces([viejas[0],
                               ("Nueva convocatoria de artes mediales", "/aviso/d")])
    vigia.correr([FUENTE], str(estado), abrir=abridor({url: pagina2}),
                 notificar=False, ahora=despues, max_vistos=3)

    quedan = [json.loads(line) for line in
              (estado / vigia.VISTOS).read_text(encoding="utf-8").splitlines()]
    titulos_quedan = {r["titulo"] for r in quedan}
    assert "Antigua residencia en La Serena todavia listada" in titulos_quedan, (
        "un hash aun visible en la pagina no se archiva")
    assert "Nueva convocatoria de artes mediales" in titulos_quedan
    assert "Antigua beca de teatro ya cerrada" not in titulos_quedan

    archivos = list((estado / "archive").glob("vistos_*.jsonl"))
    assert len(archivos) == 1, "lo archivado se mueve, no se borra"
    archivadas = [json.loads(line) for line in
                  archivos[0].read_text(encoding="utf-8").splitlines()]
    assert {r["titulo"] for r in archivadas} == {
        "Antigua beca de teatro ya cerrada",
        "Antiguo concurso de danza ya cerrado"}
    # Nada se pierde: la union de ambos archivos es el contenido original + d.
    assert len(quedan) + len(archivadas) == 4

    # Y el movimiento quedo FIRMADO (el incidente de los 217 informes sin
    # autor, 2026-07-30: mover estado sin firma es lo prohibido).
    assert firmas and firmas[0][0] == "vigia_compactar"
    assert "2 registros" in firmas[0][1]

    # El hash conservado sigue haciendo su trabajo: la misma pagina no
    # re-notifica nada.
    r3 = vigia.correr([FUENTE], str(estado), abrir=abridor({url: pagina2}),
                      notificar=False, ahora=despues + 3600)[0]
    assert r3["nuevos"] == []


def test_compactar_bajo_el_tope_no_toca_nada(tmp_path):
    estado = tmp_path / "estado"
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({FUENTE["url"]: _pagina(["Convocatoria de artes escenicas 2026"])}),
                 notificar=False, ahora=1000.0)
    antes = (estado / vigia.VISTOS).read_text(encoding="utf-8")
    c = vigia.compactar_vistos(str(estado), ahora=1000.0 + 400 * DIA,
                               max_registros=vigia.MAX_VISTOS)
    assert c["archivados"] == 0
    assert (estado / vigia.VISTOS).read_text(encoding="utf-8") == antes
    assert not (estado / "archive").exists()


def test_compactar_lo_reciente_se_queda_aunque_deje_la_pagina(monkeypatch, tmp_path):
    """El corte es doble: viejo Y fuera de la pagina. Un aviso que salio ayer
    de la pagina sigue en la memoria hasta cumplir los dias."""
    monkeypatch.setattr(vigia, "registrar_mutacion", lambda *a, **k: True)
    estado = tmp_path / "estado"
    url = FUENTE["url"]
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: _pagina_enlaces(
                     [("Convocatoria breve de video arte", "/aviso/x")])}),
                 notificar=False, ahora=1000.0)
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: _pagina_enlaces(
                     [("Otra convocatoria de fotografia analoga", "/aviso/y")])}),
                 notificar=False, ahora=1000.0 + 2 * DIA)
    c = vigia.compactar_vistos(str(estado), ahora=1000.0 + 3 * DIA,
                               max_registros=0)
    assert c["archivados"] == 0, "2 dias no son %d" % vigia.DIAS_COMPACTAR


def test_compactar_conserva_una_linea_malformada(monkeypatch, tmp_path):
    """Una linea que no parsea es un dato de alguien que no podemos fechar:
    se queda donde esta."""
    monkeypatch.setattr(vigia, "registrar_mutacion", lambda *a, **k: True)
    estado = tmp_path / "estado"
    estado.mkdir()
    (estado / vigia.VISTOS).write_text(
        "esto no es json\n"
        + json.dumps({"h": "abc", "fuente": "demo",
                      "titulo": "Vieja convocatoria sin pagina",
                      "url": "", "ts": 0}) + "\n",
        encoding="utf-8")
    c = vigia.compactar_vistos(str(estado), ahora=400 * DIA, max_registros=0)
    assert c["archivados"] == 1
    assert "esto no es json" in (estado / vigia.VISTOS).read_text(encoding="utf-8")


def test_compactar_desde_la_cli(tmp_path, capsys):
    """--compactar es el verbo de mantenimiento: compacta y sale, sin tocar
    la red ni las fuentes."""
    estado = tmp_path / "estado"
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({FUENTE["url"]: _pagina(["Convocatoria reciente de muralismo"])}),
                 notificar=False)
    codigo = vigia.main(["--estado", str(estado), "--compactar"])
    assert codigo == 0
    assert "compactado: 0 de 1" in capsys.readouterr().out


def test_la_firma_es_la_de_mutaciones_de_plataforma():
    """No una segunda bitacora: la que ya contesta 'quien movio esto'."""
    assert vigia.registrar_mutacion is not None, "mutaciones no se pudo importar"
    import mutaciones
    assert vigia.registrar_mutacion is mutaciones.registrar


def test_una_fuente_caida_no_mata_la_corrida(tmp_path):
    """Un 403 en una fuente no puede llevarse las otras cinco por delante."""
    import urllib.error
    rota = dict(FUENTE, id="rota", url="https://caida.cl/x")
    sana = dict(FUENTE, id="sana", url="https://viva.cl/x")
    paginas = {
        rota["url"]: urllib.error.HTTPError(rota["url"], 403, "Forbidden", {}, None),
        sana["url"]: _pagina(["Convocatoria abierta de arte sonoro"]),
    }
    res = vigia.correr([rota, sana], str(tmp_path / "estado"),
                       abrir=abridor(paginas), notificar=False, ahora=1000.0)
    por_id = {r["id"]: r for r in res}
    assert "403" in por_id["rota"]["error"]
    assert len(por_id["sana"]["nuevos"]) == 1


# ------------------------------------------------------------- extraccion

def test_decodifica_aunque_el_servidor_mienta_sobre_el_charset():
    """Caso real medido en empleospublicos.cl y fondos.gob.cl: declaran utf-8
    y mandan cp1252. Decodificar 'como dijeron' destruiria las tildes."""
    crudo = "Técnico en Enfermería".encode("cp1252")
    texto = vigia.decodificar(crudo, {"Content-Type": "application/json; charset=utf-8"})
    assert texto == "Técnico en Enfermería"
    assert "�" not in texto


def test_utf8_valido_se_respeta():
    crudo = "Composición Musical".encode("utf-8")
    assert vigia.decodificar(crudo, {"Content-Type": "text/html"}) == "Composición Musical"


def test_un_ancla_sin_cerrar_no_se_come_el_resto_de_la_pagina():
    """El defecto que hacia parsear 0 convocatorias en resartis.org: sin cierre
    inferido, un <a> abierto se tragaba todos los enlaces siguientes."""
    html = ('<div><a href="/roto">enlace sin cerrar de la cabecera'
            '<h2><a href="/aviso/1">Residencia internacional en Bruselas</a></h2>'
            '<h2><a href="/aviso/2">Beca de movilidad para creadores</a></h2></div>')
    items = vigia.extraer_html(html, "https://ejemplo.cl/lista")
    titulos = [i["titulo"] for i in items]
    assert "Residencia internacional en Bruselas" in titulos
    assert "Beca de movilidad para creadores" in titulos


def test_filtro_por_url_y_por_palabra():
    html = ('<a href="/open-call/uno">Residencia de invierno en Oslo</a>'
            '<a href="/quienes-somos">Conoce a nuestro equipo</a>'
            '<a href="/open-call/dos">Beca de fotografia documental</a>')
    items = vigia.extraer_html(html, "https://ejemplo.org/")
    assert len(vigia.filtrar(items, None, ["/open-call/"])) == 2
    assert len(vigia.filtrar(items, ["residencia"], ["/open-call/"])) == 1
    assert len(vigia.filtrar(items, None, None)) == 3


def test_extraccion_json_de_un_listado_real():
    """Forma exacta del endpoint de empleospublicos."""
    fuente = {"id": "ep", "formato": "json",
              "json_titulo": ["Cargo", "Institución / Entidad"],
              "json_url": ["url"]}
    crudo = json.dumps([
        {"Cargo": "Técnico en Enfermería",
         "Institución / Entidad": "Hospital de San Carlos",
         "url": "https://www.empleospublicos.cl/pub/x.aspx?i=1"},
        {"Cargo": "Enfermero(a) de Urgencia",
         "Institución / Entidad": "Servicio de Salud Ñuble",
         "url": "https://www.empleospublicos.cl/pub/x.aspx?i=2"},
    ], ensure_ascii=False)
    items = vigia.extraer(crudo, fuente, "https://www.empleospublicos.cl/")
    assert len(items) == 2
    assert items[0]["titulo"] == "Técnico en Enfermería - Hospital de San Carlos"
    assert items[1]["url"].endswith("i=2")


RSS_FIJO = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
 <channel>
  <title>Convocatorias del centro cultural</title>
  <link>https://ejemplo.cl/</link>
  <item>
   <title><![CDATA[Residencia de creación en Valparaíso]]></title>
   <link>https://ejemplo.cl/convocatorias/residencia-valparaiso</link>
   <content:encoded><![CDATA[<p>bases y condiciones</p>]]></content:encoded>
  </item>
  <item>
   <title>Beca corta</title>
   <link>/convocatorias/beca-corta</link>
  </item>
  <item>
   <title><![CDATA[Residencia de creación en Valparaíso]]></title>
   <link>https://ejemplo.cl/convocatorias/residencia-valparaiso</link>
  </item>
 </channel>
</rss>"""

ATOM_FIJO = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>Fondos abiertos</title>
 <link rel="self" href="https://fondos.ejemplo.org/feed.xml"/>
 <entry>
  <title>Fondo de fomento a la música regional</title>
  <link rel="self" href="https://fondos.ejemplo.org/api/entrada/9"/>
  <link rel="alternate" href="https://fondos.ejemplo.org/fondo/musica"/>
 </entry>
 <entry>
  <title>Fondo del libro y la lectura</title>
  <link href="/fondo/libro"/>
 </entry>
</feed>"""


def test_extraccion_rss_con_cdata_tildes_y_url_relativa():
    """Un feed WordPress real: CDATA, namespaces, enlaces relativos y un item
    repetido. El titulo conserva sus tildes; la URL se resuelve absoluta."""
    items = vigia.extraer_feed(RSS_FIJO, "https://ejemplo.cl/feed/")
    assert len(items) == 2, "el item duplicado se pliega"
    assert items[0]["titulo"] == "Residencia de creación en Valparaíso"
    assert items[0]["url"] == "https://ejemplo.cl/convocatorias/residencia-valparaiso"
    assert items[1]["url"] == "https://ejemplo.cl/convocatorias/beca-corta"


def test_extraccion_rss_no_aplica_la_heuristica_de_navegacion():
    """En un feed cada <item> ES un item por contrato: un titulo corto
    ('Beca corta', 2 palabras) se queda. Botarlo seria el parser fabricando
    el cero silencioso que la regla de oro persigue."""
    items = vigia.extraer_feed(RSS_FIJO, "https://ejemplo.cl/feed/")
    assert any(i["titulo"] == "Beca corta" for i in items)


def test_extraccion_atom_prefiere_el_enlace_alternate():
    items = vigia.extraer_feed(ATOM_FIJO, "https://fondos.ejemplo.org/feed.xml")
    assert len(items) == 2
    assert items[0]["url"] == "https://fondos.ejemplo.org/fondo/musica", (
        "rel=self es la API del feed; rel=alternate es la página que lee la persona")
    assert items[1]["url"] == "https://fondos.ejemplo.org/fondo/libro"


def test_xml_roto_da_cero_sin_reventar_y_la_regla_de_oro_lo_ve(tmp_path):
    """Un feed que deja de ser XML parsea a cero; eso no tumba la corrida y
    el cero-tras-no-cero grita como con HTML."""
    assert vigia.extraer_feed("<rss><channel><item>", "https://x.cl/") == []
    fuente = dict(FUENTE, id="feed", formato="rss")
    estado = tmp_path / "estado"
    url = fuente["url"]
    vigia.correr([fuente], str(estado),
                 abrir=abridor({url: RSS_FIJO.encode("utf-8")}),
                 notificar=False, ahora=1000.0)
    r = vigia.correr([fuente], str(estado),
                     abrir=abridor({url: b"pagina de mantenimiento"}),
                     notificar=False, ahora=2000.0)[0]
    assert r["n_items"] == 0
    assert "0 items" in r["alerta"]


def test_el_diff_funciona_igual_sobre_un_feed(tmp_path):
    """El contrato completo de la fuente rss: primera corrida todo nuevo,
    segunda nada, y una entrada agregada al feed es exactamente un aviso."""
    fuente = dict(FUENTE, id="feed", formato="rss")
    estado = tmp_path / "estado"
    url = fuente["url"]
    crudo = RSS_FIJO.encode("utf-8")
    r1 = vigia.correr([fuente], str(estado), abrir=abridor({url: crudo}),
                      notificar=False, ahora=1000.0)[0]
    assert len(r1["nuevos"]) == 2
    r2 = vigia.correr([fuente], str(estado), abrir=abridor({url: crudo}),
                      notificar=False, ahora=2000.0)[0]
    assert r2["nuevos"] == []

    con_extra = RSS_FIJO.replace(
        " </channel>",
        " <item><title>Nueva convocatoria de danza contemporánea</title>"
        "<link>https://ejemplo.cl/convocatorias/danza</link></item>\n </channel>")
    r3 = vigia.correr([fuente], str(estado),
                      abrir=abridor({url: con_extra.encode("utf-8")}),
                      notificar=False, ahora=3000.0)[0]
    assert len(r3["nuevos"]) == 1
    assert r3["nuevos"][0]["titulo"] == "Nueva convocatoria de danza contemporánea"


def test_el_filtro_de_palabras_tambien_rige_para_feeds():
    fuente = {"id": "feed", "formato": "rss"}
    items = vigia.extraer(RSS_FIJO, fuente, "https://ejemplo.cl/feed/")
    assert len(vigia.filtrar(items, ["residencia"], None)) == 1


def test_no_hay_modelo_en_el_vigia():
    """v1 es un diff. Si algun dia aparece un LLM aca, que sea una decision
    explicita y no un deslizamiento: este test es el guardarrail."""
    fuente = (VIGIA_DIR / "vigia.py").read_text(encoding="utf-8").lower()
    for palabra in ("import torch", "openai", "ollama", "anthropic",
                    "llm(", "gpt-", "transformers"):
        assert palabra not in fuente, "el vigia v1 no usa modelos: %s" % palabra


# ------------------------------------------------------------- fuentes.json

def test_fuentes_json_es_valido_y_completo():
    fuentes = vigia.cargar_fuentes(str(VIGIA_DIR / "fuentes.json"))
    assert fuentes, "la lista de vigilancia no puede estar vacia"
    ids = [f["id"] for f in fuentes]
    assert len(ids) == len(set(ids)), "ids duplicados: el hash se mezclaria"
    for f in fuentes:
        assert f["url"].startswith("https://"), f["id"]
        assert f.get("nombre") and f.get("tipo"), f["id"]
        assert f.get("formato", "html") in ("html", "json", "rss", "atom"), f["id"]
        assert f["id"].isascii(), "los ids son claves de maquina"


def test_hay_una_fuente_de_enfermeria_para_el_topico_aparte():
    fuentes = vigia.cargar_fuentes(str(VIGIA_DIR / "fuentes.json"))
    assert any(f["tipo"] == "enfermeria" for f in fuentes)
    assert any(f["tipo"] != "enfermeria" for f in fuentes)


# ------------------------------------------------------------- notificacion

def test_notificacion_por_lote_y_por_topico_separado(monkeypatch, tmp_path):
    """Dos telefonos distintos, y como maximo un mensaje por lote y topico:
    notificar item por item convertiria el vigia en spam en un dia."""
    enviados = []
    monkeypatch.setattr(vigia, "ntfy_publish",
                        lambda t, m, title="", priority="default", errors=None:
                        enviados.append((t, m, title, priority)) or True)
    monkeypatch.setenv("VIGIA_NTFY_TOPIC", "general")
    monkeypatch.setenv("VIGIA_NTFY_TOPIC_ENFERMERIA", "salud")

    enf = dict(FUENTE, id="enf", tipo="enfermeria", url="https://salud.cl/x")
    res = dict(FUENTE, id="res", tipo="residencias", url="https://arte.cl/x")
    paginas = {enf["url"]: _pagina(["Enfermera de urgencia en Rancagua",
                                    "Tecnico en enfermeria en Chillan"]),
               res["url"]: _pagina(["Residencia de arte sonoro en Berlin"])}
    vigia.correr([enf, res], str(tmp_path / "estado"),
                 abrir=abridor(paginas), notificar=True, ahora=1000.0)

    por_topico = {t: m for t, m, _, _ in enviados}
    assert set(por_topico) == {"salud", "general"}
    assert len(enviados) == 2, "un mensaje por topico, no uno por aviso"
    assert "Enfermera de urgencia en Rancagua" in por_topico["salud"]
    assert "Residencia de arte sonoro" in por_topico["general"]
    assert "Enfermera" not in por_topico["general"], "los topicos no se cruzan"


def test_la_alerta_de_la_regla_de_oro_va_en_prioridad_alta(monkeypatch, tmp_path):
    enviados = []
    monkeypatch.setattr(vigia, "ntfy_publish",
                        lambda t, m, title="", priority="default", errors=None:
                        enviados.append((t, m, title, priority)) or True)
    monkeypatch.setenv("VIGIA_NTFY_TOPIC", "general")
    monkeypatch.delenv("VIGIA_NTFY_TOPIC_ENFERMERIA", raising=False)

    estado = tmp_path / "estado"
    url = FUENTE["url"]
    vigia.correr([FUENTE], str(estado),
                 abrir=abridor({url: _pagina(["Residencia de invierno en Lima"])}),
                 notificar=True, ahora=1000.0)
    enviados.clear()
    vigia.correr([FUENTE], str(estado), abrir=abridor({url: b"<html></html>"}),
                 notificar=True, ahora=2000.0)

    assert enviados, "la fuente rota tiene que notificar"
    assert any(p == "high" for _, _, _, p in enviados)
    assert any("ROTO" in titulo for _, _, titulo, _ in enviados)


def test_sin_topico_configurado_no_revienta(monkeypatch, tmp_path):
    monkeypatch.delenv("VIGIA_NTFY_TOPIC", raising=False)
    monkeypatch.delenv("VIGIA_NTFY_TOPIC_ENFERMERIA", raising=False)
    vigia.correr([FUENTE], str(tmp_path / "estado"),
                 abrir=abridor({FUENTE["url"]: _pagina(["Beca de residencia en Quito"])}),
                 notificar=True, ahora=1000.0)


def test_reutiliza_ntfy_publish_de_research_lib():
    """No una segunda implementacion: la del organismo."""
    assert vigia.ntfy_publish is not None, "research_lib no se pudo importar"
    import research_lib
    assert vigia.ntfy_publish is research_lib.ntfy_publish


# ------------------------------------------------------------------ guardia

def test_la_guardia_usa_su_propio_lock():
    """Nunca el lock compartido de curatoria/micelio: el vigia no toca la GPU
    y quedaria esperando horas detras de una percepcion."""
    sh = (VIGIA_DIR / "vigia_guardia.sh").read_text(encoding="utf-8")
    # Solo lo ejecutable: los comentarios SI nombran el lock compartido, porque
    # explican por que este no lo usa.
    codigo = [ln for ln in sh.splitlines() if not ln.lstrip().startswith("#")]
    assert any("flock -n 9" in ln for ln in codigo)
    assert any(".vigia.lock" in ln and "exec 9>" in ln for ln in codigo)
    assert not any("guardia.lock" in ln for ln in codigo)


def test_la_guardia_esta_en_el_crontab():
    cron = (RAIZ / "cultura" / "mak_plataforma" / "crontab.mak").read_text(
        encoding="utf-8")
    lineas = [ln for ln in cron.splitlines() if "MAK-VIGIA" in ln]
    assert len(lineas) == 1, "una sola linea de cron para el vigia"
    assert "vigia_guardia.sh" in lineas[0]
    assert lineas[0].startswith("45 * * * *"), "cada hora, no cada minuto"


@pytest.mark.parametrize("nombre", ["vigia.py", "fuentes.json",
                                    "vigia_guardia.sh"])
def test_el_departamento_esta_completo(nombre):
    assert (VIGIA_DIR / nombre).exists()


def test_solo_stdlib():
    """Estilo mak_lenguaje: sin dependencias externas. Lo unico de fuera es
    research_lib, que tambien es stdlib y vive en el mismo repo."""
    fuente = (VIGIA_DIR / "vigia.py").read_text(encoding="utf-8")
    externas = {"requests", "bs4", "beautifulsoup", "lxml", "feedparser",
                "httpx", "aiohttp", "selenium", "playwright", "numpy"}
    for linea in fuente.splitlines():
        ls = linea.strip()
        if ls.startswith(("import ", "from ")):
            modulo = ls.split()[1].split(".")[0].lower()
            assert modulo not in externas, ls


def test_el_tiempo_no_se_congela(tmp_path):
    """time.time() por defecto: el parametro 'ahora' es solo para los tests."""
    antes = time.time()
    res = vigia.correr([FUENTE], str(tmp_path / "estado"),
                       abrir=abridor({FUENTE["url"]: _pagina(["Convocatoria de video experimental"])}),
                       notificar=False)
    assert res[0]["nuevos"][0]["ts"] >= int(antes)
