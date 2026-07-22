#!/usr/bin/env python3
"""test_mineria_rd.py -- tests para cultura/mak_plataforma/mineria_rd.py (pytest)."""
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

test_dir = Path(__file__).parent
proyecto_dir = test_dir.parent
sys.path.insert(0, str(proyecto_dir / "cultura" / "mak_plataforma"))

import mineria_rd  # noqa: E402


# ---------------------------------------------------------------------------
# barrer()
# ---------------------------------------------------------------------------

class TestBarrer:
    def test_clasifica_por_extension(self, tmp_path):
        (tmp_path / "flyer.jpg").write_bytes(b"x")
        (tmp_path / "brief.pdf").write_bytes(b"x")
        (tmp_path / "logo.ai").write_bytes(b"x")
        (tmp_path / "notas.txt").write_bytes(b"x")

        resultado = mineria_rd.barrer(str(tmp_path))
        tipos = {Path(r["path"]).name: r["tipo"] for r in resultado}

        assert tipos["flyer.jpg"] == "imagen"
        assert tipos["brief.pdf"] == "pdf"
        assert tipos["logo.ai"] == "ai"
        assert tipos["notas.txt"] == "otro"

    def test_salta_archivos_grandes(self, tmp_path):
        chico = tmp_path / "chico.jpg"
        chico.write_bytes(b"x" * 10)
        grande = tmp_path / "grande.jpg"
        grande.write_bytes(b"x" * (mineria_rd.LIMITE_TAMANO_BYTES + 1))

        resultado = mineria_rd.barrer(str(tmp_path))
        nombres = {Path(r["path"]).name for r in resultado}

        assert "chico.jpg" in nombres
        assert "grande.jpg" not in nombres

    def test_salta_directorios_archive(self, tmp_path):
        (tmp_path / "_archive").mkdir()
        (tmp_path / "_archive" / "viejo.jpg").write_bytes(b"x")
        (tmp_path / "vivo.jpg").write_bytes(b"x")

        resultado = mineria_rd.barrer(str(tmp_path))
        nombres = {Path(r["path"]).name for r in resultado}

        assert "vivo.jpg" in nombres
        assert "viejo.jpg" not in nombres

    def test_raiz_inexistente_devuelve_vacio(self, tmp_path):
        assert mineria_rd.barrer(str(tmp_path / "no_existe")) == []


# ---------------------------------------------------------------------------
# ocr_pdf() / ocr_imagen()
# ---------------------------------------------------------------------------

class TestOcr:
    def test_ocr_pdf_usa_pdftotext_si_hay_texto(self):
        proc_ok = subprocess.CompletedProcess(args=[], returncode=0, stdout="hola mundo\n")
        with mock.patch("mineria_rd.subprocess.run", return_value=proc_ok) as run_mock:
            texto = mineria_rd.ocr_pdf("archivo.pdf")
        assert texto == "hola mundo"
        assert run_mock.call_count == 1
        assert run_mock.call_args[0][0][0] == "pdftotext"

    def test_ocr_pdf_cae_a_tesseract_si_pdftotext_vacio(self):
        proc_vacio = subprocess.CompletedProcess(args=[], returncode=0, stdout="")
        proc_tesseract = subprocess.CompletedProcess(args=[], returncode=0, stdout="texto escaneado")
        with mock.patch(
            "mineria_rd.subprocess.run", side_effect=[proc_vacio, proc_tesseract]
        ) as run_mock:
            texto = mineria_rd.ocr_pdf("escaneado.pdf")
        assert texto == "texto escaneado"
        assert run_mock.call_count == 2
        assert run_mock.call_args_list[1][0][0][0] == "tesseract"

    def test_ocr_pdf_no_revienta_si_falla_todo(self):
        with mock.patch("mineria_rd.subprocess.run", side_effect=OSError("no existe")):
            texto = mineria_rd.ocr_pdf("no_existe.pdf")
        assert texto == ""

    def test_ocr_imagen_llama_tesseract_spa(self):
        proc_ok = subprocess.CompletedProcess(args=[], returncode=0, stdout="OPENKLUB VIERNES\n")
        with mock.patch("mineria_rd.subprocess.run", return_value=proc_ok) as run_mock:
            texto = mineria_rd.ocr_imagen("flyer.jpg")
        assert texto == "OPENKLUB VIERNES"
        comando = run_mock.call_args[0][0]
        assert comando[0] == "tesseract"
        assert "-l" in comando and "spa" in comando

    def test_ocr_imagen_no_revienta_si_falla(self):
        with mock.patch("mineria_rd.subprocess.run", side_effect=subprocess.TimeoutExpired("tesseract", 120)):
            texto = mineria_rd.ocr_imagen("flyer.jpg")
        assert texto == ""


