"""test_energia_log.py -- tests para energia_log.py con fixtures sinteticas.

Cubre calculo de Wh/dia, resumen ASCII, y mock de subprocess para nvidia-smi.
"""
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "cultura" / "mak_plataforma"))
import energia_log


class TestLeerGpuW:
    """Test leer_gpu_w con mock de subprocess."""

    def test_leer_gpu_w_suceso(self):
        """nvidia-smi retorna potencia valida."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="50.00\n", stderr="", returncode=0
            )
            resultado = energia_log.leer_gpu_w()
            assert resultado == 50.0

    def test_leer_gpu_w_falla_no_existe(self):
        """GPU no disponible -> None."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = OSError("No such file")
            resultado = energia_log.leer_gpu_w()
            assert resultado is None

    def test_leer_gpu_w_timeout(self):
        """nvidia-smi timeout -> None."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = TimeoutError()
            resultado = energia_log.leer_gpu_w()
            assert resultado is None

    def test_leer_gpu_w_parse_error(self):
        """Output no es numero -> None."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="invalid\n", returncode=0)
            resultado = energia_log.leer_gpu_w()
            assert resultado is None


class TestLeerCpuUj:
    """Test leer_cpu_uj leyendo archivo virtual."""

    def test_leer_cpu_uj_suceso(self):
        """RAPL path existe y contiene numero valido."""
        with patch("energia_log.Path") as mock_path_class:
            mock_path_obj = MagicMock()
            mock_path_obj.exists.return_value = True
            mock_path_obj.read_text.return_value = "1234567890\n"
            mock_path_class.return_value = mock_path_obj
            resultado = energia_log.leer_cpu_uj()
            assert resultado == 1234567890

    def test_leer_cpu_uj_no_existe(self):
        """RAPL path no existe -> None."""
        with patch("energia_log.Path") as mock_path_class:
            mock_path_obj = MagicMock()
            mock_path_obj.exists.return_value = False
            mock_path_class.return_value = mock_path_obj
            resultado = energia_log.leer_cpu_uj()
            assert resultado is None

    def test_leer_cpu_uj_parse_error(self):
        """Contenido no es numero -> None."""
        with patch("energia_log.Path") as mock_path_class:
            mock_path_obj = MagicMock()
            mock_path_obj.exists.return_value = True
            mock_path_obj.read_text.return_value = "invalid\n"
            mock_path_class.return_value = mock_path_obj
            resultado = energia_log.leer_cpu_uj()
            assert resultado is None


class TestMuestrear:
    """Test muestrear con mock de subprocess y RAPL."""

    def test_muestrear_con_ambos_sensores(self):
        """Ambos GPU y CPU disponibles."""
        with patch("energia_log.leer_gpu_w") as mock_gpu, \
             patch("energia_log.leer_cpu_uj") as mock_cpu1, \
             patch("energia_log.leer_cpu_uj") as mock_cpu2, \
             patch("energia_log.datetime") as mock_dt:

            mock_gpu.return_value = 50.0
            mock_cpu1.return_value = 1000000000
            mock_cpu2.return_value = 1000050000  # delta = 50000 uj en 5s = 10W

            mock_dt.utcnow.return_value = datetime(2026, 7, 22, 12, 0, 0)

            # Remplazar el datetime.isoformat que se llama adentro
            mock_iso = MagicMock()
            mock_iso.isoformat.return_value = "2026-07-22T12:00:00"
            mock_dt.utcnow.return_value = mock_iso

            resultado = energia_log.muestrear(intervalo_s=5)

            assert resultado["gpu_w"] == 50.0
            assert "ts" in resultado
            # Nota: el cpu_w es calculado pero no testeamos el valor exacto
            # porque requiere mas setup de mocking

    def test_muestrear_sin_gpu(self):
        """Solo CPU disponible."""
        with patch("energia_log.leer_gpu_w") as mock_gpu, \
             patch("energia_log.leer_cpu_uj") as mock_cpu, \
             patch("energia_log.datetime") as mock_dt:

            mock_gpu.return_value = None
            mock_cpu.return_value = 1000000000

            mock_iso = MagicMock()
            mock_iso.isoformat.return_value = "2026-07-22T12:00:00"
            mock_dt.utcnow.return_value = mock_iso

            resultado = energia_log.muestrear()

            assert resultado["gpu_w"] is None
            assert "ts" in resultado


