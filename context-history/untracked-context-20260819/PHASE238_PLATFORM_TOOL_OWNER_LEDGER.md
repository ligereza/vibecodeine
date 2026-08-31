# Phase 238 — Platform tool owner/equivalence ledger

## Scope

Read-only comparison of the direct files shared by the canonical source
`/home/mak/flujo/cultura/mak_plataforma` and the Linux runtime projection
`/home/mak/plataforma`. No SSH, service, cron, provider or deploy sync was
used. The existing `tools/mak_ops/check_mak_mirror.py` was not executed because
its implementation calls SSH to `192.168.50.2`, which is outside this plan.

## Result

The two local surfaces share 56 direct files:

- 36 are byte-identical by SHA-256;
- 20 are divergent and must not be merged by filename;
- 32 active source/test files import or directly consume the canonical
  `cultura.mak_plataforma` package.

### Exact copies

Exact copies are classified as runtime projections, not as two independent
owners. Their source of truth is `cultura/mak_plataforma`; the `/home/mak/plataforma`
path is retained because the installed service/paused manifest refers to it.
This is the safe fusion shape: one semantic owner, one compatibility path.

### Divergent files

`backlog.py`, `backlog_codex.py`, `backlog_codex.txt`, `backup.sh`,
`capataz.py`, `chat_agente.py`, `coherence.py`, `contrato_archivo.py`,
`entregar_micelio.py`, `junta.py`, `latido.py`, `material.py`,
`puente_issues.py`, `revision.py`, `roles.py`, `salud.py`, `tandas.py`,
`trabajo.py`, `vigilar_red.py` and `watchdog_mak.sh` differ in content or
size. They include operational stubs, runtime-specific state and provider/
automation boundaries. They remain at both paths until each has a consumer
crosswalk and foreground gate.

## Consumer and platform evidence

- `flujo` imports the canonical package in CLI/autonomy/conductor/curatoria
  paths, and its tests target the canonical source.
- `mak-hub.service` points to `/home/mak/plataforma/hub.py`; the paused
  `crontab.mak` manifest points multiple operational jobs to
  `/home/mak/plataforma/*.py`.
- The installed crontab has zero active entries and all relevant user units
  are inactive, so no runtime copy was executing during this audit.
- Human-facing content is Spanish; identifiers and machine metadata remain
  ASCII; the paths are Linux runtime paths. Windows-origin references remain
  historical in `/home/mak/WIN`.

## Decision

Objective 10 advances to `OWNER_FUSED_WITH_RUNTIME_PROJECTIONS`: canonical
ownership is established for the equivalent family, while divergent files are
explicitly unresolved rather than falsely merged. No files changed.

## Next concrete action

Apply the same consumer-ledger method to the remaining document families and
the 20 divergent platform files. Only a specific file with a proven redundant
launcher may enter reversible quarantine; preserve working runtime paths and
historical evidence.
