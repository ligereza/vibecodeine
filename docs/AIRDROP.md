# Sistema de Airdrop — flujo

Mecanismo para recibir cambios de forma ordenada.

## Uso

```bash
bash scripts/apply_airdrop.sh --dry-run
bash scripts/apply_airdrop.sh --apply
```

## Estructura

```
_airdrop/                 (NO commitear)
_airdrop_backups/         (NO commitear)
scripts/apply_airdrop.sh
```

## Reglas

- Nunca commitear `_airdrop/` ni `_airdrop_backups/`
- Usar siempre `--dry-run` primero
- Hacer checkpoint después de aplicar

---

**Versión:** Mejorada (junio 2026)
