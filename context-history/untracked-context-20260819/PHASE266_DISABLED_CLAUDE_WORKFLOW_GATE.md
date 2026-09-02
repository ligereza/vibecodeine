# Phase 266 — disabled Claude workflow boundary

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Finding

The active test contract expected `.github/workflows/claude.yml`, but the file
was absent. The only physical source was the historical WIN workflow, whose
permissions included `contents: write`, `pull-requests: write` and
`issues: write`; promoting it would have reactivated an external write path.

## Action

Added one minimal active contract:

`/home/mak/flujo/.github/workflows/claude.yml`

It has only `workflow_dispatch: {}`, `permissions: {}` and a job guarded by
`if: ${{ false }}`. It contains no issue/PR trigger, Git push, PR creation or
write permission. WIN and all historical copies remain unchanged.

## Validation

The first run of the 16-file local candidate group exited `1` because the
missing file caused two `test_git_web_contract.py` failures. After the minimal
contract was added:

```text
pytest -q --disable-warnings \
  tests/test_becas_calendario.py tests/test_blender_nodes.py \
  tests/test_blender_nodes_video.py tests/test_busqueda_ciega.py \
  tests/test_capataz_enrutamiento.py tests/test_consulta_busqueda.py \
  tests/test_copilot.py tests/test_corpus_a_micelio.py \
  tests/test_git_web_contract.py tests/test_iconos_conjunto.py \
  tests/test_manifest.py tests/test_psicosis_agente.py \
  tests/test_reactivo_matcher.py tests/test_tilde_paridad.py \
  tests/test_validate_airdrop.py tests/test_zipper.py
exit 0; 188 tests passed
```

## Risk and rollback

No workflow was dispatched and no external system was contacted. Rollback is a
narrow removal of the new disabled contract after explicit review; do not
replace it with the writable WIN workflow.

## Next concrete action

Recalculate the residual candidate inventory, then continue only with pure
fixture groups. Keep all external/provider/worker/XIO/n8n and live mutation
paths deferred.
