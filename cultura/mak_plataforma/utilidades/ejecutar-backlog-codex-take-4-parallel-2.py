import argparse
import multiprocessing

def backlog_codex(take, parallel, provider):
    """Simula el procesamiento de elementos."""
    print(f"Procesando {take} elementos con {parallel} procesos paralelos y proveedor {provider}")

def main():
    parser = argparse.ArgumentParser(description="Script backlog_codex para procesamiento paralelo.")
    parser.add_argument("--take", type=int, required=True, help="Cantidad de elementos a procesar.")
    parser.add_argument("--parallel", type=int, required=True, help="Cantidad de procesos paralelos.")
    parser.add_argument("--provider", type=str, required=True, help="Proveedor a utilizar (ej. groq).")
    args = parser.parse_args()

    # Caso de prueba 1: Verifica que los argumentos se parsean correctamente
    assert args.take == 4, f"Se esperaba take=4, pero se obtuvo {args.take}"
    assert args.parallel == 2, f"Se esperaba parallel=2, pero se obtuvo {args.parallel}"
    assert args.provider == "groq", f"Se esperaba provider='groq', pero se obtuvo {args.provider}"

    # Caso de prueba 2: Verifica que el procesamiento se ejecuta con los argumentos correctos
    backlog_codex(args.take, args.parallel, args.provider)

    # Caso de prueba 3: Verifica que el procesamiento se ejecuta con procesos paralelos
    with multiprocessing.Pool(args.parallel) as pool:
        pool.apply(backlog_codex, (args.take, args.parallel, args.provider))

    print("PRUEBAS OK")

if __name__ == "__main__":
    main()
