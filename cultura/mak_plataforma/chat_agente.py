#!/usr/bin/env python3
"""chat_agente.py -- hablale directo al agente local, como en este chat.
Loop interactivo real (no cron, no un solo disparo): vos escribis, el
modelo decide si usa herramientas o solo responde, mantiene la
conversacion completa entre turnos.
"""
import json
import os
import subprocess
import sys

from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

HOME = os.path.expanduser("~")
sys.path.insert(0, os.path.join(HOME, "plataforma"))


@register_tool('leer_estado')
class LeerEstado(BaseTool):
    description = 'lee las metricas actuales del organismo MAK (backlog, PRs, produccion de hoy)'
    parameters = []

    def call(self, params, **kwargs):
        try:
            import junta
            return json.dumps(junta.metricas(), ensure_ascii=False)
        except Exception as e:
            return f"error: {e}"


@register_tool('vetear')
class Vetear(BaseTool):
    description = 'revisa y mergea PRs capataz/ listos, gateado por CI'
    parameters = []

    def call(self, params, **kwargs):
        r = subprocess.run(["python3", os.path.join(HOME, "plataforma", "revisor.py"), "--enforce"],
                            capture_output=True, text=True, timeout=120)
        return f"exit={r.returncode} stdout={r.stdout[-500:]}"


@register_tool('entregar')
class Entregar(BaseTool):
    description = 'entrega UNA pieza codex lista al repo como PR draft'
    parameters = []

    def call(self, params, **kwargs):
        r = subprocess.run(["python3", os.path.join(HOME, "plataforma", "entregar.py"), "--limit", "1"],
                            capture_output=True, text=True, timeout=120)
        return f"exit={r.returncode} stdout={r.stdout[-500:]}"


@register_tool('leer_bitacora')
class LeerBitacora(BaseTool):
    description = 'lee las ultimas lineas de la bitacora del capataz (que se hizo antes)'
    parameters = []

    def call(self, params, **kwargs):
        path = os.path.join(HOME, "plataforma", "bitacora_capataz.jsonl")
        try:
            with open(path, encoding="utf-8") as f:
                lineas = f.readlines()[-5:]
            return "".join(lineas)
        except Exception as e:
            return f"error: {e}"


def main():
    import sys
    modelo = sys.argv[1] if len(sys.argv) > 1 else "llama3.1:8b"
    llm_cfg = {'model': modelo, 'model_server': 'http://192.168.50.1:11434/v1', 'api_key': 'ollama'}
    bot = Assistant(llm=llm_cfg, function_list=['leer_estado', 'vetear', 'entregar', 'leer_bitacora'],
                     system_message="Sos el capataz de MAK, conversas con el usuario en espanol. "
                                     "Usa las herramientas cuando haga falta info real o una accion.")
    print(f"=== chat con {modelo} en MAK -- escribi tu pregunta, 'salir' para terminar ===")
    historia = []
    while True:
        try:
            texto = input("\ntu> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if texto.lower() in ("salir", "exit", "quit"):
            break
        if not texto:
            continue
        historia.append({'role': 'user', 'content': texto})
        respuesta_final = None
        for r in bot.run(messages=historia):
            respuesta_final = r
        if respuesta_final:
            historia.extend(respuesta_final)
            ultimo_asst = [m for m in respuesta_final if m.get('role') == 'assistant' and m.get('content')]
            if ultimo_asst:
                print(f"\nagente> {ultimo_asst[-1]['content']}")


if __name__ == "__main__":
    main()
