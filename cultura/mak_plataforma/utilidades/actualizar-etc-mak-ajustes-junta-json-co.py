import json
import subprocess
import sys
from unittest.mock import patch, mock_open, call

def main(provider_weights, last_action_ts):
    # Actualizar /etc/mak/ajustes_junta.json
    with open('/etc/mak/ajustes_junta.json', 'w') as f:
        json.dump({'provider_weights': provider_weights, 'last_action_ts': last_action_ts}, f)

    # Recargar cadena de proveedores
    subprocess.run(['cadena_de_proveedores', 'reload', '--config', '/etc/mak/ajustes_junta.json'])

    # Crear /etc/cron.d/mak_provider_failover
    with open('/etc/cron.d/mak_provider_failover', 'w') as f:
        f.write('*/5 * * * * root /opt/mak/bin/provider_health_check --config /etc/mak/ajustes_junta.json --threshold 60 --action reload\n')

    # Lanzar backlog_codex
    subprocess.run(['backlog_codex', 'enqueue', 'auto_review_batch', '--provider=cerebras', '--parallel=4', '--limit=13', '--target_pct=80', '--timeout=600s'])

    # Registrar en ajustes_junta.json
    with open('/etc/mak/ajustes_junta.json', 'r+') as f:
        data = json.load(f)
        data['last_maintenance'] = 'auto_review_launch'
        f.seek(0)
        json.dump(data, f)
        f.truncate()

    # Refrescar cadena de proveedores
    subprocess.run(['cadena_de_proveedores', 'refresh'])

if __name__ == '__main__':
    # --- Casos de prueba ---
    def test_caso_1():
        """Parámetros válidos con pesos y timestamp correctos."""
        provider_weights = {"cerebras": 0.60, "azure": 0.30, "groq": 0.10, "searxng": 0.00}
        last_action_ts = "2026-07-20T15:46:05Z"

        with patch('builtins.open', mock_open()) as mocked_open, \
             patch('subprocess.run') as mocked_run:

            main(provider_weights, last_action_ts)

            # Verificar que se abrieron los archivos esperados
            open_calls = [call('/etc/mak/ajustes_junta.json', 'w'),
                          call('/etc/cron.d/mak_provider_failover', 'w'),
                          call('/etc/mak/ajustes_junta.json', 'r+')]
            mocked_open.assert_has_calls(open_calls, any_order=True)

            # Verificar que se llamó a subprocess.run tres veces
            assert mocked_run.call_count == 3

            # Verificar contenido del primer dump
            handle = mocked_open()
            handle.write.assert_any_call('*/5 * * * * root /opt/mak/bin/provider_health_check --config /etc/mak/ajustes_junta.json --threshold 60 --action reload\n')

    def test_caso_2():
        """provider_weights vacío (diccionario vacío)."""
        provider_weights = {}
        last_action_ts = "2026-07-20T15:46:05Z"

        with patch('builtins.open', mock_open()) as mocked_open, \
             patch('subprocess.run') as mocked_run:

            main(provider_weights, last_action_ts)

            # Verificar que se escribió el JSON con el diccionario vacío
            handle = mocked_open()
            # El primer open es para escritura, luego el tercero es para lectura/escritura
            # No podemos verificar el contenido exacto del dump fácilmente, pero podemos verificar que se llamó a json.dump
            # En su lugar, verificamos que no haya excepciones y que se llamen los subprocess
            assert mocked_run.call_count == 3

    def test_caso_3():
        """last_action_ts con formato diferente (sin 'Z')."""
        provider_weights = {"cerebras": 1.0}
        last_action_ts = "2026-07-20T15:46:05"

        with patch('builtins.open', mock_open()) as mocked_open, \
             patch('subprocess.run') as mocked_run:

            main(provider_weights, last_action_ts)

            # Verificar que se ejecutaron los comandos
            expected_calls = [
                call(['cadena_de_proveedores', 'reload', '--config', '/etc/mak/ajustes_junta.json']),
                call(['backlog_codex', 'enqueue', 'auto_review_batch', '--provider=cerebras', '--parallel=4', '--limit=13', '--target_pct=80', '--timeout=600s']),
                call(['cadena_de_proveedores', 'refresh'])
            ]
            mocked_run.assert_has_calls(expected_calls, any_order=False)

    # Ejecutar las pruebas
    test_caso_1()
    test_caso_2()
    test_caso_3()

    print("PRUEBAS OK")
