#!/usr/bin/env python3
"""
osc_encode.py - Codifica un mensaje OSC 1.0 con un único argumento float32.

Uso como módulo:
    from osc_encode import encode
    mensaje = encode("/direccion", 3.14)

Uso como CLI:
    python osc_encode.py "/direccion" 3.14 > mensaje.bin
    python osc_encode.py -h  # muestra ayuda
"""

import argparse
import struct
import sys


def encode(address: str, value: float) -> bytes:
    """
    Codifica un mensaje OSC con una dirección y un único argumento float32.

    Parámetros
    ----------
    address : str
        Ruta OSC (p. ej. "/synth/freq").
    value : float
        Valor a codificar como float32.

    Retorna
    -------
    bytes
        Mensaje OSC binario listo para enviarse por UDP/TCP.
    """
    # --- Dirección (string ASCII terminada en NUL y alineada a 4 bytes) ---
    addr_bytes = address.encode('ascii') + b'\x00'
    # Calcular padding necesario para que la longitud total sea múltiplo de 4
    addr_padding = (4 - len(addr_bytes) % 4) % 4
    addr_padded = addr_bytes + b'\x00' * addr_padding

    # --- Type tag (siempre ",f" terminado en NUL y alineado a 4 bytes) ---
    type_tag = b',f\x00'
    type_padding = (4 - len(type_tag) % 4) % 4
    type_padded = type_tag + b'\x00' * type_padding

    # --- Valor float32 en big-endian ---
    float_bytes = struct.pack('>f', value)

    # --- Mensaje completo ---
    return addr_padded + type_padded + float_bytes


def main():
    parser = argparse.ArgumentParser(
        description="Genera un paquete OSC 1.0 con dirección y un float32."
    )
    parser.add_argument(
        "address",
        type=str,
        nargs="?",
        help="Ruta OSC (ej. /synth/freq)"
    )
    parser.add_argument(
        "value",
        type=float,
        nargs="?",
        help="Valor numérico a codificar como float32"
    )
    args = parser.parse_args()

    if args.address is None or args.value is None:
        parser.print_help()
        # Si no hay argumentos, ejecutar auto-tests
        if args.address is None and args.value is None:
            run_tests()
        sys.exit(0)

    mensaje = encode(args.address, args.value)
    sys.stdout.buffer.write(mensaje)


def run_tests():
    """Ejecuta tres casos de prueba con assert."""
    # 1. Dirección sencilla, valor positivo
    msg1 = encode("/test", 1.0)
    assert msg1 == b'/test\x00\x00\x00' + b',f\x00\x00' + b'\x3f\x80\x00\x00', \
        "Fallo test 1"

    # 2. Dirección con varios niveles, valor negativo
    msg2 = encode("/a/b/c", -2.5)
    # "/a/b/c\0" = 7 bytes, padding 1 -> 8 bytes total
    assert msg2 == b'/a/b/c\x00\x00' + b',f\x00\x00' + b'\xc0\x20\x00\x00', \
        "Fallo test 2"

    # 3. Dirección de longitud múltiplo de 4 (no padding), valor cero
    msg3 = encode("/four", 0.0)
    # "/four\0" = 6 bytes, padding 2 -> 8 bytes total
    assert msg3 == b'/four\x00\x00\x00' + b',f\x00\x00' + b'\x00\x00\x00\x00', \
        "Fallo test 3"

    print("PRUEBAS OK")


if __name__ == "__main__":
    main()
