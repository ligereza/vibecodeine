Identity: LUNA-10

# PHASE10 — Platform semantic triage

## Scope

Assigned scope: `/home/mak/flujo/cultura/mak_plataforma`, `/home/mak/plataforma`,
the local snapshot `/home/mak/WIN/flujo/cultura/mak_plataforma`, and the
`mak_conductor` consumers that reference platform modules. Phase 8 and Phase 9
were reused as the bounded inventory and verification baseline. No Git, SSH,
network, service, cron, watchdog, worker, handler, repair script, or live-data
operation was used.

The physical bounded totals already established by Phase 8 are source 60 files,
runtime 133 files, and WIN 64 files. This report's 47 CSV rows are semantic
decision points: consumer-facing modules, declarations, known blockers, and
Windows counterparts. Excluded live JSON/JSONL, logs, locks, databases,
credentials, backups, generated runs, and large data surfaces remain preserved
and are not evidence for adoption. Unlisted bounded files are not silently
promoted; they remain evidence pending a specific owner/consumer contract.

## Bilingual vocabulary matrix

| Human/function | Spanish, English, aliases searched |
|---|---|
| platform | `plataforma`, `platform`, `mak_plataforma`, `platforma` |
| work | `trabajo`, `work`, `job`, `task` |
| guard | `guardia`, `watchdog`, `guardian`, `vigia`, `vigilar` |
| ledger | `bitácora`, `bitacora`, `log`, `ledger`, `journal` |
| state/health | `estado`, `state`, `status`, `salud`, `health` |
| path/directory | `carpeta`, `directory`, `dir`, `ruta`, `route`, `path` |
| service | `servicio`, `service`, `unit`, `systemd` |
| schedule | `cron`, `timer`, `crontab`, `scheduled` |
| queue | `cola`, `queue`, `backlog`, `pending` |
| research | `investigación`, `investigacion`, `research` |
| curation | `curatoria`, `curation`, `curate` |
| conductor | `conductor`, `dispatcher`, `runner`, `handler`, `worker` |
| delivery | `entrega`, `delivery`, `deliver`, `output` |
| backup/history | `respaldo`, `backup`, `archive`, `restore`, `legado`, `legacy` |
| lifecycle | `obsoleto`, `obsolete`, `reemplazado`, `superseded`, `sin desarrollar`, `undeveloped` |

Coverage included accented/unaccented forms, casefold, localized directories,
aliases/slugs, human labels, and exact identifiers such as
`handler_registry`, `platform.entregar.main`, `platform.puente_issues.una_pasada`,
`QueueStore`, `dispatch_sync`, `LOCK`, `STATE`, `LOG`, and `BANDEJA`. Residual
false-negative risk: Unicode normalization variants, dynamic/reflection-based
imports, environment-variable paths, symlinks outside the bounded map,
excluded live data/configuration, and aliases with no shared literal. A name,
hash, import, or inventory row alone never established adoption.

## Classification counts

The CSV contains 47 semantic rows:

| Classification | Count | Meaning in this triage |
|---|---:|---|
| LIVE/ADOPTABLE | 26 | Current Debian owner, named consumer, dependency contract, and foreground import/AST/help evidence are present; no promotion or execution was needed. |
| BLOCKED | 5 | A named path exists but its contract crosses forbidden lock/log/network/persistence boundaries, or parsing fails. |
| WINDOWS_LEGACY | 10 | Historical WIN copy; current Debian owner/consumer contract is not proven. |
| EVIDENCE_ONLY | 6 | Mapping, doctrine, catalog, runtime, or service declaration without sufficient operational proof. |
| SUPERSEDED | 0 | No safe semantic replacement proof was established. |
| OBSOLETE | 0 | Age, naming, or duplication was not used as evidence. |
| UNDEVELOPED | 0 | No path was labeled undeveloped without explicit evidence. |

The combined label `LIVE/ADOPTABLE` is intentionally used only for the rows
with all four gates; it does not mean a job or permanent process was run.

## Evidence summary

