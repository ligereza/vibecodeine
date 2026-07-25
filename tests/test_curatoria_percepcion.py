#!/usr/bin/env python3
"""test_curatoria_percepcion.py -- tests para cultura/mak_curatoria/
(pytest). Sin ollama/tesseract/ffmpeg reales: todo mockeado."""
import json
import sys
from pathlib import Path
from unittest import mock

test_dir = Path(__file__).parent
proyecto_dir = test_dir.parent
sys.path.insert(0, str(proyecto_dir / "cultura" / "mak_curatoria"))

import percepcion  # noqa: E402
import reporter  # noqa: E402


# ---------------------------------------------------------------------------
# recorrer() / clasificar_ext() -- orden estable + filtro de extensiones
# ---------------------------------------------------------------------------

class TestRecorrer:
    def test_clasifica_por_extension(self, tmp_path):
        (tmp_path / "flyer.jpg").write_bytes(b"x")
        (tmp_path / "reel.mp4").write_bytes(b"x")
        (tmp_path / "brief.pdf").write_bytes(b"x")
        (tmp_path / "notas.txt").write_bytes(b"x")

        resultado = percepcion.recorrer(tmp_path, "rd")
        tipos = {r["ruta_rel"]: r["tipo"] for r in resultado}

        assert tipos["flyer.jpg"] == "imagen"
        assert tipos["reel.mp4"] == "video"
        assert tipos["brief.pdf"] == "pdf"
        assert tipos["notas.txt"] == "otro"

    def test_orden_estable_por_ruta_rel(self, tmp_path):
        (tmp_path / "z.jpg").write_bytes(b"x")
        (tmp_path / "a.jpg").write_bytes(b"x")
        (tmp_path / "m.jpg").write_bytes(b"x")

        resultado = percepcion.recorrer(tmp_path, "rd")
        rutas = [r["ruta_rel"] for r in resultado]
        assert rutas == sorted(rutas)

    def test_raiz_inexistente_devuelve_vacio(self, tmp_path):
        assert percepcion.recorrer(tmp_path / "no_existe", "rd") == []

    def test_fuente_se_propaga(self, tmp_path):
        (tmp_path / "a.jpg").write_bytes(b"x")
        resultado = percepcion.recorrer(tmp_path, "ig")
        assert resultado[0]["fuente"] == "ig"

    def test_construir_trabajo_solo_fuente(self, tmp_path):
        raiz_rd = tmp_path / "rd"
        raiz_ig = tmp_path / "ig"
        raiz_rd.mkdir()
        raiz_ig.mkdir()
        (raiz_rd / "a.jpg").write_bytes(b"x")
        (raiz_ig / "b.jpg").write_bytes(b"x")

        trabajo = percepcion.construir_trabajo(str(raiz_rd), str(raiz_ig), solo_fuente="rd")
        assert len(trabajo) == 1
        assert trabajo[0]["fuente"] == "rd"

        trabajo_todo = percepcion.construir_trabajo(str(raiz_rd), str(raiz_ig))
        assert len(trabajo_todo) == 2


# ---------------------------------------------------------------------------
# checkpoint: procesados.txt
# ---------------------------------------------------------------------------

class TestCheckpoint:
    def test_correr_no_reprocesa_archivos_ya_hechos(self, tmp_path):
        raiz = tmp_path / "rd"
        raiz.mkdir()
        (raiz / "a.jpg").write_bytes(b"a")
        (raiz / "b.jpg").write_bytes(b"b")
        dir_out = tmp_path / "out"

        ficha_ok = {
            "id": "x", "fuente": "rd", "ruta_rel": "a.jpg", "tipo": "imagen",
            "bytes": 1, "mtime": "2026-01-01", "ocr_texto": "", "vision": {},
            "datos_evento": {}, "calidad_senal": "baja", "error": None, "ts": "t",
        }
        with mock.patch("percepcion.construir_ficha", return_value=ficha_ok) as cf_mock:
            rc = percepcion.correr(str(raiz), None, str(dir_out))
            assert rc == 0
            assert cf_mock.call_count == 2

            rc2 = percepcion.correr(str(raiz), None, str(dir_out))
            assert rc2 == 0
            # nada nuevo que procesar
            assert cf_mock.call_count == 2

    def test_procesados_txt_tiene_clave_fuente_ruta(self, tmp_path):
        raiz = tmp_path / "rd"
        raiz.mkdir()
        (raiz / "a.jpg").write_bytes(b"a")
        dir_out = tmp_path / "out"

        ficha_ok = {
            "id": "x", "fuente": "rd", "ruta_rel": "a.jpg", "tipo": "imagen",
            "bytes": 1, "mtime": "2026-01-01", "ocr_texto": "", "vision": {},
            "datos_evento": {}, "calidad_senal": "baja", "error": None, "ts": "t",
        }
        with mock.patch("percepcion.construir_ficha", return_value=ficha_ok):
            percepcion.correr(str(raiz), None, str(dir_out))

        procesados = percepcion.cargar_procesados(dir_out)
        assert "rd:a.jpg" in procesados