# ---------------------------------------------------------------------------
# parece_flyer() -- heuristica
# ---------------------------------------------------------------------------

class TestPareceFlyer:
    def test_detecta_arroba(self):
        assert mineria_rd.parece_flyer("sigue a @productora.rd en instagram")

    def test_detecta_fecha(self):
        assert mineria_rd.parece_flyer("viernes 12/09 desde las 23:00")

    def test_detecta_palabra_evento(self):
        assert mineria_rd.parece_flyer("GRAN FESTIVAL DE VERANO")

    def test_texto_plano_no_es_flyer(self):
        assert not mineria_rd.parece_flyer("factura numero 4521 total 15000")

    def test_texto_vacio_no_es_flyer(self):
        assert not mineria_rd.parece_flyer("")


# ---------------------------------------------------------------------------
# vision_flyer() -- via ollama mockeado
# ---------------------------------------------------------------------------

class TestVisionFlyer:
    def _respuesta_ollama(self, texto_modelo):
        cuerpo = json.dumps({"response": texto_modelo}).encode("utf-8")
        cm = mock.MagicMock()
        cm.read.return_value = cuerpo
        cm.__enter__.return_value = cm
        cm.__exit__.return_value = False
        return cm

    def test_parsea_json_limpio(self, tmp_path):
        imagen = tmp_path / "flyer.jpg"
        imagen.write_bytes(b"contenido-falso")
        texto_modelo = json.dumps({
            "productora": "Amelie", "evento": "Verano", "venue": "OpenKlub",
            "fecha": "2026-02-14", "instagram_handles": ["@amelie.rd"],
        })
        respuesta = self._respuesta_ollama(texto_modelo)
        with mock.patch("mineria_rd.urllib.request.urlopen", return_value=respuesta):
            resultado = mineria_rd.vision_flyer(str(imagen))
        assert resultado["productora"] == "Amelie"
        assert resultado["venue"] == "OpenKlub"
        assert resultado["instagram_handles"] == ["@amelie.rd"]

    def test_parsea_json_con_texto_alrededor(self, tmp_path):
        imagen = tmp_path / "flyer.jpg"
        imagen.write_bytes(b"contenido-falso")
        texto_modelo = (
            'Claro, aca esta el JSON solicitado:\n'
            '{"productora": "Dame", "evento": "", "venue": "", "fecha": "", '
            '"instagram_handles": []}\n'
            "Espero que te sirva."
        )
        respuesta = self._respuesta_ollama(texto_modelo)
        with mock.patch("mineria_rd.urllib.request.urlopen", return_value=respuesta):
            resultado = mineria_rd.vision_flyer(str(imagen))
        assert resultado["productora"] == "Dame"

    def test_respuesta_sin_json_da_error_controlado(self, tmp_path):
        imagen = tmp_path / "flyer.jpg"
        imagen.write_bytes(b"contenido-falso")
        respuesta = self._respuesta_ollama("no tengo idea de que es esto")
        with mock.patch("mineria_rd.urllib.request.urlopen", return_value=respuesta):
            resultado = mineria_rd.vision_flyer(str(imagen))
        assert "error" in resultado

    def test_archivo_inexistente_no_revienta(self):
        resultado = mineria_rd.vision_flyer("no_existe.jpg")
        assert "error" in resultado

    def test_ollama_no_disponible_da_error_controlado(self, tmp_path):
        import urllib.error
        imagen = tmp_path / "flyer.jpg"
        imagen.write_bytes(b"contenido-falso")
        with mock.patch(
            "mineria_rd.urllib.request.urlopen",
            side_effect=urllib.error.URLError("conexion rechazada"),
        ):
            resultado = mineria_rd.vision_flyer(str(imagen))
        assert "error" in resultado


