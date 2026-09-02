# Phase 185 — optional local-agent gate

Status: `CONTROLLED_DEFERRED_DEPENDENCY`

## Finding and change

`/home/mak/plataforma/chat_agente.py` (projection of the canonical
`cultura/mak_plataforma/chat_agente.py`) and the runtime-only
`/home/mak/plataforma/agente_real.py` import `qwen-agent`, which is not present
in the current venv and is not declared in the active MAK requirements.

Both tools were changed to treat that framework as optional at import time:
their tool declarations remain inspectable, and execution returns a clear
code `2` explaining that the dependency is missing and was not installed
automatically. No package was installed and no Ollama/model session was
started.

## Validation

- Isolated import of `chat_agente.py`: exit `0`.
- Isolated import of `agente_real.py`: exit `0`.
- Direct execution of each without `qwen-agent`: exit `2` with the controlled
  dependency message.
- No network/provider/GPU/worker/service/cron/mutator/WIN/Git action occurred.
- Initial validation caught and fixed a local `sys` scope error in
  `chat_agente.main`; the final gate passes.

## Decision

These are not silently promoted into the core dependency set. They remain
available as explicit optional local-agent tools. Installing `qwen-agent` and
testing its live Ollama loop is a separate authority decision; the repository
is now honest and import-safe without it.
