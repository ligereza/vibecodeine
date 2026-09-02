# Phase 243 - dependency slice closure

Date: 2026-08-15 (America/Santiago)
Owner: LUNA principal

## Scope

This gate closes the dependency map for the active MAK slices. It starts from
`/home/mak/*`, treats `/home/mak/flujo` as the canonical authoring root, and
does not convert the Windows global environment into a MAK requirements file.
The Spanish/English source surfaces were scanned by AST; import names were
then classified against the local package layout and the declared extras.

## Foreground evidence

Commands executed:

```text
PYTHONDONTWRITEBYTECODE=1 /home/mak/venvs/flujo/bin/python <AST/import classification>
/home/mak/venvs/flujo/bin/python -m pip check
PYTHONDONTWRITEBYTECODE=1 /home/mak/venvs/flujo/bin/python <find_spec availability probe>
```

Observed results:

- AST scan: 118 files across the dependency slices, 0 parse failures.
- The wider active projection AST gate remains 445 files, 444 pass, with only
  the known truncated `/home/mak/plataforma/panel_directivo.py` failure from
  Phase 234; this phase did not alter that evidence.
- Base environment `pip check`: exit 0, `No broken requirements found.`
- All nine declared base distributions were discoverable in
  `/home/mak/venvs/flujo`: matplotlib, PyYAML, Pillow, pydantic, typer, rich,
  jsonschema, requests and boto3.
- No package was installed, upgraded or removed. No service, cron, provider,
  model or upload path was started.

## Slice disposition

| Slice | Base/runtime dependencies | Optional or local dependencies | Result |
|---|---|---|---|
| FLUJO CLI, hub reads, jobs and knowledge | typer, rich, PyYAML, pydantic, requests, jsonschema, Pillow | `projects` is local under `/home/mak/flujo/projects`; pywebview, pystray and PyInstaller are optional extras and absent from the base venv | BASE_PASS; read CLI and hub gates already pass |
| RD catalog, field report and database readers | PyYAML and SQLite/Python stdlib | local `flujo` package only; field store remains empty and privacy-protected | BASE_PASS; read-only and empty-report gates pass |
| RD quote, plano and SVG asset reads | Pillow, matplotlib and base package | cairosvg is render-only and absent from the base venv; browser fallback remains code-defined | BASE_PASS_OPTIONAL_RENDER |
| Canonical MAK Platform | Pillow, boto3 and Python stdlib | `mak_conductor`, `mak_plataforma` local; numpy is present in base but used by lazy paths; MobileCLIP source is `/home/mak/src/ml-mobileclip`; torch exists only in `/home/mak/venvs/visual-index-pilot`; qwen_agent exists only in user-local site packages | BASE_PASS; GPU/provider/chat paths deferred and guarded |
| Research | Python stdlib plus local `fondart_corpus.py` and `mak_conductor` | numpy is a lazy acceleration path; no provider/model call in this gate | LOCAL_PASS_OPTIONAL_NUMPY |
| Codex and semantic motor | Pillow, Python stdlib and local `motor_semantico` | cairosvg is the render extra; available only in `/home/mak/research/.venv`, not the base venv | LOCAL_PASS_OPTIONAL_RENDER |
| Curatoria | Pillow, PyYAML, SQLite/stdlib | local `mak_conductor` and `mak_plataforma`; research helpers are package-local | BASE_LOCAL_PASS |
| Language/Tilde | Python stdlib and local wrappers | capable-model/provider dependencies are invoked only by explicit correction paths | STDLIB_PASS_PROVIDER_DEFERRED |

## Classification decisions

1. `PyInstaller`, `pywebview` and `pystray` remain build/desktop extras. Their
   absence from the base venv is not a broken runtime dependency.
2. `cairosvg` remains the declared `render` extra. The base read and fixture
   paths do not require it; the semantic rasterizer catches import and backend
   errors instead of failing at module import.
3. `projects`, `mak_conductor`, `mak_plataforma`, `motor_semantico` and
   `fondart_corpus` are local MAK sources, not third-party packages. They must
   be resolved through the owning source roots, not added to requirements.
4. `mobileclip` is local source plus a model contract, while `torch` is tied to
   the separate visual-index environment. Neither is silently promoted to the
   base venv.
5. `qwen_agent` is present only in the user-local site-packages tree and is
   guarded by `chat_agente.py`; it is not a base dependency.
6. `numpy` is present in the base venv and appears in lazy research/visual
   paths. It is not declared in the base project dependencies; no declaration
   change is justified until the specific consumer is intentionally promoted
   to a required slice.
7. The Windows `pip check` conflicts describe a mixed Windows environment and
   remain evidence only. They do not justify changing the MAK base lock.

## Changed files and rollback

Only this report and its CSV companion were added under `context/`. Active
source, runtime paths, databases, assets, WIN evidence and dependency files
were unchanged. Rollback is removal of these two evidence files only; no
operational rollback is required.

## Open risk and next action

The optional visual, provider, desktop and render paths still require their
own explicitly bounded environment/authority if they are promoted. The next
safe action is a read-only entrypoint matrix for the remaining active
non-RD projections, followed by objective reconciliation. Do not install
extras, enable providers, start services or rewrite the base requirements.
