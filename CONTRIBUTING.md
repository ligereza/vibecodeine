# Contributing to flujo

Personal creative-operations repo with a unified CLI (`flujo`).

## Mandatory entry point

1. Read `/home/mak/AGENTS.md`: current contract and pointers. Measure the
   machine with `.venv/bin/python tools/mak_status.py`; use
   `context/HANDOFF_HISTORICO.md` only as historical context.
2. Decisions already closed are recorded in `DECISIONES.md`; current state is
   not inferred from prose.

## Proposing changes

1. Issues are the user's channel (Gmail -> issue -> render), not a task board:
   agents do not open them. Describe the change in a message instead.
2. Branch + PR against `main`; CI must pass. No direct pushes to `main`.
3. Agents without push use the repository's explicit delivery mechanism and
   validate any airdrop payload with:
   ```bash
   py scripts/validate_airdrop.py
   py scripts/run_airdrop_checks.py "short message"
   ```

## Minimum verification

```bash
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```

## Code style

- Python 3.10+; typed with `from __future__ import annotations`; stdlib first.
- No `print()` inside modules: use `rich.console` or logging.
- Tests with pytest under `tests/test_<module>.py`.
- Do not commit heavy files or credentials.
- Windows uses `py` (not `python`/`python3`).

## Language

Write everything in this repo in English: code, comments, docs, commit messages,
PR titles and bodies. The one exception is anything a human reads as a product —
RD pieces and data, iskvw curation — which goes in correct Spanish **with
diacritics**. A title reading "reduciendo ano" instead of "reduciendo daño" is
not a typo, it is a defect that reaches the client.
