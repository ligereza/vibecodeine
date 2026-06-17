# Limpieza y Mantenimiento — flujo

## Scripts disponibles

- `scripts/cleanup_moderate.sh` — Limpieza moderada (mover carpetas a _archive)
- `scripts/find_duplicates.py` — Detecta archivos duplicados por contenido
- `scripts/sanitize_sensitive.py` — Reemplaza información sensible por placeholders

## Uso recomendado

```bash
# 1. Detectar duplicados
python scripts/find_duplicates.py

# 2. Sanitizar información sensible
python scripts/sanitize_sensitive.py

# 3. Limpieza moderada
bash scripts/cleanup_moderate.sh
```

## Reglas

- Nunca eliminar sin confirmación
- Usar `_archive/` para cosas en pausa
- Ejecutar `sanitize_sensitive.py` antes de compartir el repo

---

**Versión:** Junio 2026
