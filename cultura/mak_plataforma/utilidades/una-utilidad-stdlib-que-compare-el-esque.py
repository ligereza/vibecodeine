from pathlib import Path
import json
import re
import tempfile
import argparse
from typing import Set, Dict, List

def parse_schema(src_path: str) -> Set[str]:
    """Extrae los nombres de columna del CREATE TABLE productoras.
    Devuelve un conjunto de nombres en minúscula."""
    with open(src_path, 'r') as f:
        content = f.read()
    
    match = re.search(r'CREATE TABLE productoras\s*\((.*?)\);', content, re.IGNORECASE)
    if not match:
        raise ValueError('No se encontró la definición de tabla en el archivo')
        
    columns = [col.split()[0].lower() for col in match.group(1).split(',')]
    
    return set(columns)

def find_extra_fields(json_dir: str, schema_fields: Set[str]) -> Dict[Path, List[str]]:
    """Compara cada JSON bajo `json_dir` con `schema_fields`.
    Retorna un dict:  {ruta_json: [campo_extra, ...]}."""
    
    extra_fields = {}
    for json_file in Path(json_dir).glob('**/*.json'):
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, dict):
            extra = set(data.keys()) - schema_fields
        elif isinstance(data, list):  # JSON como lista de objetos
            extra = set().union(*[set(d.keys()) for d in data]) - schema_fields
        else:
            raise ValueError('Formato no soportado')
            
        if extra:
            extra_fields[json_file] = list(extra)
    
    return extra_fields

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_path', help='Ruta al archivo fuente de la base de datos')
    parser.add_argument('json_dir', help='Ruta a los archivos JSON con las entradas')
    args = parser.parse_args()
    
    schema_fields = parse_schema(args.src_path)
    extra_fields = find_extra_fields(args.json_dir, schema_fields)
    
    if extra_fields:
        print('Los siguientes campos están presentes en los archivos JSON pero no están declarados en el esquema:')
        for json_file, fields in extra_fields.items():
            print(f'{json_file}: {", ".join(fields)}')
        raise SystemExit(1)
    
    print('Todos los campos de los archivos JSON están declarados en el esquema.')

if __name__ == "__main__":
    main()
