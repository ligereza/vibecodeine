#!/usr/bin/env python3
"""test_mak_backlog.py -- tests para backlog.py (pytest)."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Agregar el directorio del backlog al path
test_dir = Path(__file__).parent
proyecto_dir = test_dir.parent
sys.path.insert(0, str(proyecto_dir / "cultura" / "mak_plataforma"))

import backlog


class TestNormYHash:
    """Tests para _norm y _hash."""

    def test_norm_lowercase(self):
        """_norm convierte a lowercase."""
        assert backlog._norm("HOLA") == "hola"

    def test_norm_removes_accents(self):
        """_norm quita accents."""
        assert backlog._norm("ÁÉÍÓÚ") == "aeiou"
        assert backlog._norm("ñ") == "n"

    def test_norm_collapses_whitespace(self):
        """_norm colapsa whitespace."""
        assert backlog._norm("  hola   mundo  ") == "hola mundo"

    def test_hash_length(self):
        """_hash retorna 12 caracteres."""
        h = backlog._hash("pregunta")
        assert len(h) == 12
        assert all(c in "0123456789abcdef" for c in h)

    def test_hash_deterministic(self):
        """_hash es deterministico."""
        h1 = backlog._hash("pregunta")
        h2 = backlog._hash("pregunta")
        assert h1 == h2

    def test_hash_insensitive_to_norm_differences(self):
        """_hash ignora case/accents."""
        h1 = backlog._hash("Pregunta")
        h2 = backlog._hash("pregunta")
        h3 = backlog._hash("PREGUNTA")
        assert h1 == h2 == h3


class TestParsearLagunas:
    """Tests para parsear_lagunas."""

    def test_basic_bullets_dash(self):
        """Parsea bullets con '-'."""
        texto = """
## LAGUNAS DE INFORMACION
- pregunta uno
- pregunta dos
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas) == 2
        assert "pregunta uno" in preguntas
        assert "pregunta dos" in preguntas

    def test_basic_bullets_star(self):
        """Parsea bullets con '*'."""
        texto = """
## LAGUNAS DE INFORMACION
* pregunta uno
* pregunta dos
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas) == 2

    def test_basic_bullets_numbered(self):
        """Parsea bullets numerados."""
        texto = """
## LAGUNAS DE INFORMACION
1. primera pregunta
2. segunda pregunta
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas) == 2
        assert "primera pregunta" in preguntas

    def test_header_variant_plain_line(self):
        """Parsea con linea plain 'LAGUNAS DE INFORMACION'."""
        texto = """
LAGUNAS DE INFORMACION
- pregunta uno
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas) == 1
        assert "pregunta uno" in preguntas

    def test_section_ends_at_next_header(self):
        """La seccion termina en el proximo header."""
        texto = """
## LAGUNAS DE INFORMACION
- pregunta uno
- pregunta dos
## SIGUIENTE SECCION
- esto no se parsea
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas) == 2
        assert "esto no se parsea" not in preguntas

    def test_section_ends_at_eof(self):
        """La seccion termina en EOF si no hay header."""
        texto = """
## LAGUNAS DE INFORMACION
- pregunta uno
- pregunta dos"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas) == 2

    def test_no_section_returns_empty(self):
        """Sin seccion LAGUNAS retorna []."""
        texto = """
## OTRA SECCION
- pregunta uno
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert preguntas == []

    def test_ignores_empty_lines(self):
        """Ignora lineas vacias entre bullets."""
        texto = """
## LAGUNAS DE INFORMACION
- pregunta uno

- pregunta dos
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas) == 2

    def test_strips_whitespace_from_questions(self):
        """Strip whitespace de preguntas."""
        texto = """
## LAGUNAS DE INFORMACION
-   pregunta uno
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert preguntas[0] == "pregunta uno"

    def test_caps_at_300_chars(self):
        """Pregunta se capea a 300 caracteres."""
        pregunta_larga = "a" * 400
        texto = f"""
## LAGUNAS DE INFORMACION
- {pregunta_larga}
"""
        preguntas = backlog.parsear_lagunas(texto)
        assert len(preguntas[0]) == 300


class TestCargarYGuardar:
    """Tests para cargar y guardar_append."""

    def test_cargar_empty_file(self, tmp_path):
        """cargar archivo vacio retorna []."""
        f = tmp_path / "backlog.jsonl"
        f.write_text("")
        assert backlog.cargar(str(f)) == []

    def test_cargar_valid_jsonl(self, tmp_path):
        """cargar lee jsonl valido."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1"},
            {"id": "bl-2", "pregunta": "p2"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))
        cargadas = backlog.cargar(str(f))
        assert len(cargadas) == 2
        assert cargadas[0]["id"] == "bl-1"

    def test_cargar_skips_corrupt_lines(self, tmp_path):
        """cargar salta lineas corruptas silenciosamente."""
        f = tmp_path / "backlog.jsonl"
        contenido = """{"id":"bl-1","pregunta":"p1"}
