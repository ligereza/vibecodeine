# Phase 53 — vigia read-only gate

## Result

`/home/mak/vigia` has a real MAK consumer: the active operational declaration
`/home/mak/flujo/cultura/mak_plataforma/crontab.mak` schedules
`/home/mak/vigia/vigia_guardia.sh` hourly. The script owns its lock and calls
the local watcher with the configured sources, ledger and state paths. This
phase did not run that watcher, touch the network or mutate `estado/`.

## Foreground validation

```text
find /home/mak/* then bounded vigia/source listing
exit=0; runtime and FLUJO department surfaces both present

AST parse of /home/mak/vigia/vigia.py and cultura/mak_vigia/vigia.py
exit=0; both PASS

behavior-only AST parity (function/class docstrings removed)
result=True; the only raw difference is a documentation string

bash -n vigia_guardia.sh in runtime and source
exit=0

JSON parse of both fuentes.json files
exit=0; both valid, two top-level keys and six configured source entries

offline HTML fixture: extraer() + filtrar()
exit=0; 2 items extracted and 2 retained; no URL opener called

pytest focused attempt
not run: pytest command absent on MAK; no package installed
```

## Decision

`vigia` is `LIVE_LOCAL_CONSUMER_VERIFIED` for its static/parser contract.
Network freshness, notifications, append-only state and ledger enqueue remain
runtime behaviors outside this read-only gate. Keep the scheduled script and
state untouched. The next and final department gate is `xio_puente`, pending
ADB availability and explicit device-test authority.
