# Phase 317 — corpus projection consumer gate

Date: 2026-08-15 (America/Santiago)
Scope: one exact `mak_research` projection family only.

## Paths and ownership

- Canonical implementation: `/home/mak/flujo/cultura/mak_research/corpus_a_micelio.py`
- Root projection/legacy entrypoint: `/home/mak/research/corpus_a_micelio.py`
- Active consumer: `/home/mak/flujo/cultura/mak_conductor/handler_registry.py`, which imports
  `cultura.mak_research.corpus_a_micelio._main_unlocked`.
- Producer declaration: `/home/mak/flujo/cultura/mak_conductor/producer_catalog.py`.
- A paused historical cron projection also names the root path in
  `/home/mak/flujo/cultura/mak_plataforma/crontab.mak`; it is not active.

## Static and foreground validation

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
... AST parse, SHA-256 and byte-equality check for both paths ...
PY
```

Result: exit code 0. Both files parse; both are 8,511 bytes, SHA-256
`a5f14ead9e3d6aab9eac034615cd0aea6ee4297736d55edbe0f166a398265f03`, and are
byte-identical. The module exposes `_slug`, `_texto`, `documento`, `main` and
`_main_unlocked`.

The mutating path was not called. `main()`/`_main_unlocked()` can create and
rewrite `~/research/corpus`; this write set remains outside the pure gate.

Command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/mak/flujo:/home/mak/flujo/cultura/mak_research python3 - <<'PY'
... documento() fixture with author text, publication date and mtime ...
PY
```

Result: exit code 0, `PURE_DOCUMENT_FIXTURE=PASS`, `main_not_called=True`.
The fixture preserved author text separately, retained publication date and
mtime as distinct fields, and did not touch the corpus output directory.

The repository pytest command was attempted first:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/mak/flujo:/home/mak/flujo/cultura/mak_research python3 -m pytest -q /home/mak/flujo/tests/test_corpus_a_micelio.py`.
It returned exit code 1 because `/usr/bin/python3` has no `pytest` module;
no package was installed. The direct pure fixture and AST gate passed.

## Disposition

`PROTECT_CONSUMER_BACKED_WRITER_PROJECTION`.

Do not merge or delete either copy in this phase. The conductor owns the
canonical import, while the root copy is a historical/deployment projection
and is named by a paused cron manifest. Replacing it or running it would alter
the corpus write set. A future consolidation requires an explicit launcher
decision, corpus snapshot/rollback and a focused test environment.

## Changes and risks

- Source/data changes: none.
- Services, cron, providers and writers: not started.
- Risk: pytest availability is unresolved; the direct pure contract is covered,
  but the full test file still needs a pre-existing test runner or an explicit
  environment decision.
- Rollback: no rollback needed because no file changed.

