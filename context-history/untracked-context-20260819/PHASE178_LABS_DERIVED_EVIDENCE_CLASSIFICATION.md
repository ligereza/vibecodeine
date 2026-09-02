# Phase 178 — labs derived-evidence classification

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Physical findings

`/home/mak/labs` contains dated experiment outputs, not an active department
runtime. The relevant evidence surfaces are:

- `rd-auto-index-20260813`: source `/home/mak/RD`, 1,742 assets,
  60,864,246,614 bytes, 47 exact-duplicate relations, 1,578 full hashes,
  164 pending hashes, no perception run, three candidate rows.
- `portable-ssd-index-20260813`: source `/media/mak/PortableSSD`, 45,536
  assets, 940,704,720,908 bytes, 111 exact-duplicate relations, 45,424
  pending hashes, no perception run.
- `triple-cartel-20260813` and lineage/organism runs: derived plans, manifests,
  SQLite/WAL, locks and temporal evidence; not canonical RD data.
- `visual-index-pilot` and `nudo-blender-companion`: bounded experiments with
  model/render evidence; not active MAK services.

## Decision

Classify lab directories as `DERIVED_EVIDENCE` with provenance and rollback
protection. Do not merge their SQLite databases, promote candidate brands,
run pending perception, delete locks/WALs or treat `hash_pending` as duplicate
proof. The RD asset consumer remains `/home/mak/RD` plus the FLUJO/curatoria
readers; the next gate is a read-only metadata/duplicate crosswalk.
