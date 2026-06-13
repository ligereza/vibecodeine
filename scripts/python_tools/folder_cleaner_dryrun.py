#!/usr/bin/env python3
"""
Folder Cleaner Dry Run

Primera versión segura: NO mueve ni borra archivos.
Solo escanea una carpeta y propone categorías.

Uso:
  python scripts/python_tools/folder_cleaner_dryrun.py /ruta/a/carpeta
"""

from pathlib import Path
import sys
import json
from datetime import datetime

CATEGORIES = {
    "editables_diseno": {".psd", ".psb", ".ai", ".indd", ".fig", ".xd"},
    "imagenes_preview": {".jpg", ".jpeg", ".png", ".webp"},
    "imagenes_pesadas": {".tif", ".tiff", ".raw", ".exr", ".hdr"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "audio": {".mp3", ".wav", ".aiff", ".flac", ".m4a"},
    "documentos": {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".md"},
    "fuentes": {".ttf", ".otf", ".woff", ".woff2"},
    "comprimidos": {".zip", ".rar", ".7z"},
    "scripts": {".py", ".jsx", ".js", ".bat", ".sh"},
}

TARGET_FOLDERS = {
    "editables_diseno": "_editables",
    "imagenes_preview": "_previews",
    "imagenes_pesadas": "_imagenes_pesadas",
    "video": "_video",
    "audio": "_audio",
    "documentos": "_documentos",
    "fuentes": "_fuentes",
    "comprimidos": "_comprimidos",
    "scripts": "_scripts",
    "otros": "_otros_review",
}


def categorize(path: Path) -> str:
    ext = path.suffix.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "otros"


def main():
    if len(sys.argv) < 2:
        print("Uso: python folder_cleaner_dryrun.py /ruta/a/carpeta")
        sys.exit(1)

    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Carpeta inválida: {root}")
        sys.exit(1)

    report = {
        "root": str(root),
        "date": datetime.now().isoformat(timespec="seconds"),
        "mode": "dry-run",
        "actions": [],
        "summary": {},
    }

    for item in root.iterdir():
        if item.is_file():
            cat = categorize(item)
            target = TARGET_FOLDERS[cat]
            report["actions"].append({
                "file": item.name,
                "category": cat,
                "suggested_target": target,
                "action": "move_suggestion_only"
            })
            report["summary"][cat] = report["summary"].get(cat, 0) + 1

    print(json.dumps(report, ensure_ascii=False, indent=2))

    out = root / "folder_cleaner_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReporte creado: {out}")
    print("No se movió ni borró ningún archivo.")


if __name__ == "__main__":
    main()