| Surface | Evidence | Decision |
|---|---|---|
| Source/runtime `ledger`, `trabajo`, providers, discernment, mineria, visual index, tandas, revisor, capataz, junta, latido, material, backlog | `mak_conductor.handler_registry` imports the functional set; Phase 8 observed 30 handlers; AST/import/help checks passed; stdlib dependencies are available. | LIVE/ADOPTABLE, no change |
| `entregar.py` source/runtime | Phase 9 source inspection shows even `--dry-run --limit 0` enters an exclusive lock and appends `entregar.log`; non-dry path reaches Git/GH boundaries. | BLOCKED, retain unchanged |
| `puente_issues.py` source/runtime | Phase 9 shows dry path can call GH and persistent queue/observation state. | BLOCKED, retain unchanged |
| `/home/mak/plataforma/panel_directivo.py` | Compile-from-text fails with the known `SyntaxError` at line 145. | BLOCKED, do not repair |
| `mak_conductor` registry/catalog/runtime | Real mapping and persistence contracts are visible, but no safe isolated handler harness exists. | EVIDENCE_ONLY |
| service declarations and `hub.py` | Files exist and parse/declarations were inspected; no service was enabled or started, and no owner contract was established. | EVIDENCE_ONLY |
| WIN platform and conductor copies | Physical historical variants, including divergent hashes; no current Debian contract. | WINDOWS_LEGACY |

The Phase 8 divergence in runtime `tandas.py` and the historical differences in
WIN `providers.py`, `tandas.py`, `hub.py`, service declarations, and delivery
files are provenance signals only. They are not reasons to merge, copy, delete,
revive, or repair.

## Commands and exit codes

| Command/action | Exit | Result |
|---|---:|---|
| `sed -n ... agents.md` and `LAST_HANDOFF.md` | 0 | Read-first contract and current open work loaded. |
| Phase 8 bounded inventory/hash/AST/import/help evidence | 0 | Reused: source/runtime/WIN totals 60/133/64; 30 registry handlers; known panel parse failure retained. |
| Phase 9 handler audit and side-effect inspection | 0 | Reused: no handler invoked; `entregar` and `puente_issues` safety gates failed. |
| bounded `find`/metadata listing of assigned roots | 0 | Physical paths and sizes inspected; live data not opened. |
| `sha256sum` on selected source/runtime/WIN evidence | 0 | Hashes recorded in CSV; hash equality/divergence used only as provenance. |
| Python stdlib CSV validation | 0 | Header exact; 47 rows; 13 columns; allowed classifications only. |
| Git/SSH/network/service/cron/worker/repair execution | N/A | Not issued under mission constraints. |

## Owner, consumer, dependency contracts

The only current Debian consumer evidence is the foreground import of
`mak_conductor.handler_registry` and its named `cultura.mak_plataforma` module
references, plus the Phase 8 imports of `mak_curatoria` and `flujo.autonomia`.
The dependency contract for the adoptable rows is Python/stdlib plus the
repository package path. This proves an importable interface, not successful
delivery, queue mutation, publication, service operation, or health monitoring.
For blocked rows, the named consumer exists but the safe contract does not.
For WIN rows, the historical owner/consumer is unknown and no Debian contract
was demonstrated.

## No-change decisions and risks

- No source, runtime, WIN, artwork, logs, JSON/JSONL, locks, databases,
  credentials, products, or services were modified.
- `panel_directivo.py` remains unchanged at SyntaxError line 145.
- No service unit, cron declaration, watchdog, worker, backup, queue, handler,
  Git operation, GH operation, or network path was executed.
- No duplicate hash, matching name, old branch, file age, or inventory row was
  treated as a merge/delete/move/copy/revive/repair instruction.
- `/home/mak/WIN` remains evidence only. Historical tools that once called MAK
  but lack a current Debian contract remain WINDOWS_LEGACY.
- Live data and generated trees were not re-scanned or opened; their exclusion
  is an explicit risk boundary, not evidence of absence or adoption.

## Next action

Keep this triage as no-change. The next admissible action is to design an
authorized, networkless, temporary isolated harness for one `mak_conductor`
handler with synthetic inputs, a temporary home/config/queue, suppressed live
logging/locks, and before/after path measurement. Until that harness exists,
retain `entregar`, `puente_issues`, the registry/catalog, panel, declarations,
and all WIN variants as classified evidence; do not promote or repair them.
