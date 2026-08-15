# Phase 478 — remote candidate audit

The remote branch cleanup removed names, not useful objects. Historical heads
were preserved as `archive/remote/*` tags and compared against current `main`
on 2026-08-15.

## Useful code not yet in main

| Candidate | Physical evidence | Current status | Decision |
|---|---|---|---|
| `cultura/mak_research/fondart_corpus.py` | Exact blob match with `/home/mak/research/fondart_corpus.py` and `/home/mak/WIN/flujo/cultura/mak_research/fondart_corpus.py`; 31,568 bytes | Absent from `main`; present in `archive/remote/codex-three-plane-consolidation` | Retain as next research slice |
| `cultura/mak_research/source_pipeline.py` | Exact blob match with `/home/mak/research/source_pipeline.py` and WIN; 22,988 bytes | Absent from `main`; dependency of the Fondart candidate | Retain; validate offline before promotion |
| `src/flujo/knowledge/three_plane.py` and schemas | Present in the three-plane archive tag, absent from current `main` | Useful authority/provenance contract; not a runtime migration | Retain for a later read-only slice |
| `src/flujo/knowledge/reconciliation.py` | Present only in the three-plane archive tag | Reads SQLite sources read-only and emits a reconciliation plan | Retain; never run in write mode |
| `tools/inferential_archaeology.py` | Present in the research archive tag and recovered evidence | Useful for session/memory evidence, not an active consumer yet | Retain as evidence candidate |
| `tools/mak_ops/sync_mak_safe.py` | Present in archive/WIN/rollback material | Contains an explicit transport/apply path despite a read-only default | Do not promote until a separate authority gate |

## Already preserved or intentionally not restored

- Portfolio code in the historical web branches is older than the current
  `main` catalog boundary and is not restored wholesale.
- `openklub.yaml` and `paralelo_89.yaml` from old branches remain archived; the
  current corrections (producer/brand and lineup token, not venue) take
  precedence.
- The obsolete sync mutator and old service recipes remain historical/quarantined.

## Verification

The nine historical remote heads resolve as tags on GitHub. The Fondart and
source-pipeline physical files have identical Git blob IDs to the preserved
tag. No candidate was deleted, copied, executed against external providers or
promoted by this audit.

Disposition:
`USEFUL_RESEARCH_CANDIDATES_PRESERVED; NOT_YET_IN_MAIN;
PORTFOLIO_OLDER_VARIANTS_REJECTED; MUTATOR_NOT_PROMOTED`.

## Next bounded slice

Use `/home/mak/research/fondart_corpus.py` plus `source_pipeline.py` as the
candidate source, validate their offline contracts and tests against temporary
fixtures, then integrate the smallest complete source-preserving unit. Do not
call Firecrawl/Crawl4AI, modify research state, or create proposal outputs
until the offline gate passes.
