# Phase 312 — external runtime and root configuration gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `EXTERNAL_SURFACES_CLASSIFIED_NO_MUTATION`

## Scope

The physical search began at `/home/mak/*` and covered the remaining root-side
surfaces named by the architecture queue. Active MAK source/departments were
searched for Spanish and English path references. No provider, service,
installer, Git operation, Blender launch or network call was made.

## Disposition

| Path | Evidence | Decision |
|---|---|---|
| `/home/mak/blender` | real consumer in `cultura/mak_conductor/handler_registry.py` and the curatoria diagnostic; expected executable path is `/home/mak/blender/blender` | retain as live external runtime; do not merge into Python source |
| `/home/mak/blender-4.5.3-viejo` | parallel installed Blender tree; no active path consumer found | retain as `OLD_EXTERNAL_RUNTIME_CANDIDATE`; compare launcher/package identity before quarantine |
| `/home/mak/model-config/Modelfile` | no active exact path consumer; optional Ollama model declaration | preserve optional artifact; no model pull/promotion |
| `/home/mak/searxng/settings.yml` | research provider uses a local SearXNG URL contract; this file is service configuration | preserve external config; secret/key review is an operational gate; do not expose or rotate here |
| `/home/mak/venv-providers` | isolated provider virtual environment; no active exact path consumer | preserve isolated environment; no package install or promotion |
| `/home/mak/GENESIS.md` | host/project narrative with no runtime import | preserve historical narrative |
| `/home/mak/PENDIENTES_SUDO.md` | operator notes with no runtime import | preserve; never execute implicitly |

The two root installers and standalone WatsonX/Qwen tools were already
classified in Phase 271 and remain execution-gated; this phase did not rerun
them.

## Foreground validation

```text
static exact-path crosswalk: Blender 3 active references; model-config,
  venv-providers, GENESIS, PENDIENTES_SUDO and standalone provider tools 0
  exact path consumers; SearXNG path 0 direct path refs but provider contract
  exists by local URL/health state
bash -n /home/mak/install_mak.sh: exit 0
bash -n /home/mak/instalar.sh: exit 0
AST /home/mak/cli_watsonx.py and /home/mak/oi-qwen.py: 2/2 OK
no Blender, Ollama, SearXNG, provider or sync process observed
```

No file changed. No configuration value, credential, runtime environment,
database, asset or historical evidence was overwritten.

## Risks and next decision

The old Blender tree may be a usable rollback even though the active consumer
points to the newer root. It is not safe to call it junk from its name alone.
The SearXNG settings file contains operationally sensitive configuration; the
next security/operations task must review it without printing the value or
rotating it implicitly.

Before proposing Git branches, the remaining physical work is now a bounded
candidate manifest: old Blender path comparison, exact duplicate document
families with consumer ownership, and any confirmed regenerable residue. No
whole-root deletion is justified by this gate.
