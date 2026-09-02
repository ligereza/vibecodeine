Identity: LUNA principal

# Phase 33 — ISKVW show-kit/setlist read-only gate

## Decision

The ISKVW show-kit surface is integrated in MAK as a local read-only hub
consumer. `GET /api/show-kit` reads the setlist, duration map, cue map and
saved JSONL records from `xio/show_kit/`; it does not activate the show
hardware chain. The same six read-surface files exist in WIN with equal content
after CRLF/LF normalization. No relay, OSC, Chataigne, Resolume, phone or
venue network was contacted.

The hardware-facing scripts and Windows launchers remain separate evidence and
are not promoted by this gate: `artnet_relay.py`, `cue_engine.py`,
`map_dref.py`, `relay_luces.bat`, `cargar_setlist.bat` and `cue_engine.bat`.

## Vertical contract

```text
ISKVW / Show kit
    -> GET /api/show-kit
    -> xio/show_kit/setlist_festival_sentir.txt
    -> xio/show_kit/setlist_durations_dref.json
    -> xio/show_kit/cue_map_dref.json
    -> xio/show_kit/registros/**/*.jsonl (evidence counts only)
```

The API returns normalized setlist fields `indice`, `timecode`, `tema`,
`duracion_s`; cue fields `timecode`, `layer`, `clip`, `nota`; and record
summaries with file names, event counts and sizes. It returns no relay command,
OSC destination or live phone state.

Search vocabulary covered both language variants and aliases: `show kit`,
`show-kit`, `show`, `setlist`, `lista`, `cues`, `señales`, `timecode`,
`timecode`, `OSC`, `relay`, `puente`, `hardware`, `FOH`, `Resolume`,
`Chataigne` and `registro`/`record`.

## Static and fixture gate

Foreground command: AST parse of the hub and four show-kit scripts without
importing or executing hardware modules; JSON/JSONL schema checks; direct
read-only invocation of the hub reader on an uninitialized handler object; and
normalized-content crosswalk of the six input/evidence files against WIN.

Observed exit code: `0`.

- AST parse: 4 modules, PASS. Hardware modules were not imported or run.
- Inputs: 21 duration entries, 21 cues, 21 setlist lines, FPS 30, PASS.
- Records: 3 JSONL files, 2,384 JSON objects, 0 invalid rows, PASS.
- Hub reader: 21 setlist items, 21 cues, 1 recorded show, connected true,
  allowlisted output, PASS. Nineteen items have measured durations; two are
  explicitly `null` in the source and remain unknown.
- WIN/MAK read surface: 6 files, normalized content equal, PASS.

## Temporary HTTP result

After documenting the boundary, a temporary in-process
`ThreadingHTTPServer` bound to `127.0.0.1:<ephemeral>` served one GET request
and was shut down, closed and joined in the same foreground command.

- `GET /api/show-kit`: HTTP 200; 21 topics, 21 cues, 1 record group and 19
  measured durations, PASS.
- Temporary server shutdown: PASS.
- Snapshot of the hub and every file under `xio/show_kit/`:
  `writes_detected=0`.
- No POST, relay, OSC, hardware, network, launcher, package install or
  permanent service was used.

Final status: `INTEGRATED_READ_ONLY`.

## Mutation boundary and rollback

The endpoint reads local text, JSON and JSONL only. Hardware scripts and
external addresses are outside the call graph exercised here. Rollback is
temporary-server shutdown; if any protected file changes, reject the gate and
preserve the existing reader. Any future activation of OSC/Art-Net/Resolume
must be a separate platform-specific phase with an explicit dry-run boundary.

## Risks and next action

- The saved records prove historical show evidence, not current hardware
  availability or live phone state.
- The Windows `.bat` launchers and network/hardware relays remain
  Windows/venue-specific and are not Linux runtime dependencies.
- The next unresolved hub consumer is the optional MAK status panel
  (`/api/mak`) or the deferred mutating automation surface. Select only a
  read-only local target next; do not call external MAK URLs or activate
  automation without a new boundary.
