# Sistema de Airdrop — flujo

El sistema de airdrop permite recibir cambios grandes de forma ordenada y segura.

## Cómo funciona

1. La IA genera un ZIP que contiene la carpeta `_airdrop/`
2. Descargas y reemplazas tu carpeta `_airdrop/` local con la del ZIP
3. Ejecutas el script de aplicación:

```bash
# Primero revisas qué va a hacer (recomendado)
bash scripts/apply_airdrop.sh --dry-run

# Luego aplicas los cambios
bash scripts/apply_airdrop.sh --apply
```

4. El script hace **backup automático** de los archivos que va a sobrescribir
5. Los backups se guardan en `_airdrop_backups/`
6. Después de aplicar, haces tus pruebas y commit

## Estructura

```
_airdrop/                 ← Archivos nuevos o modificados (NO se commitea)
_airdrop_backups/         ← Backups automáticos (NO se commitea)
scripts/apply_airdrop.sh  ← Script de aplicación
docs/AIRDROP.md           ← Esta documentación
```

## Reglas importantes

- Nunca hagas commit de `_airdrop/` ni `_airdrop_backups/`
- Usa siempre `--dry-run` primero
- Después de aplicar, ejecuta pruebas locales antes de commitear
- Cada airdrop debe ser lo más quirúrgico posible

## Buenas prácticas

- Un airdrop ideal contiene solo los archivos estrictamente necesarios
- Evita airdrops gigantes que reemplacen grandes porciones del repo
- Documenta brevemente qué incluye cada airdrop en el ZIP (README_AIRDROP.md)

---

**Sistema de Airdrop v2** — Mejorado para mayor claridad y seguridad.
