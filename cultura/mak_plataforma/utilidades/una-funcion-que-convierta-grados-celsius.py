#!/usr/bin/env python3
"""
Conversor de grados Celsius a Fahrenheit.

Uso:
    python c_to_f.py [CELSIUS]

Sin argumentos ejecuta pruebas automáticas.
Con un argumento numérico imprime la conversión.
"""

import sys


def celsius_to_fahrenheit(c: float) -> float:
    """
    Convierte grados Celsius a Fahrenheit.

    Args:
        c: Temperatura en grados Celsius (int o float).

    Returns:
        Temperatura en grados Fahrenheit como float.

    Raises:
        TypeError: Si el argumento no es numérico.
    """
    if not isinstance(c, (int, float)):
        raise TypeError(
            f"Se esperaba un número (int o float), pero se recibió {type(c).__name__}"
        )
    return c * 9.0 / 5.0 + 32.0


def _ejecutar_pruebas() -> None:
    """Ejecuta las pruebas de autoverificación con asserts."""
    # Prueba 1: 0 °C -> 32 °F
    assert celsius_to_fahrenheit(0) == 32.0, "Fallo: 0 °C debe ser 32.0 °F"

    # Prueba 2: 100 °C -> 212 °F
    assert celsius_to_fahrenheit(100) == 212.0, "Fallo: 100 °C debe ser 212.0 °F"

    # Prueba 3: -40 °C -> -40 °F
    assert celsius_to_fahrenheit(-40) == -40.0, "Fallo: -40 °C debe ser -40.0 °F"

    # Prueba adicional: verificar que se lanza TypeError con entrada no numérica
    try:
        celsius_to_fahrenheit("no_numérico")
        raise AssertionError("Fallo: Debería haber lanzado TypeError")
    except TypeError:
        pass  # Comportamiento esperado

    print("PRUEBAS OK")


def main() -> None:
    """Punto de entrada principal del script."""
    if len(sys.argv) == 1:
        # Sin argumentos: ejecutar pruebas
        _ejecutar_pruebas()
    elif len(sys.argv) == 2:
        # Un argumento: intentar convertir
        try:
            celsius = float(sys.argv[1])
            resultado = celsius_to_fahrenheit(celsius)
            print(resultado)
        except ValueError:
            print(
                f"Error: '{sys.argv[1]}' no es un número válido.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print("Uso: python c_to_f.py [CELSIUS]", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
