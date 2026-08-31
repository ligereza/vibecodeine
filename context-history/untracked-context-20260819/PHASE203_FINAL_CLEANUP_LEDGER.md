# Phase 203 — Final cleanup ledger (LUNA-1)

Date: 2026-08-15 (America/Santiago)

## Scope

This ledger converts the already classified duplicate/legacy families into
reversible decisions. It does not move, delete, overwrite, merge databases,
or alter runtime code. A candidate is actionable only when its full hash,
mode, consumer surface, platform role, and rollback are explicit.

## Decisions

| ID | Family | Evidence | Consumer/role | Mode | Decision | Rollback |
|---|---|---|---|---|---|---|
| C203-01 | RD pack catalog duplicate | `/home/mak/RD/packs_servicios_rd.json` and `/home/mak/RD/New Folder/assets/packs_servicios_rd.json` are byte-identical; SHA-256 `39e68671500360393a534554606d65cdb71efb7d87e9b5f52cad74b5c012d54b` | Delivery/archive evidence. Active tariff consumer is `/home/mak/flujo/data/rd_packs.json` through `src/flujo/plano/packs.py`; neither RD copy is an active runtime source. | regular file, 0644, 3740 bytes | `PRESERVE_NO_MOVE`: historical/delivery evidence is protected; not safe to delete or silently merge. | None; preserve both original paths. |
| C203-02 | RD job pack variant | `/home/mak/flujo/jobs/2026-07-04_eventos-brief/packs_servicios_rd.json`; SHA-256 `ad52c97046daa2f5e85a5345579d6b093c5f26e53aca5848a41f0d61bd1766ff` | Job brief evidence; numeric contract matches the canonical tariff, but wording/schema differ. | regular file, 0644, 3685 bytes | `PRESERVE_VARIANT`: semantic variant, not an exact duplicate. | None; restore/retain the job path. |
| C203-03 | Old platform research UI | `/home/mak/plataforma/interfaz.py`; SHA-256 `6712ddff059eab2c3633fc1bf819994c1c6b6e620fe3410144cf6d0f7d602b72` | No active launcher/config reference found in the bounded consumer search. `mak-research.service` owns `/home/mak/research/interfaz.py`; the platform copy is a legacy candidate and direct execution previously failed on missing `pausa`. | regular file, 0644, 150949 bytes | `QUARANTINE_CANDIDATE_ONLY`: potentially reversible, but no move is authorized in this ledger. Require a second consumer scan and explicit move approval. | If approved later: move to `/home/mak/flujo/context/quarantine/phase203_platform_ui/interfaz.py`; rollback by moving it back to `/home/mak/plataforma/interfaz.py`, then re-run import/launcher checks. |
| C203-04 | Incomplete direct platform panel | `/home/mak/plataforma/panel_directivo.py`; SHA-256 `4a85f10015f9e25a7f6bc739e6ae81c38f6c5b2e69d71536544816ded824afc7` | No active consumer; known syntax failure at line 145. It is historical/incomplete source, not a verified duplicate. | regular file, 0644, 4785 bytes | `PRESERVE_NO_REPAIR`: do not delete, auto-fix, or promote. | Original path remains the rollback. |

## Gate result

No candidate is safe for immediate deletion. C203-03 is the only reversible
quarantine candidate, and it remains pending because the current evidence
supports absence of an active launcher but does not grant authority to remove
historical source. Exact RD duplicates are protected evidence, not basura by
hash alone. The active tariff remains the canonical MAK path and is unchanged.

## Validation record

- `sha256sum` completed with exit 0 for all five ledger paths.
- `stat -c '%A %a %s %Y %n'` completed with exit 0 for all five paths.
- Bounded consumer search for `plataforma/interfaz.py` returned no active
  launcher/config match; exit 0 because the command used an explicit empty
  result fallback.
- Bounded source search for `packs_servicios_rd.json` did not identify the RD
  archive copies as active tariff inputs; exit 0 with no mutation.
- `systemctl --user is-active mak-research.service mak-codex.service
  mak-hub.service mak-interfaz.service` returned four `inactive` states.
- No move, delete, database write, package install, service start, or Git
  mutation occurred.

## Next concrete action

Run one final bounded consumer/reference scan for C203-03, then decide whether
to leave it preserved or request a reversible quarantine. In parallel continue
the open functional audit: non-`serve` FLUJO commands, dependency dispositions,
and the 13-objective closeout. Keep RD field-data mutators deferred and keep
WIN historical.

