#!/usr/bin/env python3
"""
Utilidad para calcular tasas de éxito de jobs por modo en una ventana de tiempo.
Lee un archivo JSON Lines (jobs.jsonl) y reporta estadísticas de éxito por modo.
"""

import argparse
import json
import sys
import tempfile
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone


def parse_iso8601(s: str) -> datetime:
    """
    Convierte una cadena ISO8601/RFC3339 a datetime timezone-aware UTC.
    
    Args:
        s: Cadena con timestamp en formato ISO8601 (soporta sufijo 'Z').
    
    Returns:
        datetime con zona horaria UTC.
    
    Raises:
        ValueError: Si la cadena no tiene un formato válido.
    """
    # Reemplazar 'Z' por '+00:00' para compatibilidad con fromisoformat
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    
    dt = datetime.fromisoformat(s)
    
    # Si no tiene zona horaria, asumir UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convertir a UTC para consistencia
    return dt.astimezone(timezone.utc)


def compute_success_rates(path: str, window_hours: int = 24, now: datetime | None = None) -> dict:
    """
    Calcula tasas de éxito por modo para jobs en una ventana de tiempo.
    
    Args:
        path: Ruta al archivo JSON Lines con los jobs.
        window_hours: Ventana de tiempo en horas hacia atrás desde 'now'.
        now: Timestamp de referencia (por defecto: ahora en UTC).
    
    Returns:
        Diccionario con estructura: {mode: (success_count, total_count, success_rate)}
        donde success_rate es un float entre 0.0 y 1.0.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    
    # Asegurar que now es timezone-aware UTC
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)
    
    cutoff = now - timedelta(hours=window_hours)
    
    # Contadores por modo: {mode: [success_count, total_count]}
    stats = defaultdict(lambda: [0, 0])
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    job = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Advertencia: línea {line_num} no es JSON válido, ignorando.", file=sys.stderr)
                    continue
                
                # Validar campos requeridos
                if not all(k in job for k in ('timestamp', 'mode', 'status')):
                    print(f"Advertencia: línea {line_num} no tiene campos requeridos (timestamp, mode, status), ignorando.",
                          file=sys.stderr)
                    continue
                
                try:
                    ts = parse_iso8601(job['timestamp'])
                except ValueError as e:
                    print(f"Advertencia: línea {line_num} timestamp inválido '{job['timestamp']}': {e}, ignorando.",
                          file=sys.stderr)
                    continue
                
                # Verificar si está dentro de la ventana
                if ts < cutoff or ts > now:
                    continue
                
                mode = job['mode']
                counts[mode][1] += 1  # total_count
                
                if job['status'].lower() == 'success':
                    counts[mode][0] += 1  # success_count
    
    except FileNotFoundError:
        print(f"Error: archivo no encontrado '{path}'.", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error inesperado al procesar '{path}': {e}", file=sys.stderr)
        return {}
    
    # Calcular tasas
    result = {}
    for mode, (success, total) in counts.items():
        rate = success / total if total > 0 else 0.0
        result[mode] = (success, total, rate)
    
    return result


def run_self_tests():
    """Ejecuta casos de prueba con asserts para verificar el comportamiento."""
    now = datetime.fromisoformat("2026-01-02T12:00:00+00:00")
    
    # Caso A: mezcla dentro/fuera de ventana
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        f.write('{"timestamp":"2026-01-02T11:00:00Z","mode":"m1","status":"success"}\n')
        f.write('{"timestamp":"2026-01-02T10:00:00Z","mode":"m1","status":"failure"}\n')
        f.write('{"timestamp":"2026-01-01T11:00:00Z","mode":"m1","status":"success"}\n')
        temp_path = f.name
    
    try:
        result = compute_success_rates(temp_path, window_hours=24, now=now)
        assert result == {"m1": (1, 2, 0.5)}, f"Caso A falló: {result}"
    finally:
        os.unlink(temp_path)
    
    # Caso B: modo solo fallos
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        f.write('{"timestamp":"2026-01-02T09:00:00Z","mode":"m2","status":"failure"}\n')
        f.write('{"timestamp":"2026-01-02T08:00:00Z","mode":"m2","status":"failure"}\n')
        temp_path = f.name
    
    try:
        result = compute_success_rates(temp_path, window_hours=24, now=now)
        assert result == {"m2": (0, 2, 0.0)}, f"Caso B falló: {result}"
    finally:
        os.unlink(temp_path)
    
    # Caso C: sin eventos en ventana
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        f.write('{"timestamp":"2026-01-01T00:00:00Z","mode":"m3","status":"success"}\n')
        temp_path = f.name
    
    try:
        result = compute_success_rates(temp_path, window_hours=24, now=now)
        assert result == {}, f"Caso C falló: {result}"
    finally:
        os.unlink(temp_path)
    
    print("PRUEBAS OK")


def main():
    """Función principal con CLI."""
    parser = argparse.ArgumentParser(
        description="Calcula tasa de éxito por modo en jobs.jsonl para una ventana de tiempo."
    )
    parser.add_argument(
        '--file', default='./jobs.jsonl',
        help='Ruta al archivo jobs.jsonl (default: ./jobs.jsonl)'
    )
    parser.add_argument(
        '--window', type=int, default=24,
        help='Ventana de tiempo en horas (default: 24)'
    )
    parser.add_argument(
        '--now', type=str, default=None,
        help='Timestamp de referencia ISO8601 (útil para pruebas)'
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Emitir salida en formato JSON'
    )
    
    args = parser.parse_args()
    
    # Determinar now
    if args.now:
        try:
            now = parse_iso8601(args.now)
        except ValueError as e:
            print(f"Error: timestamp '--now' inválido: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        now = datetime.now(timezone.utc)
    
    # Calcular tasas
    rates = compute_success_rates(args.file, window_hours=args.window, now=now)
    
    if args.json:
        # Formato JSON
        output = {}
        for mode, (success, total, rate) in rates.items():
            output[mode] = {
                "success": success,
                "total": total,
                "rate": rate
            }
        print(json.dumps(output, indent=2))
    else:
        # Formato texto legible
        if not rates:
            print("No hay datos en la ventana de tiempo especificada.")
        else:
            for mode in sorted(rates.keys()):
                success, total, rate = rates[mode]
                percentage = rate * 100
                print(f"{mode} {success}/{total} ({percentage:.1f}%)")


if __name__ == "__main__":
    import sys
    
    # Ejecutar self-tests primero
    run_self_tests()
    
    # Luego ejecutar CLI normal
    main()
