# Phase 267 — CLI manifest reconciliation

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Finding

The local `tools/gen_mapa_comandos.py --check` exposed a real stale contract:
`context/comandos.json` and the generated command block in `MAPA.md` did not
match the current CLI. The first candidate-suite run exited `1` in
`test_comandos_manifiesto.py`.

## Action

Updated the generator's `autonomia run` requirement to describe local dry-run
boundaries without SSH or the obsolete MAK address. Then regenerated only the
active command contracts:

- `/home/mak/flujo/tools/gen_mapa_comandos.py`
- `/home/mak/flujo/MAPA.md`
- `/home/mak/flujo/context/comandos.json`

The generator reported 95 current commands. WIN was not modified.

## Validation

```text
tools/gen_mapa_comandos.py
exit 0; context/comandos.json updated; MAPA.md updated

tools/gen_mapa_comandos.py --check
exit 0; MAPA.md y context/comandos.json al dia con el CLI.

Focused ISKVW/validator group after repair:
exit 0; 110 tests passed
```

The group covered position/phase contracts, manifest generation, fiche
consolidation, Curatoria round-trip, documentation hygiene, safe hub command
allow-list, Chataigne fixture shape, ISKVW skin/stands/index validation and
Curatoria/vinculos validators. All external calls were local or fixture-bound.

## Risk and rollback

No service, workflow, provider, database, Git or external route was invoked.
Rollback is a narrow restoration of the three active generated contracts plus
the generator wording; do not restore the stale SSH requirement.

## Next concrete action

Recalculate the residual risk inventory after these 13 additional promoted
tests. Continue only with pure local candidates; keep XIO, n8n, workers,
providers, external integrations and live mutators deferred.
