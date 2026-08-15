# Scoped branch contract

Branch: `iskvw/publication-gate`
Owner: `LUNA-505`
Base: `main` at `e0ff6a1`
Domain: `iskvw`
Consumer: `.github/workflows/publicar_iskvw.yml`

## Objective

Make the existing explicit GitHub Pages publication boundary executable in
tests: only `iskvw/` is deployable, while RD databases, technical venue JSON,
MAK, Curatoria and WIN remain outside the public artifact.

## Allowed write set

- `tests/test_git_web_contract.py`
- `contracts/branches/iskvw-publication-gate/agents.md`
- `context/handoffs/iskvw-publication-gate.md`

The workflow and all publication inputs are read-only in this branch.

## Validation gate

```text
python -m pytest -q tests/test_git_web_contract.py tests/test_gen_archivo_iskvw.py
python -m py_compile tools/gen_archivo_iskvw.py
git diff --check
```

The gate must assert explicit dispatch, `iskvw/`-only copy scope and absence
of RD/venue/MAK/WIN paths in the publication workflow.

## Forbidden

Do not deploy, call Cloudflare, change domain settings, edit generated site
files, expose technical venue records, merge databases or touch README/WIN.

## Rollback

Revert the test-only commit or delete the short-lived branch. The existing
manual Pages workflow remains unchanged.
