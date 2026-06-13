#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path
from datetime import datetime

IG_RE = re.compile(r"https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_-]+/?[^\s]*")

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "evento"

def create_project(name):
    date = datetime.now().strftime("%Y-%m-%d")
    safe = slugify(name)

    base = Path("projects/flyer_eventos")
    project = base / f"{date}_{safe}"

    # Si ya existe, agrega sufijo
    n = 2
    original = project
    while project.exists():
        project = Path(f"{original}-{n:02d}")
        n += 1

    for folder in ["input", "working", "exports", "refs"]:
        d = project / folder
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch()

    manifest = {
        "tool": "flyer_eventos",
        "name": name,
        "date": date,
        "status": "created",
        "input": {
            "main_image": "",
            "event_name": name,
            "event_date": "",
            "format": "",
            "notes": ""
        },
        "steps": {
            "photoshop": "pending",
            "blender": "pending",
            "export": "pending"
        },
        "outputs": []
    }

    (project / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    (project / "README.md").write_text(
        f"""# Flyer evento — {name}

Fecha: {date}

## Objetivo

Crear flyer para evento importado desde correo.

## Estado

- [ ] Revisar link Instagram
- [ ] Descargar imagen/video
- [ ] Completar datos del evento
- [ ] Photoshop
- [ ] Blender
- [ ] Export final
""",
        encoding="utf-8"
    )

    return project

def update_manifest(project_dir, url, index, total):
    manifest = project_dir / "manifest.json"

    data = json.loads(manifest.read_text(encoding="utf-8"))

    data["status"] = "from_email_pending_download"

    data.setdefault("source", {})
    data["source"]["type"] = "email"
    data["source"]["instagram_url"] = url
    data["source"]["email_imported_at"] = datetime.now().isoformat(timespec="seconds")
    data["source"]["link_index"] = index
    data["source"]["link_total"] = total

    data.setdefault("extracted_info", {})
    data["extracted_info"]["event_name"] = ""
    data["extracted_info"]["producer"] = ""
    data["extracted_info"]["venue"] = ""
    data["extracted_info"]["event_date"] = ""
    data["extracted_info"]["needs_manual_review"] = True

    data.setdefault("download", {})
    data["download"]["status"] = "pending"
    data["download"]["possible_types"] = ["image", "video", "private_or_unavailable"]
    data["download"]["manual_download_needed"] = False

    data.setdefault("notes", [])
    data["notes"].append("Creado desde correo. Falta descargar/analizar flyer.")

    manifest.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def main():
    if len(sys.argv) < 2:
        print('Uso: py scripts/flyer_from_email.py "ruta/correo.txt"')
        sys.exit(1)

    email_path = Path(sys.argv[1])

    if not email_path.exists():
        print(f"ERROR: no existe archivo: {email_path}")
        sys.exit(1)

    text = email_path.read_text(encoding="utf-8", errors="ignore")
    links = IG_RE.findall(text)

    links = [link.split("?")[0].rstrip("/") for link in links]
    links = list(dict.fromkeys(links))

    if not links:
        print("No encontré links de Instagram.")
        sys.exit(0)

    print(f"Encontré {len(links)} link(s) de Instagram.")
    print("")

    for i, url in enumerate(links, start=1):
        name = f"email_evento_{i:02d}"

        print(f"[{i}/{len(links)}] Creando proyecto para: {url}")

        project = create_project(name)
        update_manifest(project, url, i, len(links))

        print(f"OK: {project}")

    print("")
    print("Listo. Revisa con:")
    print("bash scripts/flyer_list.sh")

if __name__ == "__main__":
    main()
