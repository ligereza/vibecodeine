# Phase 88 — research_lib projection gate

## Finding

`research_lib.py` is byte-identical across:

- `/home/mak/flujo/cultura/mak_research/research_lib.py`
- `/home/mak/research/research_lib.py`
- `/home/mak/WIN/flujo/cultura/mak_research/research_lib.py`

The files are not interchangeable by hash alone. The active canonical
`cultura.mak_research.research_lib` is imported by the conductor and tests,
while `cultura/mak_plataforma/roles.py` explicitly lists the root path
`/home/mak/research/research_lib.py` in `MODULOS`. `backlog_codex.py` and
`trabajo.py` consume that list for the local dogfood/cleanup rotation. The
mirror checker also treats `research_lib.py` as a required root projection.

## Validation

- Three-way SHA parity -> pass.
- Canonical and root source AST/compile -> pass in the MAK venv.
- Root path reference search -> confirmed in `roles.py`, mirror tooling and
  operational tests.
- No research worker, provider, queue or service was started.

## Decision

Status: `PROTECTED_ROOT_PROJECTION_WITH_ACTIVE_PATH_CONSUMER`. Do not delete
the root file or silently rewrite `roles.MODULOS`; doing so would change the
dogfood target and mirror contract. A future fusion requires an explicit
ownership adapter that updates those consumers and validates the research
workflow/rollback.

## Next

Continue with another pure duplicate/tool candidate, or design the bounded
research ownership adapter after the remaining consumer map is complete.
