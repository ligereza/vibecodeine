# AGENT_GUIDE — flujo

> Para IAs que trabajan en este repo. Lee esto primero.

**Repo:** `flujo` — arte + automatización

## Stack

- Python 3.10+
- `py -m pip install -e .`
- CLI: `flujo` (Typer)
- Descarga IG: solo instaloader
- Análisis: colores + OCR opcional

## Comandos principales

```bash
flujo health
flujo flyer-import inbox/correo.txt
flujo analyze
flujo index --rebuild
flujo export <proyecto>
flujo open <proyecto> --ps
flujo open <proyecto> --ai
```

## Estructura principal

```
projects/
  flyer_eventos/
  piezas_vectoriales/
  tapiz/

src/flujo/          # CLI moderno
tools/
  flyer_eventos/SPEC.md
  piezas_vectoriales/SPEC.md
```

## Reglas

- No automatizar Photoshop / Illustrator / Blender
- Solo instaloader
- Mantener checkpoints
- No hacer limpiezas agresivas sin consultar

## Scripts de mantenimiento

- `scripts/find_duplicates.py`
- `scripts/sanitize_sensitive.py`
- `scripts/cleanup_moderate.sh`

---

**Última actualización:** Junio 2026
