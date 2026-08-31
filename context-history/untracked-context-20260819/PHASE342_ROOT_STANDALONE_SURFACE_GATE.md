# Phase 342 — root standalone surface gate

Date: 2026-08-15 (America/Santiago)

## Classification

| Path | Evidence | Disposition |
|---|---|---|
| `/home/mak/bin/mak_sync_safe.py` | AST-valid; active deploy-worktree consumer documented in Phase 280; mutates deploy/projections | `PROTECT_EXTERNAL_DEPLOY_OWNER` |
| `/home/mak/cli_watsonx.py` | AST-valid, SHA `7b914658...`; no active code consumer; external provider CLI | `PROTECT_OPTIONAL_PROVIDER` |
| `/home/mak/oi-qwen.py` | AST-valid, SHA `63602db3...`; no active code consumer; local/provider launcher | `PROTECT_OPTIONAL_TOOL` |
| `/home/mak/diag-barrier-now.sh` | bash syntax pass; no app consumer; host diagnostic | `PROTECT_HOST_DIAGNOSTIC` |
| `/home/mak/diag-kvm-linux.sh` | bash syntax pass; no app consumer; host diagnostic | `PROTECT_HOST_DIAGNOSTIC` |
| `/home/mak/diag-red-linux.sh` | bash syntax pass; no app consumer; host diagnostic | `PROTECT_HOST_DIAGNOSTIC` |

All hashes and sizes were recorded in the foreground. No standalone tool was
executed, no provider/network call was made and no file changed. The bounded
consumer search found only documentation references for the optional tools
and diagnostics; deploy ownership remains explicit for `mak_sync_safe.py`.

## Decision

None of these six files is confirmed basura. The optional provider tools and
host diagnostics are preserved as external evidence; `mak_sync_safe.py` stays
outside the canonical source because its deploy worktree is a separate owner.
Future cleanup requires a separate owner decision, not filename similarity.

