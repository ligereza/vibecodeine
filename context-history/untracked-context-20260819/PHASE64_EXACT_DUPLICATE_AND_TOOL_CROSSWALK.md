# Phase 64 — exact duplicates and equivalent-tool crosswalk

## Inventory boundary

Read-only hash inventory began at selected active MAK roots and excluded
`/home/mak/WIN`, `.git`, virtual environments, `__pycache__`, `node_modules`,
rollback trees, indexes, models and caches. It covered text/document formats
up to 50 MB; large media and binary files require a separate bounded pass.

Result: 6,678 files hashed, 320 exact-hash groups, 843 files in those groups.
This is a collision inventory, not a deletion list.

## High-confidence findings

| Collision family | Paths | Interpretation | Action |
|---|---|---|---|
| RD evidence JSON | `/home/mak/flujo/data/rd_fuentes/testeo_eventos_2025_evidence.json` and recovered Claude raw copy | same evidence with runtime and recovered provenance | keep both until provenance manifest records the canonical reader |
| RD reference PDFs | `/home/mak/RD/REFERENCIA_VALORES.pdf`, `/home/mak/flujo/REFERENCIA_VALORES.pdf`, `/home/mak/RD/New Folder/assets/brief_packs_plano_dark.pdf` | exact/related business documents in different workflow locations | compare human purpose; do not merge by hash alone |
| RD SVG/PDF workspace copies | `/home/mak/RD/suplementos/workspace-*/...` and `flyers_vector_2800x2000/...`; several `flujo/jobs/...` output pairs | source/output or delivery projections | preserve until job manifest identifies source and delivery |
| `flujo` HTML builds | `context/flujo_hub.html`, `context/plano_demo.html`, `context/svg_visualizer.html`; several `web/dist*/mapping.html` families | generated/static UI artifacts | classify build owner; no deletion without route check |
| platform mirror | `/home/mak/flujo/cultura/mak_plataforma/*` and `/home/mak/plataforma/*` exact pairs | repository source plus physical department projection | active FLUJO imports use `cultura.mak_plataforma`; root copy is a synchronized/projection surface |
| curatoria mirror | `/home/mak/flujo/cultura/mak_curatoria/*` and `/home/mak/curatoria/*` exact pairs | repository source plus department projection | active FLUJO imports use `cultura.mak_curatoria`; retain until sync policy is replaced |
| research mirror | selected exact pairs such as `research.py`, `research_lib.py`, `memoria.py` | shared library projection | many MAK consumers import the `cultura` implementation; root copy still has department/runtime context |
| codex mirror | `/home/mak/flujo/cultura/mak_codex/*` and `/home/mak/codex/*` exact pairs | source/projection pair | consumer and launcher audit required before consolidation |
| research corpus captures | repeated hash-identical captures across dated smoke/worker/version trees | reproducibility snapshots, not ordinary duplicates | preserve as research provenance; never collapse automatically |

## Consumer evidence

The following active consumers import the `cultura` implementations directly:

- `src/flujo/cli.py` and `src/flujo/autonomia.py` import
  `cultura.mak_plataforma`.
- `src/flujo/rd/database.py` loads `cultura/mak_research/fuentes.py`.
- `src/flujo/cultura/mak_conductor/handler_registry.py` dispatches
  `mak_research`, `mak_plataforma` and `mak_curatoria` modules.
- `src/flujo/cultura/mak_curatoria` imports `cultura.mak_plataforma`.
- `mak_vigia` reuses `research_lib` and `mak_plataforma` from the `cultura`
  tree.

This proves the mirror families are not independent competing tools. It does
not yet prove that the root projections can be removed: launchers, human
workflows, reports and the paused synchronization declaration still refer to
them. The next merge candidate is therefore a sync/projection policy, not a
file deletion.

## Tool merge candidates

| Candidate | Current owner | Consumer | Decision |
|---|---|---|---|
| `cultura/mak_plataforma` vs `/home/mak/plataforma` | `cultura` code is imported by FLUJO; root is projection | FLUJO CLI, autonomy, conductor, department users | consolidate ownership first; preserve root projection until launcher audit |
| `cultura/mak_curatoria` vs `/home/mak/curatoria` | `cultura` code is imported by conductor; root has matching files | curatoria ingestion/diagnostics and conductor | same as above |
| `cultura/mak_research` vs `/home/mak/research` | `cultura` modules are imported by many consumers | RD database, conductor, vigia, codex | same as above; corpus evidence stays separate |
| `cultura/mak_codex` vs `/home/mak/codex` | `cultura` package is the FLUJO-side source | codex handlers and human tools | inspect entrypoints before changing ownership |
| RD `flyer_auto.py` vs Windows automation scripts | Python FLUJO consumer vs external Blender/Adobe/EXE workflow | event issue/URL chain and human production | adapter/path contract, not blind merge |

## Decision

No duplicate is `JUNK_CONFIRMED` yet. The first safe consolidation slice is to
document one-way ownership and replace any whole-tree synchronization behavior
with an explicit projection contract, after verifying all root launchers. No
source, data, evidence, output or historical file was moved, merged or deleted.
