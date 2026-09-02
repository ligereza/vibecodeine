# Phase 189 — top-level MAK surface audit

Status: `BOUNDED_INVENTORY_COMPLETE`

This pass inspected only immediate children of `/home/mak` and selected
department roots. It did not recursively copy, hash, move, delete, or open
external mounts.

## Department/runtime roots

| Root | Immediate shape | Classification |
|---|---:|---|
| `flujo` | 72 entries | Authoring/integration source |
| `RD` | 148 entries | Active creative corpus; Phase 179–181 gates apply |
| `research` | 94 entries | Active Research runtime/output surface |
| `codex` | 25 entries | Active Codex runtime projection |
| `curatoria` | 33 entries | Active Curatoria runtime/output surface |
| `plataforma` | 129 entries | Active platform runtime plus legacy candidates |
| `vigia` | 7 entries | Active watch runtime; parity-gated |
| `labs` | 14 directories | Derived dated evidence; no promotion |

## External, historical and excluded roots

| Root | Classification |
|---|---|
| `apps`, `Apps` | Installed/external application layers; not MAK Python merge targets |
| `src` | External source; MobileCLIP is a declared visual-index consumer |
| `models` | Model artifacts; keep separate from source and requirements |
| `WIN` | Historical archive only |
| `GoogleDrive` | Empty at immediate level during this pass; no mount assumption |
| `OneDrive` | Mount error `Errno 107: Transport endpoint is not connected`; external state, no repair attempted |
| `n8n-local` | Discarded as a department per user clarification; preserve evidence until final cleanup ledger |
| `xio_puente` | Excluded from current work per user clarification; no ADB action |

## State/evidence roots requiring explicit role labels

`indexes`, `backups`, `rollback`, `quarantine`, `state`, `portfolio_media`,
`curatoria_inbox` and the many user media/document roots are not automatically
garbage. They contain indexes, reversible evidence, runtime state, inboxes or
user material and must be classified by consumer before any move.

## Decision

The top-level shape supports the Phase 188 architecture. There is no safe
single “clean” command: the house contains active departments, derived
evidence, external apps/models, user material and historical roots. The next
cleanup ledger must be path-level and consumer-backed, starting with one
bounded family rather than deleting by directory name.

## Validation record

The immediate inventory exited `0`. The disconnected OneDrive mount was
recorded as an external-state observation. No mount, service, provider, cron,
package, WIN, Git or file mutation was attempted.
