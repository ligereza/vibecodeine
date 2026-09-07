# Fases consolidadas

Consolidación de los documentos de fase repetidos en cuatro rutas físicas.
Se conserva un contenido por fase y se registran todas las rutas originales.
Los documentos originales no se eliminan mediante este consolidado.

Fases únicas: 16
Rutas originales registradas: 64


---

## PHASE39_HUB_AGENT_ROLES_READONLY_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE39_HUB_AGENT_ROLES_READONLY_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE39_HUB_AGENT_ROLES_READONLY_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE39_HUB_AGENT_ROLES_READONLY_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE39_HUB_AGENT_ROLES_READONLY_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE39_HUB_AGENT_ROLES_READONLY_GATE.md`

# Phase 39 — hub agent roles read-only gate

Identity: LUNA principal
Status: INTEGRATED_READ_ONLY_WITH_POLICY_BOUNDARY
Scope: validate the local role catalog exposed to the FLUJO hub UI without
dispatching roles or changing delegation state.

## Consumer and provenance

- Hub route: `GET /api/agents-roles`.
- MAK source: `/home/mak/flujo/src/flujo/web/hub.py`, method
  `HubRequestHandler._get_agents_roles`.
- WIN comparison source: `/home/mak/WIN/flujo/src/flujo/web/hub.py`.
- The route returns a static role definition map with prompt templates. The
  nearby `_handle_delegate` method was not called; no subagent, process,
  provider or delegation state was created.
- Search vocabulary used: `agent`, `agente`, `role`, `rol`, `delegate`,
  `delegar`, `creative`, `visual`, `pipeline`, `packaging`, `future`,
  `prompt`, `task`, `tarea`, `LUNA`. Residual risk is limited to future role
  definitions not returned by this route.

## Static and direct validation

Foreground command (exit 0):

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python - <<'PY'
  ast.parse(MAK hub.py); ast.parse(WIN hub.py)
  import flujo.web.hub
  HubRequestHandler._get_agents_roles()
PY
```

Observed:

- AST/import gate: `PASS`.
- Five unique ASCII role IDs: `creative-director`, `visual-polish`,
  `pipeline`, `future`, `packaging`.
- Each role has exactly `id`, `name`, `short`, `focus` and
  `prompt_template`; every template contains `{task}`.
- MAK/WIN role IDs match by bounded AST extraction.
- Direct response envelope keys: `roles`, `note`.

## Temporary HTTP gate

A temporary in-process `ThreadingHTTPServer` was bound to
`127.0.0.1:<ephemeral>`. Exactly one `GET /api/agents-roles` was served, then
the server was shut down and joined.

- HTTP status: `200`.
- HTTP payload matched the direct payload exactly.
- Dispatch called: `false`.
- Protected hub-source snapshot: `writes_detected=false`.
- No POST, subprocess, provider, network call or worker ran.

## Policy boundary and decision

The role catalog is integrated as a read-only UI contract and is physically
present in both WIN and MAK. It is not the delegation authority for this
migration: the active policy remains LUNA-only, maximum three active agents,
no recursive delegation, and traceable `LUNA-N` identities. The generic app
roles must not be used to infer or dispatch subagents in this task.

Rollback is physical preservation: retain the static role reader and do not
invoke `_handle_delegate` unless a separate, authorized delegation slice
defines its identity, write set and runtime boundary.


---

## PHASE103_CODEX_CORE_OWNERSHIP_MERGE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE103_CODEX_CORE_OWNERSHIP_MERGE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE103_CODEX_CORE_OWNERSHIP_MERGE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE103_CODEX_CORE_OWNERSHIP_MERGE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE103_CODEX_CORE_OWNERSHIP_MERGE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE103_CODEX_CORE_OWNERSHIP_MERGE.md`

# Phase 103 — CODEX core ownership merge

## Scope and evidence

The active MAK root and canonical copies of `codex_lib.py` and `generar.py`
were byte-identical. WIN `generar.py` also matched; WIN `codex_lib.py` was a
distinct historical variant. CODEX consumers import `codex_lib` from the
generator, review/debug/test tools, conductor handlers and icon pipeline.

## Action

