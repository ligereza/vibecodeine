# Airdrop - logo_clean_lab + hotfix checkpoint timeout

Este airdrop incluye dos cosas:

1. Proyecto experimental sin terminar `projects/logo_clean_lab/` con script Illustrator `logo_clean_master.jsx`.
2. Hotfix para que `run_airdrop_checks.py` no quede pegado indefinidamente en auto-checkpoint/push.

## Aplicar desde root del repo

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "logo clean lab experimental"
```

## Si ya aplicaste parte del airdrop anterior y se pego en checkpoint

Usa resume y evita push automatico:

```bash
py scripts/run_airdrop_checks.py --resume "logo clean lab experimental" --skip-push
```

Luego haces el push manual para ver prompts reales:

```bash
git push
```

## Que cambia el hotfix

- Muestra salida en vivo de `git push`.
- Agrega timeout al push y comandos git.
- Agrega `--skip-push` para dejar commit local sin empujar.
- Si falla push, no queda pegado: deja instruccion para empujar manualmente.
