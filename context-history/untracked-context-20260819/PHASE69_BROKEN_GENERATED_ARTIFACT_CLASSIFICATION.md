# Phase 69 — broken/generated artifact classification

## Findings

### `panel_directivo.py`

`/home/mak/plataforma/panel_directivo.py` ends at line 144 inside a nested
`try` block. AST compilation fails with `SyntaxError: expected 'except' or
'finally' block` at line 145. The file contains its own historical launcher
comment but no active FLUJO/conductor consumer was found. Its intended output
is described by dated Codex manifests and markdown pieces under
`/home/mak/codex/piezas/`.

Classification: `EVIDENCE_BROKEN_GENERATED`, not `LIVE_SOURCE`, not
`JUNK_CONFIRMED`. Repair would be a separate product decision because the file
is an incomplete projection and its intended complete version is not proven.

### Seven malformed Codex pieces

The following dated `.py` files fail compilation:

```text
20260724-005009-implementar-cron-jobs-codex-retry-y-code.py
20260724-065114-implementar-los-ajustes-de-la-cadena-de-.py
20260801-013822-generar-ascii-art-a-partir-de-una-imagen.py
20260723-053837-un-formateador-stdlib-que-tome-un-inform.py
20260716-212204-funcion-aplanar-anidada-que-aplane-una-l.py
20260722-184627-generar-script-usr-local-bin-backlog-cod.py
20260727-085032-generar-script-bash-que-reinicie-el-serv.py
```

Their contents include refusal text, prose, incomplete drafts or unterminated
strings. The Codex writer intentionally stores dated pieces and companion
markdown/manifests; logs reference this directory as an output surface. No
active import or conductor route consumes these seven files.

Classification: `EVIDENCE_BROKEN_GENERATED`. Preserve the `.py` plus companion
evidence until a future bounded archive decision. Do not repair them by
guessing the original prompt and do not delete them as generic cache.

## Validation

- bounded `compile()` scan of `/home/mak/codex/piezas/*.py`: 7 failures;
- targeted consumer search: no active import of the seven filenames;
- targeted panel search: only the panel itself, historical handoff and logs;
- no process, service, provider, queue or filesystem mutation was run.

## Next decision

These artifacts are excluded from the cleanup candidate set. Continue with
active MAK entrypoint and department health checks, then create a cleanup
manifest containing only exact caches or files proven to have no evidence or
consumer role.
