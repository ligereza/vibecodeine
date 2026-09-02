Identity: LUNA-27

# Phase 25 WIN FLUJO APP hub route crosswalk

## Scope and method

Read-only comparison of `/home/mak/WIN/flujo` (historical Windows archive, including MAK genealogy) with `/home/mak/flujo` (current MAK authoring/integration baseline). Inspected the four migration anchors and `abrir_hub.bat`; Git was not used as a physical inventory. Search vocabulary covered ASCII and localized forms: `RD`, `Reduciendo`, `reduc`, `ISKVW`, `iskvw`, `CULTURA`, `cultura`, `Culture`, `Portafolio`, `Portfolio`, `hub`, `app`, `serve`, `visualizer`, `plano`, `api`, plus `/rd`, `/iskvw`, `/cultura`.

`rg` was unavailable (exit 127); bounded `grep`, `sed`, `diff`, `stat`, `sha256sum`, and a read-only Python regex extractor were used. No hub, service, worker, cron, SSH, network, provider, external API, or operational function was started.

## Crosswalk result

| WIN surface | Current MAK counterpart | Domain exposure | Consumer and route contract | Classification |
|---|---|---|---|---|
| `src/flujo/cli.py` | `/home/mak/flujo/src/flujo/cli.py` | `flujo serve`; alias `flujo app` | Calls `flujo.web.hub.launch`; defaults `127.0.0.1:8765`; `--desktop` uses pywebview | migration anchor |
| `src/flujo/web/hub.py` | `/home/mak/flujo/src/flujo/web/hub.py` | Full hub HTTP/API surface | Serves `/flujo_hub.html`, `/visualizer`, `/plano`, RD/ISKVW/MAK APIs, UI POST actions | migration anchor |
| `src/flujo/serve/server.py` | `/home/mak/flujo/src/flujo/serve/server.py` | Lightweight `flujo serve` baseline | `127.0.0.1:8777`, `/context/flujo_hub.html`, `/api/materials` (RD heuristic); not the current full `flujo app` consumer | same baseline |
| `context/flujo_hub.html` | `/home/mak/flujo/context/flujo_hub.html` | RD, ISKVW and CULTURA navigation/cards | Static UI selected by hub root aliases; fetches the APIs listed below | migration anchor |
| `abrir_hub.bat` | `/home/mak/flujo/abrir_hub.bat` | Windows launch adapter | `cd /d` to checkout and calls sibling `launch-flujo.bat`; both WIN and MAK copies have that sibling | Windows adapter |

### Domain route/button map

- RD: UI mode `rd` / “Reduciendo Daño”; views include dashboard, `Plano / Rider`, cotización, piezas, pedidos, `rd-db`, and automation. Backend consumers: `/api/rd-db`, `/api/rd-db/logo`, `/api/rd-packs`, `/api/rd-datos-summary`, `/api/cotizacion-servicios`, `/api/cotizacion/render`, `/api/plano/render`, and `/api/parse-real-pedido`.
- ISKVW: UI mode `iskvw` / “ISKVW”; views include `Show kit`, `Mapping LED`, `SVG Studio`, `Portafolio`, and `Cultura`. Consumers: `/api/show-kit`, `/api/list-svg-works` (also `/api/svg-index`), `/api/portafolio`, `/api/mak`, and shared plano endpoints.
- CULTURA: bundled UI key `cultura`, label “Cultura”, described as “tapiz, tilde, psicosis, precursor”. There is no dedicated `/cultura` HTTP route or `/api/cultura` endpoint in either `hub.py` or the HTML. It is an ISKVW UI view backed by static/project/document paths and the portfolio catalog; this is genealogy evidence, not proof of a separately integrated service.
- Commands/buttons: `/api/comandos` supplies the manifest and `/api/comando` or `/api/run-safe-command` execute command actions. CLI equivalent: `flujo delegate <role> "task"`; `/api/delegate` serves the role-oriented delegation consumer. These are generic hub controls, not separate department backends.

## Hashes, mtimes and physical findings

`mtime` is auxiliary only; WIN archive import metadata and current editing times do not establish lineage by themselves. `server.py` is byte-identical. The `.bat` difference is CRLF versus LF; its command body is otherwise identical. The other three anchors have content differences, but route-token sets are unchanged: `hub.py` 48 WIN / 48 MAK and HTML 20 WIN / 20 MAK.

Exact file data and bounded route rows are in `PHASE25_WIN_HUB_ROUTE_CROSSWALK.csv`.

## Risks and next action

- `flujo app` currently consumes `web/hub.py`; `serve/server.py` is a smaller historical/lightweight server. Treating the latter as the full migration target would lose RD/ISKVW/CULTURA behavior.
- `abrir_hub.bat` remains Windows-only despite a same-path MAK copy; it is not a Linux launcher. `launch-flujo.bat` exists in both trees, but was not executed.
- HTML is a minified bundle, so labels and fetches were statically extracted; no browser verification was performed by instruction.
- `/api/run-safe-command`, upload/render POST routes, and `/api/comando` can mutate state; none were called.

Next action: review this crosswalk against the intended migration contract, then choose the smallest authorized adapter/integration change for the real MAK consumer. No source/runtime change is justified by this read-only pass alone.

## Verification record

- Required context read with `sed`; exit 0.
- `stat` and `sha256sum`; exit 0 for all ten anchor paths.
- Python stdlib route extraction; exit 0; hub 48/48 equal, HTML 20/20 equal.
- `diff -u`; exit 0 for identical `server.py`, nonzero expected for divergent anchors.
- Only this Markdown and CSV were created; WIN, source, runtime, data, logs, locks, databases, credentials, and artwork were not modified.
