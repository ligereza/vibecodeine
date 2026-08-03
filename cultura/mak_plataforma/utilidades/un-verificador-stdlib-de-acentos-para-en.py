import re
import sys
import os
import tempfile

# Diccionario de palabras que deben llevar tilde (forma sin tilde -> forma con tilde)
PALABRAS_CON_TILDE = {
    'ano': 'año',
    'dano': 'daño',
    'cancion': 'canción',
    'accion': 'acción',
    'telefono': 'teléfono',
    'publico': 'público',
    'musica': 'música',
    'pagina': 'página',
    'arbol': 'árbol',
    'facil': 'fácil',
    'dificil': 'difícil',
    'lapiz': 'lápiz',
    'camara': 'cámara',
    'ingles': 'inglés',
    'frances': 'francés',
    'portugues': 'portugués',
    'japon': 'Japón',
    'cientifico': 'científico',
    'practico': 'práctico',
    'teorico': 'teórico',
    'ultimo': 'último',
    'examen': 'examen',  # no lleva tilde, pero se incluye para evitar falsos positivos? mejor no
    # Se pueden añadir más según necesidad
}

def verificar_acentos(rutas):
    """
    Verifica la presencia de formas mutiladas (sin tilde) en los archivos dados.
    Devuelve una lista de tuplas (ruta, número_de_línea, palabra_encontrada).
    """
    resultados = []
    for ruta in rutas:
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
        except (FileNotFoundError, IOError) as e:
            print(f"Error al leer {ruta}: {e}", file=sys.stderr)
            continue
        for num_linea, linea in enumerate(lineas, start=1):
            # Encuentra todas las palabras (secuencias de letras, incluyendo acentos)
            palabras = re.findall(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b', linea)
            for palabra in palabras:
                if palabra.lower() in PALABRAS_CON_TILDE:
                    resultados.append((ruta, num_linea, palabra))
    return resultados

def main():
    """
    Función principal para ejecución desde línea de comandos.
    Toma rutas de archivos como argumentos y muestra los resultados.
    """
    if len(sys.argv) < 2:
        print("Uso: python acentos.py <archivo1> [archivo2 ...]")
        sys.exit(1)
    rutas = sys.argv[1:]
    resultados = verificar_acentos(rutas)
    if resultados:
        print("Formas mutiladas encontradas:")
        for ruta, linea, palabra in resultados:
            print(f"{ruta}: línea {linea}: '{palabra}'")
    else:
        print("No se encontraron formas mutiladas.")

if __name__ == "__main__":
    # --- Pruebas automáticas con assert ---
    # Creamos directorios temporales para simular las rutas de los casos de prueba
    with tempfile.TemporaryDirectory() as tmpdir:
        # Crear estructura de directorios simulada
        data_dir = os.path.join(tmpdir, "flujo", "data", "productoras")
        docs_dir = os.path.join(tmpdir, "flujo", "docs", "rd")
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)

        # Caso 1: Archivo JSON con forma mutilada
        ruta1 = os.path.join(data_dir, "ejemplo.json")
        with open(ruta1, 'w', encoding='utf-8') as f:
            f.write('{"nombre": "dano"}')
        resultado1 = verificar_acentos([ruta1])
        assert resultado1 == [(ruta1, 1, 'dano')], f"Caso 1 falló: {resultado1}"

        # Caso 2: Archivo HTML con título defectuoso
        ruta2 = os.path.join(docs_dir, "ejemplo.html")
        with open(ruta2, 'w', encoding='utf-8') as f:
            f.write('<title>reduciendo ano</title>')
        resultado2 = verificar_acentos([ruta2])
        assert resultado2 == [(ruta2, 1, 'ano')], f"Caso 2 falló: {resultado2}"

        # Caso 3: Archivo JSON sin formas mutiladas
        ruta3 = os.path.join(data_dir, "ejemplo.json")  # mismo nombre, pero sobrescribimos
        with open(ruta3, 'w', encoding='utf-8') as f:
            f.write('{"nombre": "daño"}')
        resultado3 = verificar_acentos([ruta3])
        assert resultado3 == [], f"Caso 3 falló: {resultado3}"

    print("PRUEBAS OK")
