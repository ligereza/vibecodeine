# Phase 281 — root external review

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Reconciled the remaining root-side review surfaces against the layered MAK
owner map. No service, model, provider, renderer or installer was launched.

## Findings and disposition

| Surface | Evidence | Disposition |
|---|---|---|
| `/home/mak/model-config/Modelfile` | Optional Ollama/model artifact; no absolute active consumer found | Preserve external optional asset; no model pull or promotion |
| `/home/mak/searxng/settings.yml` | External search configuration containing protected secret material; no absolute active consumer found | Preserve protected external config; never print, rotate or call it in this phase |
| `/home/mak/blender` | Current 1.2 GB external Blender install; active render tools exist and may resolve `blender` by PATH | Preserve external runtime; optional consumer gate remains |
| `/home/mak/blender-4.5.3-viejo` | Older 1.2 GB external install; main binaries differ (`cmp` rc=1) | Preserve until version/provenance decision; no age/size deletion |
| `/home/mak/venv-providers` | 57 MB provider environment; no absolute active consumer found | Preserve isolated optional runtime; no provider import/call |
| loose root narratives/logs/installers | Phase 269/271 path-level dispositions | Preserve evidence or execution-gated; no broad root cleanup |

The active render tools under FLUJO mean Blender cannot be called unconsumed
solely because its absolute installation path is not hardcoded. Conversely,
the old Blender binary is not a duplicate by byte comparison. Both stay
external until an explicit runtime/version test selects one.

## Decision

No root external item passed all junk gates (no consumer, no evidence role, no
protected data, reversible quarantine, and foreground validation). No file was
moved or deleted. Secrets, models, environments, databases, media, WIN and
Git state were untouched.

## Next concrete action

Create the visual architecture closeout and reconcile it with the existing
branch proposal. Keep branch creation, merge, deploy, provider/GPU, Blender,
XIO, n8n and live mutator operations gated.
