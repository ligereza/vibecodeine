# Phase 240 — Divergent Platform projection gate

## Result

The 20 divergent direct files from Phase 238 were inspected by file type and
entrypoint shape:

- 17 divergent Python files: all 17 parse successfully;
- 2 divergent shell files: both are non-empty wrapper/entrypoint surfaces;
- 1 divergent text file: `backlog_codex.txt`, a data output rather than a
  Python implementation;
- the runtime Python wrappers expose canonical source paths or explicit
  compatibility projections where their contract requires it.

The runtime stubs are intentional projections: for example, `puente_issues.py`
and `watchdog_mak.sh` retain historical `/home/mak/plataforma` entrypoints but
delegate to `/home/mak/flujo/cultura/mak_plataforma`. The paused manifest and
`mak-hub.service` still refer to runtime paths, so deleting or replacing them
without a foreground service gate would break the contract.

## Decision

No divergent file qualifies for quarantine from this gate. Objective 10's
remaining work is not “merge every different file”; it is per-file consumer
review for any legacy implementation that is not already a projection. The
canonical owner and runtime projection relationship is now verified for the
active family.

## Validation

- Local SHA-256 comparison: 56 shared files, 20 divergent.
- AST parse of all 17 divergent Python files: exit 0.
- Shell/text surfaces: non-empty and retained as entrypoint/data contracts.
- No SSH, service, cron, provider, deploy sync, file move or Git operation.

## Next concrete action

Close the local duplicate/tool audit with a final no-change decision for this
family, then return to the explicit external gates: real RD field input, live
mutator authority, optional runtime requirements and any physical DB choice.