Replaced only `/home/mak/codex/codex_lib.py` and
`/home/mak/codex/generar.py` with compatibility projections to the canonical
MAK implementations. Direct generator execution remains available through
`__main__`; the library remains import-oriented. WIN, generated CODEX pieces,
logs, state and sandbox outputs were not changed.

## Foreground validation

- Root `codex_lib` import: exit 0; exported library contract available.
- Root `generar.py --help`: exit 0.
- Root bridges and canonical sources compiled: exit 0.
- No generator, sandbox, provider, model, worker, hub, Blender or Ollama
  process was started.

## Rollback and risk

Rollback is local from the pre-edit root files or preserved WIN copies. WIN
`codex_lib.py` divergence remains a semantic review item. Public/private names
are re-exported; module metadata callers remain an untested edge. External
CODEX execution remains gated.

## Result

MAK CODEX core and generator now have one active implementation owner while
historical WIN behavior and generated evidence remain preserved.

---

## PHASE104_CODEX_CONSUMER_FAMILY_OWNERSHIP_MERGE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE104_CODEX_CONSUMER_FAMILY_OWNERSHIP_MERGE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE104_CODEX_CONSUMER_FAMILY_OWNERSHIP_MERGE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE104_CODEX_CONSUMER_FAMILY_OWNERSHIP_MERGE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE104_CODEX_CONSUMER_FAMILY_OWNERSHIP_MERGE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE104_CODEX_CONSUMER_FAMILY_OWNERSHIP_MERGE.md`

# Phase 104 — CODEX consumer family ownership merge

## Scope and evidence

`revisar.py`, `testear.py` and `worker_codex.py` were byte-identical across
active MAK root, canonical source and WIN. They have real consumers through
`interfaz_codex.py`, conductor handlers and the worker mode table. In
contrast, `agente_libre.py` differs between canonical MAK and root/WIN and was
not treated as a duplicate.

## Action

Replaced only the three active root files with compatibility projections to
the canonical implementations. Direct `revisar.py` and `testear.py`
entrypoints remain available; `worker_codex.py` remains import-oriented. No
review, test generation, worker, provider, model, sandbox, notification or
output action ran. `agente_libre.py`, WIN, generated pieces, logs and state
were untouched.

## Foreground validation

- Root imports for all three modules: exit 0.
- `revisar.py --help` and `testear.py --help`: exit 0.
- Root bridges and canonical sources compiled: exit 0.
- No CODEX worker, generator, provider, model, hub, Blender or Ollama process
  remained.

## Rollback and risk

Rollback is local from the pre-edit root files or WIN copies. `agente_libre.py`
requires a separate semantic comparison because canonical and root/WIN content
diverge. External-capable CODEX execution remains gated; module metadata
callers are an untested edge.

## Result

Three active CODEX consumers now have one implementation owner, while the
divergent free-agent tool remains explicitly open rather than being silently
replaced.

---

## PHASE105_CODEX_FREE_AGENT_OWNERSHIP_MERGE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE105_CODEX_FREE_AGENT_OWNERSHIP_MERGE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE105_CODEX_FREE_AGENT_OWNERSHIP_MERGE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE105_CODEX_FREE_AGENT_OWNERSHIP_MERGE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE105_CODEX_FREE_AGENT_OWNERSHIP_MERGE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE105_CODEX_FREE_AGENT_OWNERSHIP_MERGE.md`

# Phase 105 — CODEX free-agent ownership merge

## Scope and evidence

`agente_libre.py` had three byte differences between canonical MAK and root/WIN,
all in comments; functions, constants and structure were identical. It has
real consumers in `capataz.py`, conductor handlers and the producer catalog,
but its pipeline can write CODEX pieces/jobs and call models.

## Action

Replaced only `/home/mak/codex/agente_libre.py` with a compatibility projection
to the canonical implementation. The behavioral content was unchanged; the
root direct entrypoint remains available. WIN, CODEX pieces, jobs, logs and
state were not changed.

## Foreground validation

- Root import and exported `_correr_unlocked`/`main` contract: exit 0.
- Root `agente_libre.py --help`: exit 0.
- Root bridge and canonical source compile: exit 0.
- No free-agent pipeline, model, provider, file write, worker, hub, Blender or
  Ollama process was started.

## Rollback and risk

