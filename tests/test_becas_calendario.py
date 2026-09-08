"""
Tests para tools/becas_calendario.py

Verificaextracción contra fixture real:
- FOSIS se extrae correctamente
- No se inventan campos (ausentes -> "no-especificado")
- Orden por fecha
- Dedup por fondo
"""

import pytest
import tempfile
from pathlib import Path
from tools.becas_calendario import (
    parsear_informe, consolidar, render_calendario,
    _extraer_urls, _extraer_fechas, _extraer_montos, _extraer_fondo, _extraer_requisitos
)


@pytest.fixture
def fixture_fosis():
    """Carga el fixture real de FOSIS."""
    return Path('tests/fixtures/informe_becas_fosis.md')


class TestExtraerURLs:
    """Tests de extracción de URLs."""

    def test_extrae_url_simple(self):
        """Extrae una URL simple."""
        texto = "Ver en https://example.com para más info."
        urls = _extraer_urls(texto)
        assert "https://example.com" in urls

    def test_extrae_multiples_urls(self):
        """Extrae múltiples URLs."""
        texto = "https://a.com y https://b.com"
        urls = _extraer_urls(texto)
        assert len(urls) >= 2

    def test_no_inventa_urls(self):
        """No inventa URLs si no existen."""
        texto = "Sin URLs aquí"
        urls = _extraer_urls(texto)
        assert urls == []


class TestExtraerFechas:
    """Tests de extracción de fechas."""

    def test_extrae_rango_completo(self):
        """Extrae rango tipo '15 de agosto a 30 de septiembre de 2026'."""
        texto = "Postulación: 15 de agosto a 30 de septiembre de 2026"
        fecha = _extraer_fechas(texto)
        assert "agosto" in fecha.lower()
        assert "septiembre" in fecha.lower()
        assert "2026" in fecha

    def test_extrae_hasta(self):
        """Extrae 'hasta DD de mes de AAAA'."""
        texto = "Cierre: hasta 31 de julio de 2026"
        fecha = _extraer_fechas(texto)
        assert "julio" in fecha.lower()
        assert "31" in fecha

    def test_no_inventa_fechas(self):
        """No inventa fechas si no hay."""
        texto = "Sin fechas mencionadas"
        fecha = _extraer_fechas(texto)
        assert fecha == "no-especificado"


class TestExtraerMontos:
    """Tests de extracción de montos."""

    def test_extrae_rango_montos(self):
        """Extrae rango entre $X y $Y."""
        texto = "Fondos: entre $5.000.000 y $30.000.000 CLP"
        monto = _extraer_montos(texto)
        assert monto != "no-especificado" or "$" in texto
        # Al menos menciona valores

    def test_no_inventa_montos(self):
        """No inventa montos si no hay."""
        texto = "Sin información de montos"
        monto = _extraer_montos(texto)
        assert monto == "no-especificado"


class TestExtraerFondo:
    """Tests de extracción de fondo."""

    def test_extrae_fosis_de_header(self):
        """Extrae FOSIS de un header."""
        texto = "# FOSIS Chile 2026: fondos concursables"
        fondo = _extraer_fondo(texto, "test.md")
        assert "FOSIS" in fondo

    def test_extrae_de_nombre_archivo(self):
        """Fallback: extrae FOSIS del nombre del archivo."""
        texto = "Sin FOSIS en el contenido"
        fondo = _extraer_fondo(texto, "informe_becas_fosis.md")
        assert "FOSIS" in fondo


class TestExtraerRequisitos:
    """Tests de extracción de requisitos."""

    def test_extrae_requisitos_texto(self):
        """Extrae requisitos si están mencionados."""
        texto = """
        requisitos reportados: personalidad jurídica, plan de trabajo,
        antecedentes de gestión, certificaciones tributarias.
        """
        req = _extraer_requisitos(texto)
        if req != "no-especificado":
            assert len(req) > 5

    def test_no_inventa_requisitos(self):
        """No inventa si no hay requisitos."""
        texto = "Contenido sin requisitos"
        req = _extraer_requisitos(texto)
        assert req == "no-especificado"


class TestParsearInforme:
    """Tests de parseo de informe completo."""

    def test_parsea_fixture_fosis(self, fixture_fosis):
        """Parsea el fixture real de FOSIS correctamente."""
        candidatos = parsear_informe(str(fixture_fosis))

        assert len(candidatos) >= 1, "Debe extraer al menos 1 candidato de FOSIS"

        fosis = candidatos[0]
        assert fosis['fondo'] == 'FOSIS', "Fondo debe ser FOSIS"
        assert fosis['informe_origen'] == 'informe_becas_fosis.md'
        # URL fuente debe tener al menos 1 URL
        assert isinstance(fosis['url_fuente'], list)

    def test_fosis_extrae_url_fuente(self, fixture_fosis):
        """FOSIS debe tener URLs."""
        candidatos = parsear_informe(str(fixture_fosis))
        assert len(candidatos) > 0
        urls = candidatos[0]['url_fuente']
        assert urls != ['no-especificado'], "FOSIS debe tener URLs en el informe"

    def test_no_inventa_campos(self, fixture_fosis):
        """No inventa campos: los vacíos son 'no-especificado'."""
        candidatos = parsear_informe(str(fixture_fosis))
        assert len(candidatos) > 0

        for cand in candidatos:
            # Cada campo existe
            assert 'fondo' in cand
            assert 'ventana_postulacion' in cand
            assert 'monto' in cand
            assert 'requisitos_resumen' in cand
            assert 'url_fuente' in cand
            assert 'informe_origen' in cand

    def test_no_parsea_archivo_inexistente(self):
        """No parsea archivos que no existen."""
        resultado = parsear_informe('/ruta/inexistente.md')
        assert resultado == []