esto no es json valido
{"id":"bl-2","pregunta":"p2"}"""
        f.write_text(contenido)
        cargadas = backlog.cargar(str(f))
        assert len(cargadas) == 2
        assert cargadas[0]["id"] == "bl-1"
        assert cargadas[1]["id"] == "bl-2"

    def test_cargar_nonexistent_file(self, tmp_path):
        """cargar archivo inexistente retorna []."""
        f = tmp_path / "noexiste.jsonl"
        assert backlog.cargar(str(f)) == []

    def test_guardar_append_creates_parent_dir(self, tmp_path):
        """guardar_append crea directorio padre si no existe."""
        f = tmp_path / "subdir" / "backlog.jsonl"
        entradas = [{"id": "bl-1", "pregunta": "p1"}]
        backlog.guardar_append(str(f), entradas)
        assert f.exists()
        assert json.loads(f.read_text().split("\n")[0])["id"] == "bl-1"

    def test_guardar_append_appends(self, tmp_path):
        """guardar_append agrega lineas."""
        f = tmp_path / "backlog.jsonl"
        e1 = [{"id": "bl-1", "pregunta": "p1"}]
        e2 = [{"id": "bl-2", "pregunta": "p2"}]
        backlog.guardar_append(str(f), e1)
        backlog.guardar_append(str(f), e2)
        contenido = f.read_text()
        assert "bl-1" in contenido
        assert "bl-2" in contenido


class TestCosechar:
    """Tests para cosechar."""

    def test_cosechar_basic(self, tmp_path):
        """cosechar extrae lagunas de .md y agrega al backlog."""
        informes_dir = tmp_path / "informes"
        informes_dir.mkdir()

        informe = informes_dir / "test.md"
        informe.write_text("""
# Informe Test
## LAGUNAS DE INFORMACION
- pregunta uno
- pregunta dos
""")

        backlog_path = tmp_path / "backlog.jsonl"
        n = backlog.cosechar([str(informes_dir)], str(backlog_path))

        assert n == 2
        entradas = backlog.cargar(str(backlog_path))
        assert len(entradas) == 2
        assert all(e["estado"] == "pendiente" for e in entradas)

    def test_cosechar_respects_max_por_informe(self, tmp_path):
        """cosechar respeta max_por_informe."""
        informes_dir = tmp_path / "informes"
        informes_dir.mkdir()

        informe = informes_dir / "test.md"
        informe.write_text("""
## LAGUNAS DE INFORMACION
- p1
- p2
- p3
- p4
- p5
""")

        backlog_path = tmp_path / "backlog.jsonl"
        n = backlog.cosechar([str(informes_dir)], str(backlog_path), max_por_informe=2)

        assert n == 2

    def test_cosechar_skips_already_processed(self, tmp_path):
        """cosechar salta archivos ya procesados (por mtime)."""
        informes_dir = tmp_path / "informes"
        informes_dir.mkdir()

        informe = informes_dir / "test.md"
        informe.write_text("""
## LAGUNAS DE INFORMACION
- pregunta uno
""")

        backlog_path = tmp_path / "backlog.jsonl"

        # Primera cosecha
        n1 = backlog.cosechar([str(informes_dir)], str(backlog_path))
        assert n1 == 1

        # Segunda cosecha del mismo archivo (mismo mtime)
        n2 = backlog.cosechar([str(informes_dir)], str(backlog_path))
        assert n2 == 0

        # Verificar que el backlog solo tiene 1 entrada
        entradas = backlog.cargar(str(backlog_path))
        assert len(entradas) == 1

    def test_cosechar_dedup_by_hash(self, tmp_path):
        """cosechar dedup por _hash()."""
        informes_dir = tmp_path / "informes"
        informes_dir.mkdir()

        # Primer informe con pregunta
        informe1 = informes_dir / "informe1.md"
        informe1.write_text("""
## LAGUNAS DE INFORMACION
- pregunta de prueba
""")

        backlog_path = tmp_path / "backlog.jsonl"
        n1 = backlog.cosechar([str(informes_dir)], str(backlog_path))
        assert n1 == 1

        # Segundo informe con misma pregunta (diferente case/accents)
        informe2 = informes_dir / "informe2.md"
        informe2.write_text("""