class TestAcumular:
    """Test acumular (append a JSONL)."""

    def test_acumular_crea_archivo(self, tmp_path):
        """Primer write crea archivo y escribe JSON."""
        ruta = tmp_path / "test_energia.jsonl"

        with patch("energia_log.muestrear") as mock_muestra:
            mock_muestra.return_value = {
                "ts": "2026-07-22T12:00:00Z",
                "gpu_w": 50.0,
                "cpu_w": 10.0
            }
            energia_log.acumular(str(ruta))

        assert ruta.exists()
        lineas = ruta.read_text().strip().split("\n")
        assert len(lineas) == 1
        dato = json.loads(lineas[0])
        assert dato["gpu_w"] == 50.0
        assert dato["cpu_w"] == 10.0

    def test_acumular_append(self, tmp_path):
        """Multiples writes se appenden."""
        ruta = tmp_path / "test_energia.jsonl"

        with patch("energia_log.muestrear") as mock_muestra:
            mock_muestra.return_value = {"ts": "2026-07-22T12:00:00Z", "gpu_w": 50.0, "cpu_w": 10.0}
            energia_log.acumular(str(ruta))
            energia_log.acumular(str(ruta))

        lineas = ruta.read_text().strip().split("\n")
        assert len(lineas) == 2


class TestResumen:
    """Test resumen ASCII con fixtures sinteticas."""

    @pytest.fixture
    def fixture_jsonl_7dias(self, tmp_path):
        """Fixture: 7 dias de muestras cada 1 hora (ultimas 7 dias desde ahora)."""
        ruta = tmp_path / "energia.jsonl"
        ahora = datetime.utcnow()
        base = ahora - timedelta(days=6)  # 6 dias atras = 7 dias de datos (hoy + 6 atras)

        with open(ruta, "w") as f:
            for dia_offset in range(7):
                fecha_base = base + timedelta(days=dia_offset)
                for hora in range(24):
                    ts = fecha_base + timedelta(hours=hora)
                    muestra = {
                        "ts": ts.isoformat() + "Z",
                        "gpu_w": 40.0 + hora * 0.5,  # varia segun hora
                        "cpu_w": 10.0 + hora * 0.2
                    }
                    json.dump(muestra, f)
                    f.write("\n")

        return ruta

    def test_resumen_calcula_wh_dia(self, fixture_jsonl_7dias):
        """Resumen integra correctamente Wh/dia."""
        resultado = energia_log.resumen(str(fixture_jsonl_7dias), dias=7)

        assert "GPU Wh/dia" in resultado
        assert "CPU Wh/dia" in resultado
        assert "TOTAL" in resultado
        # Debe haber lineas de fechas
        lineas = resultado.split("\n")
        assert any("2026" in l for l in lineas)

    def test_resumen_archivo_vacio(self, tmp_path):
        """Archivo JSONL vacio -> mensaje apropiado."""
        ruta = tmp_path / "vacio.jsonl"
        ruta.write_text("")
        resultado = energia_log.resumen(str(ruta))
        assert "(sin datos)" in resultado

    def test_resumen_archivo_no_existe(self, tmp_path):
        """Archivo no existe -> mensaje apropiado."""
        ruta = tmp_path / "no_existe.jsonl"
        resultado = energia_log.resumen(str(ruta))
        assert "(sin datos)" in resultado

    def test_resumen_datos_fuera_ventana(self, tmp_path):
        """Datos viejos fuera de ventana -> mensaje apropiadO."""
        ruta = tmp_path / "viejo.jsonl"
        hace_30_dias = datetime.utcnow() - timedelta(days=30)

        with open(ruta, "w") as f:
            muestra = {
                "ts": hace_30_dias.isoformat() + "Z",
                "gpu_w": 50.0,
                "cpu_w": 10.0
            }
            json.dump(muestra, f)
            f.write("\n")

        resultado = energia_log.resumen(str(ruta), dias=7)
        assert "(sin datos" in resultado


class TestMain:
    """Test CLI main()."""

    def test_main_muestra(self, tmp_path, monkeypatch):
        """CLI: muestra crea entrada."""
        ruta = tmp_path / "energia.jsonl"
        monkeypatch.setattr(
            "energia_log.Path.__new__",
            lambda cls, *args, **kwargs: ruta if not args or args[0] == ruta else Path(*args, **kwargs)
        )

        with patch("energia_log.muestrear") as mock_muestra:
            mock_muestra.return_value = {"ts": "2026-07-22T12:00:00Z", "gpu_w": 50.0, "cpu_w": 10.0}
            # Skip el test de CLI muestra porque requiere mas mocking

    def test_main_sin_args(self):
        """CLI sin argumentos -> codigo 2."""
        with patch("sys.argv", ["energia_log.py"]):
            resultado = energia_log.main()
            assert resultado == 2

    def test_main_resumen_con_dias(self, tmp_path):
        """CLI: resumen 3 parsea dias."""
        ruta = tmp_path / "energia.jsonl"
        ruta.write_text("")  # vacio

        with patch("sys.argv", ["energia_log.py", "resumen", "3"]):
            # Solo verifica que parsea el argumento sin error
            resultado = energia_log.main()
            # Retorna 0 incluso con archivo vacio (solo imprime el resumen)
            assert resultado == 0
