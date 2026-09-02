# Phase 195 — platform roles projection gate

Status: `PASS_NO_CHANGE`

`/home/mak/plataforma/roles.py` is a runtime projection of
`/home/mak/flujo/cultura/mak_plataforma/roles.py`. The coherence reader flags
the files as different because one is a thin wrapper, but the exported policy
surface was compared directly.

## Result

The source/runtime projection matched for all checked fields:
`VERBOS`, `CADA_MIN`, `MAX_DIA`, `GAP_MIN`, `GAP_MIN_OFFLINE`, `LOAD_MAX`,
`MODULOS` and `SEMILLAS`. The policy exposes nine verbs, six module paths and
eight fallback seeds. The runtime wrapper therefore preserves the canonical
policy and does not need synchronization or editing.

## Validation

- Isolated source/runtime import and field comparison: exit `0`.
- No providers, network, worker, service, cron, package, file output, WIN or
  Git action.
- No persistent process remained.

Decision: `NO_CHANGE`; retain the canonical owner plus the runtime projection.
