# Phase 150 — RD PDF and human-delivery manifest

Date: 2026-08-15
Scope: event-pack PDFs under `/home/mak/RD/*` and the active FLUJO job.

## Source and consumer chain

```text
/home/mak/flujo/data/rd_packs.json
  -> jobs/2026-07-04_eventos-brief/flows/gen_packs.py
  -> job JSON + editable SVGs (active, promoted in Phase 148)
  -> PDF rendering/delivery (historical Windows output; not regenerated here)
```

`brief.yaml` declares the job delivered, but its product names still describe
the older wording (`Informativo + Testeo` and `Servicio Completo (evento
masivo)`). `resultado.md` still says `Aún no activado`. This is a metadata
contract conflict, not a reason to overwrite the PDFs silently.

## Manifest and decisions

| path/family | observed role | evidence | decision |
|---|---|---|---|
| `/home/mak/RD/REFERENCIA_VALORES.pdf` | RD human/business reference | 3-page A4; SHA-256 `e0a458...a65321` | keep canonical RD reference |
| `/home/mak/RD/New Folder/assets/brief_packs_plano_dark.pdf` | human combined delivery | byte-identical to `REFERENCIA_VALORES.pdf`; 3-page A4 | keep as named delivery until human owner chooses one name |
| `/home/mak/flujo/REFERENCIA_VALORES.pdf` | FLUJO documentation mirror | same reference hash | keep runtime/documentation mirror |
| `/home/mak/RD/packs_servicios_rd_{dark,gris}.pdf` | RD human pack delivery | exact pair with `RD/New Folder/assets` | keep delivery family; no hash-only deletion |
| `/home/mak/RD/plano_rider_{dark,gris}.pdf` | RD human plan/rider delivery | exact pair with `RD/New Folder/assets`; 2-page A4 landscape | keep delivery family |
| `/home/mak/flujo/jobs/2026-07-04_eventos-brief/*.pdf` | FLUJO job delivery snapshot | 1-page pack PDFs, 2-page rider PDFs, 3-page combined PDFs; old text | preserve as historical job output; no PDF promotion |
| `/home/mak/WIN/flujo/jobs/2026-07-04_eventos-brief/*.pdf` | Windows historical snapshot | exact hashes for inspected dark outputs | protected historical evidence |

The exact duplicates retain distinct names and human/workflow roles. No PDF is
`JUNK_CONFIRMED`. The canonical tariff is now newer than the PDF text, so
replacing these documents requires a controlled renderer plus a human delivery
decision.

## Renderer gate

The bounded search found the repository's Windows-first `tools/svg/svg_to_pdf.py`
and references to Edge, but no local `microsoft-edge`, `google-chrome`,
`chromium`, `wkhtmltopdf` or `weasyprint` executable. The isolated generator
therefore produced JSON/SVG successfully, while PDF promotion is `NO_PROMOTE`.
No dependency was installed and no PDF was overwritten.

Read-only validation passed for the selected PDFs: `pdfinfo` reported valid A4
dimensions and expected page counts; `pdftotext` confirmed semantic differences
between the older job PDFs and the newer canonical JSON/SVG wording. The only
unresolved piece is human delivery ownership plus a renderer available on MAK.

## Next action

Do not silently rewrite `brief.yaml`, `resultado.md` or human PDFs. Continue to
the next active MAK consumer slice; return to this family only when a renderer
and explicit delivery promotion contract exist.

## Commands and codes

- bounded `/home/mak` PDF inventory: exit 0 (OneDrive was excluded from this
  scoped read because its mount endpoint is unavailable).
- `sha256sum`, `pdfinfo`, `pdftotext`, `cmp` checks: exit 0 for inspected files.
- renderer binary lookup: no renderer found; exit 0 with empty candidates.
- no files changed in Phase 150.