# ---------------------------------------------------------------------------
# minar() -- resumibilidad
# ---------------------------------------------------------------------------

class TestMinar:
    def test_resumible_no_reprocesa_archivos_ya_hechos(self, tmp_path):
        raiz = tmp_path / "RD"
        raiz.mkdir()
        (raiz / "a.jpg").write_bytes(b"a")
        (raiz / "b.jpg").write_bytes(b"b")

        estado_path = tmp_path / "estado.json"
        jsonl_path = tmp_path / "candidatos.jsonl"

        with mock.patch("mineria_rd.ocr_imagen", return_value="") as ocr_mock:
            mineria_rd.minar(
                str(raiz), estado_path=str(estado_path), jsonl_path=str(jsonl_path)
            )
            assert ocr_mock.call_count == 2

            # segunda corrida: nada nuevo que procesar
            mineria_rd.minar(
                str(raiz), estado_path=str(estado_path), jsonl_path=str(jsonl_path)
            )
            assert ocr_mock.call_count == 2

        estado = json.loads(estado_path.read_text(encoding="utf-8"))
        assert len(estado["procesados"]) == 2

        lineas = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lineas) == 2

    def test_resumible_procesa_solo_lo_nuevo_tras_agregar_archivo(self, tmp_path):
        raiz = tmp_path / "RD"
        raiz.mkdir()
        (raiz / "a.jpg").write_bytes(b"a")

        estado_path = tmp_path / "estado.json"
        jsonl_path = tmp_path / "candidatos.jsonl"

        with mock.patch("mineria_rd.ocr_imagen", return_value=""):
            mineria_rd.minar(str(raiz), estado_path=str(estado_path), jsonl_path=str(jsonl_path))

        (raiz / "b.jpg").write_bytes(b"b")

        with mock.patch("mineria_rd.ocr_imagen", return_value="") as ocr_mock:
            mineria_rd.minar(str(raiz), estado_path=str(estado_path), jsonl_path=str(jsonl_path))
            assert ocr_mock.call_count == 1

        lineas = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lineas) == 2

    def test_limite_corta_la_corrida(self, tmp_path):
        raiz = tmp_path / "RD"
        raiz.mkdir()
        for i in range(5):
            (raiz / f"f{i}.jpg").write_bytes(b"x")

        estado_path = tmp_path / "estado.json"
        jsonl_path = tmp_path / "candidatos.jsonl"

        with mock.patch("mineria_rd.ocr_imagen", return_value=""):
            mineria_rd.minar(
                str(raiz), limite=2, estado_path=str(estado_path), jsonl_path=str(jsonl_path)
            )

        lineas = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lineas) == 2

    def test_solo_tipo_filtra_pdfs(self, tmp_path):
        raiz = tmp_path / "RD"
        raiz.mkdir()
        (raiz / "flyer.jpg").write_bytes(b"x")
        (raiz / "brief.pdf").write_bytes(b"x")

        estado_path = tmp_path / "estado.json"
        jsonl_path = tmp_path / "candidatos.jsonl"

        with mock.patch("mineria_rd.ocr_pdf", return_value="") as ocr_pdf_mock, \
             mock.patch("mineria_rd.ocr_imagen", return_value="") as ocr_img_mock:
            mineria_rd.minar(
                str(raiz), solo_tipo="pdfs",
                estado_path=str(estado_path), jsonl_path=str(jsonl_path),
            )

        assert ocr_pdf_mock.call_count == 1
        assert ocr_img_mock.call_count == 0

    def test_vision_solo_se_llama_si_parece_flyer(self, tmp_path):
        raiz = tmp_path / "RD"
        raiz.mkdir()
        (raiz / "flyer.jpg").write_bytes(b"x")
        (raiz / "factura.jpg").write_bytes(b"x")

        estado_path = tmp_path / "estado.json"
        jsonl_path = tmp_path / "candidatos.jsonl"

        def ocr_falso(path):
            return "FESTIVAL @productora 12/09" if "flyer" in path else "factura 4521 total"

        with mock.patch("mineria_rd.ocr_imagen", side_effect=ocr_falso), \
             mock.patch("mineria_rd.vision_flyer", return_value={"productora": "X"}) as vision_mock:
            mineria_rd.minar(
                str(raiz), estado_path=str(estado_path), jsonl_path=str(jsonl_path)
            )

        assert vision_mock.call_count == 1

    def test_archivo_ai_no_se_le_hace_ocr(self, tmp_path):
        raiz = tmp_path / "RD"
        raiz.mkdir()
        (raiz / "logo.ai").write_bytes(b"x")

        estado_path = tmp_path / "estado.json"
        jsonl_path = tmp_path / "candidatos.jsonl"

        with mock.patch("mineria_rd.ocr_pdf") as ocr_pdf_mock, \
             mock.patch("mineria_rd.ocr_imagen") as ocr_img_mock:
            mineria_rd.minar(str(raiz), estado_path=str(estado_path), jsonl_path=str(jsonl_path))

        ocr_pdf_mock.assert_not_called()
        ocr_img_mock.assert_not_called()

        lineas = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
        registro = json.loads(lineas[0])
        assert registro["tipo"] == "ai"
        assert registro["ocr_texto"] == ""


