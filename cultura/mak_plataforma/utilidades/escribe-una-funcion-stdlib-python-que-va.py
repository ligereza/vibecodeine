def validate_dmx_range(start: int, end: int) -> tuple[int, int]:
    if not isinstance(start, int):
        raise ValueError("start ({} is not an integer)".format(start))
    if not isinstance(end, int):
        raise ValueError("end ({} is not an integer)".format(end))
    if start < 1 or start > 512:
        raise ValueError("start ({}) fuera de rango 1..512".format(start))
    if end < 1 or end > 512:
        raise ValueError("end ({}) fuera de rango 1..512".format(end))
    if start > end:
        raise ValueError("start ({}) > end ({})".format(start, end))
    return (start, end)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Uso: python dmx_range.py START END", file=sys.stderr)
        sys.exit(1)
    
    try:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    except ValueError as e:
        print("Error al parsear los argumentos: {}".format(e), file=sys.stderr)
        sys.exit(1)
    
    try:
        result = validate_dmx_range(start, end)
        print("Rango válido: {}-{}".format(result[0], result[1]))
        sys.exit(0)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