## LAGUNAS DE INFORMACION
- Pregunta de Prueba
""")

        # Borrar estado para permitir re-procesar el segundo archivo
        estado_path = str(backlog_path) + ".estado.json"
        if os.path.exists(estado_path):
            os.remove(estado_path)

        n2 = backlog.cosechar([str(informes_dir)], str(backlog_path))
        assert n2 == 0  # Dedup por hash

    def test_cosechar_creates_estado_file(self, tmp_path):
        """cosechar crea archivo de estado."""
        informes_dir = tmp_path / "informes"
        informes_dir.mkdir()

        informe = informes_dir / "test.md"
        informe.write_text("## LAGUNAS DE INFORMACION\n- p1")

        backlog_path = tmp_path / "backlog.jsonl"
        backlog.cosechar([str(informes_dir)], str(backlog_path))

        estado_path = str(backlog_path) + ".estado.json"
        assert os.path.exists(estado_path)


class TestDerivador:
    """Tests para derivar."""

    def test_derivar_basic(self):
        """derivar construye entrada hijo con linaje."""
        padre = {
            "id": "bl-parent",
            "pregunta": "papa",
            "linaje": []
        }
        hijo = backlog.derivar(padre, "nueva pregunta")

        assert hijo is not None
        assert hijo["linaje"] == ["bl-parent"]
        assert hijo["pregunta"] == "nueva pregunta"
        assert hijo["estado"] == "pendiente"

    def test_derivar_depth_1(self):
        """derivar con linaje de profundidad 1."""
        padre = {
            "id": "bl-1",
            "pregunta": "p",
            "linaje": ["bl-0"]
        }
        hijo = backlog.derivar(padre, "nueva")

        assert hijo is not None
        assert hijo["linaje"] == ["bl-0", "bl-1"]

    def test_derivar_depth_2(self):
        """derivar con linaje de profundidad 2 falla (llega a 3)."""
        padre = {
            "id": "bl-2",
            "pregunta": "p",
            "linaje": ["bl-0", "bl-1"]
        }
        hijo = backlog.derivar(padre, "nueva")

        # El linaje seria ["bl-0", "bl-1", "bl-2"], que tiene len 3
        # Por contrato, profundidad_max=3 significa que si len(linaje) >= 3, rechaza
        # Espera: revisar la semantica. "profundidad de linaje capada en 3" significa
        # que el linaje puede tener hasta 3 elementos.
        # Entonces derivar debe retornar None si ya tiene 3.
        assert hijo is None


class TestPopPendiente:
    """Tests para pop_pendiente."""

    def test_pop_pendiente_empty(self, tmp_path):
        """pop_pendiente en backlog vacio retorna None."""
        f = tmp_path / "backlog.jsonl"
        f.write_text("")
        assert backlog.pop_pendiente(str(f)) is None

    def test_pop_pendiente_selects_highest_score(self, tmp_path):
        """pop_pendiente selecciona mayor score."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 0.5, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-2", "pregunta": "p2", "score": 1.0, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-3", "pregunta": "p3", "score": 0.2, "estado": "pendiente", "fecha": "2026-01-01"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        seleccionada = backlog.pop_pendiente(str(f))
        assert seleccionada["id"] == "bl-2"

    def test_pop_pendiente_tiebreak_oldest(self, tmp_path):
        """pop_pendiente desempata con mas vieja (menor fecha)."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 1.0, "estado": "pendiente", "fecha": "2026-01-02"},
            {"id": "bl-2", "pregunta": "p2", "score": 1.0, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-3", "pregunta": "p3", "score": 1.0, "estado": "pendiente", "fecha": "2026-01-03"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        seleccionada = backlog.pop_pendiente(str(f))
        assert seleccionada["id"] == "bl-2"

    def test_pop_pendiente_marks_en_curso(self, tmp_path):
        """pop_pendiente marca como en_curso."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 1.0, "estado": "pendiente", "fecha": "2026-01-01"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        backlog.pop_pendiente(str(f))

        cargadas = backlog.cargar(str(f))
        assert cargadas[0]["estado"] == "en_curso"

    def test_pop_pendiente_ignores_non_pendiente(self, tmp_path):
        """pop_pendiente solo considera pendiente."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 1.0, "estado": "listo", "fecha": "2026-01-01"},
            {"id": "bl-2", "pregunta": "p2", "score": 0.5, "estado": "pendiente", "fecha": "2026-01-01"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        seleccionada = backlog.pop_pendiente(str(f))
        assert seleccionada["id"] == "bl-2"


class TestMarcar:
    """Tests para marcar."""

    def test_marcar_updates_estado(self, tmp_path):
        """marcar cambia el estado."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "estado": "pendiente"}
        ]
        f.write_text(json.dumps(entradas[0]))

        resultado = backlog.marcar(str(f), "bl-1", "listo")
        assert resultado is True

        cargadas = backlog.cargar(str(f))
        assert cargadas[0]["estado"] == "listo"

    def test_marcar_nonexistent_id(self, tmp_path):
        """marcar id inexistente retorna False."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "estado": "pendiente"}
        ]
        f.write_text(json.dumps(entradas[0]))

        resultado = backlog.marcar(str(f), "bl-999", "listo")
        assert resultado is False

    def test_marcar_multiple_entries(self, tmp_path):
        """marcar solo cambia la entrada especificada."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "estado": "pendiente"},
            {"id": "bl-2", "pregunta": "p2", "estado": "pendiente"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        backlog.marcar(str(f), "bl-1", "listo")

        cargadas = backlog.cargar(str(f))
        assert cargadas[0]["estado"] == "listo"
        assert cargadas[1]["estado"] == "pendiente"


class TestCurar:
    """Tests para curar."""

    def test_curar_no_action_if_under_limit(self, tmp_path):
        """curar no hace nada si pendientes <= max."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 1.0, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-2", "pregunta": "p2", "score": 0.5, "estado": "pendiente", "fecha": "2026-01-01"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        n = backlog.curar(str(f), max_pendientes=10)
        assert n == 0

    def test_curar_discards_excess_lowest_score(self, tmp_path):
        """curar descarta el exceso (scores mas bajos)."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 0.1, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-2", "pregunta": "p2", "score": 0.9, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-3", "pregunta": "p3", "score": 0.5, "estado": "pendiente", "fecha": "2026-01-01"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        n = backlog.curar(str(f), max_pendientes=2)
        assert n == 1

        cargadas = backlog.cargar(str(f))
        descartadas = [e for e in cargadas if e["estado"] == "descartado"]
        assert len(descartadas) == 1
        assert descartadas[0]["id"] == "bl-1"

    def test_curar_with_rankear_callable(self, tmp_path):
        """curar aplica rankear si se proporciona."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 0.0, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-2", "pregunta": "p2", "score": 0.0, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-3", "pregunta": "p3", "score": 0.0, "estado": "pendiente", "fecha": "2026-01-01"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        def rankear_mock(preguntas):
            # Retorna scores inversamente correlacionados con posicion
            return [0.9, 0.5, 0.1]

        n = backlog.curar(str(f), rankear=rankear_mock, max_pendientes=2)
        assert n == 1

        cargadas = backlog.cargar(str(f))
        # El de menor score es el 3 (score 0.1)
        descartadas = [e for e in cargadas if e["estado"] == "descartado"]
        assert len(descartadas) == 1
        assert descartadas[0]["id"] == "bl-3"

    def test_curar_never_deletes_entries(self, tmp_path):
        """curar nunca borra entradas, solo marca."""
        f = tmp_path / "backlog.jsonl"
        entradas = [
            {"id": "bl-1", "pregunta": "p1", "score": 0.1, "estado": "pendiente", "fecha": "2026-01-01"},
            {"id": "bl-2", "pregunta": "p2", "score": 0.9, "estado": "pendiente", "fecha": "2026-01-01"}
        ]
        f.write_text("\n".join(json.dumps(e) for e in entradas))

        backlog.curar(str(f), max_pendientes=1)

        cargadas = backlog.cargar(str(f))
        # Ambas entradas siguen existiendo
        assert len(cargadas) == 2


class TestIntegration:
    """Tests de integracion."""

    def test_full_workflow(self, tmp_path):
        """Workflow completo: cosechar -> pop -> marcar -> curar."""
        # Cosechar
        informes_dir = tmp_path / "informes"
        informes_dir.mkdir()

        informe = informes_dir / "test.md"
        informe.write_text("""
## LAGUNAS DE INFORMACION
- pregunta uno
- pregunta dos
- pregunta tres
""")

        backlog_path = tmp_path / "backlog.jsonl"
        n_cosechadas = backlog.cosechar([str(informes_dir)], str(backlog_path))
        assert n_cosechadas == 3

        # Pop una
        entry = backlog.pop_pendiente(str(backlog_path))
        assert entry["estado"] == "en_curso" or entry["estado"] == "pendiente"
        # Pop la actualiza a en_curso
        cargadas = backlog.cargar(str(backlog_path))
        en_curso = [e for e in cargadas if e["estado"] == "en_curso"]
        assert len(en_curso) == 1

        # Marcar como listo
        backlog.marcar(str(backlog_path), en_curso[0]["id"], "listo")

        # Verificar
        cargadas = backlog.cargar(str(backlog_path))
        listos = [e for e in cargadas if e["estado"] == "listo"]
        pendientes = [e for e in cargadas if e["estado"] == "pendiente"]
        assert len(listos) == 1
        assert len(pendientes) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
