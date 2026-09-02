# Phase 269 — physical architecture gap list

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Compared the frozen architecture documents against the current physical
surface beginning at `/home/mak/*`. No Git inventory, move, delete or service
execution was used.

## Gap list and disposition

| Physical path | Evidence/consumer | Current disposition | Action before any move |
|---|---|---|---|
| `/home/mak/searxng/settings.yml` | Research code uses the local SearXNG URL; the service is not active in this audit | external service configuration, disabled/protected | retain; verify service authority separately |
| `/home/mak/model-config/Modelfile` | no active first-party consumer found in bounded non-Git search | optional model artifact | retain as external model evidence; no promotion |
| `/home/mak/bin/mak_sync_safe.py` | explicitly consumed by `/home/mak/flujo-deploy`; sync is paused | external deploy owner | retain; never run or merge into canonical source here |
| `/home/mak/flujo-deploy` | deploy worktree with recorded projection consumer | external deploy surface | retain separately; rollback owner is its own audit |
| `/home/mak/_archive` | dated archive metadata and patch evidence | recovery/provenance | retain; no restore from archive by filename |
| `/home/mak/descargas` | default output of the platform downloader; manifest present | runtime output | retain with downloader consumer |
| `/home/mak/documentos` | empty host/user directory; no active consumer found | host user surface | preserve empty; not junk by emptiness alone |
| `/home/mak/tmp` | empty after reversible shadow quarantine; historical temp contract | host temporary surface | preserve empty; no recreation or cleanup needed |
| `/home/mak/GoogleDrive` | disconnected mount; RD lab metadata references a render source below it | external storage | leave untouched; do not repair mount or move media |
| `/home/mak/GENESIS.md` | original MAK organism narrative; no runtime import | historical narrative | retain outside canonical code; review stale claims only as documentation |
| `/home/mak/PENDIENTES_SUDO.md` | operator notes for host privileges; no runtime import | host operations note | retain; never execute commands implicitly |
| `/home/mak/cli_watsonx.py` | standalone provider CLI; no active first-party consumer found | optional provider tool | retain as external evidence; no provider call |
| `/home/mak/oi-qwen.py` | standalone Open Interpreter/Ollama launcher; no active consumer found | optional local tool | retain; no launch or dependency promotion |
| `/home/mak/install_mak.sh` | legacy host installer that mutates user services/config | historical installer | preserve; do not run; candidate only after explicit replacement decision |
| `/home/mak/instalar.sh` | legacy Docker/Open WebUI installer | obsolete installer candidate | preserve for provenance; no Docker/service action |
| `/home/mak/diag-*.sh` | host diagnostics, no application consumer | toolbox/history | retain; run only as a separate diagnostic request |
| `/home/mak/bucle`, `/home/mak/vibecodeine` | cultural/source projects without bounded active MAK consumer | source projects | preserve; no merge into FLUJO by similarity |

## Architecture conclusion

The final house remains layered:

```text
/home/mak/flujo       canonical FLUJO source, tests, data and contracts
/home/mak/{research,codex,curatoria,plataforma,vigia,lenguaje}
                       runtime projections with explicit consumers
/home/mak/RD          protected creative corpus
/home/mak/{labs,indexes,state}
                       derived evidence and audit state
/home/mak/{renders,portfolio_media,trazos}
                       generated/source delivery surfaces
/home/mak/{apps,src,models,venvs,blender,searxng}
                       external runtimes/configuration
/home/mak/WIN         immutable historical Windows source
/home/mak/{backups,rollback,quarantine}
                       recovery and reversible evidence
```

The missing architecture decision is not a broad folder move. It is a
path-level consumer gate for legacy platform UI and root installer/tool
artifacts. Treating them as junk now would violate provenance; treating them
as active would overstate integration.

## Next concrete action

Audit `/home/mak/plataforma/interfaz.py` against every non-Git active consumer
and its canonical projection. If no consumer exists and the replacement is
verified, prepare a reversible quarantine record; do not delete it.
