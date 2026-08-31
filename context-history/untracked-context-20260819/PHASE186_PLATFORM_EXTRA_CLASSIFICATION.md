# Phase 186 — platform runtime-only extra classification

Status: `CLASSIFIED; ONE LEGACY ARTIFACT BLOCKED`

## Runtime-only files not present in canonical `mak_plataforma`

| Path | Finding | Consumer/owner | Decision |
|---|---|---|---|
| `/home/mak/plataforma/agente_real.py` | Optional `qwen-agent` local agent; now import-safe and controlled exit 2 when absent | Human operator; no automatic service | Preserve as optional tool; dependency not installed |
| `/home/mak/plataforma/interfaz.py` | Large legacy research web UI | Research runtime boundary; canonical research UI is `/home/mak/research/interfaz.py` | Preserve and do not silently merge; requires separate route/port comparison |
| `/home/mak/plataforma/memoria.py` | Legacy local memory/RAG implementation | Research memory consumer, but canonical owner is `mak_research/memoria.py` | Preserve as historical candidate; canonical research wrapper is the active path |
| `/home/mak/plataforma/panel_directivo.py` | Truncated at line 145 inside `_calidad_piezas`; AST/SyntaxError | No verified active service or canonical owner | Blocked evidence; do not reconstruct or delete in this phase |
| `/home/mak/plataforma/vigia.py` | Older watch implementation | Canonical owner is `mak_vigia`; runtime `/home/mak/vigia` already parity-gated | Preserve until final folder architecture; not a new migration slice |

The platform service declarations point to `/home/mak/research/interfaz.py`
and `/home/mak/codex/interfaz_codex.py`, not `panel_directivo.py`. The only
known `panel_directivo.py` references are historical phase records; no active
systemd unit was found for it.

## Validation

- Static AST/import gate for 14 remaining platform projections: all AST parses
  passed; 13 imports passed.
- `chat_agente.py` initially exposed missing `qwen-agent`; Phase 185 changed it
  to a controlled optional-dependency boundary. Final import/execution gate is
  recorded in Phase 185.
- `panel_directivo.py` remains the known intentional failure: syntax error at
  line 145, unchanged. It is incomplete, so a syntax-only repair would create
  false confidence rather than a functioning panel.
- No services, sockets, cron jobs, mutators, providers, GPU, packages, WIN or
  Git actions were used.

## Next

Compare the two surviving research UI candidates (`/home/mak/plataforma/interfaz.py`
and `/home/mak/research/interfaz.py`) by routes, output roots, ports and
runtime dependencies using static/fixture evidence. Do not start either UI or
merge/delete either file during that comparison.
