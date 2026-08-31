# Phase 87 — curatoria projection ownership gate

## Scope

Compared the same bounded consumer across the canonical source,
root-level MAK projection and WIN historical archive:

- `/home/mak/flujo/cultura/mak_curatoria/diagnostico_proyectos.py`
- `/home/mak/curatoria/diagnostico_proyectos.py`
- `/home/mak/WIN/flujo/cultura/mak_curatoria/diagnostico_proyectos.py`

All three SHA-256 values are
`48bf8c1ec4a0e7292ffdc691da5fecca11dd919e46633f187fbb43854616fa5c`.

## Foreground validation

- Canonical `py_compile` -> exit `0`.
- Root projection `py_compile` -> exit `0`.
- Canonical `--help` -> exit `0`.
- Root `--help` -> exit `0`.
- No database/output arguments were supplied, so no curatoria output was
  generated or modified.

## Ownership decision

This is an exact duplicate but **not confirmed junk**. The root curatoria
surface contains `fichas/fichas.jsonl`, drainage JSON/JSONL and operational
logs, and the root file retains a direct script entrypoint. The canonical
`cultura.mak_curatoria` is the active import source for conductor consumers;
the root remains a protected operational projection until its direct entrypoint
and state ownership are migrated explicitly.

No deletion or overwrite is justified by hash equality alone. WIN remains
historical and untouched.

## Next

Continue with another pure, consumer-backed duplicate or complete the root
curatoria ownership adapter before any further cleanup. Preserve state/logs and
avoid executing the diagnostic writer in this gate.
