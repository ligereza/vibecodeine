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

def _load_env(fname: str) -> None:
    """Carga un .env a os.environ sin depender de python-dotenv (no siempre esta
    instalado, y pip puede estar bloqueado por la politica de red). No pisa
    variables ya presentes en el entorno."""
    path = os.path.join(os.path.dirname(__file__), fname)
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip().strip('"').strip("'")
                os.environ.setdefault(key, val)
    except FileNotFoundError:
        pass


for _f in (".env", ".env.local"):
    _load_env(_f)

import requests

_REPO = Path(__file__).resolve().parents[2]
_DOSSIERS = _REPO / "projects" / "cultura" / "dossiers"
# Modelos verificados contra ListModels de esta key (2026-07-10): soportan
# generateContent + google_search grounding. gemini-3.x no existe para esta key.
_MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]

# Bloque de prompt: primer fenced code block del dossier.
_PROMPT_RE = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.DOTALL)
# Marcador donde va la respuesta (tolera texto extra en la linea del header).
_FINDINGS_RE = re.compile(r"(## Findings[^\n]*\n)(.*?)(\n## |\Z)", re.DOTALL)


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
                    cand = data["candidates"][0]
                    parts = cand["content"]["parts"]
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        # Fuentes REALES del grounding (URLs verificables), no los
                        # titulos que el modelo escribe en el texto (pueden ser
                        # inventados). Leccion de la corrida 2026-07-10.
                        chunks = cand.get("groundingMetadata", {}).get("groundingChunks", [])
                        urls = []
                        for c in chunks:
                            web = c.get("web", {})
                            if web.get("uri"):
                                urls.append(f"- {web.get('title', 'fuente')}: {web['uri']}")
                        if urls:
                            seen = list(dict.fromkeys(urls))
                            text += "\n\n**Fuentes verificables (grounding real):**\n" + "\n".join(seen)
                        else:
                            text += ("\n\n_ADVERTENCIA: la respuesta no trajo groundingMetadata; "
                                     "las fuentes citadas en el texto NO estan verificadas._")
                        print(f"[ok] {model} con key {_mask(key)} ({len(urls)} fuentes grounding)", file=sys.stderr)
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
