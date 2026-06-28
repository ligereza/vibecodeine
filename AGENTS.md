# AGENTS.md

**Punto de entrada obligatorio (diario):** `flujo app` (o `flujo app --desktop`) — lanza la app real y sirve el hub como workspace central. Si falta el servidor, el fallback es abrir `context/flujo_hub.html` directamente.

El hub es el workspace central: intake de pedidos, visualizadores SVG, plano demo, comandos y delegación a agentes especializados. La fuente de verdad operativa diaria es `context/LAST_HANDOFF.md`.

**Estado actual (2026-06-28)**

`flujo app` sigue siendo la entrada diaria principal. Version operativa actual: v0.40.1. El hub agrupa intake, visuales, planos, agentes y herramientas. El historial de handoffs se centraliza en `docs/handoffs/README.md`. Windows: `py`.

**Avances recientes:**
- Hub con tabs, datadrop operativo y addons `py -m flujo hub ...` para serve/index/route.
- Delegación paralela con roles de visual, pipeline, futuro y packaging.
- Packaging `flujo package` → .exe desktop. Launchers ps1/bat. Higiene + robustez.

**Hacia dónde vamos:**
- Auto-compact sesiones (parallel + LAST_HANDOFF).
- Centralizar y limpiar handoffs, docs y recursos viejos.
- Daily: siempre `flujo app` → hub como workspace único.
- Más packaging standalone, higiene, privacy, especialización agentes.

## Quick start (agentes)

1. Ejecuta `flujo app` (o `flujo app --desktop`) — entrada diaria obligatoria única que sirve el hub.
2. Leer `context/LAST_HANDOFF.md` (estado actual + tareas)
3. Leer `docs/AGENT_OPERATING_MANUAL.md` (dos flujos + modelo formal delegación a agentes especializados)
4. Usar el hub (dentro de la app) para pegar pedidos → match + comandos → visualizers → export. Usar sección "Delegar..." para copiar prompts completos por rol (5 roles).

```bash
py -m pip install -e .
flujo version
flujo health
flujo daily
flujo app
# Todo lo demás se hace desde el hub o copiando comandos/prompts que genera
```

## Delegación

El hub contiene botones para generar y copiar prompts listos para:
- Visual Polish Agent
- Pipeline & Integration Agent
- Brand Guardian
- Future/Modern Agent
- Packaging & Distribution Agent

Ver modelo completo en AGENT_OPERATING_MANUAL.md. Lanza en clones paralelos (usa `flujo app` primero en cada uno).

## Reglas

- No yt-dlp. Solo instaloader.
- Análisis: colores + OCR en `analysis/`
- Privacidad: `flujo privacy scan/sanitize` antes de IAs externas
- Jobs lifecycle: borrador → ... → entregado (ver `docs/JOB_PIPELINE.md`)
- Siempre empezar por `flujo app` + hub + LAST_HANDOFF para ahorrar tokens.