Rollback is local from the pre-edit root file or WIN copy. The write and
external-model boundaries remain gated; only safe import/help validation ran.

## Result

CODEX now has one active owner for the free-agent harness. Historical WIN and
generated evidence remain preserved.

---

## PHASE168_CODEX_SEMANTIC_ENGINE_FIXTURE_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE168_CODEX_SEMANTIC_ENGINE_FIXTURE_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE168_CODEX_SEMANTIC_ENGINE_FIXTURE_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE168_CODEX_SEMANTIC_ENGINE_FIXTURE_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE168_CODEX_SEMANTIC_ENGINE_FIXTURE_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE168_CODEX_SEMANTIC_ENGINE_FIXTURE_GATE.md`

# Phase 168 — Codex semantic engine fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical package: `/home/mak/flujo/cultura/mak_codex/motor_semantico`
- Runtime package: `/home/mak/codex/motor_semantico`
- Consumer: Codex icon generation and SVG review workflows
- Interface: `compilador.py spec.json output.svg`

## Result

All source/runtime semantic-engine Python files compiled. The canonical and
runtime CLI were run independently against the same temporary semantic spec;
both returned exit `0`, emitted the same success contract and produced
byte-identical SVG output (`3802` bytes, `viewBox="0 0 120 120"`). No real Codex
piece, provider, worker, service or persistent process was touched.

## Decision

The exact engine package is functionally reconciled. Keep `piezas/` and their
manifests as historical/generated evidence; do not collapse them into source
code or delete them. Next inspect the Codex job/worker boundary, where provider
calls and writes require fixture isolation.

---

## PHASE169_CODEX_JOB_BOUNDARY_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE169_CODEX_JOB_BOUNDARY_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE169_CODEX_JOB_BOUNDARY_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE169_CODEX_JOB_BOUNDARY_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE169_CODEX_JOB_BOUNDARY_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE169_CODEX_JOB_BOUNDARY_GATE.md`

# Phase 169 — Codex job boundary gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical library: `/home/mak/flujo/cultura/mak_codex/codex_lib.py`
- Runtime library: `/home/mak/codex/codex_lib.py` (compatibility projection)
- Canonical worker: `/home/mak/flujo/cultura/mak_codex/worker_codex.py`
- Runtime worker: `/home/mak/codex/worker_codex.py` (compatibility projection)
- Consumer: Codex API/service job dispatch

## Result

All four files compiled. Source/runtime library imports exposed the same coder
chain parsing contract, including invalid-key fallback to the complete default
chain. Source/runtime workers were imported with dispatch disabled and their
safe boundaries were exercised: unknown mode returns a structured failure and
an out-of-scope path is rejected before subprocess/provider work. No LLM,
Ollama, NIM, Watson, job subprocess, lock, event, service or persistent
process was started.

## Decision

The runtime Codex library/worker projections are already canonicalized. Keep
provider-backed `run_pedido()` execution gated; its normal path writes jobs and
pieces and acquires GPU/locks. Next inspect the local non-provider Codex
validation path (`calidad_loop.py` or `testear.py`) with a fixture.

---

## PHASE170_CODEX_QUALITY_FIXTURE_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE170_CODEX_QUALITY_FIXTURE_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE170_CODEX_QUALITY_FIXTURE_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE170_CODEX_QUALITY_FIXTURE_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE170_CODEX_QUALITY_FIXTURE_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE170_CODEX_QUALITY_FIXTURE_GATE.md`

# Phase 170 — Codex quality loop fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical: `/home/mak/flujo/cultura/mak_plataforma/calidad_loop.py`
- Runtime: `/home/mak/plataforma/calidad_loop.py`
- Inputs: Codex `jobs.jsonl`, optional delivery state and backlog text
- Output: sibling `CALIDAD_LOOP.md`
- Consumer: local operator quality/rate report

## Result

Both source/runtime files compiled. A temporary fixture containing ready,
blocked, review and failed jobs plus dated/undated backlog entries was processed
through both CLIs. Both returned exit `0`, wrote identical reports and exposed
the same metrics: four jobs, one guard block, two backlog items and fourteen
days maximum age. No real jobs, delivery state, backlog, generated pieces,
providers or services were touched.

## Decision

