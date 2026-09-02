# Phase 341 — cleanup ledger result

Date: 2026-08-15 (America/Santiago)

## Materialized decisions

| ID | Current location | Result |
|---|---|---|
| C339-01 | `context/quarantine/phase339_root_installers/install_mak.sh` | quarantined; hash/mode preserved |
| C339-02 | `context/quarantine/phase339_root_installers/instalar.sh` | quarantined; hash/mode preserved |
| C339-03 | `/home/mak/blender-4.5.3-viejo` | preserved; provenance open |
| C339-04 | `context/quarantine/phase270_platform_ui/interfaz.py` | existing reversible quarantine preserved |

The active root no longer contains the two mutating installer entrypoints.
No evidence, database, media, credentials, generated product, runtime tree or
WIN content was deleted. The previous ledger's inverse paths remain valid.

## External state note

`dockerd` is a pre-existing host process, not created by this phase. There are
no running containers; stopped `searxng` and `open-webui` containers remain as
external evidence. They are not part of this cleanup set.

