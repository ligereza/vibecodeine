# Phase 268 — residual boundary and architecture handoff

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Residual inventory

After the Phase 267 CLI/manifest repair and the 13 local validator groups:

```text
promoted test files: 91
residual files: 89
residual executable-risk: 63
residual fixture-marked but externally bounded: 26
AST parse failures in residual classification: 0
```

The 26 bounded files are not safe local candidates for this task's current
authority boundary:

- autonomy/SSH/provider execution: `test_autonomia_cli.py`;
- concurrency/worker/queue: `test_backlog_descargar_concurrency.py`,
  `test_mak_backlog.py`, `test_mak_codex_nodos.py`,
  `test_mak_delegar.py`, `test_mak_hub_eventos.py`,
  `test_mak_micelio_ideas.py`, `test_mak_reanudar.py`,
  `test_mak_research_iconos_auto.py`;
- destructive scheduler: `test_cron_nocturno.py`;
- Git boundary: `test_idioma_ratchet.py`;
- provider/IMAP/Instagram/issue bridge: `test_eventos_flyer_auto.py`,
  `test_flyer_auto_parth.py`, `test_ig_*.py`, `test_imap_apagado.py`,
  `test_puente_issues.py`, `test_reception.py`;
- show/render external surface: `test_render_video_rd.py`,
  `test_resolume_automator.py`;
- explicitly excluded by the user: `test_xio_evidence.py`,
  `test_xio_portfolio_link.py`, `test_xio_superficie.py`.

The 63 executable-risk files remain parseable but were not batch-executed;
their imports/calls require per-consumer authority rather than a blanket test
run.

## Architecture transition

With local fixture candidates exhausted, the next work moves to the actual
MAK architecture: one canonical owner per tool, explicit runtime projections,
protected data/evidence, historical WIN, and quarantine only for confirmed
junk. No broad move or deletion is implied by this inventory.

## Next concrete action

Read the existing architecture disposition and compare it against current
physical consumers under `/home/mak/*`; produce one gap list of paths that
still need a real owner/consumer decision before any Git branch proposal.
