# Phase 339 — cleanup candidate ledger refresh

Date: 2026-08-15 (America/Santiago)
Status: `LEDGER_ONLY; NO_MOVE`

| ID | Original path | SHA-256 | Role/evidence | Disposition | Inverse action |
|---|---|---|---|---|---|
| C339-01 | `/home/mak/install_mak.sh` | `46a231f1ce5c44bef388f745f4a32fa763e1df55ee98adbdbc5d67fa200051a` | historical MAK installer; mutates cron/systemd/projections | quarantine candidate, preserve | move from `context/quarantine/phase339_root_installers/install_mak.sh` back to original |
| C339-02 | `/home/mak/instalar.sh` | `20ac37fd1169db6589c2eee4735f519e2e9840c964a0f7ce1f87df3f20b81de0` | obsolete Docker/Open WebUI installer; no active code consumer | quarantine candidate, preserve | move from `context/quarantine/phase339_root_installers/instalar.sh` back to original |
| C339-03 | `/home/mak/blender-4.5.3-viejo` | binary 4.5.3; full tree not hashed | distinct old external runtime; 110 RD blend assets make provenance plausible | preserve pending project owner | restore whole directory from quarantine only after exact manifest |
| C339-04 | `/home/mak/plataforma/interfaz.py` | recorded in Phase 270 | legacy UI already moved reversibly by prior phase | quarantined existing | reverse move recorded in Phase 270 |

## Gate

No candidate is deleted. C339-01/02 have exact file hashes and no active code
references, but their historical installation knowledge is retained. C339-03
is not a cleanup candidate yet because it is a distinct runtime with unresolved
asset provenance. C339-04 remains in its prior reversible quarantine.

Any future move must use a new phase quarantine directory, verify the target is
not already occupied, preserve mode/hash and run a post-move consumer scan.
Until that action is authorized within the cleanup slice, this document is a
ledger only.

