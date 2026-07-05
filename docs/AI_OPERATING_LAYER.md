# AI Operating Layer - flujo

Como trabaja una IA en este repo sin leer todo, sabiendo que modelo usar y como entregar.
Companion: `docs/AI_PROVIDER_ROUTING.md` (que modelo), `docs/AIDER_API_SETUP.md` (Aider),
`docs/TASK_PROMPTS.md` (prompts).

## Que leer primero (3-5 archivos, no el repo entero)

1. `AGENTS.md` - contrato operativo (entrega, verificacion, continuidad).
2. `context/LAST_HANDOFF.md` - estado actual / listo / pendiente / bloqueadores / proximo paso.
3. `docs/AI_PROVIDER_ROUTING.md` - que modelo para cada tarea.
4. `docs/REPO_MAP.md` - fuentes de verdad vs generadas.
5. El archivo especifico de la tarea.

Con eso un agente nuevo ya puede trabajar. `CLAUDE.md` define la identidad (Cauce).

## Como evitar leer todo el repo

- **Mapa mecanico (0 tokens):** `py tools/vibo_voz/contexto_repo.py` (o `map`).
- **Contexto para una tarea:** `py tools/vibo_voz/contexto_repo.py task "<keywords>"`
  imprime las rutas recomendadas + como derivarlas. Salida copiable para Claude/Aider/Qwen.
- **Derivar lectura pesada a un modelo barato:** Qwen/NIM resume rutas gordas (prompt 1 de
  TASK_PROMPTS.md) o `py tools/vibo_voz/pedir_a_gemini.py "consulta" ruta...`.
- Da a Aider/Qwen **solo los archivos de la tarea**, no el repo.

## Fuentes de verdad (editar aqui)

| Ruta | Que es |
|---|---|
| `src/flujo/` | Paquete Python + CLI `flujo` |
| `tests/` | Tests |
| `web/src/` | Hub React/Vite (build -> `context/*.html`) |
| `pyproject.toml` | Version y deps (la version manda) |
| `AGENTS.md`, `CLAUDE.md`, `docs/REPO_MAP.md` | Contrato, identidad, mapa |
| `context/LAST_HANDOFF.md`, `context/SESSION_STATE.json` | Estado / continuidad |
| `.claude/skills/*/SKILL.md` | Playbooks |

## Generadas / historicas (NO editar a mano)

`jobs/20*`, `projects/piezas_vectoriales/20*`, `datadrops/` (salida), `context/*.html`
(se generan con `npm run build:context`), `_airdrop*`, `_logs/`, `.archive/`,
`docs/handoffs/archive/`. Leer solo si el pipeline lo exige.

## Como entregar cambios

- Cambios minimos y completos: sin TODO, sin stubs, sin try/except vacio.
- Commits atomicos. **No pushear a `main` directo**: rama + PR (guardrail lo bloquea).
- Sin push directo (sesion remota): entregar por airdrop, ver `docs/AGENT_AIRDROP_PROTOCOL.md`.
- Nunca versionar secretos: `.env`, `*.key`, `.aider.conf.yml` estan gitignored.

## Como verificar (obligatorio)

Python:
```
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```
Web (si tocaste `web/`):
```
cd web && npm run typecheck && npm run build:context && cd ..
```
No declares OK sin correr la verificacion que corresponde. Reporta el error real si falla.

## Como cerrar una sesion

1. Verificacion en verde (arriba).
2. Actualizar `context/LAST_HANDOFF.md` (ASCII-only, compacto, 5 secciones) y
   `context/SESSION_STATE.json` (version = `pyproject.toml`, date real, done/doing/next/
   blockers/ai_stack). Reflejar lo que cambio de verdad; no dejar version/fecha vieja.
3. Reporte formal de verificacion (formato en AGENTS.md).
