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

    def test_un_error_no_se_marca_como_procesado_y_se_reintenta(self, tmp_path):
        raiz = tmp_path / "rd"
        raiz.mkdir()
        (raiz / "a.jpg").write_bytes(b"a")
        dir_out = tmp_path / "out"
        error = {
            "id": "x", "fuente": "rd", "ruta_rel": "a.jpg", "tipo": "imagen",
            "error": "timeout", "seg_proceso": 0.1,
        }
        ok = dict(error, error=None)

        with mock.patch("percepcion.construir_ficha", side_effect=[error, ok]) as construir:
            assert percepcion.correr(str(raiz), None, str(dir_out)) == 0
            assert "rd:a.jpg" not in percepcion.cargar_procesados(dir_out)
            assert percepcion.correr(str(raiz), None, str(dir_out)) == 0

        assert construir.call_count == 2
        assert "rd:a.jpg" in percepcion.cargar_procesados(dir_out)
        assert "rd:a.jpg" not in percepcion.cargar_fallos(dir_out)

    def test_error_persistente_entra_en_cuarentena(self, tmp_path):
        raiz = tmp_path / "rd"
        raiz.mkdir()
        archivo = raiz / "a.jpg"
        archivo.write_bytes(b"a")
        dir_out = tmp_path / "out"
        error = {
            "id": "x", "fuente": "rd", "ruta_rel": "a.jpg", "tipo": "imagen",
            "error": "timeout", "seg_proceso": 0.1,
        }

        with mock.patch("percepcion.construir_ficha", return_value=error) as construir:
            for _ in range(percepcion.MAX_INTENTOS_FALLIDOS + 1):
                assert percepcion.correr(str(raiz), None, str(dir_out)) == 0

        assert construir.call_count == percepcion.MAX_INTENTOS_FALLIDOS
        registro = percepcion.cargar_fallos(dir_out)["rd:a.jpg"]
        assert registro["cuarentena"] is True
        assert registro["intentos"] == percepcion.MAX_INTENTOS_FALLIDOS
        assert "rd:a.jpg" not in percepcion.cargar_procesados(dir_out)

    def test_archivo_cambiado_sale_de_cuarentena(self, tmp_path):
        entry = {"bytes": 1, "mtime": 1.0}
        fallos = {}
        clave = "rd:a.jpg"
        for _ in range(percepcion.MAX_INTENTOS_FALLIDOS):
            percepcion.registrar_fallo(fallos, clave, entry, "timeout")
        assert percepcion.esta_en_cuarentena(fallos, clave, entry)
        assert not percepcion.esta_en_cuarentena(
            fallos, clave, {"bytes": 2, "mtime": 2.0})

    def test_migra_checkpoint_historico_fallido_usando_el_ultimo_intento(self, tmp_path):
        out = tmp_path / "out"
        fichas = out / "fichas"
        fichas.mkdir(parents=True)
        (out / "procesados.txt").write_text(
            "rd:falla.jpg\nrd:recuperada.jpg\nrd:ok.jpg\n", encoding="utf-8")
        rows = [
            {"fuente": "rd", "ruta_rel": "falla.jpg", "error": "timeout"},
            {"fuente": "rd", "ruta_rel": "recuperada.jpg", "error": "timeout"},
            {"fuente": "rd", "ruta_rel": "recuperada.jpg", "error": None},
            {"fuente": "rd", "ruta_rel": "ok.jpg", "error": None},
        ]
        (fichas / "fichas.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

        resultado = percepcion.reconciliar_checkpoint_fallido(
            out, percepcion.cargar_procesados(out))

        assert resultado == {"rd:recuperada.jpg", "rd:ok.jpg"}
        assert percepcion.cargar_procesados(out) == resultado
        compactadas = [json.loads(line) for line in
                   (fichas / "fichas.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(compactadas) == 3
        recuperada = next(row for row in compactadas if row["ruta_rel"] == "recuperada.jpg")
        assert recuperada["error"] is None


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
            "ocr_texto", "vision", "datos_evento", "medicion", "calidad_senal",
            "error", "seg_proceso", "ts",
        }
        assert ficha["fuente"] == "rd"
        assert ficha["ruta_rel"] == "flyer.jpg"
        assert ficha["ocr_texto"] == ""
        assert ficha["categoria"] == ""
        # `medicion` entra el 2026-07-31 y es lo que este caso demuestra mejor
        # que ningun otro: la vision REVENTÓ y el ocr corrio vacio, y hasta hoy
        # las dos cosas se escribian igual -- vacio. Medido sobre las 3.138
        # fichas reales, `ocr_texto` venia vacio en el 76% sin decir nunca si
        # era "no habia texto", "no aplica" o "se cayo".
        assert ficha["medicion"]["vision"]["estado"] == "fallo"
        assert "ollama_no_disponible" in ficha["medicion"]["vision"]["detalle"]
        assert ficha["medicion"]["ocr"]["estado"] == "fallo"
        # El esquema depende del corpus desde 2026-07-26: habia UN prompt para
        # dos trabajos distintos (extraer datos de un flyer de RD vs. mapear
        # conceptualmente una obra del archivo), y el constructor de fichas
        # descartaba en silencio todo campo que el prompt nuevo pedia -- entre
        # ellos `headliners`, que es la mitad de la formula de triangulacion.
        # Ante fallo total, `vision` queda vacio: no hay nada que reportar.
        assert ficha["vision"] == {}
        assert set(ficha["datos_evento"].keys()) == {
            "productora", "venue", "fecha", "headliners", "handles"}
        assert ficha["datos_evento"]["handles"] == []
        assert ficha["datos_evento"]["headliners"] == []
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
        # 'estilo' es vocabulario del archivo del artista, no de un flyer de
        # RD: bajo el esquema por corpus (2026-07-26) una ficha de RD guarda lo
        # extraible -- texto visible y colores -- y no interpreta la pieza.
        assert "estilo" not in ficha["vision"]
        assert ficha["vision"]["colores"] == ["#fff"]

    def test_clasificacion_otro_sin_analisis(self, tmp_path):
        with mock.patch("percepcion.ocr_tesseract") as ocr_mock, \
             mock.patch("percepcion.vision_imagen") as vision_mock:
            ficha = percepcion.construir_ficha(self._entry(tipo="otro", ruta_rel="notas.txt"),
                                               tmp_path, 5)

        ocr_mock.assert_not_called()
        vision_mock.assert_not_called()
        assert ficha["tipo"] == "otro"
        assert ficha["ocr_texto"] == ""
        # Sin analisis no hay nada percibido: `vision` vacio en vez de un
        # diccionario de claves vacias que aparentaba contenido.
        assert ficha["vision"] == {}
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
        assert estado["procesados"] == 0
        assert estado["fallos_reintentables"] == 3
        assert estado["cuarentena"] == 0
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
        assert estado["procesados"] == 1
        assert estado["fallos_reintentables"] == 4


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


# ---------------------------------------------------------------------------
# The alarm that cried wolf, and the probe flag
# ---------------------------------------------------------------------------

class TestAvisoDeDescarte:
    """The discard warning added on 2026-07-31 was itself announcing a discard
    that does not happen.

    `datos_evento` is built from CLAVES_EVENTO and `categoria` is read a few
    lines below, both from the same `vision` dict -- so those keys are USED,
    not dropped. The warning subtracted neither, and the RD probe of
    2026-08-01 printed "se descartan: categoria, fecha, handles, headliners,
    productora, venue" for 7 of 10 files while storing every one of them.

    A false alarm is the mirror image of a silent discard: it sends whoever is
    reading to chase a ghost, and the next real alarm is not believed. Both are
    the interface lying about what the machine did.
    """

    def _entry(self):
        return {"fuente": "rd", "ruta_rel": "flyer.jpg", "ruta_abs": "flyer.jpg",
                "tipo": "imagen", "bytes": 1, "mtime": 0}

    def test_keys_that_are_stored_elsewhere_are_not_called_discarded(
            self, tmp_path, capsys):
        vision = {"texto_visible": "OCT 04", "colores": ["negro"],
                  "categoria": "flyer_evento", "productora": "RD",
                  "venue": "Parque", "fecha": "OCT 04",
                  "headliners": [], "handles": ["@rd"]}
        with mock.patch("percepcion.ocr_tesseract", return_value=""), \
             mock.patch("percepcion.vision_imagen", return_value=vision):
            ficha = percepcion.construir_ficha(self._entry(), tmp_path, 5)

        assert "se descartan" not in capsys.readouterr().out
        # and they really are stored, which is why the warning was wrong
        assert ficha["datos_evento"]["venue"] == "Parque"
        assert ficha["categoria"] == "flyer_evento"

    def test_a_genuinely_unknown_key_is_still_announced(self, tmp_path, capsys):
        """The alarm has to keep working; the fix narrows it, not silences it."""
        vision = {"texto_visible": "x", "clave_que_nadie_declaro": "algo"}
        with mock.patch("percepcion.ocr_tesseract", return_value=""), \
             mock.patch("percepcion.vision_imagen", return_value=vision):
            ficha = percepcion.construir_ficha(self._entry(), tmp_path, 5)

        salida = capsys.readouterr().out
        assert "se descartan" in salida
        assert "clave_que_nadie_declaro" in salida
        assert "clave_que_nadie_declaro" not in ficha["vision"]


class TestLimite:
    """`--limite` exists to PROBE a corpus without running it whole: the user
    asked for 10 RD flyers, not the 1.737 files that root holds."""

    def test_the_cut_is_announced(self, tmp_path, capsys):
        for i in range(5):
            (tmp_path / ("%02d.jpg" % i)).write_bytes(b"x")
        salida_dir = tmp_path / "out"
        ficha = {"id": "x", "error": None, "fuente": "rd", "tipo": "imagen"}
        with mock.patch("percepcion.construir_ficha", return_value=ficha):
            percepcion.correr(str(tmp_path), None, str(salida_dir), limite=2)

        salida = capsys.readouterr().out
        assert "LIMITE: sonda de 2 de 5 archivos" in salida, (
            "un total mas chico sin explicacion se lee como 'eso era todo el "
            "corpus', y quien compare cobertura despues divide por el numero "
            "equivocado")

    def test_without_the_flag_nothing_is_cut(self, tmp_path, capsys):
        for i in range(3):
            (tmp_path / ("%02d.jpg" % i)).write_bytes(b"x")
        ficha = {"id": "x", "error": None, "fuente": "rd", "tipo": "imagen"}
        with mock.patch("percepcion.construir_ficha", return_value=ficha):
            percepcion.correr(str(tmp_path), None, str(tmp_path / "out"))
        assert "LIMITE" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Was it READ, or was it inferred?
# ---------------------------------------------------------------------------

class TestRespaldoEvento:
    """Measured on 300 real RD files on 2026-08-01: `venue` appeared in the
    text read from the image 99% of the time and `headliners` 97%, but
    `productora` only 33% -- of 173 extracted productoras, 116 were nowhere in
    the text. Almost all of them said "Reduciendo Dano": the model inferred the
    producer from CONTEXT (this is RD material) instead of reading it off the
    poster.

    That is not a lie, but it is not reading either, and the RD database is fed
    from here: a wrong productora is a wrong client. So it is MARKED, never
    deleted -- an inferred value can be the right one, and the person curating
    it decides. What cannot happen is that it reaches the database
    indistinguishable from one that was read.
    """

    def test_a_value_that_appears_in_the_text_is_supported(self):
        r = percepcion.respaldo_evento(
            {"venue": "Club Hipico"}, "CLUB HIPICO 01 MAYO", "")
        assert r == {"con_respaldo": ["venue"]}

    def test_a_value_nobody_read_is_flagged(self):
        r = percepcion.respaldo_evento(
            {"productora": "Reduciendo Dano"}, "SUSTANCIA NEBULA", "")
        assert r["sin_respaldo"] == ["productora"]
        assert "con_respaldo" not in r

    def test_the_flag_never_deletes_the_value(self):
        datos = {"productora": "Reduciendo Dano"}
        percepcion.respaldo_evento(datos, "", "")
        assert datos["productora"] == "Reduciendo Dano", (
            "un dato deducido puede ser el correcto; el que decide es quien lo "
            "cura, no este archivo")

    def test_the_vision_text_counts_as_read_too(self):
        """Tesseract reads 62% of these files and the model 84%. Scoring only
        against OCR would flag as invented what the model actually read."""
        r = percepcion.respaldo_evento(
            {"headliners": ["ADRIATIQUE"]}, "", "ADRIATIQUE COLYN")
        assert r == {"con_respaldo": ["headliners"]}

    def test_dates_are_not_scored_at_all(self):
        """The model normalises ("VIERNES 01 MAYO" -> "2026-05-01"), so word
        overlap would report "unsupported" over a correct reading. Measuring
        with the wrong instrument and reporting the result is worse than not
        measuring."""
        r = percepcion.respaldo_evento(
            {"fecha": "2026-05-01"}, "VIERNES 01 MAYO", "")
        assert "fecha" not in r.get("sin_respaldo", [])
        assert "fecha" not in r.get("con_respaldo", [])

    def test_handles_are_not_scored_either(self):
        """An @ is legitimately derived from an email on the poster."""
        r = percepcion.respaldo_evento(
            {"handles": ["@reduciendodano.cl"]}, "eventos@reduciendodano.cl", "")
        assert r == {}

    def test_accents_do_not_break_the_match(self):
        r = percepcion.respaldo_evento(
            {"venue": "Teatro Caupolicán"}, "TEATRO CAUPOLICAN", "")
        assert r == {"con_respaldo": ["venue"]}

    def test_nothing_extracted_says_nothing(self):
        assert percepcion.respaldo_evento({}, "texto", "texto") == {}

    def test_it_lands_in_the_ficha(self, tmp_path):
        entry = {"fuente": "rd", "ruta_rel": "f.jpg", "ruta_abs": "f.jpg",
                 "tipo": "imagen", "bytes": 1, "mtime": 0}
        vision = {"texto_visible": "CLUB HIPICO", "venue": "Club Hipico",
                  "productora": "Reduciendo Dano"}
        with mock.patch("percepcion.ocr_tesseract", return_value=""), \
             mock.patch("percepcion.vision_imagen", return_value=vision):
            ficha = percepcion.construir_ficha(entry, tmp_path, 5)
        med = ficha["medicion"]["datos_evento"]
        assert med["con_respaldo"] == ["venue"]
        assert med["sin_respaldo"] == ["productora"]
