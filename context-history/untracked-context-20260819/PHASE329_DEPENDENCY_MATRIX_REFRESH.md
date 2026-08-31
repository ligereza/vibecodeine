# Phase 329 — dependency matrix refresh

Date: 2026-08-15 (America/Santiago)

| Slice | Active consumer | Evidence | Disposition |
|---|---|---|---|
| Base CLI/RD/privacy/hub | `flujo.cli`, `flujo.rd.*`, `flujo.web.hub` | six imports pass; venv `pip check` rc=0 | `VERIFIED` |
| RD temporary builder/ingest/report | database/data/informe | temporary DB/CSV fixtures pass; canonical DB unchanged | `VERIFIED_TEMPORARY` |
| Plano/symbol tracing | `plano.engine`, `plano.trazador` | Pillow in-memory SVG/rider fixture passes | `VERIFIED_PIL` |
| Laser measurement | `flujo.laser medir` | existing SVG measured; no external dependency | `VERIFIED_LOCAL_QUALITY_GATE` |
| Laser generation | `flujo.laser hatched/flow` | vpype/hatched/flow missing; state rc=1 | `OPTIONAL_UNRESOLVED` |
| Research source gate | `mak_research.fuentes` → RD database | bilingual primary/secondary fixtures pass | `VERIFIED_STDLIB` |
| Research/Codex provider calls | `research_lib` provider methods | not called by this audit | `EXTERNAL_GATED` |
| Desktop/package extras | pywebview/pystray/PyInstaller | absent; not required for Linux CLI/hub baseline | `OPTIONAL_WINDOWS_GATED` |
| Windows global environment | received Windows `pip check` conflicts | evidence only; not Linux contract | `OUT_OF_SCOPE_FOR_LINUX_REQUIREMENTS` |

## Decision

The active Linux base does not need a dependency edit. Optional laser and
Windows desktop/provider surfaces remain explicit boundaries; installing them
would be a new operational decision, not cleanup.

