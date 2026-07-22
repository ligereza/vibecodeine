"""
Validador de archivos JSON.

Proporciona una función para validar si una cadena JSON es parseable
y reporta la línea y columna del primer error si no lo es.
"""

import json
import sys


def validate_json(json_str: str):
    """
    Valida si una cadena es JSON válido.

    Args:
        json_str: Cadena de texto a validar como JSON.

    Returns:
        True si el JSON es válido.
        (False, línea, columna) si el JSON es inválido, indicando la posición del primer error.
    """
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError as e:
        return False, e.lineno, e.colno


def _ejecutar_pruebas():
    """Ejecuta los casos de prueba definidos en la especificación."""
    casos_de_prueba = [
        ('{"nombre": "Juan", "edad": 30}', True),
        ("{nombre: Juan, edad: 30}", (False, 1, 2)),
        ('{"nombre": "Juan", "edad": 30, "otro": ¡hola!}', (False, 1, 34)),
    ]

    for json_str, resultado_esperado in casos_de_prueba:
        resultado = validate_json(json_str)
        assert resultado == resultado_esperado, (
            f"Error en caso de prueba: {json_str!r}\n"
            f"  Esperado: {resultado_esperado}\n"
            f"  Obtenido: {resultado}"
        )

    print("PRUEBAS OK")


def _cli():
    """
    Interfaz de línea de comandos.
    Uso: python json_validator.py <ruta_al_archivo_json>
    """
    if len(sys.argv) != 2:
        print("Uso: python json_validator.py <ruta_al_archivo_json>", file=sys.stderr)
        sys.exit(1)

    ruta_archivo = sys.argv[1]
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado: {ruta_archivo}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error al leer el archivo: {e}", file=sys.stderr)
        sys.exit(1)

    resultado = validate_json(contenido)
    if resultado is True:
        print("True")
    else:
        _, linea, columna = resultado
        print(f"False, línea {linea}, columna {columna}")


if __name__ == "__main__":
    # Si se pasa un argumento, se usa como archivo; si no, se ejecutan las pruebas.
    if len(sys.argv) > 1:
        _cli()
    else:
        _formar_pruebas()
