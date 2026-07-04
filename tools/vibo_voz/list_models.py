"""Lista los modelos que tu key de Gemini soporta para la Live API (voz en vivo).

Uso:
    py list_models.py

Busca modelos que soporten 'bidiGenerateContent' (los unicos validos para el
asistente de voz). Copia uno de esos ids a VIBO_LIVE_MODEL en tu .env.
"""
from __future__ import annotations

import os

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:  # noqa: BLE001
    pass

from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("Falta GEMINI_API_KEY (ponla en el .env).")

client = genai.Client(api_key=api_key)

print("Modelos que soportan la Live API (bidiGenerateContent):\n")
encontrados = []
for m in client.models.list():
    acciones = getattr(m, "supported_actions", None) or []
    if "bidiGenerateContent" in acciones:
        encontrados.append(m.name)
        print(f"  {m.name}")

if not encontrados:
    print("  (ninguno) - revisa que tu key sea de AI Studio y tenga acceso a Live.")
else:
    print(f"\nCopia uno de estos (sin el prefijo 'models/') a VIBO_LIVE_MODEL en .env.")
