Identity: LUNA-29

# Phase 27 MAK consumer surface

## Scope and method

Read-only crosswalk of the WIN FLUJO APP hub into the physical MAK roots. The
authority set was `/home/mak/flujo`, `/home/mak/WIN/flujo`,
`/home/mak/curatoria_inbox/flujo_windows_probe/`, and the active roots under
`/home/mak` named in the task. Git, HTTP, SSH, services, workers, cron,
packages and runtime mutation were not used.

Search vocabulary covered English and Spanish, accented and unaccented forms,
case variants and aliases: `flujo serve`, `flujo app`, `delegate`, `hub`,
`RD`, `Reduciendo`, `reduc`, `ISKVW`, `iskvw`, `CULTURA`, `cultura`, `Culture`,
`Portafolio`, `Portfolio`, `show kit`, `show-kit`, `SVG Studio`, `visualizer`,
`plano`, `rider`, `cotizacion`, `cotización`, `comandos`, `mak`, `tapiz`,
`tilde`, `psicosis` and `precursor`.

## Result

The recommended vertical slice is:

`/home/mak/flujo/src/flujo/cli.py` (`flujo app` / `flujo serve`)
→ `/home/mak/flujo/src/flujo/web/hub.py`
→ `/home/mak/flujo/context/flujo_hub.html`
→ RD read/render consumers in `src/flujo/rd`, `src/flujo/plano`,
`src/flujo/cotizaciones_base.py`, and `data/`.

This is the best MAK destination because it is already a complete local route:
the CLI entrypoint, full hub, static UI, RD tariff/data files, plano renderer,
quote renderer, tests and documentation are co-located. It preserves the
existing MAK consumer rather than promoting a historical copy from WIN.

