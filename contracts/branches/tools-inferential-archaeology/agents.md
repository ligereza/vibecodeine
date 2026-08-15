# Scoped branch contract

Branch: `tools/inferential-archaeology`
Owner: `LUNA-502`
Base: `main` at `536d807`
Domain: `tools`
Consumer: `tools/inferential_archaeology.py`

## Objective

Harden the offline inferential-archaeology index so generated SQLite, DuckDB
and summary artifacts cannot overwrite source files in the repository. Keep
the index read-only over Git, recovered sessions, memories and MAK activity.

## Allowed write set

- `tools/inferential_archaeology.py`
- `tests/test_inferential_archaeology.py`
- `contracts/branches/tools-inferential-archaeology/agents.md`
- `context/handoffs/tools-inferential-archaeology.md`

Generated outputs must go to `/tmp` or the ignored `out/` tree only. They are
not part of the branch write set.

## Read-only inputs

- `/home/mak/flujo/.git`
- `/home/mak/flujo/tools`
- `/home/mak/flujo/data`
- `/home/mak/.claude`
- `/home/mak/.codex`
- `/home/mak/claude_sesiones_recuperadas`

## Forbidden

Do not edit or delete source databases, recovered sessions, `WIN`, README,
historical context, provider state or generated public products. Do not call
model/provider APIs, start services, install packages or add network access.

## Validation gate

```text
python -m py_compile tools/inferential_archaeology.py tests/test_inferential_archaeology.py
python -m pytest -q tests/test_inferential_archaeology.py
python tools/inferential_archaeology.py build --repo /home/mak/flujo --output /tmp/...
python tools/inferential_archaeology.py report --sqlite /tmp/.../evidence.sqlite
git diff --check
```

The gate must include a negative output-path test and a source hash check.

## Rollback

Do not remove evidence. Revert this branch commit or delete the short-lived
branch after promoting durable facts to the root handoff.