The quality loop is reconciled as an exact data-path-compatible projection.
Keep its report output behind the fixture gate; the next Codex step is the
local `testear.py` validation path, not worker execution.

---

## PHASE171_CODEX_TESTEAR_FIXTURE_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE171_CODEX_TESTEAR_FIXTURE_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE171_CODEX_TESTEAR_FIXTURE_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE171_CODEX_TESTEAR_FIXTURE_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE171_CODEX_TESTEAR_FIXTURE_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE171_CODEX_TESTEAR_FIXTURE_GATE.md`

# Phase 171 — Codex testear isolation fix and fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Finding

The initial fixture exposed a real defect in
`/home/mak/flujo/cultura/mak_codex/testear.py`: it copied the module and
generated tests into a temporary directory, then invoked `python -I -m
unittest`. Python isolated mode removed the temporary directory from
`sys.path`, so the valid fixture failed with `ModuleNotFoundError` before the
test ran.

## Fix

The canonical source now keeps `-I` and runs a tiny isolated `-c` runner that
inserts the known temporary directory into `sys.path` before invoking
`unittest.main(module='test_pieza')`. The runtime
`/home/mak/codex/testear.py` is already a canonical compatibility wrapper and
was not edited.

## Foreground result

Both source and runtime compiled. With the provider replaced by a local fake
coder and `REVISIONES` redirected to temporary directories, both paths generated
and executed the same pure-Python test successfully: `SOURCE_OK=True RC=0`,
`RUNTIME_OK=True RC=0`, report status `OK`, process gate clear. No provider,
real piece, manifest, worker, service or persistent process was touched.

## Next action

Run the core compile/health/web checks after this source fix, then continue the
Codex surface with `generar.py`/`iconos.py` only through provider-free validation
or fixtures.

---

## PHASE173_CODEX_ICONOS_FIXTURE_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE173_CODEX_ICONOS_FIXTURE_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE173_CODEX_ICONOS_FIXTURE_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE173_CODEX_ICONOS_FIXTURE_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE173_CODEX_ICONOS_FIXTURE_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE173_CODEX_ICONOS_FIXTURE_GATE.md`

# Phase 173 — Codex iconos fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

Canonical and runtime `iconos.py` were compiled and executed with a local
planner stub and temporary piece/report destinations. Both produced
`smoke_ok=True`, valid visual metrics, `dedupe=unique` and byte-identical SVG
output. The real Codex pieces and providers were untouched; no service or
process remained.

Paths:

- `/home/mak/flujo/cultura/mak_codex/iconos.py`
- `/home/mak/codex/iconos.py`

Decision: keep the existing runtime/source pair and generated pieces
classified; no wrapper or deletion is needed.

---

## PHASE174_CODEX_GENERAR_FIXTURE_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE174_CODEX_GENERAR_FIXTURE_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE174_CODEX_GENERAR_FIXTURE_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE174_CODEX_GENERAR_FIXTURE_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE174_CODEX_GENERAR_FIXTURE_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE174_CODEX_GENERAR_FIXTURE_GATE.md`

# Phase 174 — Codex generar fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

Canonical and runtime `generar.py` were compiled and run through the complete
plan -> code -> scan -> sandbox -> piece contract using local planner/coder,
scanner and sandbox stubs. Both returned `ok=True`, `smoke_ok=True`, wrote only
temporary reports/pieces and emitted identical generated code. No LLM/provider,
real Codex piece, worker, lock, service or persistent process was touched.

Paths:

- `/home/mak/flujo/cultura/mak_codex/generar.py`
- `/home/mak/codex/generar.py`

Decision: keep the canonical generator projection; provider-backed execution
remains gated by its existing runtime boundary.

---

## PHASE185_OPTIONAL_AGENT_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE185_OPTIONAL_AGENT_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE185_OPTIONAL_AGENT_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE185_OPTIONAL_AGENT_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE185_OPTIONAL_AGENT_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE185_OPTIONAL_AGENT_GATE.md`

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

---

## PHASE193_CODEX_ROLE_MATRIX.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE193_CODEX_ROLE_MATRIX.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE193_CODEX_ROLE_MATRIX.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE193_CODEX_ROLE_MATRIX.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE193_CODEX_ROLE_MATRIX.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE193_CODEX_ROLE_MATRIX.md`

