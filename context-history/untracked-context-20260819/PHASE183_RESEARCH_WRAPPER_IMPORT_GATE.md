# Phase 183 — research runtime wrapper import gate

Status: `PASS_AFTER_PATH_FIX`

## Finding

The runtime projections in `/home/mak/research` correctly delegated to the
canonical implementations in `/home/mak/flujo/cultura/mak_research`, but the
nine wrappers did not add the canonical directory to `sys.path`. Invoking a
wrapper from outside the repository therefore failed before doing any work;
the first probe returned:

```text
ModuleNotFoundError: No module named 'formato_ensayo'
RESEARCH_GATE_RC=1
```

## Change

Added a guarded canonical-parent `sys.path` insertion to these runtime
projections only:

`cadena.py`, `cola.py`, `fuentes.py`, `grafo.py`, `memoria.py`, `panel.py`,
`refutar.py`, `research.py`, and `worker.py`.

The canonical implementations remain the semantic owners. No generated
research output, mailbox, checkpoint, lock, provider or service was touched.

## Validation

- AST parse of canonical and runtime Python surfaces: 63 files, exit `0`.
- Isolated import subprocess for all nine wrappers: 9/9 exit `0`.
- Existing stale PID files `.cola.pid=5172` and `.webui.pid=68022` had no
  matching live processes.
- No research command, network/provider call, worker, cron or service started.
- No package was installed.

Runtime-only extra files (`fondart_corpus.py`, `patch_interfaz.py`,
`source_pipeline.py`, and test scripts) remain preserved as historical/runtime
evidence. They are not silently deleted merely because the canonical source
does not contain them.

Next: continue with a bounded, no-provider contract check for research input
validation and the platform bridge; defer live provider execution and
permanent workers until separately authorized.