| ID | Domain / vertical route | Physical WIN source | Current MAK consumer | Proposed migration destination | Owner / consumer | Dependencies | Platform assumptions | Evidence command | Status |
|---|---|---|---|---|---|---|---|---|---|
| hub_entrypoint | hub: `flujo app`, alias `flujo serve` | `/home/mak/WIN/flujo/src/flujo/cli.py` | `/home/mak/flujo/src/flujo/cli.py` imports `flujo.web.hub.launch` | Keep the MAK CLI as the migration entrypoint; reconcile behavior only after this matrix | Flujo CLI / daily operator | Python package, Typer, Rich, `flujo.web.hub` | Linux foreground process; optional pywebview desktop | `grep -nE 'app|serve|hub.launch|delegate' src/flujo/cli.py` | ADOPTABLE_VERTICAL |
| hub_backend | hub HTTP/API root and route aliases | `/home/mak/WIN/flujo/src/flujo/web/hub.py` | `/home/mak/flujo/src/flujo/web/hub.py` | Keep full `web.hub` as the single hub backend; do not substitute `serve/server.py` | Flujo hub / browser and desktop UI | stdlib HTTP, `flujo.serve.server`, RD, plano, quote, paths | Localhost default; no network required for local routes | `grep -nE 'def do_GET|def do_POST|/api/|/visualizer|/plano' src/flujo/web/hub.py` | ADOPTABLE_VERTICAL |
| hub_ui | hub root, `/hub`, `/index.html`, `/visualizer`, `/plano` | `/home/mak/WIN/flujo/context/flujo_hub.html` | `/home/mak/flujo/context/flujo_hub.html` plus `context/plano_demo.html` and `context/svg_visualizer.html` | Keep static UI under `context/`; connect it to the MAK hub after route contract review | Flujo web / RD and ISKVW users | Browser JavaScript, static resolver, matching API names | Browser; direct-file fallback is weaker than hub serving | `grep -oE '/api/[A-Za-z0-9_/-]+' context/flujo_hub.html | sort -u` | ADOPTABLE_VERTICAL |
| rd_quote_plano | RD quote, plano/rider, render | `/home/mak/WIN/flujo/src/flujo/web/hub.py` and `src/flujo/plano/` | `/home/mak/flujo/src/flujo/plano/`, `src/flujo/cotizaciones_base.py`, hub POST routes | First migration slice: hub UI → MAK quote/plano renderers, with bounded static/AST validation before runtime | RD / event operator and proposal producer | `data/rd_packs.json`, `data/cotizacion_servicios.json`, event JSON, `pypdf`/render dependencies as applicable | Local files; POST routes mutate or render and require explicit later validation | `grep -nE 'cotizacion|plano/render|render_plano_api|generar_cotizacion_base' src/flujo/web/hub.py` | ADOPTABLE_VERTICAL |
| rd_database | RD database, productoras, venues, logo | `/home/mak/WIN/flujo/src/flujo/web/hub.py`, `src/flujo/rd/` | `/home/mak/flujo/src/flujo/rd/database.py`, `rd/informe.py`, `data/productoras`, `data/venues`, `knowledge/logos` | Use existing MAK RD package/data as backend for `/api/rd-db`; no copy from WIN | RD data owner / dashboard and quote UI | SQLite builder, JSON catalogues, logo files | MAK path layout; local read access; logo upload is mutating and deferred | `grep -nE '/api/rd-db|_get_rd_db|rd/database|productoras|venues' src/flujo/web/hub.py src/flujo/rd/database.py` | ADOPTABLE_VERTICAL |
| rd_field_summary | RD field data summary | `/home/mak/WIN/flujo/src/flujo/web/hub.py` and `data/rd_datos_demo/` | `/home/mak/flujo/src/flujo/rd/datos.py`, `src/flujo/rd/informe.py`, `data/rd_datos_demo/` | Retain as an optional RD panel; verify fixture/database availability before claiming live | RD field/report owner / RD panel | RD data files or database, summary serializer | Local data; demo fallback may exist, production availability unknown | `grep -nE 'rd-datos-summary|_get_rd_datos_summary|rd_datos' src/flujo/web/hub.py src/flujo/rd/*.py` | PARTIAL |
| rd_automation | RD automation and pending work UI | `/home/mak/WIN/flujo/src/flujo/web/hub.py` plus `tools/` and RD archive | `/home/mak/flujo/src/flujo/automation.py`, `src/flujo/jobs/`, `/home/mak/RD/AUTOMATIZACION/` | Keep as a separate reviewed consumer; do not activate from the migration crosswalk | RD operations / job operator | jobs, datadrops, filesystem outputs, external creative tools | Local filesystem; may create outputs; no service/worker allowed in this phase | `grep -nE 'automatizaciones|auto-pending|automation|AUTOMATIZACION' src/flujo/web/hub.py src/flujo/automation.py` | DEFERRED_MUTATING |
| iskvw_visualizer | ISKVW SVG Studio / visualizer | `/home/mak/WIN/flujo/src/flujo/web/hub.py`, `context/svg_visualizer.html`, `svg/` | `/home/mak/flujo/src/flujo/web/hub.py`, `context/svg_visualizer.html`, `src/flujo/web/svg_preview.py`, `svg/` | Destination is the MAK hub static resolver plus existing SVG index; test real asset roots before enabling | ISKVW / visual editor user | SVG catalog, `tools/portfolio` or SVG roots, browser | Local browser and filesystem; no artwork copying | `grep -nE 'visualizer|list-svg-works|svg-index|svg_visualizer' src/flujo/web/hub.py context/flujo_hub.html` | PARTIAL |
| iskvw_portfolio | ISKVW portfolio / Portafolio | `/home/mak/WIN/flujo/src/flujo/web/hub.py`, `tools/portfolio/proyectos.json`, `docs/iskvw/prototipo.html` | Same MAK hub consumer and `/home/mak/flujo/docs/iskvw/prototipo.html`; portfolio JSON presence must be checked | Keep portfolio catalog in `tools/portfolio`; do not redirect it to generic CULTURA files | ISKVW / portfolio editor and viewer | `tools/portfolio/proyectos.json`, prototype HTML, catalog schema | Local static catalog; publication state is read-only in hub | `grep -nE 'api/portafolio|_get_portafolio|tools/portfolio|prototipo' src/flujo/web/hub.py` | PARTIAL |
| iskvw_showkit | ISKVW Show kit / setlist / cues | `/home/mak/WIN/flujo/src/flujo/web/hub.py`, `xio/show_kit/` | `/home/mak/flujo/xio/show_kit/` and hub `/api/show-kit` | Destination is MAK `xio/show_kit` read surface; keep relay/control scripts outside hub migration | ISKVW/XIO operator / show panel | setlist JSON, cue records, show logs | Local files; hardware relay is Windows/venue-specific and deferred | `grep -nE 'api/show-kit|_get_show_kit|show_kit' src/flujo/web/hub.py; find xio/show_kit -maxdepth 1 -type f` | PARTIAL |
| cultura_view | CULTURA view: tapiz, tilde, psicosis, precursor | `/home/mak/WIN/flujo/projects/cultura/`, `cultura/`, hub HTML labels | `/home/mak/flujo/projects/cultura/`, `docs/cultura/`, `cultura/mak_*`, portfolio catalog | Keep as a static/project view behind the hub; do not invent `/api/cultura` or a new service | CULTURA / artist-research viewer | project files, docs, portfolio catalog, static allowlist | Local filesystem and browser; no dedicated backend route exists | `grep -RInE 'cultura|tapiz|tilde|psicosis|precursor|api/cultura' context/flujo_hub.html src/flujo/web/hub.py projects/cultura docs/cultura cultura` | GENEALOGY_ONLY |
| shared_commands | command manifest and command button | `/home/mak/WIN/flujo/context/comandos.json`, hub command routes | `/home/mak/flujo/context/comandos.json`, `src/flujo/web/hub.py`, CLI declared commands | Keep manifest-driven commands in MAK; review each command classification before any execution | Flujo operator / command panel | CLI import, manifest generator, subprocess policy | Foreground local subprocess only; mutating POST expressly deferred | `grep -nE 'api/comandos|api/comando|run-safe-command|_correr_comando|_run_safe_command' src/flujo/web/hub.py context/comandos.json` | DEFERRED_MUTATING |
| shared_delegate | role delegation | `/home/mak/WIN/flujo/src/flujo/web/hub.py` and CLI delegate surface | `/home/mak/flujo/src/flujo/web/hub.py`, `src/flujo/cli.py`, `cultura/mak_conductor/handler_registry.py` | Route delegate requests through the existing MAK CLI/registry contract only after isolated workflow and owner are confirmed | MAK conductor / role operator | handler registry, role map, optional isolated clone workflow | Local Python; no worker, SSH or external agent spawning | `grep -RInE 'api/delegate|_handle_delegate|delegate|handler_registry' src/flujo/web/hub.py src/flujo/cli.py cultura/mak_conductor` | DEFERRED_EXTERNAL |
| mak_status | MAK status panel | `/home/mak/WIN/flujo/src/flujo/web/hub.py`, MAK genealogy | `/home/mak/flujo/src/flujo/web/hub.py`, `cultura/mak_plataforma/tandas.py`, `plataforma/` | Keep endpoint as read-only optional status; destination is local MAK state, not a copied WIN service | MAK platform / hub observer | `FLUJO_MAK_URL` optional, local tandas/state files | Network URL may be configured; no HTTP/API call allowed here, so availability is unverified | `grep -nE '/api/mak|_get_mak|FLUJO_MAK_URL|mak_plataforma' src/flujo/web/hub.py` | PARTIAL_READ_ONLY |
| light_server | historical lightweight `flujo serve` | `/home/mak/WIN/flujo/src/flujo/serve/server.py` | Byte-identical `/home/mak/flujo/src/flujo/serve/server.py`; full app instead consumes `web.hub` | Preserve as compatibility baseline; do not select as destination for full RD/ISKVW/CULTURA hub | Flujo compatibility / legacy launcher | stdlib HTTP, `/context/flujo_hub.html`, `/api/materials` and plano | Port 8777 and narrower route set; no proof of full hub parity | `sha256sum /home/mak/WIN/flujo/src/flujo/serve/server.py src/flujo/serve/server.py; grep -nE 'api/materials|plano/render' src/flujo/serve/server.py` | DUPLICATE_LOOKING |
| windows_launcher | `abrir_hub.bat` / `launch-flujo.bat` | `/home/mak/WIN/flujo/abrir_hub.bat` and sibling launcher | `/home/mak/flujo/abrir_hub.bat` and sibling launcher, but no Linux equivalent | Classify as Windows evidence; later create/adapt a Linux launcher only in an authorized implementation phase | Windows operator / desktop startup | cmd.exe, `cd /d`, `.bat` sibling, Windows Python | Windows-only; MAK Linux cannot consume it directly | `sed -n '1,80p' abrir_hub.bat; find . -maxdepth 2 -iname 'launch-flujo.bat' -o -iname '*.sh'` | WINDOWS_ONLY |
| mak_departments | MAK platform, research, codex, curatoria, post, xio and aliases | `/home/mak/WIN/flujo/cultura/mak_*`, `tools/mak*` | `/home/mak/flujo/cultura/mak_*` plus physical `/home/mak/plataforma`, `/home/mak/research`, `/home/mak/codex`, `/home/mak/curatoria`, `/home/mak/post`, `/home/mak/xio_puente` | Use existing physical department owners as consumers; do not merge similarly named roots or infer hub routes from file presence | Department owners / hub consumers where explicitly wired | department contracts, registries, data/state, optional external providers | Linux paths and case sensitivity; several roots contain locks/PIDs and must remain untouched | `for d in /home/mak/plataforma /home/mak/research /home/mak/codex /home/mak/curatoria /home/mak/post /home/mak/xio_puente; do test -d "$d" && echo present:$d || echo absent:$d; done; grep -RIlE 'mak_plataforma|mak_research|mak_codex|mak_curatoria|mak_post|xio_puente' cultura src` | PARTIAL |

