# AGENTS.md

**Punto de entrada obligatorio (diario):** `flujo app` (o `flujo app --desktop`) — lanza la app real (servidor stdlib + APIs brand/parse/jobs/delegate/SSE/datadrop) + sirve los 3 HTMLs como UI pro completa (hub + visualizadores embebidos). Fallback: abre `context/flujo_hub.html` directamente.

El hub (dentro de la app) es el workspace central: intake de pedidos, visualizadores SVG embebidos por grupos, plano demo interactivo, comandos y sección para delegar a agentes especializados (5 roles paralelos). Hub = pro workspace dentro de `flujo app`.

**Estado actual (2026-06-22)**

`flujo app` es la ÚNICA entrada diaria. Hub con tabs (Intake/Jobs, Visuales, Planos, Agentes/Delegate, Herramientas) + Datadrop MVP completo (inverse airdrop: incoming → dated/ + manifests ricos con palette/OCR/traits/for_future_ai). Delegación maximizada 5 roles (incl. Packaging) con copy-prompt + live API. LAST_HANDOFF.md = low-token source of truth. Brand vía projects/flujo/flujo.json. Windows: `py`.

**Avances recientes:**
- Hub tabs + Datadrop fully working (drop bulk a incoming/, Escanear o `flujo datadrop scan`, cards UI limpia, modal robusto, _review_package.txt).
- Parallel delegation: 5 roles (Visual Polish, Pipeline & Integration, Brand Guardian, Future/Modern, Packaging). Reciente fix nav datadrop button.
- Packaging `flujo package` → .exe desktop. Launchers ps1/bat. Higiene + robustez.

**Hacia dónde vamos:**
- Auto-compact sesiones (parallel + LAST_HANDOFF).
- linea_editorial v4.1 + datadrop ground-truth para validación §10/11.
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
