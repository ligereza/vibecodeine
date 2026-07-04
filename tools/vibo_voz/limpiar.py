"""Artefacto de limpieza (gratis, sin tokens).

Mata SOLO los agentes headless que el sistema de voz lanzo y quedaron abandonados
(los identifica por sus archivos .pid en agentes/). NUNCA toca las sesiones de
Claude que abriste tu.

Uso:  py limpiar.py
CODE tambien lo puede llamar por voz con la herramienta 'limpiar_procesos'.
"""
import claude_bridge as cb

r = cb.limpiar_procesos()
if r["total_matados"]:
    print(f"Limpiados {r['total_matados']} agente(s) abandonados: {r['matados']}")
else:
    print("Nada que limpiar: no hay agentes del sistema de voz colgados.")
if r["ya_estaban_muertos"]:
    print(f"(ya estaban muertos: {r['ya_estaban_muertos']})")
