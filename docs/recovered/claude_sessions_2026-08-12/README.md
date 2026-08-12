# Recovered Claude session corpus

This directory preserves candidate material recovered from the external
session tree on 2026-08-12. It is evidence, not an operational instruction
set and not an automatic source of truth.

`raw/` keeps source-relative paths. `raw/MANIFEST.json` records the source
path, imported files, byte sizes, and SHA-256 values. The import deliberately
excludes `.venv`, Python caches, credential-shaped files, and the private
`claude_web_export_2026-08-11` directory.

Operational code must be promoted from this corpus only after a local test,
the existing department boundary, and a human gate where the material is
public-facing. The POST material is preserved here and is also registered in
`cultura/mak_post/` as an output boundary.
