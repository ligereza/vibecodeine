#!/usr/bin/env python3
"""
Investigador de dossiers de Cultura via Gemini API (con busqueda web).

Lee el bloque de prompt de cada dossier en projects/cultura/dossiers/*.md, lo
manda a Gemini con grounding de busqueda real, y escribe la respuesta en la
seccion "## Findings" del mismo archivo. Claude solo cura despues (regla del
runway: la lectura/busqueda la hace el modelo barato).

Sin API key hardcodeada: se lee de GEMINI_API_KEY (+ _2, _3 fallback) del
entorno o de tools/vibo_voz/.env (gitignored). NUNCA se imprime ni se commitea.

Uso:
    py tools/vibo_voz/investigar_cultura.py            # todos los pendientes
    py tools/vibo_voz/investigar_cultura.py tapiz      # solo uno
    py tools/vibo_voz/investigar_cultura.py --force tapiz   # re-investiga
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env.local"))
except Exception:  # noqa: BLE001
    pass

import requests

_REPO = Path(__file__).resolve().parents[2]
_DOSSIERS = _REPO / "projects" / "cultura" / "dossiers"
_MODELS = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]

# Bloque de prompt: primer fenced code block del dossier.
_PROMPT_RE = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.DOTALL)
# Marcador donde va la respuesta.
_FINDINGS_RE = re.compile(r"(## Findings\n)(.*?)(\n## |\Z)", re.DOTALL)


def _keys() -> list[str]:
    keys = [os.getenv("GEMINI_API_KEY", "")]
    i = 2
    while True:
        k = os.getenv(f"GEMINI_API_KEY_{i}", "")
        if not k:
            break
        keys.append(k)
        i += 1
    return [k for k in keys if k]


def _mask(key: str) -> str:
    return (key[:6] + "...") if key else "(vacia)"


def _ask_gemini(prompt: str) -> str:
    """Llama a Gemini con busqueda web, probando keys x modelos hasta un 200."""
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
    }
    keys = _keys()
    if not keys:
        sys.exit("Falta GEMINI_API_KEY (env o tools/vibo_voz/.env). No se paso ninguna clave.")
    last_err = ""
    for key in keys:
        for model in _MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                r = requests.post(url, json=payload, timeout=45)
            except Exception as e:  # noqa: BLE001
                last_err = f"{model}/{_mask(key)}: {e}"
                continue
            if r.status_code == 200:
                data = r.json()
                try:
                    parts = data["candidates"][0]["content"]["parts"]
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        print(f"[ok] {model} con key {_mask(key)}", file=sys.stderr)
                        return text
                except (KeyError, IndexError):
                    last_err = f"{model}/{_mask(key)}: respuesta sin texto"
                    continue
            else:
                last_err = f"{model}/{_mask(key)}: HTTP {r.status_code}"
    sys.exit(f"Ninguna combinacion respondio. Ultimo error: {last_err}")


def _process(path: Path, force: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    fm = _FINDINGS_RE.search(text)
    if fm and fm.group(2).strip() and "<!-- pending -->" not in fm.group(2) and not force:
        print(f"[skip] {path.name} ya tiene findings (usa --force para rehacer)", file=sys.stderr)
        return False
    pm = _PROMPT_RE.search(text)
    if not pm:
        print(f"[skip] {path.name} sin bloque de prompt", file=sys.stderr)
        return False
    print(f"[..] investigando {path.name}", file=sys.stderr)
    answer = _ask_gemini(pm.group(1).strip())
    block = f"## Findings\n\n_via Gemini + busqueda, curar antes de usar:_\n\n{answer}\n"
    if fm:
        # preserva la seccion siguiente (si existe) despues de Findings
        tail = text[fm.start(3):] if fm.group(3).startswith("\n## ") else ""
        new = text[: fm.start()] + block + tail
    else:
        new = text.rstrip() + "\n\n" + block
    path.write_text(new, encoding="utf-8")
    print(f"[written] {path.name}", file=sys.stderr)
    return True


def main():
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    if not _DOSSIERS.is_dir():
        sys.exit(f"No existe {_DOSSIERS}")
    targets = []
    if args:
        for name in args:
            p = _DOSSIERS / (name if name.endswith(".md") else f"{name}.md")
            if not p.is_file():
                sys.exit(f"No existe dossier: {p.name}")
            targets.append(p)
    else:
        targets = sorted(_DOSSIERS.glob("*.md"))
    done = sum(_process(p, force) for p in targets)
    print(f"\nListo: {done} dossier(s) investigado(s). Revisa y cura las secciones Findings.", file=sys.stderr)


if __name__ == "__main__":
    main()
