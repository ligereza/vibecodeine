# AI Provider Routing - flujo

Como repartir el trabajo entre modelos: barato por defecto, Claude solo para lo caro.
Regla base: **el modelo mas barato que haga bien la tarea. Claude decide y revisa, no teclea boilerplate.**

## Matriz

| Proveedor | Rol | Cuando usarlo | Cuando ESCALAR a Claude | Tipo de tarea | Riesgo |
|---|---|---|---|---|---|
| **Claude Code / Opus 4.8** | Arquitecto, bugs criticos, revisor final | Diseno de solucion, decisiones de arquitectura, bug dificil, revision de diff antes de merge, seguridad | (es el techo) | Planos, decisiones, review, refactors sensibles, prompts para los demas | Costo alto; usar con cuota justa |
| **Qwen API** (DashScope) | Editor barato, lector de contexto, tests | Edicion simple guiada por un plan, generar tests/boilerplate, resumir/mascar contexto de rutas gordas | Cuando toca arquitectura, decide entre enfoques, o el diff es riesgoso | Ediciones acotadas, tests, docstrings, contexto | Medio: puede inventar; siempre pasa por review |
| **NVIDIA NIM** | Alternativa barata/gratis a Qwen | Igual que Qwen cuando DashScope no rinde o para DeepSeek/Nemotron; endpoint OpenAI-compatible | Igual que Qwen | Igual que Qwen (edicion, tests, contexto) | Medio; disponibilidad/limites de la cuenta |
| **OpenRouter** | Router / fallback | Cuando un proveedor esta caido o quieres probar otro modelo sin cambiar setup | Igual que el editor que enrute | Fallback de edicion/lectura | Medio; costo variable por modelo |
| **Aider** | Orquestador del repo (API) | Aplicar cambios al repo con architect(Claude)+editor(barato), commits atomicos | Para el plan y el review usa Claude dentro de Aider | Implementar tareas concretas sobre archivos | Bajo si el plan es claro; medio si el prompt es vago |
| **Copilot / LMArena** | Apoyo externo | Ideas sueltas, comparar respuestas, snippets fuera del repo | Siempre que toque el repo real | Brainstorm, snippets desechables | NO es fuente de verdad; nunca pegar a ciegas |

## Reglas de escalado (barato -> Claude)

Escala a Claude cuando la tarea tiene **una o mas**:
- decision de arquitectura o de que enfoque tomar;
- toca seguridad, credenciales, workflows CI, o `src/flujo/airdrop.py`;
- el diff cambia comportamiento publico (CLI, API, formato de entrega);
- ya se intento antes y fallo (ver `src/flujo/version.py` get_changelog);
- es el review final antes de merge.

Deja en el editor barato (Qwen/NIM/OpenRouter) cuando:
- hay un plan claro y el cambio es mecanico/local;
- generar tests, docstrings, boilerplate, o mascar/resumir contexto;
- traducir un plan de Claude a ediciones concretas.

## Flujo tipo (bajo consumo)

1. **Contexto barato:** `py tools/vibo_voz/contexto_repo.py task "<keywords>"` o Qwen resume rutas gordas.
2. **Plan:** Qwen/NIM redacta borrador -> **Claude valida el plan** (barato de revisar, caro de re-hacer mal).
3. **Implementa:** Aider con architect=Claude (o plan ya fijo) + editor=Qwen/NIM.
4. **Review final:** Claude revisa el diff. Si toca lo critico de arriba, Claude manda.
5. **Cierre:** actualizar `context/LAST_HANDOFF.md` + `context/SESSION_STATE.json` (ver docs/AI_OPERATING_LAYER.md).

Prompts listos: `docs/TASK_PROMPTS.md`. Setup de Aider: `docs/AIDER_API_SETUP.md`.
