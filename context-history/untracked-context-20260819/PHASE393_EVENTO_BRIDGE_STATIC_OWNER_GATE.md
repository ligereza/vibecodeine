# Phase 393 — EVENTO issue/URL bridge static owner gate

Date: 2026-08-15 (America/Santiago)

## Owner and consumer

Canonical source: `/home/mak/flujo/cultura/mak_plataforma/puente_issues.py`.
Runtime path: `/home/mak/plataforma/puente_issues.py`, a 641-byte
`runpy` projection retained because the paused `crontab.mak` invokes the
physical runtime path. The conductor registry also names
`platform.puente_issues.una_pasada` as the issue-render producer.

## Static validation

| Check | Result |
|---|---|
| Canonical/runtime parse | both `py_compile` exit 0 |
| Runtime ownership | wrapper points to canonical absolute path |
| Consumer map | paused manifest plus `mak_conductor` registry; no active scheduler |
| Issue reader | `_gh issue list` is explicit in canonical source |
| URL extraction | Instagram links, shortcode and carousel index are parsed |
| Local state | `plataforma/puente_issues_estado.json`, RD inbox/render paths are explicit |
| External boundaries | GitHub CLI, rclone, Blender/Ollama and issue close are visible and gated |
| Current cron/process state | active cron 0; no bridge process started |

The user-confirmed EVENTO behavior is therefore represented by a canonical
owner plus runtime consumer. This phase did not replay an issue, call GitHub,
download Instagram, render Blender, upload with rclone, close an issue or
write bridge state.

Disposition: `EVENTO_BRIDGE_OWNER_VERIFIED; EXTERNAL_REPLAY_DEFERRED`.

Next action: refresh the 13-objective matrix with Phases 392–393 and keep
the bridge operationally paused unless an external replay is explicitly requested.
