# AIRDROP v4 — flujo v0.14 — análisis + index + export

Fecha: 2026-06-16

## Incluye todo de v0.12 pro + v0.13 análisis + v0.14 index/export + hotfix tests

### Análisis automático
- `flujo analyze` – colores dominantes + OCR opcional
- `analysis/palette.json`, `palette.png`, `palette.aco`, `palette.ase`
- `analysis/ocr.txt`, `ocr_hints.json`
- docs/ANALISIS.md

### Index SQLite
- `flujo index --rebuild`
- DB: `data/flujo.db`
- `flujo flyer-list` rápido

### Export ZIP
- `flujo export <proyecto>`
- ZIP listo para Photoshop: input + analysis + manifest + LEEME.txt

### Tests fix
- test_analyze_colors usa PNG lossless, assert >=200
- test_index_rebuild (nuevo)
- test_export_zip (nuevo)
- 7 tests, todos pasan

### Archivos clave
```
src/flujo/
  analyze/colors.py, ocr.py, run.py, export.py
  index/db.py
  export/zipper.py
  cli.py  # comandos analyze / index / export
scripts/flyer_analyze.py
docs/ANALISIS.md
tests/test_smoke.py  # actualizado
.github/workflows/ci.yml  # pip install -e .
pyproject.toml  # version 0.14.0
```

Aplicar:
```
bash scripts/apply_airdrop.sh --dry-run
bash scripts/apply_airdrop.sh --apply
py -m pip install -e .
flujo health
pytest -q
bash scripts/checkpoint.sh "flujo v0.14 - analisis + index + export"
```

Comandos:
```
flujo flyer-import inbox/correo.txt
flujo ig-redownload
flujo analyze
flujo analyze --all
flujo index --rebuild
flujo export projects/flyer_eventos/2026-06-16_ig_XXXX
flujo app
```
