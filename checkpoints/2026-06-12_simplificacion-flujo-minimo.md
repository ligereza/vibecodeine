# Checkpoint — Simplificación a flujo mínimo

Fecha: 2026-06-12

## Motivo

El sistema estaba creciendo con demasiadas opciones: asistentes, agentes, relay multi-IA, IA avanzada, portfolio-auto, scripts, etc. El usuario necesita empezar más simple: acumular avance y no volver a empezar desde cero.

## Decisión

Crear un flujo mínimo basado en 3 elementos:

```txt
inbox/                          archivos/códigos/carpetas básicas
context/ESTADO_ACTUAL_SIMPLE.md estado vivo resumido
scripts/simple_checkpoint.sh    guardar avance + checkpoint + git
```

## Regla

Los archivos básicos no tienen que servir perfecto. Se tratan como evidencia incompleta para entender cómo funcionan herramientas o prototipos.

## Archivos creados

- `START_SIMPLE.md`
- `context/ESTADO_ACTUAL_SIMPLE.md`
- `scripts/simple_checkpoint.sh`
- `inbox/`
- `reference_files/`

## Próximo paso

1. Copiar archivos básicos a `inbox/`.
2. Editar `context/ESTADO_ACTUAL_SIMPLE.md`.
3. Ejecutar:

```bash
bash scripts/simple_checkpoint.sh "primer avance simple"
```

4. Compartir con una IA solo:

```txt
context/ESTADO_ACTUAL_SIMPLE.md
context/INBOX_INDEX.md
último checkpoint
```
