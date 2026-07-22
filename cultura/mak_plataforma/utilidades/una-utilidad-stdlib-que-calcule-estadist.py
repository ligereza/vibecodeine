#!/usr/bin/env python3
"""
Script para calcular estadísticas básicas de una columna numérica de un CSV.
Uso: python script.py [--delimiter DELIM] [--header] [--column COL] PATH
"""

import csv
import io
import json
import math
import sys
from typing import Optional, Union, TextIO, List


def compute_csv_column_stats(
    fileobj: Union[TextIO, io.StringIO],
    column: Union[int, str] = 0,
    delimiter: str = ',',
    has_header: bool = False
) -> dict:
    """
    Calcula estadísticas (min, max, mean, median) de una columna numérica de un CSV.

    Args:
        fileobj: objeto con .read() o iterable de líneas (archivo abierto o StringIO).
        column: índice 0-based (int) o nombre de columna (str) si has_header=True.
        delimiter: delimitador de campos (por defecto ',').
        has_header: si True, la primera línea se interpreta como cabecera.

    Returns:
        dict con claves 'min', 'max', 'mean', 'median' y valores float o None si no hay datos.
    """
    reader = csv.reader(fileobj, delimiter=delimiter)
    values: List[float] = []
    header = None

    if has_header:
        try:
            header = next(reader)
        except StopIteration:
            # Archivo vacío
            return {'min': None, 'max': None, 'mean': None, 'median': None}

        if isinstance(column, str):
            try:
                col_index = header.index(column)
            except ValueError:
                raise ValueError(f"Columna '{column}' no encontrada en la cabecera: {header}")
        else:
            col_index = column
    else:
        col_index = column

    for row in reader:
        if col_index < len(row):
            try:
                val = float(row[col_index])
                values.append(val)
            except (ValueError, IndexError):
                # Ignorar valores no numéricos o filas incompletas
                pass

    if not values:
        return {'min': None, 'max': None, 'mean': None, 'median': None}

    sorted_vals = sorted(values)
    n = len(sorted_vals)
    min_val = sorted_vals[0]
    max_val = sorted_vals[-1]
    mean_val = sum(sorted_vals) / n

    if n % 2 == 1:
        median_val = sorted_vals[n // 2]
    else:
        median_val = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

    return {
        'min': min_val,
        'max': max_val,
        'mean': mean_val,
        'median': median_val
    }


def main_cli():
    """Función principal para la CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Calcula estadísticas de una columna numérica de un CSV."
    )
    parser.add_argument(
        '--delimiter', '-d', default=',',
        help="Delimitador de campos (por defecto ',')"
    )
    parser.add_argument(
        '--header', '-H', action='store_true',
        help="Indica que el CSV tiene cabecera"
    )
    parser.add_argument(
        '--column', '-c', default='0',
        help="Columna a analizar: índice (0-based) o nombre si --header está activo"
    )
    parser.add_argument(
        'path',
        help="Ruta al archivo CSV, o '-' para leer desde stdin"
    )

    args = parser.parse_args()

    # Determinar el tipo de columna
    if args.header:
        # Si hay header, el usuario puede pasar un nombre o un índice como string
        try:
            col = int(args.column)
        except ValueError:
            col = args.column  # nombre
    else:
        col = int(args.column)

    # Abrir archivo o stdin
    if args.path == '-':
        fileobj = sys.stdin
    else:
        fileobj = open(args.path, 'r', newline='')

    try:
        stats = compute_csv_column_stats(
            fileobj,
            column=col,
            delimiter=args.delimiter,
            has_header=args.header
        )
    finally:
        if args.path != '-':
            fileobj.close()

    # Salida JSON
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    # --- Pruebas internas ---
    import io
    import math

    # Caso A: CSV sin header, selección por índice (par)
    entrada_a = "1,2,3\n4,5,6\n"
    stats_a = compute_csv_column_stats(io.StringIO(entrada_a), column=1, delimiter=',', has_header=False)
    esperado_a = {'min': 2.0, 'max': 5.0, 'mean': 3.5, 'median': 3.5}
    for key in esperado_a:
        assert math.isclose(esperado_a[key], stats_a[key], rel_tol=1e-9), f"Caso A: {key} no coincide"

    # Caso B: CSV con header, delimitador ';', selección por nombre
    entrada_b = "a;b;c\n1.0;2.5;3.0\n4.0;5.5;6.0\n"
    stats_b = compute_csv_column_stats(io.StringIO(entrada_b), column='b', delimiter=';', has_header=True)
    esperado_b = {'min': 2.5, 'max': 5.5, 'mean': 4.0, 'median': 4.0}
    for key in esperado_b:
        assert math.isclose(esperado_b[key], stats_b[key], rel_tol=1e-9), f"Caso B: {key} no coincide"

    # Caso C: CSV una columna, cantidad impar (incluye negativo)
    entrada_c = "v\n-1\n0\n1\n"
    stats_c = compute_csv_column_stats(io.StringIO(entrada_c), column=0, delimiter=',', has_header=True)
    esperado_c = {'min': -1.0, 'max': 1.0, 'mean': 0.0, 'median': 0.0}
    for key in esperado_c:
        assert math.isclose(esperado_c[key], stats_c[key], rel_tol=1e-9), f"Caso C: {key} no coincide"

    # Prueba adicional: lista vacía
    entrada_vacia = "a,b\n"
    stats_vacia = compute_csv_column_stats(io.StringIO(entrada_vacia), column='a', delimiter=',', has_header=True)
    assert stats_vacia == {'min': None, 'max': None, 'mean': None, 'median': None}, "Caso vacío falló"

    print("PRUEBAS OK")
