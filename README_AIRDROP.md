# Airdrop - README general + logo_clean_lab summary

Este airdrop vuelve a documentar el flujo normal simple de airdrops y agrega contexto ejecutivo del proyecto `logo_clean_lab`.

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

Si aparece algo como `logo3d/`, sacarlo o dejarlo ignorado antes del checkpoint automatico.
