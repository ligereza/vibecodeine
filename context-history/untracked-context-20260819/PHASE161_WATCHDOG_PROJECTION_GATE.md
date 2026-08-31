# Phase 161 — watchdog projection gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Selection

`watchdog_mak.sh` is an exact source/runtime projection and the direct
`MAK-ORGANISMO watchdog` cron target. The installed entry is paused. The
script can call `guardia.py`, inspect HTTP endpoints and request
`systemctl --user start/restart`, so live execution is explicitly excluded.

## Action and validation

Preserve the exact runtime copy in quarantine and replace only the target with
an executable wrapper to the canonical source. Run `bash -n` on both files and
check the declared dependencies (`flock`, `timeout`, `curl`, `systemctl`,
`guardia.py`, service-unit declarations) without invoking them. No unit,
health endpoint, lock, log or watchdog process is touched.

## Result

`bash -n` passed for canonical and wrapper. `flock`, `timeout`, `curl` and
`systemctl` are present; `/home/mak/plataforma/guardia.py`,
`mak-hub.service` and `mak-xio.service` are readable. The wrapper is
executable (`0755`) because the paused cron calls it directly. No command
invoked `systemctl`, `curl`, `guardia.py` or the watchdog; the process gate is
clear. The previous exact target hash
`fd0c16593e3b08c83e7dec058ca9fd9e52d6390709c15890dac645a19fb597b4` is
preserved in `context/quarantine/phase161_watchdog_projection/`.
