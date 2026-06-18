# AIRDROP 2026-06-18 — flujo v0.27.0 — Catálogo oficial de formatos (v2.0)

**Tipo:** Feature (datos + metadata + filtros CLI). Con tests. Retrocompatible.

## TL;DR
Convierte el mapa real de formatos de la ONG en el catálogo oficial del sistema,
con **área** (eventos/suplementos), **medio** (impresión/digital) y
**herramienta** (Illustrator/Photoshop/Blender), más filtros en
`flujo render formats`.

👉 Contexto completo: **`HANDOFF_2026-06-18_catalogo.md`**.

## Archivos
```
_airdrop/
├── HANDOFF_2026-06-18_catalogo.md
├── README_AIRDROP.md
├── README.md                                  # tabla por área + v0.27.0
├── pyproject.toml                             # 0.26.0 → 0.27.0
├── src/flujo/
│   ├── version.py                             # 0.27.0 + changelog
│   ├── cli.py                                 # render formats -a/-m/--herramienta
│   └── render/formats.py                      # metadata v2.0 + filtros
├── tests/
│   └── test_formats_catalogo.py              # 13 tests (NUEVO)
├── tools/piezas_vectoriales/plantillas/
│   └── INDEX_FORMATOS.json                    # catálogo v2.0 (12 formatos)
├── docs/
│   ├── CATALOGO_FORMATOS.md                   # catálogo explicado (NUEVO)
│   └── INTAKE_JSON.md                         # + area + ejemplos
└── schemas/
    ├── intake.schema.json                     # + area + tipos nuevos
    └── ejemplos/
        ├── cartelera_evento.json             # NUEVO
        └── pendon_suplemento.json            # NUEVO
```

## Aplicar
```bash
flujo airdrop apply "v0.27.0 - catalogo oficial de formatos"
# o manual:
bash scripts/apply_airdrop.sh --apply
bash scripts/checkpoint.sh "v0.27.0 - catalogo oficial de formatos"

py -m pip install -e .
flujo version            # 0.27.0
flujo render formats     # 12 formatos
py -m pytest tests/ -q   # 99 passed, 1 skipped
```

## Compatibilidad
- Retrocompatible: `formats.py` ignora campos que no usa; los 6 formatos previos
  siguen funcionando (renombrados con prefijo de área, plantillas intactas).
- Sin dependencias nuevas en runtime.