## Absent, deferred and duplicate-looking findings

- `/home/mak/iskvw` and `/home/mak/cultura` as standalone top-level roots are
  absent. Their relevant MAK consumers are under `/home/mak/flujo/docs`,
  `/home/mak/flujo/projects`, `/home/mak/flujo/cultura` and the hub assets.
- There is no dedicated `/cultura` or `/api/cultura` route in the current hub;
  CULTURA is a UI view and project/catalog surface. It must not be promoted to
  a service solely because the label exists.
- `src/flujo/serve/server.py` is byte-identical between WIN and MAK but is a
  narrower compatibility server. Its equality is not full hub integration.
- `abrir_hub.bat` has a MAK copy but remains Windows-only. The `.bat` pair is
  not a Linux consumer and is deferred.
- `/home/mak/RD` is a large physical artwork/archive root, while the complete
  RD hub route consumes the smaller structured package and data under
  `/home/mak/flujo`. The archive is evidence and output storage, not a reason
  to copy or re-root the backend.
- Active state files, locks, PIDs, worker declarations and external-provider
  imports were observed but not executed. Their presence is dependency risk,
  not proof of a live hub consumer.

## Validation and handoff

Only this Markdown and its companion CSV were created. The following checks
are read-only and are the required next verification boundary:

```text
python3 -c 'import csv; from pathlib import Path; p=Path("context/PHASE27_MAK_CONSUMER_SURFACE.csv"); rows=list(csv.DictReader(p.open(encoding="utf-8"))); assert p.read_text(encoding="utf-8").startswith("Identity: LUNA-29\n"); assert len(rows)==17; assert all(set(("physical_source","current_mak_consumer","proposed_destination","owner_consumer","dependencies","platform_assumptions","evidence_command","status")) <= set(r) for r in rows); print(len(rows))'
python3 -c 'import ast; from pathlib import Path; paths=[Path("src/flujo/cli.py"),Path("src/flujo/web/hub.py"),Path("src/flujo/serve/server.py")]; [ast.parse(p.read_text(encoding="utf-8"), filename=str(p)) for p in paths]; print(len(paths))'
```

Expected exit code for both commands is `0`; expected counts are 17 CSV route
rows and 3 parsed Python anchors. Risks remaining are unverified browser/API
behavior, optional MAK URL availability, incomplete ISKVW portfolio/SVG
catalogue proof, and deferred mutating/delegation routes. Next action is to
review this matrix and then implement only the RD vertical slice against the
existing MAK hub, followed by a bounded foreground contract check.

