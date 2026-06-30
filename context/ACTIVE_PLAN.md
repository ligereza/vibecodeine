# ACTIVE PLAN - demo jefe 2026-06-29

## Objetivo

Preparar una demo presentable del sistema flujo para jefatura:

1. Sistema brief / rider / plano terminado.
2. Cotizacion base para eventos.
3. Estado visual de flyers/material suplementos.

## Ruta demo recomendada

1. Abrir:

```bash
py -m flujo app
```

2. Hub -> Intake:
   - pegar correo de ejemplo con Instagram.
   - mostrar parse de EVENTOS.
   - mostrar preset sugerido MAINSTREAM si aplica Espacio Riesco/festival.

3. Hub -> Plano:
   - seleccionar preset MAINSTREAM.
   - usar Motor Python.
   - mostrar plano editable y requerimientos.

4. Hub -> Cotizacion:
   - preset MAINSTREAM.
   - incluir cartelera digital.
   - mostrar total referencial y copiar markdown.

5. Hub -> SVG:
   - mostrar materiales reales desde `/svg`.
   - filtrar suplementos.

## Must not break

- `py -m flujo app`
- `cd web && npm run build:context`
- `py -m flujo verify`

## If interrupted

Leer en este orden:

1. `context/LAST_HANDOFF.md`
2. `context/ACTIVE_PLAN.md`
3. `context/SESSION_STATE.json`
4. `docs/ROADMAP_AI_MEMORY.md`

Luego correr:

```bash
cd web
npm ci
npm run typecheck
npm run build:context
cd ..
py -m flujo verify
```

## Next after demo

- Knowledge base productoras/venues/logos.
- Examples ingestion para que IA genere JSON desde trabajos reales.
- Logo registry + logo clean lab bridge.
- Internet enrichment asistido.
