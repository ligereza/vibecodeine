# Phase 2 Flujo Reconciliation

## Objective

Map discrepancies between the active `/home/mak/flujo` baseline and the three historical WIN manifests without merging, copying, or changing runtime code.

## Scope

- Target: `/home/mak/flujo`; consumer: `flujo = flujo.cli:app` from `pyproject.toml`.
- Compared exactly 35 manifest-listed routes; no recursive scan of the large baseline/archive.
- Source paths were treated as historical evidence only. No `/home/mak/WIN` or active code changes were made.

## Sources

- `/home/mak/WIN/manifests/flujo-final-reconciliation-20260813.json`: schema `win-archive-reconciliation-v2`, status `final_post_handoff_reconciliation`, 35 entries (14 content_changed, 21 metadata_only), errors 0.
- `/home/mak/WIN/manifests/flujo-postarchive-reconciliation-20260813.json`: schema `win-archive-reconciliation-v1`, status `post_archive_worktree_reconciliation`, 35 entries (14 content_changed, 21 metadata_only), errors 0.
- `/home/mak/WIN/manifests/flujo-working-tree-update-20260813.json`: schema `win-archive-increment-v1`, status `post_archive_worktree_changes`, 14 changed-file subset, errors 0; superseded by final reconciliation.
- `/home/mak/WIN/README_ORIGIN.md` and `/home/mak/WIN/flujo/README.md`: WIN is a provenance snapshot, not runtime truth.
- `/home/mak/flujo/pyproject.toml`: declared entrypoint.

## Method

- Parsed JSON manifests and used `archive_relative` as the route key.
- Used manifest `source_sha256`; hashed only the 35 exact target files when present.
- Compared final against postarchive and update hashes; recorded conflicts explicitly.
- Checked existence and hash status without reading file contents for the reconciliation evidence.

## Discrepancy table

| Route | Source status | Target | Target status | Provenance note |
|---|---|---:|---|---|
| `arte-ascii-readme.svg` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `context/LAST_HANDOFF.md` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash; historical hash conflict: postarchive/update differs from final |
| `docs/recovered/claude_sessions_2026-08-12/README.md` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/83087cdd-3709-48de-ab41-62325e73d863_nombre-cauce.md` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/AX.html` | `metadata_only` | yes | `hash_match_source` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/MANIFEST.json` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/bases-texto-fondos-fondart-2027.json` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/claude_sesiones_index.html` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/claude_web_export_inventory.md` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/fondos-fondart-terminos-condiciones-requisitos-2027.md` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/fondos-postulaciones-requisitos-visible-2027.md` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/fondos-postulaciones-santiago-fondart-2026-extracto.md` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/fondos-postulaciones-santiago-fondart-2026.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/fondos-postulaciones-terminos-requisitos-2027.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/lasertoolkit.html` | `metadata_only` | yes | `hash_match_source` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/organismo.html` | `metadata_only` | yes | `hash_match_source` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_fichas_entidades_2026-08-11.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_firecrawl_2026-08-11.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_firecrawl_matriz_2026-08-11.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_fuentes_catalogo_2026-08-11.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_indice_integracion_relaciones_2026-08-11.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_post_chemsex_spec_2026-08-11.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_post_chemsex_visual_brief_2026-08-11.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_post_chemsex_visual_brief_informe_2026-08-11.md` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_post_cover_prototype_2026-08-11.html` | `metadata_only` | yes | `hash_match_source` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_post_cover_prototype_2026-08-11.svg` | `metadata_only` | yes | `hash_match_source` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_reactivos_auditoria_internacional_2026-08-11.md` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_reactivos_informe_2026-08-11.md` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_testeos_eventos_2025_evidence_2026-08-12.json` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_testeos_eventos_2025_informe_2026-08-12.md` | `metadata_only` | yes | `hash_mismatch` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_testings_2025_integration_build.py` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/rd_universo_entidades_informe_2026-08-11.md` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `docs/recovered/claude_sessions_2026-08-12/raw/sinreferencia.html` | `metadata_only` | yes | `hash_match_source` | WIN metadata_only; target retained independently; absent from 14-file working-tree update subset |
| `tests/test_readme_svg.py` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |
| `tools/update_readme_svg.py` | `content_changed` | yes | `hash_mismatch` | WIN content_changed; target differs from source hash |

