# Phase 229 — Empty shell-residue quarantine

## Decision

Nine empty directories with no regular files, no symlinks and no bounded
active references were classified as malformed shell/path residue and moved
reversibly. The original paths were:

- `/home/mak/ ;`
- `/home/mak/cd`
- `/home/mak/cp`
- `/home/mak/sha256sum`
- `/home/mak/flujo/.githubworkflows`
- `/home/mak/flujo/schemasknowledge`
- `/home/mak/flujo/srcflujo`
- `/home/mak/flujo/srcflujoknowledge`
- `/home/mak/flujo/toolsmak_ops`

They now reside under:
`/home/mak/flujo/context/quarantine/phase229_empty_shell_residue/`.
The quarantine contains zero regular files and zero symlinks. This is not
deletion and does not touch source, databases, assets, documents or WIN.

## Deliberately preserved empty paths

`/home/mak/tmp`, user directories, `GoogleDrive`, `WIN/incoming-*`, the
disconnected `OneDrive` mount and other named storage surfaces were not moved.
An empty directory is not enough to remove a path that may be a user/storage
contract; those remain candidates only if a future bounded consumer check
justifies action.

## Validation

| Check | Result |
|---|---|
| Candidates before move | 9 directories |
| Files/symlinks in candidates | 0 |
| Move exit | 0 for every candidate |
| Original candidate paths after move | all absent |
| Quarantine files/symlinks | 0 |
| External provider/service/Git action | none |

## Rollback

Restore each quarantined directory to its recorded original path with `mv`
from the phase quarantine. The phase directory names preserve the mapping;
the root path containing a space/semicolon is recorded as
`root_semicolon`. Re-run the bounded reference check after any restoration.

## Next concrete action

Run the small foreground CLI/health regression after this second reversible
cleanup, then stop physical cleanup unless a new exact candidate has a
consumer-free, evidence-preserving rollback. Remaining work is functional
gates requiring real field data/mutator authority and the final Git branch
proposal, not indiscriminate deletion.
