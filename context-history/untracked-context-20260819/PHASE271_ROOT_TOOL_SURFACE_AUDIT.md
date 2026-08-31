# Phase 271 — root tool surface audit

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Audited the remaining root-level installer, diagnostic and optional-provider
tools identified by the physical architecture gap list. The audit started at
`/home/mak/*` and searched only the active canonical/runtime departments;
`.git`, evidence, rollback and quarantine were excluded from the consumer
search. No script was launched.

## Validation evidence

```text
bash -n /home/mak/install_mak.sh          rc=0
bash -n /home/mak/instalar.sh             rc=0
bash -n /home/mak/diag-barrier-now.sh     rc=0
bash -n /home/mak/diag-kvm-linux.sh       rc=0
bash -n /home/mak/diag-red-linux.sh       rc=0

AST /home/mak/cli_watsonx.py              rc=0
AST /home/mak/oi-qwen.py                  rc=0

active-reference scan                     no matches; grep rc=1 (expected)
```

The scan covered `/home/mak/flujo`, `research`, `codex`, `curatoria`,
`plataforma`, `vigia` and `lenguaje`, excluding generated/evidence records.
It found no active launcher, unit, source or test consumer for these root
paths.

## Disposition by function

| Path | Function | Evidence | Disposition |
|---|---|---|---|
| `/home/mak/install_mak.sh` | Historical MAK installer | Generates a token, creates links and writes service/config state; contains operator-only sudo notes | Preserve; do not execute or promote |
| `/home/mak/instalar.sh` | Obsolete Open WebUI/Docker installer | Installs Docker, starts/enables it and runs a container with `--restart always` | Preserve as historical evidence; do not execute |
| `/home/mak/cli_watsonx.py` | Optional IBM WatsonX CLI | Reads `WATSONX_API_KEY` and calls IBM/local HTTP endpoints | Preserve; no provider call or dependency promotion |
| `/home/mak/oi-qwen.py` | Optional Open Interpreter/Ollama CLI | Sets `auto_run=True` and calls `interpreter.chat()` | Preserve; no launch or runtime promotion |
| `/home/mak/diag-barrier-now.sh` | Host diagnostic | Syntax-valid diagnostic shell | Preserve; no MAK consumer |
| `/home/mak/diag-kvm-linux.sh` | Host diagnostic | Syntax-valid diagnostic shell | Preserve; no MAK consumer |
| `/home/mak/diag-red-linux.sh` | Host diagnostic | Syntax-valid diagnostic shell | Preserve; no MAK consumer |

These files are not classified as confirmed junk: absence of a current
consumer is not proof that historical evidence may be deleted. No file was
moved, deleted, copied, installed or executed. WIN and protected data were
untouched.

## Risk and rollback

The two installers are intentionally execution-gated because they can change
host packages, Docker state, services, tokens and restart policy. The provider
tools are network/credential-gated. The diagnostics may inspect host state but
were not needed for this application architecture decision. Rollback is
therefore the no-op preservation of the original paths; no mutation occurred.

## Next concrete action

Refresh the objective matrix and operational handoff with this root-surface
decision, then move to the remaining architecture work: enumerate the final
canonical folder tree and identify only named duplicate document/tool families
that have a consumer-backed merge plan. Keep root installers, providers,
diagnostics, XIO, n8n, workers, live mutators and Git operations gated.