# ---------------------------------------------------------------------------
# construir_ficha() -- schema completo, incluso ante fallos
# ---------------------------------------------------------------------------

class TestConstruirFicha:
    def _entry(self, tipo="imagen", ruta_rel="flyer.jpg"):
        return {
            "fuente": "rd", "ruta_rel": ruta_rel, "ruta_abs": ruta_rel,
            "tipo": tipo, "bytes": 123, "mtime": 0,
        }

    def test_schema_completo_ante_fallo_total(self, tmp_path):
        with mock.patch("percepcion.ocr_tesseract", return_value=""), \
             mock.patch("percepcion.vision_imagen",
                        return_value={"error": "ollama_no_disponible: boom"}):
            ficha = percepcion.construir_ficha(self._entry(), tmp_path, 5)

        assert set(ficha.keys()) == {
            "id", "fuente", "ruta_rel", "tipo", "categoria", "bytes", "mtime",
            "ocr_texto", "vision", "datos_evento", "calidad_senal", "error",
            "seg_proceso", "ts",
        }
        assert ficha["fuente"] == "rd"
        assert ficha["ruta_rel"] == "flyer.jpg"
        assert ficha["ocr_texto"] == ""
        assert ficha["categoria"] == ""
        assert set(ficha["vision"].keys()) == {"descripcion", "estilo", "colores", "tipo_obra"}
        assert ficha["vision"]["descripcion"] == ""
        assert ficha["vision"]["colores"] == []
        assert set(ficha["datos_evento"].keys()) == {"productora", "venue", "fecha", "handles"}
        assert ficha["datos_evento"]["handles"] == []
        assert ficha["calidad_senal"] == "baja"
        assert ficha["error"] == "ollama_no_disponible: boom"
        assert isinstance(ficha["seg_proceso"], float)
        assert ficha["seg_proceso"] >= 0.0

    def test_schema_ok_con_senal_fuerte(self, tmp_path):
        ocr_largo = "x" * 60
        vision_ok = {
            "descripcion": "un flyer de club", "estilo": "neon", "colores": ["#fff"],
            "tipo_obra": "flyer", "categoria": "flyer_evento",
            "productora": "Amelie", "venue": "OpenKlub",
            "fecha": "2026-02-14", "handles": ["@amelie.rd"],
        }
        with mock.patch("percepcion.ocr_tesseract", return_value=ocr_largo), \
             mock.patch("percepcion.vision_imagen", return_value=vision_ok):
            ficha = percepcion.construir_ficha(self._entry(), tmp_path, 5)

        assert ficha["error"] is None
        assert ficha["calidad_senal"] == "alta"
        assert ficha["categoria"] == "flyer_evento"
        assert ficha["datos_evento"]["productora"] == "Amelie"
        assert ficha["vision"]["estilo"] == "neon"

    def test_clasificacion_otro_sin_analisis(self, tmp_path):
        with mock.patch("percepcion.ocr_tesseract") as ocr_mock, \
             mock.patch("percepcion.vision_imagen") as vision_mock:
            ficha = percepcion.construir_ficha(self._entry(tipo="otro", ruta_rel="notas.txt"),
                                               tmp_path, 5)

        ocr_mock.assert_not_called()
        vision_mock.assert_not_called()
        assert ficha["tipo"] == "otro"
        assert ficha["ocr_texto"] == ""
        assert ficha["vision"]["descripcion"] == ""
        assert ficha["categoria"] == ""
        assert ficha["error"] is None
        assert ficha["calidad_senal"] == "baja"

    def test_ocr_truncado_a_1500(self, tmp_path):
        with mock.patch("percepcion.ocr_tesseract", return_value="a" * 2000), \
             mock.patch("percepcion.vision_imagen", return_value={}):
            ficha = percepcion.construir_ficha(self._entry(), tmp_path, 5)
        assert len(ficha["ocr_texto"]) == 1500

    def test_llama_preparar_imagen_para_ocr_antes_de_tesseract(self, tmp_path):
        with mock.patch("percepcion.preparar_imagen_para_ocr",
                        return_value="otra_ruta.png") as prep_mock, \
             mock.patch("percepcion.ocr_tesseract", return_value="") as ocr_mock, \
             mock.patch("percepcion.vision_imagen", return_value={}):
            percepcion.construir_ficha(self._entry(ruta_rel="flyer.jpg"), tmp_path, 5)

        prep_mock.assert_called_once()
        ocr_mock.assert_called_once_with("otra_ruta.png", timeout=5)


