#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path
from datetime import datetime

IG_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?P<kind>p|reel|tv)/(?P<code>[A-Za-z0-9_-]+)/*[^\s]*"
)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "evento"


def detect_media_guess(kind):
    if kind == "p":
        return "image_or_carousel_possible"
    if kind == "reel":
        return "video_possible"
    if kind == "tv":
        return "video_possible"
    return "unknown"


def normalize_url(kind, code):
    return f"https://www.instagram.com/{kind}/{code}"


def create_project(name):
    date = datetime.now().strftime("%Y-%m-%d")
    safe = slugify(name)

    base = Path("projects/flyer_eventos")
    project = base / f"{date}_{safe}"

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


def update_manifest(project_dir, item, index, total):
    manifest = project_dir / "manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))

    kind = item["kind"]
    code = item["code"]
    url = item["url"]
    media_guess = detect_media_guess(kind)

    data["status"] = "from_email_pending_download"

    data.setdefault("source", {})
    data["source"]["type"] = "email"
    data["source"]["email_imported_at"] = datetime.now().isoformat(timespec="seconds")
    data["source"]["link_index"] = index
    data["source"]["link_total"] = total

    data["instagram"] = {
        "url": url,
        "type": kind,
        "shortcode": code,
        "media_guess": media_guess,
        "download_status": "pending",
        "manual_download_possible": True
    }

    data.setdefault("extracted_info", {})
    data["extracted_info"]["event_name"] = ""
    data["extracted_info"]["producer"] = ""
    data["extracted_info"]["venue"] = ""
    data["extracted_info"]["event_date"] = ""
    data["extracted_info"]["needs_manual_review"] = True

    data["manual_review"] = {
        "required": True,
        "reason": "metadata_pending",
        "notes": [
            "Revisar si el post es imagen, carrusel o video.",
            "Si el perfil es privado, shadowban o requiere login, descargar manualmente.",
            "Completar nombre evento, productora, lugar y fecha desde el flyer."
        ]
    }

    data.setdefault("notes", [])
    data["notes"].append("Creado desde correo. Falta descargar/analizar flyer.")

    if kind in ["reel", "tv"]:
        data["notes"].append("Link parece video. Puede requerir descarga manual o captura de frame.")

    manifest.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def extract_instagram_links(text):
    found = []

    for m in IG_RE.finditer(text):
        kind = m.group("kind")
        code = m.group("code")
        url = normalize_url(kind, code)

        found.append({
            "kind": kind,
            "code": code,
            "url": url
        })

    unique = []
    seen = set()
    for item in found:
        if item["url"] not in seen:
            unique.append(item)
            seen.add(item["url"])

    return unique


def main():
    if len(sys.argv) < 2:
        print('Uso: py scripts/flyer_from_email.py "ruta/correo.txt"')
        sys.exit(1)

    email_path = Path(sys.argv[1])

    if not email_path.exists():
        print(f"ERROR: no existe archivo: {email_path}")
        sys.exit(1)

    text = email_path.read_text(encoding="utf-8", errors="ignore")
    items = extract_instagram_links(text)

    if not items:
        print("No encontré links de Instagram.")
        sys.exit(0)

    print(f"Encontré {len(items)} link(s) de Instagram.")
    print("")

    for i, item in enumerate(items, start=1):
        kind = item["kind"]
        media_guess = detect_media_guess(kind)
        name = f"email_evento_{i:02d}"

        print(f"[{i}/{len(items)}] Creando proyecto")
        print(f"URL: {item['url']}")
        print(f"Tipo: {kind}")
        print(f"Media guess: {media_guess}")

        project = create_project(name)
        update_manifest(project, item, i, len(items))

        print(f"OK: {project}")
        print("")

    print("Listo. Revisa con:")
    print("bash scripts/flyer_list.sh")
    print("bash scripts/flyer_status_latest.sh")


if __name__ == "__main__":
    main()
