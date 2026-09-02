# Phase 159 — vigilar_red projection gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Selection

`vigilar_red.py` is an exact source/runtime projection and the declared
`MAK-VIGILAR` cron target. The installed cron line is paused. The script reads
established TCP connections, writes
`/home/mak/plataforma/logs/vigilar_red.json`, and can publish an ntfy alert;
therefore its live `revisar()` path is not called here.

## Action and boundary

The exact runtime copy is preserved in quarantine and the active projection is
replaced with a wrapper to the canonical source. Validation is limited to
compile plus import/constant resolution. No `ss` scan, log write, ntfy call,
cron activation or service was executed.

## Result

`/usr/bin/python3 -m py_compile` passed for canonical and wrapper. Importing
the wrapper without invoking `main()` resolved the canonical path correctly;
the process gate found no `vigilar_red.py` process. The previous exact target
hash `8487f0953f0c67f8404291803e9910cf3280bf0eb9db5f12ad0a1e9d1da2647c` is
preserved in `context/quarantine/phase159_vigilar_red_projection/`.
