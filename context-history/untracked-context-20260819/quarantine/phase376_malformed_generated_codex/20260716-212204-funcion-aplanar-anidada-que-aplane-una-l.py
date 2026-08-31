```python
#!/usr/bin/env python3
"""
Módulo para aplanar listas anidadas de profundidad arbitraria.

Proporciona la función aplanar(seq) que devuelve una nueva lista plana
con todos los elementos no-list en el mismo orden de aparición.
Implementación iterativa con pila explícita para evitar límites de recursión.
"""

import ast
import sys
from typing import Any


def aplanar(seq: list) -> list:
    """
    Aplana una lista que puede contener listas anidadas a cualquier profundidad.

    Args:
        seq: Lista de entrada (debe ser instancia de list o subclase).

    Returns:
        Nueva lista con todos los elementos no-list extraídos en orden.

    Raises:
        TypeError: Si seq no es una instancia de list.

    Comportamiento:
        - No muta la lista de entrada.
        - Trata únicamente instancias de list como contenedores.
        - Otros tipos (tuplas, str, dicts, etc.) se consideran elementos atómicos.
        - Complejidad O(n) donde n es el número total de elementos visitados.
        - Soporta anidamiento muy profundo (implementación iterativa).
    """
    if not isinstance(seq, list):
        raise TypeError(
            f"Se esperaba una lista, pero se recibió {type(seq).__name__}"
        )

    resultado: list = []
    # Pila de iteradores pendientes: cada entrada es un iterador sobre una lista
    pila: list = [iter(seq)]

    while pila:
        try:
            elemento = next(pila[-1])
        except StopIteration:
            # Se terminó la lista actual, volver al nivel superior
            pila.pop()
            continue

        if isinstance(elemento, list):
            # Es una sublista: apilar su iterador para procesarla después
            pila.append(iter(elemento))
        else:
            # Es un elemento atómico: añadir directamente al resultado
            resultado.append(elemento)

    return resultado


def _ejecutar_pruebas() -> None:
    """Ejecuta los casos de prueba con asserts y termina si todos pasan."""
    # Caso 1: anidamiento simple
    assert aplanar([1, [2, 3], 4]) == [1, 2, 3, 4], "Caso 1 falló"

    # Caso 2: tipos mixtos y listas vacías
    entrada2 = ["a", ["b", ["c"]], [1, [2, []]], [[]], 3]
    esperado2 = ["a", "b", "c", 1, 2, 3]
    assert aplanar(entrada2) == esperado2, "Caso 2 falló"

    # Caso 3: profundidad arbitraria (2000 niveles)
    deep: Any = 0
    for _ in range(2000):
        deep = [deep]
    assert aplanar(deep) == [0], "Caso 3 falló"

    # Prueba adicional: no mutar la entrada
    original = [[1, 2], [3, [4, 5]]]
    copia_original = [[1, 2], [3, [4, 5]]]
    resultado = aplanar(original)
    assert original == copia_original, "La entrada fue mutada"
    assert resultado == [1, 2, 3, 4, 5], "Resultado incorrecto en prueba de no mutación"

    # Prueba adicional: TypeError para no-listas
    try:
        aplanar("no soy lista")  # type: ignore[arg-type]
        raise AssertionError("Se esperaba TypeError para str")
    except TypeError:
        pass  # Comportamiento esperado

    try:
        aplanar((1, 2))  # type: ignore[arg-type]
        raise AssertionError("Se esperaba TypeError para tupla")
    except TypeError:
        pass  # Comportamiento esperado

    print("PRUEBAS OK")


def _procesar_cli(expresion: str) -> None:
    """
    Evalúa la expresión como lista con ast.literal_eval,
    aplica aplanar
