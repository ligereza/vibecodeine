# Phase 334 — hub events and icon queue residual gate

Date: 2026-08-15 (America/Santiago)
Scope: two residual local-risk families from Phase 268.

## Boundary

- `/home/mak/flujo/tests/test_mak_hub_eventos.py` contract surface:
  malformed JSONL tolerance, local/live job ID union and orphan marking.
- `/home/mak/flujo/tests/test_mak_research_iconos_auto.py` contract surface:
  annex parsing, bounded icon queueing and best-effort Codex failure.

The repository pytest command was attempted with the existing venv and
returned rc=1 because `/home/mak/venvs/flujo/bin/python` has no `pytest`
module. No package was installed. Equivalent direct fixtures were run with
temporary directories and manual monkeypatches:

```text
HUB_EVENTOS_DIRECT_FIXTURE=PASS
ICON_QUEUE_DIRECT_FIXTURE=PASS
EXTERNAL_CALLS=0 PERSISTENT_WRITES=0
```

The hub test used a temporary JSONL file and replaced `_http_json`; the icon
test used a temporary concepts annex and replaced `_post_codex_icon`. Both
passed their core contracts, including the failure-is-best-effort behavior.

## Disposition

`VERIFIED_DIRECT_FIXTURE; TEST_RUNNER_MISSING`.

Count the behavior as bounded local evidence, not as a full pytest run. The
missing runner is an environment gap, not a reason to install packages during
this audit.

## Changes and risks

- Source, data, assets, services, providers, databases, Git and WIN: unchanged.
- Risk: the full test modules still need a future environment with pytest if
  a formal suite result is required.
- Rollback: none needed; only temporary fixtures were written.

