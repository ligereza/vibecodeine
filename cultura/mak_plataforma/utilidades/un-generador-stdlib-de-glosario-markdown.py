"""
Generador de glosario Markdown a partir de reactivos.json.

Uso:
    python glosario_md.py INPUT_JSON [OUTPUT_MD]

Si no se especifica OUTPUT_MD, se escribe en "glosario.md".
"""

import json
import sys
from pathlib import Path
from typing import List, Dict


def load_json(path: str) -> List[Dict]:
    """Lee el archivo JSON y devuelve la lista de reactivos."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_entry(entry: Dict) -> str:
    """Convierte un reactivo en una fila de tabla Markdown."""
    nombre = entry.get("nombre", "")
    familia = entry.get("familia", "")
    color = entry.get("color", "")
    seguridad = entry.get("seguridad", "")
    return f"| {nombre} | {familia} | {color} | {seguridad} |"


def generate_glossary(data: List[Dict]) -> str:
    """Crea el documento Markdown completo con encabezado y tabla."""
    lineas = [
        "# Glosario de reactivos",
        "",
        "| Nombre | Familia | Color | Seguridad |",
        "|--------|---------|-------|-----------|",
    ]
    for entry in data:
        lineas.append(render_entry(entry))
    return "\n".join(lineas) + "\n"


def write_md(content: str, path: str) -> None:
    """Graba el contenido Markdown en la ruta especificada."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    """Punto de entrada principal: procesa argumentos y genera el glosario."""
    if len(sys.argv) < 2:
        print("Uso: python glosario_md.py INPUT_JSON [OUTPUT_MD]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "glosario.md"

    data = load_json(input_path)
    md_content = generate_glossary(data)
    write_md(md_content, output_path)
    print(f"Glosario generado en: {output_path}")


if __name__ == "__main__":
    # ---------- Caso 1: entrada mínima ----------
    data1 = [
        {"nombre": "Eto", "familia": "Alcohol", "color": "#123456", "seguridad": "Inflamable"},
    ]
    md1 = generate_glossary(data1)
    assert md1.strip().splitlines() == [
        "# Glosario de reactivos",
        "",
        "| Nombre | Familia | Color | Seguridad |",
        "|--------|---------|-------|-----------|",
        "| Eto | Alcohol | #123456 | Inflamable |",
    ]

    # ---------- Caso 2: varios reactivos ----------
    data2 = [
        {"nombre": "NaCl", "familia": "Sal", "color": "#00FF00", "seguridad": "Inerte"},
        {"nombre": "Ácido clorhídrico", "familia": "Ácido", "color": "#FF0000", "seguridad": "Corrosivo"},
    ]
    md2 = generate_glossary(data2)
    rows = md2.strip().splitlines()
    assert rows[0] == "# Glosario de reactivos"
    # La línea en blanco está en índice 1, el encabezado en índice 2
    assert rows[2] == "| Nombre | Familia | Color | Seguridad |"
    assert rows[3] == "|--------|---------|-------|-----------|"
    assert rows[4] == "| NaCl | Sal | #00FF00 | Inerte |"
    assert rows[5] == "| Ácido clorhídrico | Ácido | #FF0000 | Corrosivo |"

    # ---------- Caso 3: JSON de archivo externo ----------
    import tempfile
    import pathlib

    json_content = [
        {"nombre": "H₂O", "familia": "Oxígeno", "color": "#0000FF", "seguridad": "No tóxico"},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        json_path = pathlib.Path(tmp) / "reactivos.json"
        json_path.write_text(json.dumps(json_content, ensure_ascii=False))
        # Simular la cadena completa de llamada
        data3 = load_json(str(json_path))
        md3 = generate_glossary(data3)
        assert "| H₂O | Oxígeno | #0000FF | No tóxico |" in md3

    print("PRUEBAS OK")

    # Si se ejecuta con argumentos, corre la lógica principal
    if len(sys.argv) > 1:
        main()
