# Phase 51 — Remaining MAK roots crosswalk

## Method

Started with the complete `/home/mak/*` listing, then bounded roots not
covered by Phase 49. No Git inventory, tree copy, service start or mutation
was used. The scan excluded vendored `.venv`, `venv`, `node_modules` and
`__pycache__` where stated; `curatoria_inbox` and `RD` are evidence/creative
surfaces, not runtime candidates.

## Classification

| root | bounded files | observed role | WIN relation | status |
|---|---:|---|---|---|
| `/home/mak/apps` | 1,301 | host/application assets and installed app surface | no matching department root | EVIDENCE_OR_HOST_SURFACE |
| `/home/mak/labs` | 99 | dated experiment/index evidence | no matching root | EVIDENCE_ONLY |
| `/home/mak/lenguaje` | 12 | active lexicon/measurement utility with shell/cron declarations | no matching root | LIVE_LOCAL_CANDIDATE |
| `/home/mak/src` | 148 | ML/mobileclip source and model acquisition scripts | generic WIN/flujo/src only | OPTIONAL_TOOL |
| `/home/mak/vigia` | 8 | small local guard/telemetry surface with state | no matching root | LIVE_LOCAL_CANDIDATE |
| `/home/mak/workspace` | 0 | empty workspace container | no matching root | EMPTY_CONTAINER |
| `/home/mak/curatoria_inbox` | 35,533 | incoming evidence, Windows probe and ARICA material | source/evidence, not runtime | EVIDENCE_INBOX |
| `/home/mak/RD` | 1,739 | creative/automation/render assets and reports | not a hub source by itself | CREATIVE_EVIDENCE_SURFACE |

## Decisions

`apps`, `labs`, `curatoria_inbox` and `RD` are not migration candidates from
file presence alone. `workspace` has no current consumer. `src` may become an
optional model/tool slice only after its external download contract is named.
The next locally executable small slice is `/home/mak/vigia` or
`/home/mak/lenguaje`, but both require a named consumer; the language root
also contains `cron_lexicon.sh` and `instalar_diccionarios.sh`, which remain
unexecuted. This report does not install dictionaries, models or services.

## Evidence commands and results

```text
find /home/mak -mindepth 1 -maxdepth 1 -printf '%f\\n' | sort
exit=0; complete active root list obtained
find <root> -type f ... | wc -l
exit=0; bounded counts recorded above
find /home/mak/WIN -maxdepth 5 -type d -iname <root-name>
exit=0; only generic WIN/flujo/src matches for src; no department match for
apps/labs/lenguaje/vigia/workspace/RD
```

## Risk

Counts are orientation, not proof of active use. Do not treat shell names,
cron declarations, model download scripts or generated RD material as an
authorization to run them. Preserve all evidence and keep the xio ADB gate
last.
