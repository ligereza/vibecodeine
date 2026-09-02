# Phase 115 — platform capataz/chat ownership merge

## Scope and evidence

`capataz.py` and `chat_agente.py` were identical between active MAK root and
canonical source. WIN `capataz.py` differed only in documentation; WIN
`chat_agente.py` retained the obsolete Windows/remote Ollama address
`192.168.50.1`, while MAK canonical/root correctly use local
`127.0.0.1:11434`.

## Action

Replaced only the active root files with compatibility projections to canonical
MAK. WIN was preserved as historical evidence. No capataz cycle, chat loop,
PR review, delivery, HTTP request, provider, Ollama or state write ran.

## Foreground validation

- Root `capataz` import and corrected deterministic `evaluar_riesgo`/`validar`
  fixtures using the real `investigar` action: exit 0.
- Root and canonical chat sources compile: exit 0. Runtime import is gated in
  the canonical venv because `qwen_agent` is missing
  (`ModuleNotFoundError`); no installation was attempted.
- AST inspection confirmed the active chat endpoint is local
  `http://127.0.0.1:11434/v1`; the WIN remote address is not active MAK config.
- No chat, capataz, hub, worker, Blender or Ollama process remained.

## Rollback and risk

Rollback is local from pre-edit root files or WIN copies. Chat tools `vetear`
and `entregar` remain mutating subprocess boundaries and were not invoked. The
missing `qwen_agent` dependency is an explicit runtime gate; installing it
requires separate authorization.
WIN's remote address remains historical and must not be restored as MAK runtime
configuration.

## Result

MAK capataz and chat now have one active local implementation owner, with the
obsolete Windows network target retained only in WIN history.
