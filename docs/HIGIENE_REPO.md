# Higiene del repo

Versión: v0.34.6

## Política

El repo debe mantenerse útil para trabajo real y legible para agentes. No debe convertirse en un basurero de outputs, caches o pruebas locales.

## Nunca commitear

- `_airdrop/`, `_airdrop_backups/`, `_logs/`
- `__pycache__/`, `*.pyc`
- `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`
- `*.egg-info/` nuevos
- `data/*.db`, `*.sqlite*`
- `context/DAILY.md`, `context/dashboard.html`
- `projects/**/salida_generada/`
- medios pesados descargados: `*.mp4`, `*.mov`, `*.mkv`, `*.psd`, `*.ai`, `*.zip`

## Antes de checkpoint

```bash
git status --short
py -m compileall -q src scripts tests
py -m pytest tests/ -q
py -m flujo health
```

## Antes de aceptar un airdrop externo

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje"
```

## Deuda conocida

- `projects/tapiz/vibecode.egg-info/` está trackeado históricamente.
- Hay muchos checkpoints y handoffs históricos. No limpiar agresivamente sin plan.
- Hay scripts legacy que conviene inventariar antes de borrar.