# ---------------------------------------------------------------------------
# categoria -- extraida del JSON de vision, enum validado
# ---------------------------------------------------------------------------

class TestParsearJsonVisionCategoria:
    def test_extrae_categoria_valida(self):
        texto = json.dumps({"categoria": "flyer_evento", "descripcion": "x"})
        resultado = percepcion._parsear_json_vision(texto)
        assert resultado["categoria"] == "flyer_evento"

    def test_categoria_ausente_default_vacio(self):
        texto = json.dumps({"descripcion": "x"})
        resultado = percepcion._parsear_json_vision(texto)
        assert resultado["categoria"] == ""

    def test_categoria_invalida_se_vacia(self):
        texto = json.dumps({"categoria": "algo_inventado", "descripcion": "x"})
        resultado = percepcion._parsear_json_vision(texto)
        assert resultado["categoria"] == ""

    def test_todas_las_categorias_validas_pasan(self):
        for cat in percepcion.CATEGORIAS_VALIDAS:
            texto = json.dumps({"categoria": cat})
            resultado = percepcion._parsear_json_vision(texto)
            assert resultado["categoria"] == cat


# ---------------------------------------------------------------------------
# preparar_imagen_para_ocr -- reescala si el archivo pesa mas de 8MB,
# nunca descarta el archivo
# ---------------------------------------------------------------------------

class TestPrepararImagenParaOcr:
    def test_archivo_chico_usa_original(self, tmp_path):
        imagen = tmp_path / "chica.jpg"
        imagen.write_bytes(b"x" * 100)
        ruta = percepcion.preparar_imagen_para_ocr(str(imagen), tmp_path)
        assert ruta == str(imagen)

    def test_archivo_grande_genera_copia_reescalada(self, tmp_path):
        from PIL import Image as PILImage

        imagen = tmp_path / "grande.jpg"
        img = PILImage.new("RGB", (4000, 3000), (10, 20, 30))
        img.save(imagen, format="JPEG")
        # forzamos el umbral bajo para no tener que escribir 8MB reales
        ruta = percepcion.preparar_imagen_para_ocr(
            str(imagen), tmp_path, umbral_bytes=10, max_lado=500)

        assert ruta != str(imagen)
        assert Path(ruta).exists()
        with PILImage.open(ruta) as reescalada:
            assert max(reescalada.size) <= 500

    def test_pil_ausente_cae_a_original(self, tmp_path, monkeypatch):
        imagen = tmp_path / "grande.jpg"
        imagen.write_bytes(b"x" * 100)
        monkeypatch.setattr(percepcion, "Image", None)
        ruta = percepcion.preparar_imagen_para_ocr(str(imagen), tmp_path, umbral_bytes=10)
        assert ruta == str(imagen)

    def test_archivo_inexistente_no_revienta(self, tmp_path):
        ruta = percepcion.preparar_imagen_para_ocr(
            str(tmp_path / "no_existe.jpg"), tmp_path)
        assert ruta == str(tmp_path / "no_existe.jpg")


# ---------------------------------------------------------------------------
# auto-pausa por errores seguidos
# ---------------------------------------------------------------------------

