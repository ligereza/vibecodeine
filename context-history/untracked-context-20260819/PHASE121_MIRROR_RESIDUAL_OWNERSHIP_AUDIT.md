# Phase 121 - mirror residual ownership audit

## Scope

Read-only comparison of canonical MAK department packages and their active
root projections:

- `flujo/cultura/mak_plataforma` -> `/home/mak/plataforma`
- `flujo/cultura/mak_curatoria` -> `/home/mak/curatoria`
- `flujo/cultura/mak_research` -> `/home/mak/research`
- `flujo/cultura/mak_codex` -> `/home/mak/codex`

The scan excluded virtual environments, caches and generated corpus/output
trees. WIN was not used as an inventory shortcut and was not changed.

## Result

After Phases 97-120, all root/canonical Python differences are either
documented compatibility projections or one remaining semantic candidate:

| Family | Remaining semantic Python candidate | Classification |
|---|---|---|
| platform | `entregar_micelio.py` | external writer: network, log/data writes and Git/PR actions |
| curatoria | none | remaining differences are projections or data/evidence surfaces |
| research | none | remaining differences are projections or corpus/evidence surfaces |
| codex | none | remaining differences are projections or piece/review surfaces |

The root departments still contain many non-code files: ledgers, state,
reports, research captures, proposals, corpus snapshots and human outputs.
Those are not duplicate tools and remain protected until their consumer and
provenance are mapped.

## Foreground command and result

A bounded SHA-256 comparison over `.py`, `.md`, `.json`, `.yaml`, `.yml`,
`.toml` and `.txt` files exited 0. It filtered `.venv`, `__pycache__`, cache
and generated corpus/output directories. The only non-projection semantic
Python difference was `plataforma/entregar_micelio.py`.

No imports, providers, network, Git, database, output or service action ran.

## Decision

Do not delete any department tree or classify the remaining data-only files as
junk. The mirror ownership problem is effectively closed for pure tool modules;
the last writer requires its own external-action gate.

## Next action

Read and statically gate `entregar_micelio.py` against its current consumer
and dry-run contract without calling the micelio, Git, network or log writer.
If its root variant is only documentation drift, make it a projection; if the
payload differs, preserve both until the external contract is explicit.
