# Phase 226 — Automation surface audit

## Scope

Read-only verification of FLUJO automation scheduling and runtime units. This
phase separates the user-confirmed `EVENTO ...` issue/URL workflow from paused
cron/provider/deploy mechanisms. No GitHub request, cron execution, worker,
service start, deploy sync or issue processing was performed.

## Evidence and results

| Check | Command | Exit | Result |
|---|---|---:|---|
| Installed cron | `crontab -l \| awk ...` | 0 | `CRON_ACTIVE_NONCOMMENT=0`; `CRON_PAUSED=24` |
| User units | `systemctl --user is-active <unit>` for research, queue, codex, hub, interfaz and XIO | 0 per query | All reported `inactive` |
| Issue bridge source | `grep -nE 'puente_issues...'` | 0 | `/home/mak/flujo/cultura/mak_plataforma/puente_issues.py` exists and documents the `EVENTO`/issue bridge; it contains provider and write paths |
| Cron manifest | file existence and static grep | 0 | `/home/mak/flujo/cultura/mak_plataforma/crontab.mak` is a manifest/template, not the installed crontab |
| Deploy sync | bounded static audit from the prior phase | 0 | `/home/mak/bin/mak_sync_safe.py` remains an external deploy-side effect and is paused; no sync ran |

## Classification

- The confirmed operational path is: an issue whose subject begins with
  `EVENTO ...` contains a URL, and the existing bridge consumes it. The user
  has confirmed that this path currently works. It is therefore not an open
  migration bug and was not re-executed against the external provider.
- Its source remains the canonical MAK implementation at
  `/home/mak/flujo/cultura/mak_plataforma/puente_issues.py`; the runtime paths
  it writes under `/home/mak/plataforma/` are a separate mutating boundary.
- The installed scheduler has zero active non-comment entries and 24 paused
  entries. The presence of runnable-looking lines in `crontab.mak` does not
  prove that they are installed or active.
- `n8n-local` remains discarded. XIO remains excluded from the migration list;
  its user unit is inactive and was not touched.
- Objective 4, FLUJO automations, is now classified as **user-confirmed path /
  operationally paused**, not as an unverified broken component.

## Files changed

Only this report and the operational handoff were changed. No runtime,
database, asset, scheduler, service or historical WIN file changed.

## Risks and rollback

Re-enabling the issue bridge or deploy sync would contact an external provider
and/or write platform state. That requires explicit authority and a bounded
foreground run. Rollback is to leave the installed crontab and user units in
their current inactive/paused state; no rollback action was needed here.

## Next concrete action

Move to the next remaining read-only surface in the 13-point plan: audit the
non-serve FLUJO command/dependency and consumer map already present in MAK,
then close any remaining objective only with foreground evidence. Keep the
confirmed issue workflow classified as working, do not test it externally, and
do not broaden cleanup until every candidate has a consumer and rollback.
