import json
import sys

def resumir(archivo):
    preguntas_pendientes = 0
    preguntas_resueltas = 0
    
    with open(archivo, 'r') as f:
        for line in f:
            pregunta = json.loads(line)
            if pregunta['estado'] == 'pendiente':
                preguntas_pendientes += 1
            elif pregunta['estado'] == 'resuelta':
                preguntas_resueltas += 1
    
    resumen = "# Resumen\n\n"
    resumen += f"* Preguntas pendientes: {preguntas_pendientes}\n"
    if preguntas_pendientes > 0:
        resumen += "* Estado:\n"
        resumen += f"  * Pendiente: {preguntas_pendientes}\n"
    if preguntas_resueltas > 0:
        resumen += f"  * Resuelta: {preguntas_resueltas}\n"
    
    return resumen.strip()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python resumidor.py <archivo_backlog>")
        sys.exit(1)
    archivo = sys.argv[1]
    salida = resumir(archivo)
    print(salida)
    
    # Casos de prueba autoverificados
    try:
        assert resumir("backlog_vacio.jsonl") == "# Resumen\n\n* Preguntas pendientes: 0\n* Estado:\n"
        assert resumir("backlog_una_pregunta.jsonl") == "# Resumen\n\n* Preguntas pendientes: 1\n* Estado:\n  * Pendiente: 1\n"
        assert resumir("backlog_varias_preguntas.jsonl") == "# Resumen\n\n* Preguntas pendientes: 2\n* Estado:\n  * Pendiente: 2\n"
        print("PRUEBAS OK")
    except AssertionError as e:
        print(f"ERROR en las pruebas: {e}")
