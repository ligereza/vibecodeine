Identity: LUNA principal

# Phase 32 — ISKVW portfolio catalog read-only gate

## Decision

The ISKVW portfolio catalog is already integrated in MAK as a read-only hub
consumer. `GET /api/portafolio` reads the curated
`tools/portfolio/proyectos.json`, applies an explicit eight-field allowlist and
reports the existing `docs/iskvw/prototipo.html`. The catalog contains 10
projects; all project IDs match the WIN evidence and the embedded prototype
catalog. No generator, publisher, Git command, copy or file write was run.

## Vertical contract

```text
ISKVW / Portafolio
    -> GET /api/portafolio
    -> tools/portfolio/proyectos.json (curated source)
    -> docs/iskvw/prototipo.html (existing generated/static consumer)
```

The hub output allowlist is exactly:
`id`, `nombre`, `linea`, `estado`, `descripcion`, `tags`, `ruta`, `url`.
The source catalog requires the first six fields and either a local `ruta` or
an external `url`. Human-facing Spanish text stays intact; machine IDs,
lines, states, tags and paths remain ASCII identifiers.

Search vocabulary covered both language variants and aliases: `portfolio`,
`portafolio`, `projects`, `proyectos`, `catalog`, `catalogo`, `Cultura`,
`Culture`, `ISKVW`, `archivo`, `obra` and `prototipo`.

## Static and fixture gate

Foreground command: AST parse of `src/flujo/web/hub.py`,
`tools/portfolio/generar_portfolio.py` and `tools/portfolio/generar_works.py`;
parse and schema-check MAK/WIN `proyectos.json`; invoke the hub reader on an
uninitialized handler object; verify target-path/external-URL classification;
and extract the embedded `PROYECTOS` JSON from the existing prototype.

Observed exit code: `0`.

- AST parse: 3 modules, PASS.
- MAK catalog: 10 projects; WIN catalog: 10 projects; IDs equal, PASS.
- Schema: required fields, route-or-URL boundary and 10 ASCII IDs, PASS.
- Hub allowlist: 4 top-level output keys, 10 projects and 8 project fields,
  prototype present, PASS.
- Local route targets: 8 paths exist. Two entries are explicit external URLs
  (`autocanva`, `vibecodeine`); no missing local route was hidden.
- Prototype: embedded 10 project IDs match the curated source, PASS.

The portfolio generators were parsed only. They write output or mine/build
generated catalogs and are not part of this read-only integration claim.

## Temporary HTTP result

After documenting the boundary, a temporary in-process
`ThreadingHTTPServer` bound to `127.0.0.1:<ephemeral>` served one GET request
and was shut down, closed and joined in the same foreground command.

- `GET /api/portafolio`: HTTP 200, 10 projects, `prototipo_generado=true`,
  `prototipo_ruta=docs/iskvw/prototipo.html`, PASS.
- Temporary server shutdown: PASS.
- Protected hub, curated JSON and prototype size/mtime snapshot:
  `writes_detected=0`.
- No portfolio generator, publisher, upload, POST route, Git command or
  permanent service was used.

Final status: `INTEGRATED_READ_ONLY`.

## Mutation boundary and rollback

The hub consumer reads the curated JSON and checks prototype existence. The
rollback is temporary-server shutdown; if any protected file changes, reject
the gate and preserve the current reader/catalog. Generators remain separate
write-capable tools and require a new explicitly bounded phase.

## Risks and next action

- The prototype is an existing generated/static artifact; its generator was
  not executed, so regeneration parity is not claimed.
- Two projects point to external URLs and are not local runtime consumers.
- The next unresolved ISKVW consumer is the show-kit/setlist surface. Inspect
  its local MAK records and hardware boundary separately; do not batch it with
  portfolio generation or activation.
