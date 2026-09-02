# Phase 116 — tandas CLI and autonomia dry-run gate

## Scope

Validate the current automation preparation contract across canonical MAK,
root MAK and WIN without promoting external results or writing operational
ledgers.

## Foreground validation

For each `tandas.py` variant, the following commands exited 0:

- `areas`
- `brief rd_evidence phase116 --providers groq --no-premium`
- `summary --ledger <temporary-missing-ledger>`

The three variants returned the same eight areas, `rd_evidence`/`phase116`,
provider plan `['groq']`, and valid brief output. Temporary outputs were under
`/tmp/phase116-tandas-*`; no production ledger was created.

The current canonical automation launcher also passed:

```text
/home/mak/venvs/flujo/bin/flujo autonomia run \
  --executor local --dry-run --no-ollama --allow-dirty \
  --areas rd_evidence --providers watsonx --round-id phase116 \
  --out-dir /tmp/phase116-autonomia-*/out \
  --common-ledger /tmp/phase116-autonomia-*/common.jsonl \
  --batch-ledger /tmp/phase116-autonomia-*/batch.jsonl
```

Exit `0`, result `ok=true`, `status=briefed`; one temporary brief was created
under `/tmp`. No provider, Ollama, AWS, SSH, ledger publication or persistent
process occurred. The preflight reported the already-dirty worktree; no Git
operation was performed.

## Decision

Automation preparation is `DRYRUN_VERIFIED` for this slice. External execution
and production ledger publication remain authority-gated. The `tandas.py`
semantic fork remains open because its evidence paths and WIN dispatch payload
fields differ despite equal basic CLI contracts.

## Next action

Continue the final platform read-only audit and then reconcile remaining open
objectives; do not convert the dry-run brief into a published result.
