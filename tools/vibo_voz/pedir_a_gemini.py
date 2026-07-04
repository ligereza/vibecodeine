"""Canal Claude -> Gemini: offloadea lectura/resumen pesado al modelo barato.

Un chat de Claude Code (de pago) puede llamar a esto para que GEMINI (gratis) lea
archivos/areas del repo y devuelva un RESUMEN corto, en vez de que Claude gaste
tokens leyendo todo. La lectura de archivos es local (0 tokens); solo el resumen
usa Gemini (tier free).

Uso:
    py pedir_a_gemini.py "que quiero saber" ruta1 [ruta2 ...]
    py pedir_a_gemini.py "resume el area de suplementos" svg/suplementos_rd

Requiere GEMINI_API_KEY en tools/vibo_voz/.env. Modelo: GEMINI_TEXT_MODEL
(default gemini-2.5-flash, barato).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:  # noqa: BLE001
    pass

from google import genai

_REPO = Path(__file__).resolve().parents[2]
_MODEL = os.environ.get("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
_MAX_CHARS = 180_000          # tope de material que le pasamos a Gemini
_SENSIBLES = ("id_rsa", ".pem", ".key", ".p12", "credential", "secret", "token", ".env")


def _reunir(rutas: list[str]) -> str:
    partes = []
    total = 0
    for r in rutas:
        p = (Path(r) if Path(r).is_absolute() else _REPO / r).resolve()
        if _REPO not in p.parents and p != _REPO:
            continue  # solo dentro del repo
        archivos = [p] if p.is_file() else sorted(p.rglob("*")) if p.is_dir() else []
        for a in archivos:
            if not a.is_file():
                continue
            low = a.name.lower()
            if any(s in low for s in _SENSIBLES) or a.suffix.lower() in {".png", ".jpg", ".zip", ".pdf"}:
                continue
            try:
                txt = a.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
            bloque = f"\n--- {a.relative_to(_REPO)} ---\n{txt}"
            if total + len(bloque) > _MAX_CHARS:
                partes.append("\n[...truncado por tamano...]")
                return "".join(partes)
            partes.append(bloque)
            total += len(bloque)
    return "".join(partes)


def main():
    if len(sys.argv) < 3:
        sys.exit('Uso: py pedir_a_gemini.py "consulta" ruta1 [ruta2 ...]')
    consulta = sys.argv[1]
    rutas = sys.argv[2:]
    material = _reunir(rutas)
    if not material.strip():
        sys.exit("No encontre contenido de texto en esas rutas (dentro del repo).")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Falta GEMINI_API_KEY en el .env.")
    client = genai.Client(api_key=api_key)

    prompt = (
        "Eres un operador que prepara contexto para otro agente. Lee el material y "
        "responde a la consulta de forma BREVE y util (bullet points, rutas exactas, "
        "datos concretos). No inventes; si algo no esta, dilo.\n\n"
        f"CONSULTA: {consulta}\n\nMATERIAL:\n{material}"
    )
    resp = client.models.generate_content(model=_MODEL, contents=prompt)
    print(resp.text)


if __name__ == "__main__":
    main()
