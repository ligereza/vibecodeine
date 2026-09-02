Identity: LUNA-12

# Operational declarations triage

## Scope

Read-only semantic triage of service/unit files, crontab/timer declarations, watchdog/guardia scripts, queue/worker/backup/restore paths, locks, and operational entrypoints across the existing Phase 1, 6, 8 and 9 evidence plus bounded physical checks in `/home/mak` and `/home/mak/WIN`. Declarations are classified separately from active consumers. No service, timer, cron, watchdog, worker, backup, restore, network call, Git command, or repair was run. Only this report and its CSV were created.

## Bilingual vocabulary matrix

| Function | Search vocabulary and aliases |
|---|---|
| platform/work | plataforma, platform, mak_plataforma; trabajo, work, job, task |
| guard/watch | guardia, watchdog, guardian, vigia, vigilar |
| log/state | bitácora, bitacora, log, ledger, journal; estado, state, status, salud, health |
| path/service | carpeta, directory, dir, ruta, route, path; servicio, service, unit, systemd |
| schedule/queue | cron, timer, crontab, scheduled; cola, queue, backlog, pending |
| departments | investigación, investigacion, research; curatoria, curation, curate |
| execution | conductor, dispatcher, runner, handler, worker; entrega, delivery, deliver, output |
| retention/history | respaldo, backup, archive, restore; legado, legacy; obsoleto, obsolete; reemplazado, superseded; sin desarrollar, undeveloped |

Coverage included casefold, accented/unaccented forms, localized directories, aliases/slugs, human labels and exact machine identifiers. Residual false-negative risk: dynamic imports, environment-derived paths, symlinks outside the bounded inventories, shell aliases, generated configuration, and consumers named without these semantic terms. Presence, import, equal hash, or a declaration alone is not evidence of liveness.

## Classification counts

The companion CSV contains 38 physical rows. Counts are: LIVE/ADOPTABLE 0; SUPERSEDED 0; WINDOWS_LEGACY 7; OBSOLETE 0; UNDEVELOPED 0; BLOCKED 15; EVIDENCE_ONLY 16. `decision` is `no_change` for every row.

## Evidence summary

| Evidence | Result | Meaning |
|---|---|---|
| `/home/mak/.config/systemd/user/mak-hub.service` | `is-active` exit 3 (`inactive`), `is-enabled` exit 1 (`disabled`) | Declaration exists; not active. |
| `mak-xio.service` | `is-active` exit 3, `is-enabled` exit 1 | No active consumer established. |
| shadow service/timer | both `inactive` exit 3; unit state absent for `is-enabled` exit 1 | Source declarations only; not installed/enabled. |
| `crontab -l` | exit 0; all listed MAK entries prefixed `PAUSED-*` | Schedule text exists, but no active schedule was claimed. |
| `ps` semantic filter | no MAK/conductor/worker/watchdog script process; only unrelated kernel/system processes matched broad terms | No active operational consumer observed. |
| Phase 6/8/9 reports | AST/import/help/hash checks passed for selected files; no worker/service execution | Static compatibility is not liveness. |
| WIN paths | seven historical declaration/queue rows retained | No current Debian 12 contract; classify WINDOWS_LEGACY. |

Current candidates have plausible owner names (`mak_plataforma`, `mak_conductor`, `mak_research`, `mak_vigia`) and static consumers, but no verified active Debian 12 consumer plus dependency contract. Runtime scripts that can acquire locks, write logs/state, invoke network/GitHub, or start units are BLOCKED pending an isolated contract and owner. Source declarations and probes are EVIDENCE_ONLY. The old Windows snapshot is WINDOWS_LEGACY regardless of hash equality.

## Evidence table / summary

The CSV records exact path, layer, existence, byte size, SHA-256, owner/consumer/dependency candidates, aliases, verification, classification and no-change decision. Important chains:

- `crontab.mak` -> `watchdog_mak.sh`, `backup.sh`, `trabajo.py`, `latido.py`, `entregar.py`, `capataz.py` and departmental guards. The installed crontab shows these entries paused; the source/runtime declarations are not active consumers.
- `mak-hub.service` -> `plataforma/hub.py`; installed user unit is inactive/disabled. `mak-xio.service` -> `xio_puente/monitor.py`; no active state was observed.
- `run_conductor_worker.py` -> shadow service/timer -> SQLite DB and GPU lock paths. `--help` passed in earlier evidence, but no worker was started and no sentinel/contract proves adoption.
- `queue_store.py`, `runtime.py`, `ledger.py` and `handler_registry.py` have static/import evidence in prior phases; imports do not prove a live queue consumer.
- `watchdog_mak.sh` contains lock/log paths and unit-repair logic; `backup.sh` writes backup output. Neither was executed.

## Commands and exit codes

- `sed -n '1,240p' agents.md; sed -n '1,260p' context/LAST_HANDOFF.md` -> 0.
- `rg ...` -> 127 (`rg` unavailable); fallback `find`/`grep`/Python stdlib used.
- Existing evidence scans with `find`, `grep`, and CSV/Python stdlib metadata -> 0.
- Bounded `pathlib`/`hashlib` metadata probe for 40 rows -> 0; sizes and hashes recorded in CSV.
- `systemctl --user is-active/is-enabled` for `mak-hub.service`, `mak-xio.service`, shadow service and timer -> inactive exit 3; enabled checks exit 1 (shadow units absent; hub/xio disabled).
- `crontab -l` -> 0; all observed MAK entries are commented `PAUSED-*` declarations.
- `ps -eo pid,comm,args` semantic filter -> 0; no relevant MAK operational process observed.
- `grep -nEi` over selected declarations -> 0; static `ExecStart`, `OnCalendar`, cron, lock, watchdog and backup references recorded.
- Phase 6 prior `--help` checks for `check_mak_mirror.py` and `run_conductor_worker.py` -> 0; no execution beyond help.

## Risks

No absence claim is absolute: process state and crontab state are point-in-time observations. A paused declaration may be edited externally later. `systemctl` user scope does not prove system scope. Static imports may hide runtime configuration, and identical hashes do not prove ownership or activation. `watchdog_mak.sh` includes unit-repair behavior and HTTP probes; `entregar.py`/issue routes have lock/log/network or durable queue boundaries recorded in Phase 9. `panel_directivo.py` remains untouched with its known SyntaxError at line 145. No Git, SSH, 192.168.50.2, network, repair, source, runtime data, logs, locks, databases, credentials, WIN file or product was modified.

## No-change decisions

No row is LIVE/ADOPTABLE. No merge, delete, move, copy, revive, repair, enable, start, or normalization was performed. Historical Windows tools remain evidence and are not promotion candidates. Declarations are not treated as active merely because they exist, parse, import, or have matching hashes.

## Next action

For any future adoption, assign one current Debian 12 owner and named consumer, document exact input/output and dependency contracts, isolate all logs/locks/state/network/Git boundaries, then run a bounded foreground fixture test. Re-audit activation only after explicit authorization; do not enable or start declarations during triage.
