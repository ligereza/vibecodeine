#!/usr/bin/env python3
"""
backlog_codex.py - Simula generación de codex pieces desde un backlog.
Uso: python backlog_codex.py --take N --parallel P --provider NAME [--backlog-size M]
"""

import argparse
import itertools
import math
import sys
from typing import Iterator, List, Dict, Tuple, Any

# ----------------------------------------------------------------------
# Funciones públicas
# ----------------------------------------------------------------------

def chunk(iterable: Any, n: int) -> Iterator[List[Any]]:
    """
    Divide un iterable en lotes de tamaño n (el último puede ser menor).
    """
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            break
        yield batch

def generate_codex(
    backlog: List[str],
    take: int,
    parallel: int,
    provider: str
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Toma hasta `take` items del inicio de `backlog`, los agrupa en batches
    de tamaño <= parallel, y devuelve (generated_items, remaining_backlog).
    Cada item generado es un dict con 'id', 'provider' y 'batch'.
    """
    # Tomar los primeros `take` elementos
    selected = backlog[:take]
    remaining = backlog[take:]

    generated: List[Dict[str, Any]] = []
    batch_number = 0
    for batch in chunk(selected, parallel):
        for item_id in batch:
            generated.append({
                'id': item_id,
                'provider': provider,
                'batch': batch_number
            })
        batch_number += 1

    return generated, remaining

def run_self_tests() -> None:
    """Ejecuta los tres casos de prueba con asserts."""
    # Test 1: reducción simple, preserva orden y batching
    backlog1 = ['a','b','c','d','e','f','g','h','i','j']
    gen1, rem1 = generate_codex(backlog1, take=4, parallel=2, provider='groq')
    assert len(gen1) == 4, f"Test1: len(gen1) esperado 4, obtenido {len(gen1)}"
    assert len(rem1) == 6, f"Test1: len(rem1) esperado 6, obtenido {len(rem1)}"
    assert [it['id'] for it in gen1] == ['a','b','c','d'], f"Test1: ids incorrectos"
    assert all(it['provider'] == 'groq' for it in gen1), "Test1: provider incorrecto"
    # Verificar batches: batch 0: ['a','b'], batch 1: ['c','d']
    assert gen1[0]['batch'] == 0 and gen1[1]['batch'] == 0, "Test1: batch 0 mal"
    assert gen1[2]['batch'] == 1 and gen1[3]['batch'] == 1, "Test1: batch 1 mal"
    assert all(it['batch'] in (0,1) for it in gen1), "Test1: batch fuera de rango"
    # Verificar tamaños de batch <= parallel
    for batch_num in set(it['batch'] for it in gen1):
        items_in_batch = [it for it in gen1 if it['batch'] == batch_num]
        assert len(items_in_batch) <= 2, f"Test1: batch {batch_num} tamaño {len(items_in_batch)} > 2"

    # Test 2: take > backlog
    backlog2 = ['x','y','z']
    gen2, rem2 = generate_codex(backlog2, take=5, parallel=3, provider='groq')
    assert len(gen2) == 3, f"Test2: len(gen2) esperado 3, obtenido {len(gen2)}"
    assert len(rem2) == 0, f"Test2: len(rem2) esperado 0, obtenido {len(rem2)}"
    assert [it['id'] for it in gen2] == ['x','y','z'], f"Test2: ids incorrectos"

    # Test 3: batch size límite
    backlog3 = ['1','2','3','4','5']
    gen3, rem3 = generate_codex(backlog3, take=5, parallel=4, provider='groq')
    assert len(gen3) == 5, f"Test3: len(gen3) esperado 5, obtenido {len(gen3)}"
    # Verificar batches: batch 0 tamaño 4, batch 1 tamaño 1
    batches = {}
    for it in gen3:
        batches.setdefault(it['batch'], []).append(it['id'])
    assert len(batches) == 2, f"Test3: se esperaban 2 batches, obtenidos {len(batches)}"
    assert len(batches[0]) == 4, f"Test3: batch 0 tamaño esperado 4, obtenido {len(batches[0])}"
    assert len(batches[1]) == 1, f"Test3: batch 1 tamaño esperado 1, obtenido {len(batches[1])}"
    for batch_num, items in batches.items():
        assert len(items) <= 4, f"Test3: batch {batch_num} tamaño {len(items)} > 4"
    assert all(it['provider'] == 'groq' for it in gen3), "Test3: provider incorrecto"

# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simula generación de codex pieces desde un backlog."
    )
    parser.add_argument('--take', type=int, required=True,
                        help='Cantidad de items a generar')
    parser.add_argument('--parallel', type=int, required=True,
                        help='Tamaño máximo de cada batch')
    parser.add_argument('--provider', type=str, required=True,
                        help='Proveedor a etiquetar')
    parser.add_argument('--backlog-size', type=int, default=10,
                        help='Tamaño inicial del backlog generado automáticamente (default: 10)')
    args = parser.parse_args()

    # Construir backlog automático
    backlog = [f'item-{i+1}' for i in range(args.backlog_size)]

    # Generar codex
    generated, remaining = generate_codex(
        backlog, args.take, args.parallel, args.provider
    )

    # Resumen por stdout
    print(f"Generados: {len(generated)}")
    print(f"Backlog restante: {len(remaining)}")
    print("Items generados:")
    for item in generated:
        print(repr(item))

if __name__ == "__main__":
    # Ejecutar pruebas automáticas
    run_self_tests()
    print("PRUEBAS OK")
    # Solo ejecutar CLI si se proporcionaron argumentos
    if len(sys.argv) > 1:
        main()
