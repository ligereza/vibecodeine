#!/usr/bin/env python3
"""agente_real.py -- capataz con qwen-agent: loop de agente REAL sobre
llama3.1:8b local (WIN, gratis, sin nube). Reemplaza el menu rigido de
capataz.py por herramientas reales que el modelo elige y ejecuta el mismo.
"""
import json
import subprocess
import sys
import os

from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

HOME = os.path.expanduser("~")


@register_tool('leer_estado')
class LeerEstado(BaseTool):
    description = 'lee las metricas actuales del organismo MAK (backlog, PRs, produccion de hoy)'
    parameters = []

    def call(self, params, **kwargs):
        try:
            sys.path.insert(0, os.path.join(HOME, "plataforma"))
            import junta
            return json.dumps(junta.metricas(), ensure_ascii=False)
        except Exception as e:
            return f"error leyendo metricas: {e}"


@register_tool('vetear')
class Vetear(BaseTool):
    description = 'revisa y mergea PRs capataz/ listos, gateado por CI -- accion segura por defecto'
    parameters = []

    def call(self, params, **kwargs):
        r = subprocess.run(["python3", os.path.join(HOME, "plataforma", "revisor.py"), "--enforce"],
                            capture_output=True, text=True, timeout=120)
        return f"exit={r.returncode} stdout={r.stdout[-500:]} stderr={r.stderr[-300:]}"


@register_tool('entregar')
class Entregar(BaseTool):
    description = 'entrega UNA pieza codex lista al repo como PR draft'
    parameters = []

    def call(self, params, **kwargs):
        r = subprocess.run(["python3", os.path.join(HOME, "plataforma", "entregar.py"), "--limit", "1"],
                            capture_output=True, text=True, timeout=120)
        return f"exit={r.returncode} stdout={r.stdout[-500:]} stderr={r.stderr[-300:]}"


def main():
    llm_cfg = {'model': 'llama3.1:8b', 'model_server': 'http://192.168.50.1:11434/v1', 'api_key': 'ollama'}
    bot = Assistant(llm=llm_cfg, function_list=['leer_estado', 'vetear', 'entregar'],
                     system_message=(
                         "Sos el capataz de MAK. Primero llama leer_estado. Si hay PRs "
                         "listos, usa vetear. Si hay piezas codex sin entregar, usa "
                         "entregar. Si dudas, usa vetear (accion segura). Reporta corto "
                         "en espanol al final."
                     ))
    msgs = [{'role': 'user', 'content': 'Ejecuta ahora mismo la herramienta leer_estado, sin explicar nada antes.'}]
    ultimo = None
    for r in bot.run(messages=msgs):
        ultimo = r
    bitacora = os.path.join(HOME, "plataforma", "bitacora_capataz.jsonl")
    with open(bitacora, "a", encoding="utf-8") as f:
        f.write(json.dumps({"tipo": "agente_real", "resultado": ultimo}, ensure_ascii=False) + "\n")
    print(json.dumps(ultimo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
