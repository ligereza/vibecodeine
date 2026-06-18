# AIRDROP 2026-06-18 — flujo v0.30.1 — Fixes del editor

**Tipo:** Fixes (3 bugs reportados). Con tests. Retrocompatible.

## TL;DR
Arregla lo que el dueño reportó del editor:
- **Instagram** ahora detecta URLs sin `https://` (antes daba "sin links").
- **Preview SVG responsive**: ya no se sale de pantalla ni se ve deforme.
- **Formatos verticales** (flyer físico 10×14) cargan con la orientación correcta.

👉 Contexto completo: **`HANDOFF_2026-06-18_fixes_editor.md`**.

## Archivos
```
_airdrop/
├── HANDOFF_2026-06-18_fixes_editor.md
├── README_AIRDROP.md
├── pyproject.toml                         # 0.30.0 → 0.30.1
├── src/flujo/
│   ├── version.py                         # 0.30.1 + changelog
│   ├── intake/email_parser.py             # regex IG robusto
│   └── web/
│       ├── svg_preview.py                 # render_svg(responsive=...)
│       └── editor.py                      # preview responsive + orientación
└── tests/
    └── test_web_fixes.py                  # 11 tests (NUEVO)
```

## Aplicar
```bash
flujo airdrop apply "v0.30.1 - fixes editor (IG, preview, orientacion)"
py -m pip install -e .
flujo version            # 0.30.1
flujo serve              # probar pestaña INSTAGRAM con 'instagram.com/p/XXX/'
py -m pytest tests/ -q   # 155 passed, 1 skipped
```

## Compatibilidad
- Retrocompatible. Sin dependencias nuevas.
