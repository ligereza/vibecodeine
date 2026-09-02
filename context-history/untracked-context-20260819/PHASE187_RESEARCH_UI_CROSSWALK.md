# Phase 187 — research UI candidate crosswalk

Status: `CANONICAL_SELECTED; LEGACY_PRESERVED`

## Comparison

| Candidate | Evidence | Decision |
|---|---|---|
| `/home/mak/research/interfaz.py` | Active user-service declaration points here; contains `BIND_HOST`, safer urllib error handling, fcntl lock support, and the current `/research/` Hub boundary | Canonical runtime candidate |
| `/home/mak/plataforma/interfaz.py` | Older 150,949-byte duplicate-shaped UI on the same port 8890; imports `pausa`, `formato_ensayo`, `research_lib` and `worker` without owning them, so isolated import/direct execution fails with `ModuleNotFoundError: pausa` | Legacy candidate; do not start or merge yet |

Both expose the same broad canvas routes and research output families, but the
`research` copy is newer and is the one referenced by
`/home/mak/.config/systemd/user/mak-research.service`. Running the platform
copy would compete for the same port and would not be a harmless parallel
check.

## Validation

- Static route/import comparison: completed without starting either UI.
- Isolated import of `/home/mak/plataforma/interfaz.py`: exit 1, missing local
  `pausa` module because the candidate is not self-contained.
- No UI process, socket, provider, worker, cron, service, package, WIN or Git
  action occurred.

## Decision and cleanup posture

The platform copy is a semantic duplicate candidate, not confirmed garbage:
its large inline UI and historical routes are evidence. The selected future
architecture is one Research UI owner under `/home/mak/research` backed by the
canonical source in `flujo/cultura/mak_research`. Before any quarantine or
replacement, preserve the old file and verify whether a human launcher still
references it.

Next: inspect launcher/config references for the legacy platform UI and
produce a reversible folder-architecture proposal. Do not move/delete the
legacy file in this phase.
