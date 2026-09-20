# Contributing to flujo

Personal creative-operations repo with a unified CLI (`flujo`).

## Mandatory entry point

1. Read `DECISIONES.md` for operator decisions and measure the machine with
   `.venv/bin/python tools/mak_status.py`. There is intentionally no root
   agent-contract or active handoff file.
2. Current state is not inferred from prose;
   `context/HANDOFF_HISTORICO.md` is consulted only to investigate history.
3. Vocabulary already settled (what MAK, `vibecodeine`, IRIS,
   RD and Portfolio each mean) live in `MEMORIAS.md`. Read it before answering
   a nomenclature question instead of re-deriving it from scattered docs.

## Proposing changes

1. Issues are the user's channel (Gmail -> issue -> render), not a task board:
   agents do not open them. Describe the change in a message instead.
2. Branch + PR against `main`; CI must pass. No direct pushes to `main`.
3. Agents without push use the repository's explicit delivery mechanism and
   validate any airdrop payload with `.venv/bin/python scripts/validate_airdrop.py`.

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
