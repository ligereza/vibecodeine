# Checkpoint — Flujo IA avanzada para optimización

Fecha: 2026-06-12

## Resumen corto

Se agregó un flujo especial para aprovechar chats de IA más poderosos o modernos cuando estén disponibles, sin perder versiones anteriores gracias a Git/GitHub.

## Objetivo

Permitir que una IA avanzada analice composición, contexto, jerarquía visual, copy, estructura técnica o automatizaciones, y proponga mejoras controladas.

## Decisión técnica

Usar ramas Git experimentales:

```txt
main = versión estable
ai-optimizacion/... = pruebas sugeridas por IA avanzada
```

## Archivos creados

- `docs/FLUJO_IA_AVANZADA_OPTIMIZACION.md`
- `prompts/ia_avanzada_optimizacion_composicion.md`
- `scripts/git_ai_experiment.sh`

## Próximo paso recomendado

Probar el flujo con una pieza real:

```bash
bash scripts/git_ai_experiment.sh "flyer-evento-prueba"
```

Luego compartir a una IA avanzada:

- Contexto del proyecto
- Preview JPG/PNG
- Restricciones
- Prompt `ia_avanzada_optimizacion_composicion.md`

Y aplicar cambios solo en la rama experimental.
