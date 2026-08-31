# Phase 403 — promoted CLI v035 isolated fixture

Date: 2026-08-15 (America/Santiago)

## Static gate

`tests/test_cli_v035.py` was selected from the remaining excluded surface
because its two tests use `CliRunner`, `tmp_path` and
`FLUJO_WORKSPACE_ROOT`. AST/source review found no network, provider, Git,
process, service, desktop, GPU, XIO or durable MAK path.

## Foreground validation

```text
PYTHONDONTWRITEBYTECODE=1 /home/mak/research/.venv/bin/python -m pytest -q \
  /home/mak/flujo/tests/test_cli_v035.py
2 passed; pytest_exit=0
```

The `doctor` and `init --fresh --no-rebuild-index` calls wrote only below the
pytest temporary workspace. No real `/home/mak/flujo/workspace`, database,
credential, generated product, WIN file, service or external endpoint was
used.

## Residue observation

The bounded post-check found 18 pre-existing `.pyc` files under the separate
`/home/mak/src/ml-mobileclip` source surface. They were not deleted because
that tree is a distinct ML/tool owner and the test ran with
`PYTHONDONTWRITEBYTECODE=1`; no evidence established them as confirmed junk.

Disposition: `CLI_V035_FIXTURE_PROMOTED; SEPARATE_ML_BYTECODE_PRESERVED`.
