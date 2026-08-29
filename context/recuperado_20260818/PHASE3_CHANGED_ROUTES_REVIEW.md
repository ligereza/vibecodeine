# Phase 3 Changed Routes Review

Identity: LUNA-03

## Objective

Classify only the 14 Phase 2 routes marked `content_changed`, identify safe owner, consumer, dependency and contract candidates, and preserve the Phase 2 no-change decision.

## Scope

Target/runtime baseline: `/home/mak/flujo`. Historical material under `/home/mak/WIN` was used only through the three declared manifests and bounded provenance metadata. No active source or WIN archive was modified. Secrets, tokens, `.env` files, private data and mass contents were not read or printed.

## Method

Used the Phase 2 CSV as the closed route list; checked explicit target metadata, safe README/config/manifest declarations, file kind and bounded source contracts. The declared runtime consumer is `flujo = flujo.cli:app` from `pyproject.toml`. A candidate slice was selected only where an active test and generator contract are both explicit.

## Route classification

See the companion CSV for all 14 rows. Summary: 2 active source/tool routes, 1 active test, 1 generated output, 2 operational/recovered README or handoff documents, 4 recovered reports/evidence documents, 3 recovered evidence data/index artifacts, and 1 recovered source-like script.

## Consumer/dependency map

The only real active consumer map is:

`README.md` -> `tools/update_readme_svg.py` -> `arte-ascii-readme.svg` -> `tests/test_readme_svg.py` / pytest.

Dependencies are Python standard library plus the existing SVG and README files. The package entrypoint `flujo = flujo.cli:app` is validated separately as the runtime baseline but does not consume the recovered corpus routes.

## Candidate slice

The bounded slice is `tools/update_readme_svg.py`,
`arte-ascii-readme.svg`, and `tests/test_readme_svg.py`. It has one real
consumer chain and an explicit `--check` contract, but the SVG is an artwork.
The user explicitly decided to preserve the artwork and defer any generator
change. This slice is therefore `NO CHANGE`; no promotion is authorized.

## No-change items

All 14 rows retain `decision=no_change`. The active SVG/tool/test slice is
already present in the target and has no justified WIN payload to merge. The
user explicitly ordered that the README/SVG artwork remain untouched; the
generator drift is therefore recorded, not repaired. Recovered documents,
manifests, reports, data and the recovered source-like script have no declared
active consumer or promotion contract. `context/LAST_HANDOFF.md` remains
no-change because the historical final/postarchive/update hashes conflict and
the declared archive payloads are absent; preserve provenance only.

## Verification log

- `sed -n '1,240p' agents.md; sed -n '1,240p' context/LAST_HANDOFF.md; sed -n '1,240p' context/PHASE2_FLUJO_RECONCILIATION.csv; sed -n '1,320p' context/PHASE2_FLUJO_RECONCILIATION.md` -> exit 0; four required inputs read first.
- Bounded Python metadata probe over the 14 CSV-selected routes, `pyproject.toml`, and the three manifests -> exit 0; 14 routes, all targets exist, entrypoint and manifest schemas observed. The bounded output was truncated by the terminal renderer after safe metadata listing; no source payload was printed.
- `sed -n '/\[project.scripts\]/,/^\[/p' pyproject.toml; sed -n '1,220p' tests/test_readme_svg.py; sed -n '1,260p' tools/update_readme_svg.py; sed -n '1,120p' docs/recovered/claude_sessions_2026-08-12/README.md; ...awk...` -> exit 0; active SVG contract and recovered-corpus evidence boundary observed.
- `python3 tools/update_readme_svg.py --check` -> exit 2; active SVG differs from the current expected README-derived output. No write performed.
- Generator dry output changed the artwork hash from
  `2bda5d95340a56cad6ac8c2450aa33a127966a1db358497a5b4374863546f9db` to
  `73f33e4fcda7b9e745072d071a4c301923d022aa2edeb80eefd072d66d6402ec` and
  removed the literal `MAK` assertion; this was rejected as a regression.
- `cp /home/mak/flujo-deploy/arte-ascii-readme.svg
  /home/mak/flujo/arte-ascii-readme.svg` -> exit 0; target restored to the
  verified pre-change SHA-256
  `2bda5d95340a56cad6ac8c2450aa33a127966a1db358497a5b4374863546f9db`.
- Direct structural assertions after restore -> exit 0; viewBox, 30 frames,
  150 masks, 100 tspans, no clipPath and literal `MAK` all pass.
- `PYTHONPATH=/home/mak/flujo/src pytest -q tests/test_readme_svg.py` -> exit 127; `pytest` executable unavailable.
- `python3 -m pytest -q tests/test_readme_svg.py` and the same command with `PYTHONPATH` -> exit 1 each; Python reports `No module named pytest`.
- `PYTHONDONTWRITEBYTECODE=1 python3 -c 'import ast; ...rd_testings_2025_integration_build.py...'` -> exit 0; recovered source-like script parses without creating bytecode.
- Python stdlib CSV validation for this report -> exit 0; 14 rows, 10 columns, exact ASCII header, 14 `no_change` decisions, 3 candidate-slice rows.
- Final route/hash integrity probe -> exit 0 for route-set and section checks; all target hashes remained stable except `context/LAST_HANDOFF.md`, whose current hash is `6a1dbc3b96c3ad72406f9d61a92716fdf09f309d21ba9f717c1288143e14ae9b` versus the Phase 2 CSV snapshot `728a4babf2e72516c6673552530e82b7aab21e2d1fc24e6b0d053100e0a01ba0`. No Phase 3 write was made to that path; retain provenance-only no-change.

## Risks

Hash mismatch alone does not establish semantic superiority. Recovered files may contain sensitive or private session material; classification deliberately relies on metadata and declared boundaries. The recovered source-like script is not active code and must not be promoted by copying. The handoff hash discrepancy is explicitly preserved as provenance-only and remains outside the Phase 3 write set.

## Next action

Keep the SVG/tool/test slice as explicit `NO CHANGE` and choose the next
bounded non-artwork integration slice with a real consumer. Do not regenerate
or overwrite the artwork unless the user explicitly reopens that decision.

## Last checkpoint

2026-08-14 America/Santiago — LUNA-03 classification persisted for 14
`content_changed` routes; the SVG regeneration regression was rejected and the
artwork restored from `/home/mak/flujo-deploy`; no WIN archive changed.
