# Sistema de Airdrop — flujo

Mecanismo para recibir cambios de forma ordenada.

## Flujo completo

```bash
# 1. Aplicar
bash scripts/apply_airdrop.sh --apply

# 2. Finalizar (opcional pero recomendado)
bash scripts/finish_airdrop.sh
```

## Estructura

```
_airdrop/                 (NO commitear)
_airdrop_backups/         (NO commitear)
scripts/apply_airdrop.sh
scripts/finish_airdrop.sh
```

## Reglas

- Nunca commitear `_airdrop/` ni `_airdrop_backups/`
- Usar siempre `--dry-run` primero
- Hacer checkpoint después de aplicar

---

**Versión:** Junio 2026
