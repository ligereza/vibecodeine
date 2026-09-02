# Phase 106 — curatoria panel/watchdog ownership merge

## Scope and evidence

The active MAK root and canonical copies of `panel.py` and `watchdog.py` were
byte-identical, as were their WIN historical copies. `panel.py` is a browser
server entrypoint and `watchdog.py` is a state-checking process; both have
direct consumers but neither was safe to start during this audit.

## Action

Replaced only `/home/mak/curatoria/panel.py` and
`/home/mak/curatoria/watchdog.py` with compatibility projections to canonical
MAK implementations. Direct entrypoint contracts remain represented; no
server, watchdog, notification or state mutation ran.

## Foreground validation

- Root imports for panel/watchdog: exit 0.
- Root/canonical bridges compile: exit 0.
- No panel server, watchdog, perception, worker, hub, Blender or Ollama
  process remained.

## Rollback and risk

Rollback is local from pre-edit root files or WIN copies. The panel server and
watchdog remain operational boundaries and were intentionally not launched.
`percepcion.py` remains a separate semantic gate because its WIN copy differs
in fallback diagnostics and path behavior.

## Result

Curatoria panel/watchdog now have one active MAK implementation owner while
WIN and stateful runtime surfaces remain preserved.
