# Phase 332 — Blender asset provenance refresh

Date: 2026-08-15 (America/Santiago)

Bounded scan results:

- `/home/mak/RD` contains 110 `.blend`/`.blend1` files, including scene,
  material and automation assets.
- `/home/mak/flujo` contains no Blender project files.
- No code/config reference to `blender-4.5.3-viejo` was found under the
  bounded source/tool/cultural/RD paths.
- Four active code paths reference `/home/mak/blender/blender`: the flyer and
  video render tools, curatoria diagnostics and conductor registry.

## Decision

The old 4.5.3 runtime remains `OLD_EXTERNAL_RUNTIME_REVIEW`, not confirmed
basura. The large RD Blender corpus proves that a version-specific project
dependency is plausible even though no textual old-path reference exists.
Before any quarantine, inspect only the relevant `.blend` project metadata or
obtain an owner decision; do not open/render every asset and do not move a
1.2-GB runtime speculatively.

No files changed, no render ran, and no service/process was started.

