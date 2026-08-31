# Phase 351 — delivery ZIP export consumer gate

Date: 2026-08-15 (America/Santiago)

## Scope

Validated `flujo.export.zipper.export_flyer` with a temporary flyer project.
The gate covered manifest validation, source collection, generated delivery
scripts, email draft and archive membership. No canonical project was used.

## Results

```text
ZIP_EXPORT_TEMP=PASS members=9
ZIP_DELIVERY_SCRIPTS_INCLUDED=PASS
ZIP_REAL_TREE_WRITES=NONE
PYCOMPILE_RC=0
```

The scripts are created before the archive is opened, so the ZIP contains the
delivery files that the export contract promises. The archive was written
only below a temporary directory and was inspected with the standard library.

## Disposition

`VERIFIED_TEMP_EXPORT_CONSUMER; EXTERNAL_EDITOR_HANDOFF`

The exporter is locally usable as an artifact builder. Photoshop,
Illustrator and Blender execution remain external handoffs and were not
called. Generated client artifacts are not cleanup candidates merely because
they are reproducible.

## Rollback and boundary

No real project, asset, database, service, provider, Git state or WIN evidence
changed. No rollback is required. Any real export should remain an explicit
user-directed operation because it writes a project `exports/` directory.
