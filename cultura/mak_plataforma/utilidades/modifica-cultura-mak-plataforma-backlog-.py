import csv
import re

def cargar_data(archivo):
    with open(archivo, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data

def guardar_data(data, archivo):
    with open(archivo, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

def filtrar_backlog(archivo_entrada, archivo_salida):
    data = cargar_data(archivo_entrada)
    
    # Patrón de expresión regular para detectar entradas problemáticas
    patron = re.compile('No se (encontro|pudo determinar).*')
    
    # Eliminación de las filas con la información crítica faltante
    data = [row for row in data if not patron.match(','.join(row))]
    
    guardar_data(data, archivo_salida)

if __name__ == "__main__":
    # Casos de prueba
    filtrar_backlog('backlog_ejemplo_1.csv', 'backlog_ejemplo_filtrado_1.csv')
    assert open('backlog_ejemplo_filtrado_1.csv').read() == ''
    
    filtrar_backlog('backlog_ejemplo_2.csv', 'backlog_ejemplo_filtrado_2.csv')
    assert set(open('backlog_ejemplo_filtrado_2.csv').readlines()) == {'valid1,valid2\n', 'valid3,valid4\n'}
    
    filtrar_backlog('backlog_ejemplo_3.csv', 'backlog_ejemplo_filtrado_3.csv')
    assert open('backlog_ejemplo_filtrado_3.csv').read() == open('backlog_ejemplo_3.csv').read()
    
    print("PRUEBAS OK")
