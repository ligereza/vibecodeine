# Phase 228 — Empty workspace quarantine

## Decision

`/home/mak/workspace` was a confirmed empty staging surface at the time of
the check: three nested directories, zero regular files and zero symlinks. A
bounded consumer search found no active reference to `workspace/tools`,
`doc_parser` or `simple_doc_parser`. It was moved as one reversible empty
directory tree to:

`/home/mak/flujo/context/quarantine/phase228_empty_workspace/workspace`

This is quarantine, not deletion. The quarantine contains zero regular files
and zero symlinks. No source, document, database, asset or historical WIN
evidence was moved.

## Validation

| Check | Result |
|---|---|
| Source existed before move | yes |
| Pre-move files/symlinks | 0 |
| Move command | `mv /home/mak/workspace /home/mak/flujo/context/quarantine/phase228_empty_workspace/workspace` |
| Move exit | 0 |
| Original path after move | absent |
| Quarantine path after move | present |
| Quarantine files/symlinks | 0 |
| Quarantine directories | 4, including root and three empty nested directories |

## Why the legacy platform UI was preserved

`/home/mak/plataforma/interfaz.py` was not included. It is a 150,949-byte
legacy UI candidate with historical tests/import references and a separate
canonical Research UI at `/home/mak/research/interfaz.py`; its import/runtime
contract is incomplete, but that makes it evidence requiring explicit review,
not confirmed junk.

## Rollback

Only if a future consumer is identified, restore the empty directory tree with:

`mv /home/mak/flujo/context/quarantine/phase228_empty_workspace/workspace /home/mak/workspace`

Then re-run the bounded consumer search. No rollback is currently indicated.

## Next concrete action

The immediate foreground regression gate passed. Continue the remaining
candidate ledger by consumer, language and platform. Preserve semantic tool
variants, working assets and historical evidence.