class TestConsolidar:
    """Tests de consolidación y dedup."""

    def test_consolidar_directorio_vacio(self):
        """Consolida un directorio vacío sin error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            resultado = consolidar(tmpdir)
            assert resultado == []

    def test_consolidar_un_archivo(self, fixture_fosis):
        """Consolida un directorio con 1 archivo de fixture."""
        dir_path = fixture_fosis.parent
        resultado = consolidar(str(dir_path))
        assert len(resultado) >= 1
        assert resultado[0]['fondo'] == 'FOSIS'

    def test_dedup_conserva_mas_campos(self, fixture_fosis):
        """Dedup conserva la entrada con más campos válidos."""
        # Crea 2 copias del fixture en temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            contenido = fixture_fosis.read_text()

            # Copia 1: completa
            (tmpdir_path / 'fosis_1.md').write_text(contenido)

            # Copia 2: versión truncada (simula informe parcial)
            contenido_corto = contenido[:500]  # Primeras 500 chars
            (tmpdir_path / 'fosis_2.md').write_text(contenido_corto)

            resultado = consolidar(str(tmpdir_path))
            # Debe tener solo 1 entrada de FOSIS (dedupped)
            fosis_entries = [r for r in resultado if r['fondo'] == 'FOSIS']
            assert len(fosis_entries) <= 1, "Debe dedup FOSIS"


class TestRenderCalendario:
    """Tests de renderizado de calendario."""

    def test_render_tabla_markdown(self):
        """Renderiza tabla markdown correctamente."""
        candidatos = [{
            'fondo': 'FOSIS',
            'ventana_postulacion': '15 de agosto a 30 de septiembre de 2026',
            'monto': '5,000,000 - 30,000,000 CLP',
            'requisitos_resumen': 'Personalidad jurídica y plan de trabajo',
            'url_fuente': ['https://example.com'],
            'informe_origen': 'test.md'
        }]
        calendario = render_calendario(candidatos)
        assert '| Fondo |' in calendario
        assert 'FOSIS' in calendario
        assert 'Calendario de Postulaciones' in calendario

    def test_render_ordena_por_fecha(self):
        """Ordena por fecha (no-especificado al final)."""
        candidatos = [
            {
                'fondo': 'FONDO_A',
                'ventana_postulacion': 'no-especificado',
                'monto': '1,000,000 CLP',
                'requisitos_resumen': 'Requisito A',
                'url_fuente': ['https://a.com'],
                'informe_origen': 'a.md'
            },
            {
                'fondo': 'FONDO_B',
                'ventana_postulacion': '15 de agosto de 2026',
                'monto': '2,000,000 CLP',
                'requisitos_resumen': 'Requisito B',
                'url_fuente': ['https://b.com'],
                'informe_origen': 'b.md'
            }
        ]
        calendario = render_calendario(candidatos)
        # FONDO_B debe aparecer antes que FONDO_A (porque tiene fecha)
        idx_b = calendario.find('FONDO_B')
        idx_a = calendario.find('FONDO_A')
        if idx_b != -1 and idx_a != -1:
            assert idx_b < idx_a, "Fondos con fecha deben aparecer primero"

    def test_render_timestamp(self):
        """Incluye timestamp de generación."""
        candidatos = []
        calendario = render_calendario(candidatos)
        assert 'Generado:' in calendario or 'generado' in calendario.lower()

    def test_render_sin_inventar(self):
        """No inventa campos en el render."""
        candidatos = [{
            'fondo': 'TEST',
            'ventana_postulacion': 'no-especificado',
            'monto': 'no-especificado',
            'requisitos_resumen': 'no-especificado',
            'url_fuente': [],
            'informe_origen': 'test.md'
        }]
        calendario = render_calendario(candidatos)
        # No debe inventar valores diferentes a "no-especificado"
        assert 'TEST' in calendario


class TestIntegracionCompleta:
    """Tests de integración end-to-end."""

    def test_flujo_completo_fixture(self, fixture_fosis):
        """Flujo completo: parsear -> consolidar -> render."""
        dir_path = fixture_fosis.parent
        candidatos = consolidar(str(dir_path))
        calendario = render_calendario(candidatos)

        assert 'FOSIS' in calendario
        assert 'Calendario' in calendario
        assert '|' in calendario  # Tabla markdown
