# Recovered Claude session corpus

This directory preserves candidate material recovered from the external
session tree on 2026-08-12. It is evidence, not an operational instruction
set and not an automatic source of truth.

`raw/` keeps source-relative paths. `docs/recovered/claude_sessions_2026-08-12/raw/MANIFEST.json` records the source
path, imported files, byte sizes, and SHA-256 values. The import deliberately
excludes `.venv`, Python caches, credential-shaped files, and the private
`claude_web_export_2026-08-11` directory.

Operational code must be promoted from this corpus only after a local test,
the existing department boundary, and a human gate where the material is
public-facing. The POST material is preserved here and is also registered in
`cultura/mak_post/` as an output boundary.

## Overlap with `docs/rd/prototypes/2026-08-11/` (medido 2026-08-28)

`raw/` and `docs/rd/prototypes/2026-08-11/` hold the **same files, byte for
byte**: `rd_grafo_relaciones_informe`, `rd_reactivos_auditoria_internacional`
(`.md` and `.json`), `rd_matriz_interactiva.html`, `rd_matriz_semantica_scraping`,
`rd_post_cover_prototype` (`.html`, `.svg`), `rd_post_chemsex_visual_brief_informe`,
`rd_indice_integracion_relaciones_informe`, and more. The recovery copied
instead of pointing.

Three files here are also byte-identical to live data under `data/rd_fuentes/`:
`rd_universo_entidades_2026-08-11.json` = `data/rd_fuentes/candidates/entity_universe_v0.1.json`,
`rd_indice_integracion_relaciones_2026-08-11.json` = `data/rd_fuentes/candidates/relation_index_v0.1.json`,
and `rd_testeos_eventos_2025_evidence_2026-08-12.json` (5.3 MB) =
`testeo_eventos_2025_evidence.json`.

Those duplicate pairs now **share an inode** (hardlink): every path still
resolves and the bytes are stored once. `docs/recovered/claude_sessions_2026-08-12/raw/MANIFEST.json` remains the
authority on provenance -- it records the source path and SHA-256 of each
imported file, and the dedup did not change a single hash.

Nothing was deleted from this corpus. If a promoted copy ever needs to diverge
from its twin, break the link first (`cp --remove-destination`), because a plain
edit would change both paths.
