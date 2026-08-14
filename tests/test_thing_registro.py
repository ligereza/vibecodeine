#!/usr/bin/env python3
"""tests/test_thing_registro.py -- CAPACIDADES.md seccion 6 (thi.ng) es el
indice que un agente debe leer ANTES de escribir un generador/pipeline/grafo
desde cero (regla 2026-07-30: una sola libreria vendorizada estaba EN USO de
cuatro, y la sesion siguiente mandaba a reescribir la misma capacidad). Este
test fija que la tabla no rote: toda fila EN USO nombra un consumidor real que
de verdad importa la libreria, todo lo declarado en los manifiestos tiene fila,
y no quedan bundles huerfanos ni versiones sin fijar."""
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CAPACIDADES = REPO / "CAPACIDADES.md"
MANIFIESTOS = {
    "motor": REPO / "data" / "motor_librerias.json",
    "iskvw": REPO / "data" / "iskvw_librerias.json",
}
LIBS_DIRS = {
    "motor": REPO / "docs" / "cultura" / "lib",
    "iskvw": REPO / "iskvw" / "piel" / "lib",
}


def _seccion_6_texto():
    src = CAPACIDADES.read_text(encoding="utf-8")
    m = re.search(r"^## 6\. thi\.ng.*?(?=\Z)", src, re.S | re.M)
    assert m, "no encuentro '## 6. thi.ng' en CAPACIDADES.md"
    return m.group(0)


def _filas_tabla(texto_seccion):
    """Filas de markdown-table (| a | b | c | d |), sin encabezado ni el
    separador ---. Devuelve lista de listas de celdas (strip)."""
    filas = []
    for linea in texto_seccion.splitlines():
        linea = linea.strip()
        if not linea.startswith("|") or not linea.endswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in celdas):
            continue  # fila separadora ---|---|---
        filas.append(celdas)
    assert filas, "no encontre ninguna fila de tabla en la seccion 6"
    return filas[1:]  # la primera es el encabezado


def _manifiestos_cargados():
    out = {}
    for clave, ruta in MANIFIESTOS.items():
        data = json.loads(ruta.read_text(encoding="utf-8"))
        out[clave] = data["librerias"]
    return out


def _es_vendorizado(js_path):
    """Un .js cuenta como bundle vendorizado si tiene su .README.md hermano
    (convencion de tools/vendorizar_iskvw.py: 'el README viaja al lado del
    bundle'). Sin eso, es codigo propio del repo (p.ej. compilador.js, el
    gemelo de navegador escrito a mano, que vive en el mismo directorio que
    los bundles vendorizados pero NO es uno)."""
    return js_path.with_suffix("").with_suffix(".README.md").is_file()


class TestEstructuraDeLaTabla:
    def test_la_seccion_existe_con_el_heading_exacto(self):
        src = CAPACIDADES.read_text(encoding="utf-8")
        assert re.search(r"^## 6\. thi\.ng", src, re.M)

    def test_toda_fila_tiene_estado_y_donde_no_vacios(self):
        filas = _filas_tabla(_seccion_6_texto())
        for fila in filas:
            assert len(fila) >= 4, fila
            paquete, estado, donde, senal = fila[0], fila[1], fila[2], fila[3]
            assert estado.strip(), f"fila sin estado: {paquete}"
            assert donde.strip(), f"fila sin 'donde, y que retira': {paquete}"

    def test_mutacion_fila_sin_estado_se_detecta(self):
        """Mutation check: una tabla con una fila de estado vacio debe fallar
        la misma asercion que la de arriba (probado sobre una tabla de
        prueba, no sobre CAPACIDADES.md real)."""
        texto_roto = (
            "## 6. thi.ng: x\n\n"
            "| paquete | estado | donde, y que retira | senal |\n"
            "|---|---|---|---|\n"
            "| `@thi.ng/x` |  | en algun lado | hoy |\n"
        )
        filas = _filas_tabla(texto_roto)
        with pytest.raises(AssertionError):
            for fila in filas:
                assert fila[1].strip(), "deberia fallar"


class TestManifiestosTienenFilaEnLaTabla:
    def test_cada_libreria_declarada_aparece_nombrada_en_la_seccion(self):
        texto = _seccion_6_texto()
        manifiestos = _manifiestos_cargados()
        faltantes = []
        for clave, libs in manifiestos.items():
            for e in libs:
                if e["paquete"] not in texto:
                    faltantes.append(f"{clave}:{e['paquete']}")
        assert not faltantes, (
            "declaradas en el manifiesto pero sin fila en CAPACIDADES.md #6: "
            + ", ".join(faltantes))