class TestAutoPausa:
    def _ficha_error(self, ruta_rel):
        return {
            "id": "x", "fuente": "rd", "ruta_rel": ruta_rel, "tipo": "imagen",
            "bytes": 1, "mtime": "2026-01-01", "ocr_texto": "", "vision": {},
            "datos_evento": {}, "calidad_senal": "baja",
            "error": "boom", "ts": "t",
        }

    def _ficha_ok(self, ruta_rel):
        return {
            "id": "x", "fuente": "rd", "ruta_rel": ruta_rel, "tipo": "imagen",
            "bytes": 1, "mtime": "2026-01-01", "ocr_texto": "", "vision": {},
            "datos_evento": {}, "calidad_senal": "baja", "error": None, "ts": "t",
        }

    def test_pausa_a_n_errores_seguidos_rc3(self, tmp_path):
        raiz = tmp_path / "rd"
        raiz.mkdir()
        for i in range(6):
            (raiz / ("f%d.jpg" % i)).write_bytes(b"x")
        dir_out = tmp_path / "out"

        fichas = [self._ficha_error("f%d.jpg" % i) for i in range(6)]
        with mock.patch("percepcion.construir_ficha", side_effect=fichas):
            rc = percepcion.correr(str(raiz), None, str(dir_out), max_errores_seguidos=3)

        assert rc == 3
        estado = percepcion.cargar_estado(dir_out)
        assert estado["pausado_por"] == "errores_seguidos"
        assert estado["errores_seguidos"] == 3
        assert estado["procesados"] == 3
        assert len(estado["ultimos_errores"]) == 3

    def test_reset_contador_con_exito(self, tmp_path):
        raiz = tmp_path / "rd"
        raiz.mkdir()
        for i in range(5):
            (raiz / ("f%d.jpg" % i)).write_bytes(b"x")
        dir_out = tmp_path / "out"

        # error, error, OK (resetea), error, error -- con umbral 3 no debe pausar
        secuencia = [
            self._ficha_error("f0.jpg"),
            self._ficha_error("f1.jpg"),
            self._ficha_ok("f2.jpg"),
            self._ficha_error("f3.jpg"),
            self._ficha_error("f4.jpg"),
        ]
        with mock.patch("percepcion.construir_ficha", side_effect=secuencia):
            rc = percepcion.correr(str(raiz), None, str(dir_out), max_errores_seguidos=3)

        assert rc == 0
        estado = percepcion.cargar_estado(dir_out)
        assert estado["errores_seguidos"] == 2
        assert estado["errores_totales"] == 4
        assert estado["procesados"] == 5


# ---------------------------------------------------------------------------
# estado.json cada 10 archivos
# ---------------------------------------------------------------------------

class TestEstadoPeriodico:
    def test_guardado_cada_10_y_al_final(self, tmp_path):
        raiz = tmp_path / "rd"
        raiz.mkdir()
        for i in range(12):
            (raiz / ("f%d.jpg" % i)).write_bytes(b"x")
        dir_out = tmp_path / "out"

        ficha_ok = {
            "id": "x", "fuente": "rd", "ruta_rel": "x", "tipo": "imagen",
            "bytes": 1, "mtime": "2026-01-01", "ocr_texto": "", "vision": {},
            "datos_evento": {}, "calidad_senal": "baja", "error": None, "ts": "t",
        }
        with mock.patch("percepcion.construir_ficha", return_value=ficha_ok), \
             mock.patch("percepcion.guardar_estado", wraps=percepcion.guardar_estado) as guard_mock:
            rc = percepcion.correr(str(raiz), None, str(dir_out))

        assert rc == 0
        # guarda al llegar a 10 procesados + guarda final (12) = 2 llamadas
        assert guard_mock.call_count == 2

        estado = percepcion.cargar_estado(dir_out)
        assert estado["procesados"] == 12
        assert estado["pausado_por"] == "fin"


# ---------------------------------------------------------------------------
# contact sheet -- comando ffmpeg bien compuesto
# ---------------------------------------------------------------------------

class TestContactSheet:
    def test_fps_normal_sin_duracion(self):
        comando = percepcion.construir_comando_contact_sheet("v.mp4", "sheet.jpg")
        assert comando[0] == "ffmpeg"
        assert "v.mp4" in comando
        vf = comando[comando.index("-vf") + 1]
        assert "fps=%s" % (1.0 / 3.0) in vf
        assert "scale=480:-1" in vf
        assert "tile=3x3" in vf
        assert comando[-1] == "sheet.jpg"

    def test_fps_normal_video_corto(self):
        comando = percepcion.construir_comando_contact_sheet("v.mp4", "sheet.jpg", duracion=60)
        vf = comando[comando.index("-vf") + 1]
        assert "fps=%s" % (1.0 / 3.0) in vf

    def test_fps_proporcional_video_largo(self):
        duracion = 300.0
        comando = percepcion.construir_comando_contact_sheet("v.mp4", "sheet.jpg", duracion=duracion)
        vf = comando[comando.index("-vf") + 1]
        fps_esperado = percepcion.TILE_FRAMES / duracion
        assert "fps=%s" % fps_esperado in vf
        assert fps_esperado < (1.0 / 3.0)

    def test_umbral_video_largo_no_dispara_debajo_del_limite(self):
        comando = percepcion.construir_comando_contact_sheet(
            "v.mp4", "sheet.jpg", duracion=percepcion.VIDEO_LARGO_SEG)
        vf = comando[comando.index("-vf") + 1]
        assert "fps=%s" % (1.0 / 3.0) in vf


