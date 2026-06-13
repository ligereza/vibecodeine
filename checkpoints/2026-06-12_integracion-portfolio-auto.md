# Checkpoint — Integración de repo portfolio-auto

Fecha: 2026-06-12

## Repo revisado

https://github.com/ligereza/portfolio-auto

## Resumen

Se revisó el repo público `portfolio-auto`, un portafolio/archivo digital HTML/CSS/JS vanilla con `data/works.json`, `CURATOR.html`, `README-AGENTS.txt` y despliegue pensado para Cloudflare Pages.

## Estado

WIP / dejado a medias / requiere integración.

## Hallazgos principales

1. Tiene estructura web funcional.
2. Tiene memoria de agentes en `README-AGENTS.txt`.
3. Tiene contrato de datos en `data/works.json`.
4. Tiene panel `CURATOR.html` para webhook n8n.
5. Usa placeholders externos en vez de obras reales.
6. Automatización n8n/GitHub API no está confirmada como funcional.
7. Puede integrarse como proyecto externo conectado al sistema de checkpoints.

## Decisión

Tratar `portfolio-auto` como proyecto vinculado, no como reemplazo de `ai-workflow-checkpoints`.

```txt
ai-workflow-checkpoints = memoria técnica / productor / sistema operativo
portfolio-auto = producto web / archivo público / portfolio
```

## Archivos creados

- `docs/PORTFOLIO_AUTO_INTEGRACION.md`
- `projects/portfolio-auto/README.md`
- `projects/portfolio-auto/ESTADO_ACTUAL.md`
- `projects/portfolio-auto/ERRORES_PENDIENTES.md`
- `projects/portfolio-auto/PLAN_INTEGRACION.md`
- `prompts/revisar_portfolio_auto_ia_avanzada.md`

## Errores abiertos

- `ERROR-PROD-001`: Automatización Curator/n8n incompleta.
- `ERROR-PROD-002`: Assets/obras reales no integradas.
- `ERROR-PROD-003`: Falta sincronización con sistema de checkpoints.

## Nota sobre herramientas existentes

Las dos herramientas implementadas del usuario deben quedar marcadas como error/revisión pendiente:

1. Automatización flyers Instagram → Photoshop → Blender → jefe eventos.
2. Slowmo Blender → After Effects → consolidación frames.

Motivo: funcionan como prototipos, pero requieren auditoría, documentación, manejo de errores y mejora antes de tratarlas como producción estable.

## Próximo paso

Cuando el usuario suba archivos:

1. Importarlos al workspace.
2. Revisar scripts/automatizaciones reales.
3. Crear reportes de error por herramienta.
4. Preparar paquete para IA avanzada.
5. Priorizar una integración mínima: portfolio-auto como salida/archivo para obras o piezas seleccionadas.