# ---------------------------------------------------------------------------
# consolidar() -- dedup + conteo de evidencia
# ---------------------------------------------------------------------------

def _escribir_jsonl(path, registros):
    with open(path, "w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r) + "\n")


class TestConsolidar:
    def test_agrupa_por_productora_con_evidencia(self, tmp_path):
        jsonl_path = tmp_path / "candidatos.jsonl"
        _escribir_jsonl(jsonl_path, [
            {"path": "a.jpg", "tipo": "imagen", "ocr_texto": "", "vision": {
                "productora": "Nueva Productora", "evento": "Fiesta 1", "venue": "",
                "fecha": "", "instagram_handles": ["@nueva"],
            }},
            {"path": "b.jpg", "tipo": "imagen", "ocr_texto": "", "vision": {
                "productora": "nueva productora", "evento": "Fiesta 2", "venue": "",
                "fecha": "", "instagram_handles": [],
            }},
        ])

        resultado = mineria_rd.consolidar(str(jsonl_path), repo_root=tmp_path)
        nuevas = resultado["productoras_nuevas"]

        assert len(nuevas) == 1
        (slug, datos), = nuevas.items()
        assert datos["evidencia"] == 2
        assert set(datos["archivos_fuente"]) == {"a.jpg", "b.jpg"}
        assert datos["instagram_handles"] == ["@nueva"]

    def test_no_propone_productora_ya_conocida(self, tmp_path):
        dir_productoras = tmp_path / "data" / "productoras"
        dir_productoras.mkdir(parents=True)
        (dir_productoras / "amelie.json").write_text(
            json.dumps({"name": "Amelie", "aliases": ["AMELIE"]}), encoding="utf-8"
        )

        jsonl_path = tmp_path / "candidatos.jsonl"
        _escribir_jsonl(jsonl_path, [
            {"path": "a.jpg", "tipo": "imagen", "ocr_texto": "", "vision": {
                "productora": "amelie", "evento": "", "venue": "",
                "fecha": "", "instagram_handles": [],
            }},
            {"path": "b.jpg", "tipo": "imagen", "ocr_texto": "", "vision": {
                "productora": "Productora Fantasma", "evento": "", "venue": "",
                "fecha": "", "instagram_handles": [],
            }},
        ])

        resultado = mineria_rd.consolidar(str(jsonl_path), repo_root=tmp_path)
        nuevas = resultado["productoras_nuevas"]

        assert len(nuevas) == 1
        assert list(nuevas.values())[0]["nombre"] == "Productora Fantasma"

    def test_no_propone_venue_ya_conocido(self, tmp_path):
        dir_venues = tmp_path / "knowledge" / "venues"
        dir_venues.mkdir(parents=True)
        (dir_venues / "openklub.yaml").write_text(
            "id: openklub\nname: OpenKlub\ntype: club\n", encoding="utf-8"
        )

        jsonl_path = tmp_path / "candidatos.jsonl"
        _escribir_jsonl(jsonl_path, [
            {"path": "a.jpg", "tipo": "imagen", "ocr_texto": "", "vision": {
                "productora": "", "evento": "", "venue": "OpenKlub",
                "fecha": "", "instagram_handles": [],
            }},
            {"path": "b.jpg", "tipo": "imagen", "ocr_texto": "", "vision": {
                "productora": "", "evento": "", "venue": "Bodega Nueva",
                "fecha": "", "instagram_handles": [],
            }},
        ])

        resultado = mineria_rd.consolidar(str(jsonl_path), repo_root=tmp_path)
        nuevos = resultado["venues_nuevos"]

        assert len(nuevos) == 1
        assert list(nuevos.values())[0]["nombre"] == "Bodega Nueva"

    def test_ignora_registros_sin_vision_o_con_error(self, tmp_path):
        jsonl_path = tmp_path / "candidatos.jsonl"
        _escribir_jsonl(jsonl_path, [
            {"path": "a.jpg", "tipo": "imagen", "ocr_texto": "", "vision": None},
            {"path": "b.pdf", "tipo": "pdf", "ocr_texto": "texto", "vision": None},
            {"path": "c.jpg", "tipo": "imagen", "ocr_texto": "", "vision": {"error": "sin_json_en_respuesta", "raw": ""}},
        ])

        resultado = mineria_rd.consolidar(str(jsonl_path), repo_root=tmp_path)
        assert resultado == {"productoras_nuevas": {}, "venues_nuevos": {}}

    def test_jsonl_inexistente_devuelve_vacio(self, tmp_path):
        resultado = mineria_rd.consolidar(str(tmp_path / "no_existe.jsonl"), repo_root=tmp_path)
        assert resultado == {"productoras_nuevas": {}, "venues_nuevos": {}}


# ---------------------------------------------------------------------------
# proponer() -- nunca escribe fuera de outdir, calca el schema real
# ---------------------------------------------------------------------------

class TestProponer:
    def _consolidado_ejemplo(self):
        return {
            "productoras_nuevas": {
                "nueva_productora": {
                    "nombre": "Nueva Productora",
                    "evidencia": 3,
                    "archivos_fuente": ["a.jpg", "b.jpg", "c.jpg"],
                    "instagram_handles": ["@nueva"],
                    "eventos": ["Fiesta 1"],
                }
            },
            "venues_nuevos": {
                "bodega_nueva": {
                    "nombre": "Bodega Nueva",
                    "evidencia": 2,
                    "archivos_fuente": ["a.jpg", "b.jpg"],
                }
            },
        }

    def test_escribe_borradores_con_schema_real(self, tmp_path):
        outdir = tmp_path / "propuestas_mineria"
        mineria_rd.proponer(self._consolidado_ejemplo(), outdir=str(outdir))

        prod_path = outdir / "productoras" / "nueva_productora.json"
        assert prod_path.exists()
        borrador = json.loads(prod_path.read_text(encoding="utf-8"))

        # mismas keys que data/productoras/*.json real
        assert set(borrador.keys()) == {
            "name", "aliases", "instagram", "tipos_fecha", "logos",
            "venues", "confirmed", "fuente_datos", "notes",
        }
        assert borrador["name"] == "Nueva Productora"
        assert borrador["instagram"] == "@nueva"

        venue_path = outdir / "venues" / "bodega_nueva.yaml"
        assert venue_path.exists()
        contenido = venue_path.read_text(encoding="utf-8")
        assert "id:" in contenido and "name:" in contenido
        assert "requirements_defaults: {}" in contenido

        resumen_path = outdir / "RESUMEN.md"
        assert resumen_path.exists()
        assert "Nueva Productora" in resumen_path.read_text(encoding="utf-8")
        assert "Bodega Nueva" in resumen_path.read_text(encoding="utf-8")

    def test_nunca_escribe_fuera_de_outdir(self, tmp_path):
        outdir = tmp_path / "propuestas_mineria"
        consolidado = {
            "productoras_nuevas": {
                "../../fuera": {
                    "nombre": "Traversal",
                    "evidencia": 1,
                    "archivos_fuente": ["a.jpg"],
                    "instagram_handles": [],
                    "eventos": [],
                }
            },
            "venues_nuevos": {},
        }

        # el slug hostil se re-sanitiza; nada se escribe fuera de outdir
        mineria_rd.proponer(consolidado, outdir=str(outdir))

        for p in outdir.rglob("*"):
            assert p.is_relative_to(outdir)

        fuera = tmp_path / "fuera"
        assert not fuera.exists()
        assert not any(tmp_path.glob("*.json"))

    def test_no_toca_data_ni_knowledge_reales(self, tmp_path, monkeypatch):
        # aunque REPO_ROOT real exista, proponer() no debe escribir ahi
        outdir = tmp_path / "propuestas_mineria"
        antes = set(mineria_rd.REPO_ROOT.rglob("*")) if mineria_rd.REPO_ROOT.exists() else set()

        mineria_rd.proponer(self._consolidado_ejemplo(), outdir=str(outdir))

        despues = set(mineria_rd.REPO_ROOT.rglob("*")) if mineria_rd.REPO_ROOT.exists() else set()
        assert antes == despues


# ---------------------------------------------------------------------------
# smoke: consolidar() sobre un jsonl "real" de ejemplo
# ---------------------------------------------------------------------------

def test_smoke_consolidar_fixture(tmp_path):
    jsonl_path = tmp_path / "candidatos.jsonl"
    _escribir_jsonl(jsonl_path, [
        {"path": "RD/FEBRERO/flyer1.jpg", "tipo": "imagen", "ocr_texto": "VIERNES FESTIVAL @cachorros.rd", "vision": {
            "productora": "Cachorros", "evento": "Festival de Verano", "venue": "Espacio Riesco",
            "fecha": "2026-02-20", "instagram_handles": ["@cachorros.rd"],
        }},
        {"path": "RD/FEBRERO/flyer2.jpg", "tipo": "imagen", "ocr_texto": "SABADO @cachorros.rd", "vision": {
            "productora": "Cachorros", "evento": "After Verano", "venue": "Sala Nueva",
            "fecha": "2026-02-21", "instagram_handles": ["@cachorros.rd"],
        }},
        {"path": "RD/FEBRERO/brief.pdf", "tipo": "pdf", "ocr_texto": "cotizacion sin vision", "vision": None},
    ])

    resultado = mineria_rd.consolidar(str(jsonl_path), repo_root=tmp_path)

    assert "Cachorros" in {d["nombre"] for d in resultado["productoras_nuevas"].values()}
    cachorros = next(
        d for d in resultado["productoras_nuevas"].values() if d["nombre"] == "Cachorros"
    )
    assert cachorros["evidencia"] == 2
