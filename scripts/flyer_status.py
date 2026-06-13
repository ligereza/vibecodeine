#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print('Uso: py scripts/flyer_status.py "projects/flyer_eventos/PROYECTO"')
    sys.exit(1)

project = Path(sys.argv[1])
manifest = project / "manifest.json"

if not project.exists():
    print(f"ERROR: no existe proyecto: {project}")
    sys.exit(1)

if not manifest.exists():
    print(f"ERROR: no existe manifest: {manifest}")
    sys.exit(1)

data = json.loads(manifest.read_text(encoding="utf-8"))

print("")
print("=== Flyer status ===")
print(f"Proyecto: {project}")
print(f"Nombre: {data.get('name', '')}")
print(f"Estado: {data.get('status', '')}")
print("")

print("Inputs:")
inp = data.get("input", {})
print(f"- Imagen principal: {inp.get('main_image', '')}")
print(f"- Fecha evento: {inp.get('event_date', '')}")
print(f"- Formato: {inp.get('format', '')}")
print(f"- Notas: {inp.get('notes', '')}")
print("")

print("Pasos:")
steps = data.get("steps", {})
for k, v in steps.items():
    print(f"- {k}: {v}")

print("")
print("Outputs:")
outs = data.get("outputs", [])
if not outs:
    print("- ninguno")
else:
    for out in outs:
        print(f"- {out}")
