# Contributing to flujo

Personal creative-operations repo with a unified CLI (`flujo`).

## Mandatory entry point

1. Read `SYSTEM.md` for durable identities and invariants.
2. Measure the current checkout with `python tools/contexto_repo.py --json`.
3. Use `python tools/mak_status.py --json` when MAK runtime status matters.
4. The persistent `AGENTS.md` / handoff entry contract is retired.

## Proposing changes

1. Issues are the user's channel (Gmail -> issue -> render), not a task board:
   agents do not open them. Describe the change in a message instead.
2. Branch + PR against `main`; CI must pass. No direct pushes to `main`.
3. Agents without push must deliver changes through an explicit reviewed branch/PR path; Airdrop is retired.

## Minimum verification

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m flujo verify
```

## Code style

- Python 3.10+; typed with `from __future__ import annotations`; stdlib first.
- No `print()` inside modules: use `rich.console` or logging.
- Tests with pytest under `tests/test_<module>.py`.
- Do not commit heavy files or credentials.

## Language

Write everything in this repo in English: code, comments, docs, commit messages,
PR titles and bodies. The one exception is anything a human reads as a product —
RD pieces and data, iskvw curation — which goes in correct Spanish **with
diacritics**. A title reading "reduciendo ano" instead of "reduciendo daño" is
not a typo, it is a defect that reaches the client.