# Phase 193 — Codex role matrix

Status: `COMPLETE; SOURCE_RUNTIME_BOUNDARY_CONFIRMED`

## Evidence

The direct source/runtime comparison for the ten Codex Python modules found:

- Exact pairs: `debug.py`, `fallback_util.py`, `iconos.py`, and
  `interfaz_codex.py`.
- Semantic runtime projections: `agente_libre.py`, `codex_lib.py`,
  `generar.py`, `revisar.py`, `testear.py`, and `worker_codex.py`.
- No source-only or runtime-only Python module in this paired set.

The canonical semantic owner is `/home/mak/flujo/cultura/mak_codex`; runtime
entry points under `/home/mak/codex` are retained for service/manual paths.
The source `testear.py` path was repaired in Phase 171 and passed isolated
fixture validation. `interfaz_codex.py` is the service declaration target but
the user unit is currently inactive.

## Decision

Codex is already fused at the ownership level: one canonical implementation,
thin runtime projections for the historical paths, and exact shared helpers
where no projection is needed. No duplicate deletion or new copy is justified.

## Validation

Hash comparison exited `0`; prior Codex semantic/fixture gates passed through
Phases 168–174 and 171's test-runner fix. No provider, service, worker, package,
cron, WIN or Git action occurred in this phase.

Next: use the same matrix for the remaining platform projections, prioritizing
one actual consumer with a bounded pure fixture rather than broad cleanup.

---

## PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE258_RESEARCH_CODEX_CONTRACT_GATE.md`

# Phase 258 — Research/Codex contract gate

Date: 2026-08-15 America/Santiago
Owner: LUNA principal
Subagents: none

## Scope

Run source/configuration-only Research/Codex contracts:

- `tests/test_formatos_mak.py`
- `tests/test_codex_no_es_sandbox.py`
- `tests/test_codex_cadena.py`
- `tests/test_refutar_orden.py`
- `tests/test_formato_ensayo.py`
- `tests/test_fuentes.py`
- `tests/test_mapa_completo.py`
- `tests/test_mak_sin_gptmini.py`

These verify model/roster boundaries, prompt contracts, source gates and MAPA
coverage. They do not call providers or network-backed research.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_formatos_mak.py tests/test_codex_no_es_sandbox.py \
  tests/test_codex_cadena.py tests/test_refutar_orden.py \
  tests/test_formato_ensayo.py tests/test_fuentes.py \
  tests/test_mapa_completo.py tests/test_mak_sin_gptmini.py
exit 0; 81 tests passed
```

## Result

The read-only Research/Codex contract slice is green. Provider rosters remain
configuration evidence; no provider was contacted and no external state was
changed.

## Risk and rollback

No persistent file, database, service or provider state changed. No rollback is
needed. Provider-backed research and workers remain gated.

## Next concrete action

Promote one bounded local research-state/queue fixture group, keeping worker
threads and provider/network calls disabled.

---

## PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE266_DISABLED_CLAUDE_WORKFLOW_GATE.md`

# Phase 266 — disabled Claude workflow boundary

Date: 2026-08-15 America/Santiago
Owner: LUNA principal
Subagents: none

## Finding

The active test contract expected `.github/workflows/claude.yml`, but the file
was absent. The only physical source was the historical WIN workflow, whose
permissions included `contents: write`, `pull-requests: write` and
`issues: write`; promoting it would have reactivated an external write path.

## Action

Added one minimal active contract:

`/home/mak/flujo/.github/workflows/claude.yml`

It has only `workflow_dispatch: {}`, `permissions: {}` and a job guarded by
`if: ${{ false }}`. It contains no issue/PR trigger, Git push, PR creation or
write permission. WIN and all historical copies remain unchanged.

## Validation

The first run of the 16-file local candidate group exited `1` because the
missing file caused two `test_git_web_contract.py` failures. After the minimal
contract was added:

