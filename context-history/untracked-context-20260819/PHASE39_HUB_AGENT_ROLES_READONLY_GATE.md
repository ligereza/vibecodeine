# Phase 39 — hub agent roles read-only gate

Identity: LUNA principal
Status: INTEGRATED_READ_ONLY_WITH_POLICY_BOUNDARY
Scope: validate the local role catalog exposed to the FLUJO hub UI without
dispatching roles or changing delegation state.

## Consumer and provenance

- Hub route: `GET /api/agents-roles`.
- MAK source: `/home/mak/flujo/src/flujo/web/hub.py`, method
  `HubRequestHandler._get_agents_roles`.
- WIN comparison source: `/home/mak/WIN/flujo/src/flujo/web/hub.py`.
- The route returns a static role definition map with prompt templates. The
  nearby `_handle_delegate` method was not called; no subagent, process,
  provider or delegation state was created.
- Search vocabulary used: `agent`, `agente`, `role`, `rol`, `delegate`,
  `delegar`, `creative`, `visual`, `pipeline`, `packaging`, `future`,
  `prompt`, `task`, `tarea`, `LUNA`. Residual risk is limited to future role
  definitions not returned by this route.

## Static and direct validation

Foreground command (exit 0):

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python - <<'PY'
  ast.parse(MAK hub.py); ast.parse(WIN hub.py)
  import flujo.web.hub
  HubRequestHandler._get_agents_roles()
PY
```

Observed:

- AST/import gate: `PASS`.
- Five unique ASCII role IDs: `creative-director`, `visual-polish`,
  `pipeline`, `future`, `packaging`.
- Each role has exactly `id`, `name`, `short`, `focus` and
  `prompt_template`; every template contains `{task}`.
- MAK/WIN role IDs match by bounded AST extraction.
- Direct response envelope keys: `roles`, `note`.

## Temporary HTTP gate

A temporary in-process `ThreadingHTTPServer` was bound to
`127.0.0.1:<ephemeral>`. Exactly one `GET /api/agents-roles` was served, then
the server was shut down and joined.

- HTTP status: `200`.
- HTTP payload matched the direct payload exactly.
- Dispatch called: `false`.
- Protected hub-source snapshot: `writes_detected=false`.
- No POST, subprocess, provider, network call or worker ran.

## Policy boundary and decision

The role catalog is integrated as a read-only UI contract and is physically
present in both WIN and MAK. It is not the delegation authority for this
migration: the active policy remains LUNA-only, maximum three active agents,
no recursive delegation, and traceable `LUNA-N` identities. The generic app
roles must not be used to infer or dispatch subagents in this task.

Rollback is physical preservation: retain the static role reader and do not
invoke `_handle_delegate` unless a separate, authorized delegation slice
defines its identity, write set and runtime boundary.

