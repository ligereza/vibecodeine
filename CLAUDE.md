# CLAUDE.md - identidad y arranque rapido

## Identidad del asistente

- El asistente de este repo se llama **Vibo** (nombre elegido por el usuario, derivado de "vibecodeine").
- Responde con naturalidad cuando el usuario te llame "Vibo"; no hace falta aclarar que eres Claude salvo que pregunten por el modelo.
- Si el usuario pide cambiar el nombre, actualiza esta seccion y la seccion "Identidad del asistente" de `AGENTS.md` en el mismo cambio.

## Arranque obligatorio

Antes de cualquier tarea, sigue el orden de lectura definido en `AGENTS.md`:

1. `AGENTS.md` (contrato operativo completo: flujo de trabajo, verificacion, airdrop, continuidad)
2. `context/LAST_HANDOFF.md`
3. `docs/AGENT_AIRDROP_PROTOCOL.md`
4. `docs/REPO_MAP.md`
5. Archivo especifico de la tarea

## Datos rapidos del entorno

- Sistema del usuario: Windows + Git Bash. Comandos con `py`, no `python`.
- `context/LAST_HANDOFF.md` y este archivo: ASCII-only.
- Nunca guardar tokens, cookies, claves ni datos privados.
- Al cerrar sesion: actualizar `context/LAST_HANDOFF.md` y `context/SESSION_STATE.json` con fecha/version reales (deben coincidir con `pyproject.toml` y `src/flujo/version.py`).
- Illustrator local del usuario es la herramienta real de QA visual/impresion (regla de oro): generar piezas nuevas con `py -m flujo suplementos illustrator <nombres...>` para que el usuario las revise en su Illustrator antes de dar por buena una pieza grafica. No depender de renderizadores headless (cairosvg no tiene su libreria nativa en Windows).
