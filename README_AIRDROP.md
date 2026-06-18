# AIRDROP 2026-06-18 — flujo v0.30.2 — IG: usuario + descarga + paleta

**Tipo:** Fix + features (amplía el 0.30.2 previo no aplicado). Con tests. Retrocompatible.

## TL;DR
- **Fix:** detecta `instagram.com/<usuario>/p/CODE/` (el formato que reportaste).
- **Nuevo:** la pestaña INSTAGRAM ahora **descarga el post** (instaloader),
  **extrae la paleta** de colores y permite **aplicarla a la pieza** del editor.

👉 Contexto: **`HANDOFF_2026-06-18_ig_descarga.md`** · Guía: `docs/EDITOR_INSTAGRAM.md`.

## Archivos
```
_airdrop/
├── HANDOFF_2026-06-18_ig_descarga.md
├── README_AIRDROP.md
├── pyproject.toml                          # 0.30.1 → 0.30.2
├── src/flujo/
│   ├── version.py                          # 0.30.2 + changelog
│   ├── intake/email_parser.py              # regex IG con <usuario>
│   └── web/editor.py                       # descarga + paleta + pestaña ampliada
├── tests/
│   ├── test_ig_usuario.py                  # 7 tests del regex
│   └── test_ig_download_palette.py         # 7 tests (descarga mock + paleta)
└── docs/
    └── EDITOR_INSTAGRAM.md                  # NUEVO
```

## Aplicar
```bash
flujo airdrop apply "v0.30.2 - IG usuario + descarga + paleta"
py -m pip install -e .
flujo version            # 0.30.2
flujo serve              # INSTAGRAM: Analizar → Descargar → Aplicar paleta
py -m pytest tests/ -q   # 168 passed, 1 skipped
```

## Compatibilidad
- Descarga solo con instaloader (ya era dependencia). Sin libs nuevas.
- Retrocompatible.
