# Phase 137 - MAK side-surface boundary audit

## Physical classification

| Surface | Current role | Decision |
|---|---|---|
| `/home/mak/flujo` | canonical authoring/integration baseline | active MAK owner |
| `/home/mak/flujo-deploy` | same-version deployment snapshot with its own manifests | preserve; separate deploy audit |
| `/home/mak/vibecodeine` | separate project/workspace with its own README and manifest | preserve; outside direct merge |
| `/home/mak/actions-runner` | CI runner infrastructure, credentials and logs | protected infrastructure; do not scan/clean broadly |
| `/home/mak/bucle` | separate small project (`No mas bucles`) | preserve as separate project |
| `/home/mak/n8n-local` | discarded integration surface with env and backup files | do not activate; preserve sensitive files until explicit disposal gate |
| `/home/mak/searxng` | service settings surface | do not start or alter during migration |
| `/home/mak/venv-providers` | provider virtual environment | dependency boundary; no install |
| `/home/mak/curatoria_test` | benchmark/fixture inputs and outputs | preserve test evidence |
| `/home/mak/curatoria_encolado` | empty staging directory | unresolved; no deletion by emptiness alone |
| `/home/mak/vigia` | live watch department | read-only gate passed; state protected |
| `/home/mak/lenguaje` | live Spanish-language department | read-only gate passed; cron/model writers gated |

The three `pyproject.toml` files in `flujo`, `flujo-deploy` and `vibecodeine`
have different SHA-256 values, so they are not a single exact manifest copy.
No side surface was merged, moved or deleted.

## Foreground validation

The bounded manifest/file inventory exited 0 and read only names, sizes and
known manifest paths. Credential contents, runner state and provider files
were not opened. No service, runner, n8n, SearXNG, provider or Git action ran.

## Next action

Use this boundary map in the final folder/cleanup matrix. Continue only with
MAK consumers and exact confirmed junk; keep side repositories, credentials,
runner logs, provider environments and discarded-service secrets protected.
