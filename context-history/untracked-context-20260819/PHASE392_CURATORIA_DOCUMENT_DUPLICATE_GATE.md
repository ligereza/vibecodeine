# Phase 392 — Curatoria candidate-document duplicate family

Date: 2026-08-15 (America/Santiago)

## Scope

Compared the bounded family `/home/mak/curatoria/db` against
`/home/mak/flujo/docs/rd/candidatos_curatoria` by exact path, size, SHA-256,
line count and active consumer references. No generated data or document was
opened for semantic rewriting and no file was moved.

## Evidence

| Check | Result |
|---|---|
| Files in each family | 5 matching paths |
| Exact byte parity | all 5 matching files equal |
| `candidatos_db.jsonl` | 970 lines in each copy; SHA equal |
| Active canonical consumer | `tools/gen_propuestas_rd.py` points to `docs/rd/candidatos_curatoria/candidatos_db.jsonl` |
| Active consumer of `/home/mak/curatoria/db` | none found in bounded source scan |
| Provenance | Curatoria copy is generated/runtime evidence and was previously classified older |

## Decision

This is an exact duplicate with a clear canonical consumer, but it is not
confirmed junk: the runtime copy is generated curation evidence and may be
needed for historical comparison. A destructive delete would violate the MAK
contract. No symlink or path rewrite was introduced because that would change
the runtime evidence contract without owner approval.

Current safe fusion is semantic ownership: the FLUJO docs copy is canonical
for proposal generation; the Curatoria copy remains preserved evidence.

Disposition: `EXACT_DUPLICATE_OWNER_ASSIGNED; EVIDENCE_PRESERVED; NO_MOVE`.

Next action: continue with the next duplicate family only if it has a named
consumer and a reversible path-level operation; otherwise keep it classified.
