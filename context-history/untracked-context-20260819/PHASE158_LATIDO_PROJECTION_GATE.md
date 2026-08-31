# Phase 158 — latido projection gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Selection

`latido.py` is the next exact platform projection with a declared consumer:
the `MAK-LATIDO` line in `crontab.mak`. The installed line is paused. Its
normal execution writes heartbeat index/state/log files and sends a loopback
POST to the research hub, so live execution is outside this gate.

## Scope decision

The source and target were byte-identical. The target will be reduced to a
wrapper pointing at the canonical source. The previous target is quarantined
for rollback. No cron entry is enabled, no hub is started, and no loopback or
external request is made during validation.

## Validation contract

Compile both source and wrapper. Execute both entrypoints through a temporary
HOME with `urlopen` and load average stubbed in-process. The fake response
keeps the test local while exercising the real main path, including seed/index,
state and log outputs. Compare the resulting output shape and confirm no
`/home/mak` state is touched.

## Result

Both files compiled with `/usr/bin/python3 -m py_compile` (exit 0). The
canonical and wrapper entrypoints were run in separate temporary HOME
directories with only the loopback request stubbed; both produced one heartbeat
state update, index `1`, the expected log marker and the same temporary file
shape. No real `/home/mak` heartbeat state, network service, cron or process was
used. The old exact runtime file is preserved at
`context/quarantine/phase158_latido_projection/latido.py.pre-wrapper`.
