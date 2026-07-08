"""Canal Claude -> modelo barato (ESCRITURA): pide codigo a Gemini o NVIDIA NIM.

Contraparte de escritura de pedir_a_gemini.py (que solo lee/resume). Claude Code
prepara una tarea concreta + archivos objetivo; el modelo barato devuelve los
archivos completos corregidos; este script los muestra (default) o los aplica
con --aplicar (backup .bak antes de escribir). Sin aider, sin OpenRouter: API
directa, menos piezas que fallan.

Uso:
    py pedir_codigo.py "tarea concreta" ruta1 [ruta2 ...]
    py pedir_codigo.py --aplicar "tarea" ruta1 [ruta2 ...]
    py pedir_codigo.py --proveedor nvidia "tarea" ruta1 [ruta2 ...]

Proveedor por defecto: SOLO gemini (probado fiable). NVIDIA NIM queda como opcion
manual via --proveedor nvidia (2026-07-08: free tier saturado, 503 "workers busy"
y cortes en payloads grandes; no confiar para trabajo desatendido):
    gemini  GEMINI_API_KEY        modelo GEMINI_CODE_MODEL (default gemini-2.5-flash)
    nvidia  NVIDIA_API_KEY        modelo NVIDIA_CODE_MODEL (default deepseek-ai/deepseek-v4-flash)
    github  GITHUB_MODELS_TOKEN   modelo GITHUB_CODE_MODEL (default deepseek/deepseek-v3-0324)
            OJO: free tier limita 8k tokens de entrada / 4k de salida por request
            -> solo tareas chicas (archivos <200 lineas); verificado 2026-07-08

El modelo debe responder SOLO bloques con este formato exacto (lo parseamos):
    === FILE: ruta/relativa/al/repo ===
    <contenido completo del archivo>
    === END ===
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Windows: stdout/stderr cp1252 revienta con unicode del codigo (flechas,
# emojis en comentarios); forzar UTF-8 siempre
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except Exception:  # noqa: BLE001
    pass

_REPO = Path(__file__).resolve().parents[2]
_MAX_CHARS = 120_000
_SENSIBLES = ("id_rsa", ".pem", ".key", ".p12", "credential", "secret", "token", ".env")

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

_BLOQUE_RE = re.compile(
    r"^=== FILE: (?P<ruta>[^\n]+?) ===\n(?P<cuerpo>.*?)\n=== END ===",
    re.DOTALL | re.MULTILINE,
)


def _scrub(texto: str) -> str:
    return _SECRET_RE.sub("[REDACTADO]", texto)


def _reunir(rutas: list[str]) -> tuple[str, list[Path]]:
    partes, archivos_ok = [], []
    total = 0
    for r in rutas:
        p = (Path(r) if Path(r).is_absolute() else _REPO / r).resolve()
        if p == _REPO:
            sys.exit("Por seguridad no envio el repo ENTERO. Da archivos concretos.")
        if _REPO not in p.parents:
            sys.exit(f"Solo archivos dentro del repo: {r}")
        if not p.is_file():
            sys.exit(f"No es un archivo: {r} (este canal edita archivos concretos, no carpetas)")
        low = p.name.lower()
        if any(s in low for s in _SENSIBLES):
            sys.exit(f"Ruta sensible, no se envia: {r}")
        txt = p.read_text(encoding="utf-8", errors="replace")
        bloque = f"\n=== FILE: {p.relative_to(_REPO).as_posix()} ===\n{txt}\n=== END ===\n"
        if total + len(bloque) > _MAX_CHARS:
            sys.exit("Material demasiado grande; acota los archivos.")
        partes.append(bloque)
        archivos_ok.append(p)
        total += len(bloque)
    return "".join(partes), archivos_ok


def _prompt(tarea: str, material: str) -> str:
    return (
        "Eres un editor de codigo. Aplica la TAREA a los archivos dados.\n"
        "Reglas estrictas:\n"
        "- Cambios minimos y completos; NO refactorices nada fuera de la tarea.\n"
        "- Sin TODO, sin stubs, sin explicaciones.\n"
        "- Responde SOLO con los archivos MODIFICADOS, contenido COMPLETO, en este formato exacto:\n"
        "=== FILE: ruta/relativa ===\n<contenido completo>\n=== END ===\n"
        "- Si un archivo no necesita cambios, no lo incluyas.\n\n"
        f"TAREA: {tarea}\n\nARCHIVOS:\n{material}"
    )


def _llamar_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GEMINI_API_KEY")
    from google import genai
    client = genai.Client(api_key=api_key)
    modelo = os.environ.get("GEMINI_CODE_MODEL", "gemini-2.5-flash")
    resp = client.models.generate_content(model=modelo, contents=prompt)
    return resp.text or ""


def _llamar_nvidia(prompt: str) -> str:
    api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("NVIDIA_NIM_API_KEY")
    if not api_key:
        raise RuntimeError("Falta NVIDIA_API_KEY")
    # Verificados 2026-07-08: deepseek-v4-flash y nvidia/nemotron-3-super-120b-a12b
    # responden directo; varios del catalogo (codestral, qwen3.x) requieren
    # habilitacion de cuenta o cuelgan. Ver docs/AI_PROVIDER_ROUTING.md.
    modelo = os.environ.get("NVIDIA_CODE_MODEL", "deepseek-ai/deepseek-v4-flash")
    cuerpo = json.dumps({
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 16384,
        # apaga el modo razonamiento de los deepseek-v4 (sin esto escupe
        # reasoning_content y desperdicia presupuesto de salida)
        "chat_template_kwargs": {"thinking": False},
        # streaming obligatorio: el gateway de NIM corta respuestas no-stream
        # largas (504 conocido y sin fix oficial); con SSE el socket siempre
        # tiene trafico y no hay idle timeout que lo mate
        "stream": True,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        data=cuerpo,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
    )
    # timeout por-lectura (entre chunks), no total: una salida larga que fluye
    # nunca lo dispara. NVIDIA_TIMEOUT lo ajusta si un modelo tarda en arrancar.
    timeout_s = int(os.environ.get("NVIDIA_TIMEOUT", "120"))
    # free tier (~40 RPM compartido) escupe 503/429 transitorios: backoff
    # obligatorio segun la propia guia de NVIDIA
    ultimo_error: Exception = RuntimeError("sin intentos")
    for intento in range(4):
        if intento:
            espera = 2 ** intento
            print(f"[nvidia] reintento {intento} en {espera}s...", file=sys.stderr)
            time.sleep(espera)
        try:
            partes, crudas = [], []
            with urllib.request.urlopen(req, timeout=timeout_s) as r:
                for linea in r:
                    linea = linea.decode("utf-8", errors="replace").strip()
                    if not linea.startswith("data: "):
                        if linea:
                            crudas.append(linea)
                        continue
                    datos = linea[len("data: "):]
                    if datos == "[DONE]":
                        break
                    try:
                        delta = json.loads(datos)["choices"][0]["delta"]
                    except (KeyError, IndexError, json.JSONDecodeError):
                        continue
                    partes.append(delta.get("content") or "")
            contenido = "".join(partes)
            if contenido.strip():
                return contenido
            # sin contenido: NIM a veces responde HTTP 200 con un JSON de error
            # en el body ({"error":{...,"code":503}}) en vez de status real
            cuerpo_crudo = "".join(crudas)
            try:
                err = json.loads(cuerpo_crudo).get("error", {})
            except json.JSONDecodeError:
                err = {}
            mensaje = err.get("message", "respuesta vacia sin JSON de error")
            if err.get("code") in (429, 500, 502, 503, 504) or "busy" in mensaje.lower():
                ultimo_error = RuntimeError(f"NIM saturado: {mensaje}")
                continue
            raise RuntimeError(f"NVIDIA respondio vacio: {mensaje}")
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
            ultimo_error = e
    raise ultimo_error


def _llamar_github(prompt: str) -> str:
    token = os.environ.get("GITHUB_MODELS_TOKEN")
    if not token:
        raise RuntimeError("Falta GITHUB_MODELS_TOKEN")
    modelo = os.environ.get("GITHUB_CODE_MODEL", "deepseek/deepseek-v3-0324")
    # free tier: 8k in / 4k out por request -> abortar temprano si no entra
    if len(prompt) > 28_000:  # ~8k tokens aprox
        raise RuntimeError("prompt excede el limite de 8k tokens de GitHub Models; usa gemini")
    cuerpo = json.dumps({
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://models.github.ai/inference/chat/completions",
        data=cuerpo,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"] or ""


_PROVEEDORES = {"gemini": _llamar_gemini, "nvidia": _llamar_nvidia, "github": _llamar_github}


def _aplicar(respuesta: str, permitidos: list[Path]) -> int:
    rutas_permitidas = {p.resolve() for p in permitidos}
    n = 0
    for m in _BLOQUE_RE.finditer(respuesta):
        destino = (_REPO / m.group("ruta").strip()).resolve()
        if destino not in rutas_permitidas:
            print(f"[rechazado] fuera de alcance: {m.group('ruta').strip()}", file=sys.stderr)
            continue
        shutil.copy2(destino, destino.with_suffix(destino.suffix + ".bak"))
        destino.write_text(m.group("cuerpo"), encoding="utf-8")
        print(f"[aplicado] {destino.relative_to(_REPO)} (backup .bak)")
        n += 1
    return n


def main():
    args = sys.argv[1:]
    aplicar = "--aplicar" in args
    if aplicar:
        args.remove("--aplicar")
    proveedor_forzado = None
    if "--proveedor" in args:
        i = args.index("--proveedor")
        proveedor_forzado = args[i + 1]
        del args[i:i + 2]
    if len(args) < 2:
        sys.exit('Uso: py pedir_codigo.py [--aplicar] [--proveedor gemini|nvidia|github] "tarea" ruta1 [ruta2 ...]')

    tarea, rutas = args[0], args[1:]
    material, archivos = _reunir(rutas)
    material = _scrub(material)
    print("[aviso] contenido se envia al proveedor elegido (Google/NVIDIA). Secretos se redactan.",
          file=sys.stderr)

    orden = [proveedor_forzado] if proveedor_forzado else ["gemini"]
    respuesta, usado = "", ""
    for nombre in orden:
        fn = _PROVEEDORES.get(nombre)
        if fn is None:
            sys.exit(f"Proveedor desconocido: {nombre}")
        try:
            respuesta = fn(_prompt(tarea, material))
            usado = nombre
            break
        except Exception as e:  # noqa: BLE001
            print(f"[fallo {nombre}] {e}", file=sys.stderr)
    if not respuesta.strip():
        sys.exit("Ningun proveedor devolvio respuesta.")

    print(f"[proveedor] {usado}", file=sys.stderr)
    if aplicar:
        n = _aplicar(respuesta, archivos)
        if n == 0:
            print("Nada aplicado. Respuesta cruda:\n", file=sys.stderr)
            print(respuesta)
            sys.exit(1)
        print(f"{n} archivo(s) actualizados. Verifica con la bateria del repo.")
    else:
        print(respuesta)


if __name__ == "__main__":
    main()