# ---------------------------------------------------------------------------
# reporter.py
# ---------------------------------------------------------------------------

def _escribir_fichas(dir_out, fichas):
    dir_fichas = dir_out / "fichas"
    dir_fichas.mkdir(parents=True, exist_ok=True)
    with (dir_fichas / "fichas.jsonl").open("w", encoding="utf-8") as f:
        for ficha in fichas:
            f.write(json.dumps(ficha) + "\n")


def _escribir_estado(dir_out, estado):
    dir_out.mkdir(parents=True, exist_ok=True)
    (dir_out / "estado.json").write_text(json.dumps(estado), encoding="utf-8")


class TestVelocidadReal:
    def test_calcula_desde_seg_proceso(self):
        fichas = [{"seg_proceso": 2.0}, {"seg_proceso": 4.0}, {"seg_proceso": 3.0}]
        vel, seg_prom = reporter.velocidad_real_archivos_por_min(fichas)
        assert seg_prom == 3.0
        assert vel == 20.0  # 60/3.0

    def test_sin_seg_proceso_devuelve_cero(self):
        fichas = [{"seg_proceso": None}, {}, {"seg_proceso": 0}]
        vel, seg_prom = reporter.velocidad_real_archivos_por_min(fichas)
        assert vel == 0.0
        assert seg_prom == 0.0

    def test_usa_solo_las_ultimas_n_fichas(self):
        fichas = [{"seg_proceso": 100.0}] + [{"seg_proceso": 1.0}] * 5
        vel, seg_prom = reporter.velocidad_real_archivos_por_min(fichas, muestra=5)
        assert seg_prom == 1.0


