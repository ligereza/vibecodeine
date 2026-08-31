# Phase 290 — Curatoria duplicate preservation gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `EXACT_DUPLICATE; PROTECTED_EVIDENCE; NO_MOVE`

## Candidate

Compared `/home/mak/curatoria/db` with the canonical
`/home/mak/flujo/docs/rd/candidatos_curatoria` family:

```text
INFORME_CANDIDATOS.md:                         cmp rc=0
candidatos_db.jsonl:                           cmp rc=0; 970 valid rows
propuestas/eventos_reduciendo_cl.md:           cmp rc=0
propuestas/reduciendo_dano_chile.md:           cmp rc=0
propuestas/sundeck.md:                          cmp rc=0
all files: mode 644; exact SHA-256 matches
```

The active producer `tools/gen_propuestas_rd.py` defaults to the FLUJO docs
path. The old runtime path has no bounded active source/test reference, and
its timestamps are older, but the files are generated curation evidence.

## Decision

Do not delete, move or replace this family with a symlink. Exact equality plus
absence of an active consumer is insufficient to erase generated evidence;
the older path may be required for provenance, historical comparison or
recovery. The family is now explicitly classified as `PROTECTED_EXACT_DUPLICATE`
rather than `JUNK_CONFIRMED`.

No database, media, credential, WIN content, service or Git state changed.

## Rollback

No mutation occurred. Both original paths remain available.

## Next concrete action

Review the next named duplicate family only if its role is not protected
evidence: inspect source/runtime projection consumers and preserve all
generated outputs. Do not convert this gate into broad duplicate deletion.