Full source and target SHA-256 values are in `PHASE2_FLUJO_RECONCILIATION.csv`.

Summary: 35/35 target routes exist. 14/14 content_changed routes have target hash mismatches. 21/21 metadata_only routes exist; target hash matches source for the routes preserved from the WIN base and differs for the routes independently present in the active baseline. The final manifest and postarchive manifest have identical route sets, but one source hash differs: `context/LAST_HANDOFF.md`.

## Entrypoint verification

- `python3 -m flujo --help` -> exit code 1: `/usr/bin/python3: No module named flujo`.
- `PYTHONPATH=/home/mak/flujo/src python3 -m flujo --help` -> exit code 0; observed Typer help for `flujo` v0.56.1 and command list. This validates the module-level consumer against the source tree; the bare installed console command is not available in this environment.

## No-change decision

**NO CHANGE.** Do not copy or merge any WIN route into the active baseline in this slice. All target routes already exist, their source/target hash relations are documented, and the historical `LAST_HANDOFF.md` conflict is unresolved between final and postarchive/update manifests. Any integration would require owner/consumer/dependency review beyond reconciliation.

## Provenance conflict disposition

2026-08-14 verification compared the historical manifest metadata and checked
all declared archive destinations. The postarchive and final reconciliation
manifests recorded different hashes for `context/LAST_HANDOFF.md`; the later
`final-handoff-increment-20260813.json` and
`final-handoff-v2-increment-20260813.json` recorded further successive hashes.
The declared historical files are physically absent at the base archive,
both reconciliation increments and both final-handoff increments. Therefore
there is no historical payload available to select or merge. Under
`agents.md`, `/home/mak/flujo/context/LAST_HANDOFF.md` is the current MAK
operational handoff and `/home/mak/WIN` remains evidence only. Disposition:
classify this as a provenance-only conflict, preserve all manifest hashes,
and perform no copy, restore or merge.

## Risks

- Historical provenance conflict for `context/LAST_HANDOFF.md`: final source hash `54dd9c...afc1070`; postarchive/update source hash `e621d9...2b108`.
- Hash mismatch does not classify which side is semantically correct; no content merge was attempted.
- WIN excluded patterns: `.env`, `auth.json`, `cap_sid`, `.sandbox-secrets/**`, `*.key`, `id_rsa*`, `id_ed25519*`; excluded material was not inspected.
- All 35 routes exist in target, but presence is not integration or consumer use.

## Verification log

- JSON parse: all three manifests parsed successfully.
- Manifest counts: final/postarchive 35 entries each; update 14 entries; errors arrays empty.
- Target probe: 35/35 exact target paths exist; hashes recorded in CSV.
- Entrypoint: commands and exit codes recorded above.
- CSV validation: performed with Python standard-library `csv` reader after persistence.
- No permanent service, background worker, or Git inspection was used.
- `stat`/`sha256sum` on the current handoff and declared historical destinations:
  exit 0; current handoff exists at `/home/mak/flujo/context/LAST_HANDOFF.md`
  with SHA-256 `ab123d893d02b9e4317a2dea750ddfd4921479d82069f4a333065bd14d5dc7c1`;
  all five historical destination paths are absent.

## Next action

Review only the 14 `content_changed` routes for an explicit owner, consumer
and dependency before any integration decision. Keep the historical
`LAST_HANDOFF.md` conflict classified as provenance-only; do not restore its
absent archive payload.

## Last checkpoint

2026-08-14 America/Santiago: phase 2 reconciliation evidence persisted; the
historical `LAST_HANDOFF.md` conflict was classified as provenance-only after
all declared archive destinations were found absent; no-change decision held;
entrypoint validated with `PYTHONPATH`; active code and WIN archive unchanged.
