"""
util‑csv‑to‑md.py — Convierte datos CSV simples (coma, sin comillas ni escapes)
a una tabla Markdown bien formada.

Uso como módulo:
    from util_csv_to_md import csv_to_md
    tabla = csv_to_md("Nombre,Edad\nAna,30\nLuis,25")

Uso como CLI:
    python util-csv-to-md.py [--no-header] [ruta_entrada]
"""

import sys
from typing import List


def _parsear_lineas(csv_text: str) -> List[List[str]]:
    """Divide el texto CSV en una lista de filas, cada una lista de celdas."""
    lineas = csv_text.strip().splitlines()
    if not lineas:
        raise ValueError("El texto CSV está vacío.")
    filas = [linea.split(",") for linea in lineas]
    # Validar que todas las filas tengan la misma cantidad de columnas
    num_columnas = len(filas[0])
    for i, fila in enumerate(filas, start=1):
        if len(fila) != num_columnas:
            raise ValueError(
                f"Fila {i} tiene {len(fila)} columnas, "
                f"pero se esperaban {num_columnas} (número de columnas inconsistente)."
            )
    return filas


def _formatear_tabla(filas: List[List[str]], header: bool) -> str:
    """Construye la tabla Markdown a partir de las filas ya validadas."""
    # Determinar anchos máximos por columna para alinear correctamente
    anchos = [0] * len(filas[0])
    for fila in filas:
        for j, celda in enumerate(fila):
            anchos[j] = max(anchos[j], len(celda))

    def _formatear_fila(fila: List[str]) -> str:
        celdas = [f" {celda.ljust(anchos[j])} " for j, celda in enumerate(fila)]
        return "|" + "|".join(celdas) + "|"

    resultado = []
    if header:
        # Primera fila como encabezado
        resultado.append(_formatear_fila(filas[0]))
        # Línea separadora
        separadores = ["-" * (ancho + 2) for ancho in anchos]  # +2 por los espacios
        resultado.append("|" + "|".join(separadores) + "|")
        # Resto de filas como datos
        for fila in filas[1:]:
            resultado.append(_formatear_fila(fila))
    else:
        # Sin encabezado: todas las filas son datos, pero igual generamos separador
        # (aunque no haya encabezado, la especificación pide línea separadora)
        resultado.append(_formatear_fila(filas[0]))
        separadores = ["-" * (ancho + 2) for ancho in anchos]
        resultado.append("|" + "|".join(separadores) + "|")
        for fila in filas[1:]:
            resultado.append(_formatear_fila(fila))

    return "\n".join(resultado) + "\n"


def csv_to_md(csv_text: str, *, header: bool = True) -> str:
    """
    Convierte una cadena CSV en una tabla Markdown.

    Parámetros:
        csv_text: Texto CSV con comas como separador, sin comillas ni escapes.
        header: Si es True (por defecto), la primera fila se usa como encabezado.
                Si es False, todas las filas se tratan como datos.

    Retorna:
        Cadena con la tabla en formato Markdown.

    Lanza:
        ValueError: Si las filas tienen distinto número de columnas.
    """
    filas = _parsear_lineas(csv_text)
    return _formatear_tabla(filas, header)


def _main_cli() -> None:
    """Punto de entrada para la interfaz de línea de comandos."""
    args = sys.argv[1:]
    no_header = False
    ruta_entrada = None

    # Procesar argumentos
    for arg in args:
        if arg in ("-h", "--no-header"):
            no_header = True
        else:
            if ruta_entrada is not None:
                print("Error: Demasiados argumentos. Uso: python util-csv-to-md.py [--no-header] [ruta_entrada]",
                      file=sys.stderr)
                sys.exit(2)
            ruta_entrada = arg

    # Leer entrada
    if ruta_entrada is None:
        csv_text = sys.stdin.read()
    else:
        try:
            with open(ruta_entrada, "r", encoding="utf-8") as f:
                csv_text = f.read()
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado: {ruta_entrada}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error al leer archivo: {e}", file=sys.stderr)
            sys.exit(1)

    # Convertir y mostrar
    try:
        resultado = csv_to_md(csv_text, header=not no_header)
        sys.stdout.write(resultado)
    except ValueError as e:
        print(f"Error de formato CSV: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Si se invoca con argumentos, actuar como CLI
    if len(sys.argv) > 1:
        _main_cli()
    else:
        # Sin argumentos: ejecutar casos de prueba auto‑verificados
        # 1️⃣ CSV con encabezado explícito
        csv1 = "Nombre,Edad,País\nAlice,30,España\nBob,25,México"
        md1 = (
            "| Nombre | Edad | País |\n"
            "|--------|------|------|\n"
            "| Alice  | 30   | España |\n"
            "| Bob    | 25   | México |\n"
        )
        assert csv_to_md(csv1) == md1

        # 2️⃣ CSV sin encabezado (header=False)
        csv2 = "A,1\nB,2\nC,3"
        md2 = (
            "| A | 1 |\n"
            "|---|---|\n"
            "| B | 2 |\n"
            "| C | 3 |\n"
        )
        assert csv_to_md(csv2, header=False) == md2

        # 3️⃣ CSV con filas de longitud desigual → error
        csv3 = "X,Y\n1,2,3\n4,5"
        try:
            csv_to_md(csv3)
        except ValueError as e:
            assert "número de columnas" in str(e)
        else:
            raise AssertionError("Se esperaba ValueError por filas desiguales")

        print("PRUEBAS OK")