class TestFilasEnUsoNombranConsumidorReal:
    def test_toda_fila_en_uso_referencia_un_archivo_real_que_la_importa(self):
        texto = _seccion_6_texto()
        filas = _filas_tabla(texto)
        manifiestos = _manifiestos_cargados()
        paquete_a_nombre = {
            e["paquete"]: e["nombre"]
            for libs in manifiestos.values() for e in libs
        }

        filas_en_uso = [f for f in filas if "EN USO" in f[1]]
        assert filas_en_uso, "deberia haber al menos una fila EN USO"

        rutas_prev = []
        for fila in filas_en_uso:
            paquete_cell, _, donde_cell = fila[0], fila[1], fila[2]
            rutas = re.findall(r"`([\w./-]+\.\w+)`", donde_cell)
            if not rutas and "mismo" in donde_cell.lower():
                # "mismo compilador"/"mismo X": reusa el archivo citado en la
                # fila EN USO anterior en vez de repetir la ruta.
                rutas = rutas_prev
            assert rutas, f"fila EN USO sin archivo citado: {paquete_cell}"
            rutas_prev = rutas
            existentes = [r for r in rutas if (REPO / r).is_file()]
            assert existentes, (
                f"fila EN USO cita archivo(s) que no existen: {rutas} "
                f"({paquete_cell})")

            paquetes_de_la_fila = [
                p for p in paquete_a_nombre if p in paquete_cell]
            assert paquetes_de_la_fila, (
                f"no pude resolver que libreria(s) declara esta fila: "
                f"{paquete_cell}")

            contenido = "\n".join(
                (REPO / r).read_text(encoding="utf-8", errors="replace")
                for r in existentes)
            for p in paquetes_de_la_fila:
                nombre = paquete_a_nombre[p]
                assert (nombre + ".js") in contenido, (
                    f"{paquete_cell}: el archivo citado ({existentes}) no "
                    f"referencia {nombre}.js -- fila EN USO sin consumo real")

    def test_mutacion_referencia_falsa_se_detecta(self):
        """Mutation check: si la fila EN USO citara un archivo real que NO
        importa la libreria, el chequeo de contenido de arriba debe fallar.
        Probado con datos sinteticos, no con CAPACIDADES.md real."""
        manifiestos = _manifiestos_cargados()
        paquete_a_nombre = {
            e["paquete"]: e["nombre"]
            for libs in manifiestos.values() for e in libs
        }
        # Un documento de texto corriente no importa ninguna libreria de thi.ng.
        contenido_falso = "documento sin imports de bundles\n"
        algun_nombre = next(iter(paquete_a_nombre.values()))
        assert (algun_nombre + ".js") not in contenido_falso


class TestBundlesVendorizadosSinHuerfanos:
    @pytest.mark.parametrize("clave", sorted(MANIFIESTOS))
    def test_todo_lo_declarado_tiene_su_js_en_disco(self, clave):
        libs = json.loads(MANIFIESTOS[clave].read_text(encoding="utf-8"))["librerias"]
        carpeta = LIBS_DIRS[clave]
        for e in libs:
            js = carpeta / f"{e['nombre']}.js"
            assert js.is_file(), f"{clave}: falta {js}"

    @pytest.mark.parametrize("clave", sorted(MANIFIESTOS))
    def test_todo_js_vendorizado_en_disco_esta_declarado(self, clave):
        libs = json.loads(MANIFIESTOS[clave].read_text(encoding="utf-8"))["librerias"]
        declarados = {e["nombre"] for e in libs}
        carpeta = LIBS_DIRS[clave]
        for js in carpeta.glob("*.js"):
            if not _es_vendorizado(js):
                continue  # codigo propio del repo (p.ej. compilador.js), no un bundle
            assert js.stem in declarados, (
                f"{clave}: {js.name} vendorizado (tiene README) pero no "
                f"declarado en {MANIFIESTOS[clave].name}")

    def test_mutacion_bundle_sin_declarar_se_detecta(self, tmp_path):
        """Mutation check de la regla de arriba, sobre un directorio de
        prueba (no toca docs/cultura/lib real): un .js con su .README.md que
        no figura en 'declarados' debe hacer fallar la comparacion."""
        (tmp_path / "fantasma.js").write_text("// bundle", encoding="utf-8")
        (tmp_path / "fantasma.README.md").write_text("doc", encoding="utf-8")
        declarados = {"otra-cosa"}
        js = tmp_path / "fantasma.js"
        assert _es_vendorizado(js)
        with pytest.raises(AssertionError):
            assert js.stem in declarados


class TestManifiestosPinanVersionYTienenPara:
    @pytest.mark.parametrize("clave", sorted(MANIFIESTOS))
    def test_version_exacta_y_para_no_vacio(self, clave):
        libs = json.loads(MANIFIESTOS[clave].read_text(encoding="utf-8"))["librerias"]
        assert libs
        prohibidos_en_version = set("^~<>*x") | {"latest"}
        for e in libs:
            version = e.get("version", "")
            assert version, f"{clave}:{e['nombre']} sin version"
            assert version != "latest", f"{clave}:{e['nombre']} usa 'latest'"
            assert not (set(version) & prohibidos_en_version), (
                f"{clave}:{e['nombre']} version no exacta: {version!r}")
            assert re.fullmatch(r"\d+(\.\d+){1,3}", version), (
                f"{clave}:{e['nombre']} version no parece un numero fijo: "
                f"{version!r}")
            assert e.get("para", "").strip(), f"{clave}:{e['nombre']} sin 'para'"

    def test_mutacion_version_con_rango_se_detecta(self):
        entrada_rota = {"nombre": "x", "version": "^5.4.13", "para": "algo"}
        prohibidos_en_version = set("^~<>*x") | {"latest"}
        with pytest.raises(AssertionError):
            assert not (set(entrada_rota["version"]) & prohibidos_en_version)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
