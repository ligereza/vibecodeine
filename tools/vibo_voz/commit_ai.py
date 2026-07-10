"""commit_ai: mensaje de commit (o descripcion de PR) generado por Gemini.

Automation-agent del roadmap del director (paso 2): lo mecanico de
redactar el commit lo hace el modelo GRATIS, no Claude. NUNCA commitea ni
toca el repo: imprime el mensaje y el humano (o el flujo que lo llame)
decide. El diff staged se scrubbea de secretos ANTES de salir a Google
(mismo regex que pedir_a_gemini).

Uso:
    git add ...
    py tools/vibo_voz/commit_ai.py            # mensaje de commit
    py tools/vibo_voz/commit_ai.py --pr       # titulo + cuerpo de PR

Requiere GEMINI_API_KEY en tools/vibo_voz/.env (multi-key GEMINI_API_KEY_2...
y cadena de fallback de modelos, igual que pedir_a_gemini).
"""
from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pedir_a_gemini import _scrub  # noqa: E402 -- mismo scrub, sin 3ra copia del regex

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:  # noqa: BLE001 -- python-dotenv puede no estar; .env ya en entorno
    pass

_MODELOS = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-3.1-flash-lite"]
_MAX_DIFF = 60_000  # caracteres de diff que viajan a Gemini

_PROMPT_COMMIT = (
    "Escribe UN mensaje de commit para este diff staged. Formato Conventional "
    "Commits: 'tipo: resumen' (tipo en ingles: feat/fix/docs/chore/refactor/"
    "test; resumen en espanol sin tildes, max 50 chars). Cuerpo SOLO si el "
    "porque no es obvio del diff (2-4 lineas, espanol sin tildes, ASCII). "
    "Responde SOLO el mensaje, sin backticks ni comentarios.\n\nDIFF:\n"
)
_PROMPT_PR = (
    "Escribe titulo y cuerpo de un Pull Request para este diff. Titulo: 1 "
    "linea clara. Cuerpo en markdown: '## Que resuelve' (2-3 lineas) y "
    "'## Cambios' (bullets concretos por archivo). Espanol sin tildes, "
    "ASCII. Responde SOLO titulo y cuerpo, sin comentarios extra.\n\nDIFF:\n"
)


def _keys() -> list[str]:
    keys = [os.environ.get("GEMINI_API_KEY", "")]
    i = 2
    while os.environ.get(f"GEMINI_API_KEY_{i}"):
        keys.append(os.environ[f"GEMINI_API_KEY_{i}"])
        i += 1
    return [k for k in keys if k]


def diff_staged(repo_dir: str | None = None) -> str:
    """Diff staged, scrubbeado y acotado. Vacio si no hay nada staged."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--no-color"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=repo_dir or None, check=True,
    ).stdout
    if not out.strip():
        return ""
    out = _scrub(out)
    if len(out) > _MAX_DIFF:
        out = out[:_MAX_DIFF] + "\n[...diff truncado para el modelo...]"
    return out


def armar_prompt(diff: str, pr: bool = False) -> str:
    return (_PROMPT_PR if pr else _PROMPT_COMMIT) + diff


def pedir_mensaje(prompt: str) -> str:
    """Multi-key x fallback de modelos via REST (sin SDK, urllib puro)."""
    import json
    import urllib.error
    import urllib.request

    keys = _keys()
    if not keys:
        sys.exit("Falta GEMINI_API_KEY en tools/vibo_voz/.env")
    cuerpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    for i, key in enumerate(keys, start=1):
        for modelo in _MODELOS:
            url = ("https://generativelanguage.googleapis.com/v1beta/models/"
                   f"{modelo}:generateContent?key={key}")
            req = urllib.request.Request(
                url, data=cuerpo, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.load(r)
                return "".join(
                    p.get("text", "")
                    for p in data["candidates"][0]["content"]["parts"]
                ).strip()
            except urllib.error.HTTPError as e:
                print(f"[fallback] key{i} ({key[:6]}...) x {modelo}: HTTP {e.code}",
                      file=sys.stderr)
            except Exception as e:  # noqa: BLE001
                print(f"[fallback] key{i} ({key[:6]}...) x {modelo}: "
                      f"{type(e).__name__}", file=sys.stderr)
    sys.exit("Todas las keys x modelos fallaron (quota o red).")


def main() -> None:
    pr = "--pr" in sys.argv
    rutas = [a for a in sys.argv[1:] if a != "--pr"]
    repo = rutas[0] if rutas else None
    diff = diff_staged(repo)
    if not diff:
        sys.exit("Nada staged (git add primero).")
    print(pedir_mensaje(armar_prompt(diff, pr=pr)))


if __name__ == "__main__":
    main()
