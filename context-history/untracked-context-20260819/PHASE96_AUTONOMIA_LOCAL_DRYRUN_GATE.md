# Phase 96 — autonomia local dry-run gate

## Scope

Validated the local preparation path for FLUJO automation without calling a
provider, SSH executor or Ollama. The user-confirmed external contract remains
separate: `EVENTO ...` email -> issue -> URL -> processing.

## Foreground command

```text
/home/mak/venvs/flujo/bin/flujo autonomia run \
  --executor local --dry-run --no-ollama --allow-dirty \
  --areas rd_evidence --providers watsonx \
  --round-id phase96 --out-dir /tmp/phase96-autonomy-... \
  --common-ledger /tmp/phase96-common-...jsonl \
  --batch-ledger /tmp/phase96-batch-...jsonl
```

Result: exit `0`, `ok=true`, `status=briefed`, one temporary
`rd_evidence-phase96-watsonx.json` brief. The generated contract included
primary-source, triangulation and uncertainty fields plus the local-review
schema and allowed actions.

## Safety

- No provider API, Ollama, AWS, Watsonx or SSH call occurred.
- No common/batch ledger was created in dry-run.
- Output existed only under `/tmp`.
- No persistent process remained.
- `--allow-dirty` was used only to bypass the existing diagnostic dirty-state
  preflight; no Git operation ran.

## Decision

Local automation preparation is `DRYRUN_VERIFIED`. External execution and
production ledger publication remain authority-gated.

## Next

Continue with remaining ownership merges and explicit external/mutator gates;
do not convert a dry-run brief into a published result.
