# Phase 127 - RD document and asset ownership gate

## Exact document family

`REFERENCIA_VALORES.pdf` is byte-identical across the inspected locations:

```text
sha256=e0a45846613943f97b70a1d56ef9bfd27bfa83ce6bc9db0ab564680985a65321
pages=3, size=364382 bytes, A4
```

The copies have different roles:

| Path | Role | Decision |
|---|---|---|
| `/home/mak/RD/REFERENCIA_VALORES.pdf` | RD human/business reference; candidate records use `ruta_rel=REFERENCIA_VALORES.pdf` | canonical RD source; preserve |
| `/home/mak/flujo/REFERENCIA_VALORES.pdf` | FLUJO integration/reference surface | preserve as runtime/documentation mirror |
| `/home/mak/flujo-deploy/REFERENCIA_VALORES.pdf` | deployment snapshot | preserve until deploy ownership is separately closed |
| `/home/mak/vibecodeine/REFERENCIA_VALORES.pdf` | separate project surface | outside this merge; preserve |
| `/home/mak/actions-runner/_work/.../REFERENCIA_VALORES.pdf` | runner workspace | generated/workspace evidence; preserve |
| `/home/mak/WIN/.../REFERENCIA_VALORES.pdf` | historical Windows evidence | never alter |

The exact hash does not erase role, provenance or human workflow. No copy was
deleted, moved or replaced.

## Related plano asset

`brief_packs_plano_dark.pdf` also exists under the live FLUJO job output,
`/home/mak/RD/New Folder/assets`, and WIN. It is a source/output/delivery
family, not an automatic duplicate deletion candidate. The live job and RD
asset copies require separate consumer mapping.

## Foreground validation

`sha256sum` and `pdfinfo` were run on the active copies. All inspected
reference PDFs matched the hash, page count and A4 dimensions. Scoped text
search found RD candidate metadata and documentation references, but no safe
single-path replacement contract. No PDF rendering, database write, output
generation or external service ran.

## Decision

`JUNK_CONFIRMED`: no. `MERGE_NOW`: no. Keep these as classified document
mirrors until the human source/delivery contract names a canonical path and
provides a tested link or manifest. This advances duplicate classification
without destroying business/reference provenance.

## Next action

Map the RD job asset manifest and the `/home/mak/RD` editable/delivery roles;
then update the cleanup matrix with only path-specific candidates. Do not
deduplicate PDFs, SVGs, Blender files or office assets by hash alone.
