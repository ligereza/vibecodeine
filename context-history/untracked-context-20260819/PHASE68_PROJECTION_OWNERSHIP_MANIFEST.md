# Phase 68 — projection ownership manifest

## Rule

The FLUJO repository-side `cultura/mak_*` trees are canonical source for
runtime imports. Root department directories are projections or operational
surfaces. A projection may be refreshed only by a bounded, explicit file set
after parity and consumer validation. Whole-tree copy/sync is prohibited for
the active workflow.

## Verified projection set

| Domain | Canonical source | Protected projection | Verified slices | Remaining risk |
|---|---|---|---|---|
| plataforma | `flujo/cultura/mak_plataforma` | `/home/mak/plataforma` | `ledger.py`, `contrato_archivo.py` | root has state, launchers and one broken panel |
| curatoria | `flujo/cultura/mak_curatoria` | `/home/mak/curatoria` | parity inventory only | root has state, logs and guards |
| research | `flujo/cultura/mak_research` | `/home/mak/research` | parity inventory only | root includes corpus, queues, locks and providers |
| codex | `flujo/cultura/mak_codex` | `/home/mak/codex` | parity inventory only | root includes malformed generated pieces and job state |

## Allowed future refresh contract

Each refresh must name source files, target files, consumer, expected hash,
foreground validation and rollback. It must not copy a directory recursively,
overwrite state, alter logs, touch environments or activate a service. Files
with equal hashes are already behaviorally identical for the tested slice and
need no refresh.

## Explicit exclusions

- `/home/mak/WIN` is historical and never a projection target.
- `n8n-local`, XIO, hardware, ADB and provider services are outside the active
  migration plan.
- Databases, JSONL ledgers, locks, logs, virtual environments, corpus captures
  and generated products are not source projections.

This manifest is a control document. It changed no projection or runtime file.