class TestReporter:
    def _ficha(self, fuente, ruta_rel, ts, calidad="alta", seg_proceso=2.5,
               categoria="flyer_evento"):
        return {
            "id": "x", "fuente": fuente, "ruta_rel": ruta_rel, "tipo": "imagen",
            "categoria": categoria, "bytes": 1, "mtime": "2026-01-01", "ocr_texto": "algo",
            "vision": {"descripcion": "una obra", "estilo": "", "colores": [], "tipo_obra": ""},
            "datos_evento": {"productora": "", "venue": "", "fecha": "", "handles": []},
            "calidad_senal": calidad, "error": None, "seg_proceso": seg_proceso, "ts": ts,
        }

    def test_genera_md_con_secciones_y_estado_terminado(self, tmp_path):
        dir_out = tmp_path / "out"
        fichas = [
            self._ficha("rd", "a.jpg", "2026-07-22T10:00:00+00:00"),
            self._ficha("ig", "b.jpg", "2026-07-22T10:05:00+00:00"),
        ]
        _escribir_fichas(dir_out, fichas)
        _escribir_estado(dir_out, {
            "inicio": "2026-07-22T09:00:00+00:00",
            "total_trabajo": 2, "procesados": 2,
            "por_fuente": {"rd": 1, "ig": 1},
            "errores_totales": 0, "errores_seguidos": 0,
            "pausado_por": "fin", "ultimos_errores": [],
        })

        ruta = reporter.escribir_reporte(dir_out)
        md = ruta.read_text(encoding="utf-8")

        assert "## Resumen" in md
        assert "## Procesados por fuente y tipo" in md
        assert "## Errores" in md
        assert "## Muestra de fichas" in md
        assert "ESTADO: TERMINADO" in md
        assert "rd" in md and "ig" in md

    def test_estado_pausado_por_errores(self, tmp_path):
        dir_out = tmp_path / "out"
        _escribir_fichas(dir_out, [])
        _escribir_estado(dir_out, {
            "total_trabajo": 5, "procesados": 2, "por_fuente": {"rd": 2, "ig": 0},
            "errores_totales": 3, "errores_seguidos": 3,
            "pausado_por": "errores_seguidos",
            "ultimos_errores": [{"ruta_rel": "a.jpg", "error": "boom"}],
        })

        ruta = reporter.escribir_reporte(dir_out)
        md = ruta.read_text(encoding="utf-8")
        assert "ESTADO: PAUSADO(errores_seguidos)" in md
        assert "boom" in md

    def test_estado_corriendo_sin_pausa_explicita(self, tmp_path):
        dir_out = tmp_path / "out"
        _escribir_fichas(dir_out, [])
        _escribir_estado(dir_out, {
            "total_trabajo": 5, "procesados": 2, "por_fuente": {"rd": 2, "ig": 0},
            "errores_totales": 0, "errores_seguidos": 0,
            "pausado_por": None, "ultimos_errores": [],
        })

        ruta = reporter.escribir_reporte(dir_out)
        md = ruta.read_text(encoding="utf-8")
        assert "ESTADO: CORRIENDO" in md

    def test_sin_estado_ni_fichas_no_revienta(self, tmp_path):
        dir_out = tmp_path / "out"
        dir_out.mkdir()
        ruta = reporter.escribir_reporte(dir_out)
        md = ruta.read_text(encoding="utf-8")
        assert "ESTADO: PAUSADO(sin_estado)" in md
        assert "(sin fichas todavia)" in md

    def test_muestra_ultima_ficha_por_fuente(self, tmp_path):
        dir_out = tmp_path / "out"
        fichas = [
            self._ficha("rd", "vieja.jpg", "2026-07-22T09:00:00+00:00"),
            self._ficha("rd", "nueva.jpg", "2026-07-22T10:00:00+00:00"),
        ]
        _escribir_fichas(dir_out, fichas)
        _escribir_estado(dir_out, {
            "total_trabajo": 2, "procesados": 2, "por_fuente": {"rd": 2, "ig": 0},
            "errores_totales": 0, "errores_seguidos": 0,
            "pausado_por": "fin", "ultimos_errores": [],
        })

        ruta = reporter.escribir_reporte(dir_out)
        md = ruta.read_text(encoding="utf-8")
        assert "nueva.jpg" in md
        assert "vieja.jpg" not in md

    def test_velocidad_real_y_categoria_en_muestra(self, tmp_path):
        dir_out = tmp_path / "out"
        fichas = [
            self._ficha("rd", "a.jpg", "2026-07-22T10:00:00+00:00", seg_proceso=4.0,
                        categoria="material_rd"),
        ]
        _escribir_fichas(dir_out, fichas)
        _escribir_estado(dir_out, {
            "total_trabajo": 1, "procesados": 1, "por_fuente": {"rd": 1, "ig": 0},
            "errores_totales": 0, "errores_seguidos": 0,
            "pausado_por": "fin", "ultimos_errores": [],
        })

        ruta = reporter.escribir_reporte(dir_out)
        md = ruta.read_text(encoding="utf-8")

        assert "Velocidad real" in md
        assert "15.0" in md  # 60/4.0 archivos/min
        assert "material_rd" in md

    def test_velocidad_real_sin_datos(self, tmp_path):
        dir_out = tmp_path / "out"
        _escribir_fichas(dir_out, [])
        _escribir_estado(dir_out, {
            "total_trabajo": 1, "procesados": 0, "por_fuente": {"rd": 0, "ig": 0},
            "errores_totales": 0, "errores_seguidos": 0,
            "pausado_por": None, "ultimos_errores": [],
        })

        ruta = reporter.escribir_reporte(dir_out)
        md = ruta.read_text(encoding="utf-8")
        assert "Velocidad real: sin datos" in md

    def test_reporte_sobrescribe(self, tmp_path):
        dir_out = tmp_path / "out"
        _escribir_fichas(dir_out, [])
        _escribir_estado(dir_out, {
            "total_trabajo": 1, "procesados": 0, "por_fuente": {"rd": 0, "ig": 0},
            "errores_totales": 0, "errores_seguidos": 0,
            "pausado_por": None, "ultimos_errores": [],
        })
        ruta1 = reporter.escribir_reporte(dir_out)
        contenido1 = ruta1.read_text(encoding="utf-8")

        _escribir_estado(dir_out, {
            "total_trabajo": 1, "procesados": 1, "por_fuente": {"rd": 1, "ig": 0},
            "errores_totales": 0, "errores_seguidos": 0,
            "pausado_por": "fin", "ultimos_errores": [],
        })
        ruta2 = reporter.escribir_reporte(dir_out)
        contenido2 = ruta2.read_text(encoding="utf-8")

        assert ruta1 == ruta2
        assert contenido1 != contenido2
        assert "ESTADO: TERMINADO" in contenido2
