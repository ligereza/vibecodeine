# Airdrop - README general + limpieza operativa

Este airdrop documenta el flujo normal de airdrops y deja claro que la fuente de verdad operativa es el handoff diario y el hub local.

## Aplicar desde root del repo

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "actualiza readme y logo clean lab summary"
```

## Nota

No modifica el motor de airdrop. No requiere `--allow-airdrop-engine`.

## Antes de aplicar

Revisar que no haya carpetas locales pesadas coladas:

```bash
git status --short
```

Si aparece algo como `logo3d/`, sacarlo o dejarlo ignorado antes del checkpoint automatico. Para historial operativo, revisar `docs/handoffs/README.md` y `context/LAST_HANDOFF.md`.