```text
pytest -q --disable-warnings \
  tests/test_becas_calendario.py tests/test_blender_nodes.py \
  tests/test_blender_nodes_video.py tests/test_busqueda_ciega.py \
  tests/test_capataz_enrutamiento.py tests/test_consulta_busqueda.py \
  tests/test_copilot.py tests/test_corpus_a_micelio.py \
  tests/test_git_web_contract.py tests/test_iconos_conjunto.py \
  tests/test_manifest.py tests/test_psicosis_agente.py \
  tests/test_reactivo_matcher.py tests/test_tilde_paridad.py \
  tests/test_validate_airdrop.py tests/test_zipper.py
exit 0; 188 tests passed
```

## Risk and rollback

No workflow was dispatched and no external system was contacted. Rollback is a
narrow removal of the new disabled contract after explicit review; do not
replace it with the writable WIN workflow.

## Next concrete action

Recalculate the residual candidate inventory, then continue only with pure
fixture groups. Keep all external/provider/worker/XIO/n8n and live mutation
paths deferred.

---

## PHASE366_CODEX_PROJECTION_GATE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE366_CODEX_PROJECTION_GATE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE366_CODEX_PROJECTION_GATE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE366_CODEX_PROJECTION_GATE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE366_CODEX_PROJECTION_GATE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE366_CODEX_PROJECTION_GATE.md`

# Phase 366 — Codex projection/consumer gate

Date: 2026-08-15 (America/Santiago)

## Scope

Audited the declared Codex mirror set without traversing caches or data:
`agente_libre.py`, `interfaz_codex.py` and the service unit. The root
`agente_libre.py` is an intentional compatibility wrapper around the
canonical implementation; `interfaz_codex.py` is an exact paired projection.

## Results

```text
CODEX_CANONICAL_IMPORTS=PASS
IMPORT_RC=0
PYCOMPILE_RC=0
UNIT_VERIFY_RC=0
```

The active consumer references the canonical Codex path through the declared
deployment manifest. No server, generated job, provider, subprocess worker or
external call was started.

## Disposition

`CODEX_OWNER_PROJECTION_VERIFIED; WRAPPER_INTENTIONAL`

No merge or deletion is justified: the wrapper and the exact projection have
different roles, and the service entrypoint remains explicit.

## Rollback and boundary

No source, job ledger, generated piece, database, service state, Git, Docker or
WIN evidence changed. No rollback is required. POST/job execution remains a
separate live-mutation gate.

---

## PHASE377_CODEX_MALFORMED_OUTPUT_QUARANTINE.md

### Rutas originales

- `/home/mak/.claude/worktrees/adversarial-fixes-20260902/context-history/untracked-context-20260819/PHASE377_CODEX_MALFORMED_OUTPUT_QUARANTINE.md`
- `/home/mak/.claude/worktrees/contrato-unico-20260903/context-history/untracked-context-20260819/PHASE377_CODEX_MALFORMED_OUTPUT_QUARANTINE.md`
- `/home/mak/context-history/untracked-context-20260819/PHASE377_CODEX_MALFORMED_OUTPUT_QUARANTINE.md`
- `/home/mak/flujo/context-history/untracked-context-20260819/PHASE377_CODEX_MALFORMED_OUTPUT_QUARANTINE.md`

Contenido consolidado desde: `/home/mak/context-history/untracked-context-20260819/PHASE377_CODEX_MALFORMED_OUTPUT_QUARANTINE.md`

# Phase 377 — malformed generated Codex output quarantine

Date: 2026-08-15 (America/Santiago)

## Finding

Seven files under `/home/mak/codex/piezas` failed AST because they were
truncated, fenced Markdown or assistant refusal text rather than executable
Python. A bounded consumer scan found zero active references to their exact
filenames.

## Action

Moved exactly those seven files, without copying or editing them, to:

`/home/mak/flujo/context/quarantine/phase376_malformed_generated_codex/`

All seven retained mode `0644`, byte size and SHA-256. The inverse operation
is a direct move back to `/home/mak/codex/piezas/` using the recorded basename.

## Validation

```text
CODEX_ACTIVE_GENERATED_PY_AFTER=106
CODEX_ACTIVE_GENERATED_AST_FAIL=0
CODEX_MALFORMED_QUARANTINE=7
POST_MOVE_AST_RC=0
```

The active generated surface now parses; the quarantined products remain
recoverable evidence. No source, database, credential, service, provider, Git
or WIN state changed.

Disposition: `MALFORMED_GENERATED_OUTPUT_QUARANTINED; REVERSIBLE`.
