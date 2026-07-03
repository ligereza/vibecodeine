# HANDOFF 2026-07-02 - nombre propio del asistente: Vibo

## Problema resuelto

El usuario pidio un nombre distinto de "Claude" para dirigirse al asistente.
Se creo la identidad "Vibo" (derivado de "vibecodeine") y se dejo persistida
en el repo para que sobreviva entre sesiones y aplique a cualquier agente.

## Archivos modificados

- `CLAUDE.md` (NUEVO, raiz): definicion canonica del nombre + arranque rapido.
  Claude Code carga este archivo automaticamente al iniciar cada sesion.
- `AGENTS.md`: nueva seccion "Identidad del asistente" para que agentes
  no-Claude tambien respeten el nombre. Se agrega tambien nota de que el
  QA visual real pasa por el Illustrator local del usuario, no por
  renderizadores headless de Python (cairosvg no tiene su libreria nativa
  en Windows; se uso Edge headless como alternativa en esta sesion).

## Como cambiar el nombre en el futuro

Editar la seccion "Identidad del asistente" en `CLAUDE.md` y en `AGENTS.md`
en el mismo cambio (ambos archivos deben coincidir).

## Riesgos o pendientes reales

- Ninguno funcional: cambio docs-only, no toca codigo ni build.

## Reporte Formal de Verificacion y Tolerancia Cero a Errores

- py -m compileall src/flujo: no aplica (docs-only, cero archivos Python tocados)
- py -m pytest tests/ -q: no aplica (docs-only)
- cd web && npm run build:context: no aplica (docs-only)
- py -m flujo verify: no aplica (docs-only)
- Observaciones: CLAUDE.md verificado ASCII-only byte a byte.
