"""Canal Claude -> Gemini: offloadea lectura/resumen pesado al modelo barato.

Un chat de Claude Code (de pago) puede llamar a esto para que GEMINI (gratis) lea
archivos/areas del repo y devuelva un RESUMEN corto, en vez de que Claude gaste
tokens leyendo todo. La lectura de archivos es local (0 tokens); solo el resumen
usa Gemini (tier free).

Uso:
    py pedir_a_gemini.py "que quiero saber" ruta1 [ruta2 ...]
    py pedir_a_gemini.py "resume el area de suplementos" svg/suplementos_rd

Requiere GEMINI_API_KEY en tools/vibo_voz/.env (keys extra opcionales:
GEMINI_API_KEY_2, _3, ...). Modelos: GEMINI_TEXT_MODEL (si esta seteado) y
despues la cadena de fallback (los modelos disponibles VARIAN POR KEY; no
asumir uno fijo -- leccion 2026-07-10, gemini-2.5-flash murio para keys nuevas).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:  # noqa: BLE001
    pass

try:
    from google import genai
except ImportError:  # sin google-genai instalado (ej: CI); _scrub sigue importable
    genai = None

_REPO = Path(__file__).resolve().parents[2]
# Cadena de fallback (misma que desktop/gemini_client.py); GEMINI_TEXT_MODEL va primero.
_MODELOS_FALLBACK = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-3.1-flash-lite"]
_MODELOS = ([os.environ["GEMINI_TEXT_MODEL"]] if os.environ.get("GEMINI_TEXT_MODEL") else []) + _MODELOS_FALLBACK
_MAX_CHARS = 180_000          # tope de material que le pasamos a Gemini
_MAX_FILES = 200              # tope de archivos (no mandar el repo entero a la nube)
_SENSIBLES = ("id_rsa", ".pem", ".key", ".p12", "credential", "secret", "token", ".env")

# Redaccion de secretos POR CONTENIDO (no solo por nombre): antes de enviar a Google.
_SECRET_RE = re.compile(
    r"(AIza[0-9A-Za-z_\-]{20,}"
    r"|gh[posur]_[0-9A-Za-z]{20,}"
    r"|github_pat_[0-9A-Za-z_]{20,}"
    r"|nvapi-[0-9A-Za-z_\-]{20,}"
    r"|sk-or-v1-[0-9a-f]{20,}"
    r"|-----BEGIN[^-]*PRIVATE KEY-----"
    r"|(?:api[_-]?key|secret|token|password|authorization)\s*[:=]\s*['\"]?[^\s'\"]{6,})",
    re.IGNORECASE,
)


def _scrub(texto: str) -> str:
    return _SECRET_RE.sub("[REDACTADO]", texto)


def _reunir(rutas: list[str]) -> str:
    partes = []
    total = 0
    n_files = 0
    for r in rutas:
        p = (Path(r) if Path(r).is_absolute() else _REPO / r).resolve()
        if p == _REPO:
            sys.exit("Por seguridad no envio el repo ENTERO a la nube. Da rutas concretas.")
        if _REPO not in p.parents:
            continue  # solo dentro del repo
        archivos = [p] if p.is_file() else sorted(p.rglob("*")) if p.is_dir() else []
        for a in archivos:
            if not a.is_file():
                continue
            if n_files >= _MAX_FILES:
                partes.append(f"\n[...corte: mas de {_MAX_FILES} archivos, acota la ruta...]")
                return "".join(partes)
            n_files += 1
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
    if genai is None:
        sys.exit("Falta el paquete google-genai (pip install google-genai).")
    if len(sys.argv) < 3:
        sys.exit('Uso: py pedir_a_gemini.py "consulta" ruta1 [ruta2 ...]')
    consulta = sys.argv[1]
    rutas = sys.argv[2:]
    material = _scrub(_reunir(rutas))   # redacta secretos por contenido antes de enviar
    if not material.strip():
        sys.exit("No encontre contenido de texto en esas rutas (dentro del repo).")
    print("[aviso] el contenido de esas rutas se envia a Gemini (Google). Evita areas "
          "sensibles; los secretos detectados se redactan.", file=sys.stderr)

    # Multi-key: GEMINI_API_KEY + GEMINI_API_KEY_2, _3, ... (mismo esquema que desktop/).
    keys = [k for k in [os.environ.get("GEMINI_API_KEY")]
            + [os.environ.get(f"GEMINI_API_KEY_{i}") for i in range(2, 10)] if k]
    if not keys:
        sys.exit("Falta GEMINI_API_KEY en el .env.")

    prompt = (
        "Eres un operador que prepara contexto para otro agente. Lee el material y "
        "responde a la consulta de forma BREVE y util (bullet points, rutas exactas, "
        "datos concretos). No inventes; si algo no esta, dilo.\n\n"
        f"CONSULTA: {consulta}\n\nMATERIAL:\n{material}"
    )
    for i, api_key in enumerate(keys, start=1):
        client = genai.Client(api_key=api_key)
        for modelo in _MODELOS:
            try:
                resp = client.models.generate_content(model=modelo, contents=prompt)
            except Exception as exc:  # noqa: BLE001 -- 404 modelo muerto, 429 quota, etc.
                print(f"[fallback] key{i} ({api_key[:6]}...) x {modelo}: "
                      f"{type(exc).__name__}", file=sys.stderr)
                continue
            print(resp.text)
            return
    sys.exit("Todas las keys x modelos fallaron (quota agotada o modelos no disponibles).")


if __name__ == "__main__":
    main()
