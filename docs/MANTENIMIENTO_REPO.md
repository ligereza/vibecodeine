# Mantenimiento del repo

## Limpiar generados locales

```bash
py scripts/flujo_clean_generated.py
```

Limpia:

- `__pycache__/`
- `*.pyc`
- outputs regenerables de `projects/piezas_vectoriales/*/`

## Chequeo general

```bash
py scripts/flujo_health.py
```

Valida:

- JSONs parseables,
- ausencia de caches Python,
- configs de piezas vectoriales.

## Antes de commit

Recomendado:

```bash
py scripts/flujo_clean_generated.py
py scripts/flujo_health.py
git status
```
