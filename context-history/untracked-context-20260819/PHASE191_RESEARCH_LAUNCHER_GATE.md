# Phase 191 — Research exact-duplicate launcher gate

Status: `NO_CHANGE; ALL_AUTOMATIONS_PAUSED`

## Evidence

The installed user crontab was read without modification. Every Research
automation line observed is prefixed with a `# PAUSED-DOCTOR-*` or
`# PAUSED-FARO` marker, including watchdog, corpus, micelio and retention.
No active line invokes the exact `research.sh` pair.

The exact runtime scripts have mode `0644`, so they are not directly
executable shell entry points. The active Python paths remain explicit in the
paused declarations and service files. `research.sh` is a manual wrapper that
delegates to the runtime `research.py`; it is not safe to quarantine solely
because the source/runtime bytes match.

## Decision

No file was moved or quarantined. The duplicate ledger remains valid, but a
safe move needs a separate launcher/consumer transition and a rollback check.
This is a correct no-change result, not a stalled investigation.

## Validation

- `crontab -l`: exit `0`; all relevant lines visibly paused.
- `stat` for exact shell scripts: exit `0`; mode `0644` observed.
- No process, service, provider, cron enablement, package, media, database,
  WIN or Git action occurred.

Next: select a non-runtime documentation family or build the final duplicate
role matrix; do not force a quarantine when the consumer gate is inconclusive.
