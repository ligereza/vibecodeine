Identity: LUNA-28

# Phase 27 — matriz de dependencias de rutas de flujo app

## Alcance y criterio

La ruta real es flujo app -> flujo.cli:app -> flujo.web.hub.launch ->
context/flujo_hub.html -> rutas RD, ISKVW y la vista CULTURA. No se confunde
flujo serve con flujo app: src/flujo/serve/server.py es un servidor liviano,
byte-identico entre WIN y MAK, y no expone el hub completo. WIN es evidencia
física; MAK es el destino activo. No se usó Git como inventario ni se copiaron
árboles.

Clasificación: core = necesario para arrancar CLI/hub; route-optional = solo
una vista/acción; MAK-local = código/dato que el hub consume desde MAK;
dynamic = import o resolución en runtime; Windows-only = launcher o empaquetado
Windows; unresolved = detectado por la sonda pero sin consumidor probado en
esta ruta.

## Evidencia

- environment.json: Windows 11 Home, Python 3.11.8, pip 26.1.2 y flujo 0.56.1.
- imports.json: 262 archivos escaneados; mezcla el hub con todo el árbol, por
  lo que un import aislado no se eleva a dependencia de ruta.
- requirements-candidates.txt: 85 candidatos; pip-freeze.txt: 519 líneas.
  Conflictos de pip check son ruido de entorno hasta ligarlos a un consumidor
  FLUJO real.
- PHASE25_WIN_HUB_ROUTE_CROSSWALK.md/.csv: 48 tokens de ruta en hub.py, 20 en
  el HTML, y no existe /cultura ni /api/cultura.
- anchors-metadata.json da hashes/fechas Windows. Creación/ctime son
  auxiliares: se usan junto con hash, contenido, ruta y consumidor.
- server.py WIN/MAK es igual; cli.py, hub.py y el HTML difieren en contenido,
  aunque conservan el conjunto de tokens de ruta.

## Matriz

La fuente tabular exacta es el CSV. Windows evidence conserva el hecho
observable; verification distingue lectura estática de ejecución. No se llamó
HTTP, no se inició el hub y no se instalaron paquetes.

| ID | Class | Package/local module | Source file | Route/domain | Current MAK counterpart | Windows evidence | pyproject/requirements status | Platform assumption | Verification |
|---|---|---|---|---|---|---|---|---|---|
| core-cli | core | flujo.cli | WIN/flujo/src/flujo/cli.py | flujo app; flujo serve | src/flujo/cli.py | hash 0cc6...b23871; local flujo import | entry point flujo=flujo.cli:app; no separate req | Python >=3.10; Linux/Windows | MAK help passed; source/hash read |
| core-hub | core | flujo.web.hub | WIN/flujo/src/flujo/web/hub.py | /; /hub; /api/* | src/flujo/web/hub.py | hash 0cb0...6181d9; 48 route tokens | no extra; local modules plus optional UI deps | stdlib HTTP; localhost; desktop optional | AST/import inventory; crosswalk |
| core-html | core | hub HTML bundle | WIN/flujo/context/flujo_hub.html | RD; ISKVW; CULTURA navigation | context/flujo_hub.html | 20 route tokens; WIN hash in probe | static file; no Python requirement | browser JavaScript; direct-file fallback | static extraction; no browser |
| core-stdlib | core | http.server, pathlib, json, urllib, threading | src/flujo/web/hub.py | all GET/POST dispatch | same stdlib | probe stdlib imports | implicit Python stdlib | Linux/Windows | AST imports |
| core-typer | core | typer | src/flujo/cli.py | CLI dispatch | package dependency | typer 0.27 candidate/freeze | declared >=0.27 in pyproject/requirements | Python package | declared; help evidence |
| core-rich | core | rich | src/flujo/cli.py | CLI output | package dependency | rich 15 candidate/freeze | declared >=15 | terminal independent | declared; help evidence |
| route-desktop | route-optional | webview / pywebview | src/flujo/web/hub.py; cli.py | flujo app --desktop | same source; extra web | pywebview 6.2.1; webview import | pyproject [web]; not base req | GUI backend differs | static option mapping |
| route-tray | route-optional | pystray | src/flujo/web/hub.py | desktop tray | same source | pystray 0.19.5 | pyproject [desktop-extras] | Linux tray vs Windows tray | dynamic import; unexecuted |
| route-image | route-optional | PIL / Pillow | src/flujo/web/hub.py | uploads; palette; previews | same source | Pillow 12.3 candidate/freeze | pyproject [render]/[desktop-extras] | native wheels possible | static import/use sites |
| rd-plano | route-optional | flujo.plano | src/flujo/web/hub.py; serve/server.py | /plano; /api/plano/render | src/flujo/plano | WIN plano modules and route | local package; no extra | SVG/filesystem render | module paths/crosswalk |
| rd-packs | route-optional | flujo.plano.packs plus RD data | src/flujo/web/hub.py | /api/rd-packs | same module/data path | WIN data/rd_packs.json; route | local data; no dependency | filesystem read; no network | source/data/route |
| rd-database | route-optional | flujo.rd.panel and informe | src/flujo/web/hub.py | /api/rd-db; /api/rd-datos-summary | src/flujo/rd | WIN RD package/handlers | local; base deps only | local JSON/DB may be absent | static map; endpoint not called |
| rd-quotes | route-optional | cotizaciones_base and quote project | src/flujo/web/hub.py | /api/cotizacion-servicios; /api/cotizacion/render | cotizaciones_base.py; projects/cotizaciones | WIN route/data | local; no dedicated req | stateful writes/render | read-only inspection |
| rd-assets | route-optional | flujo.export.illustrator | src/flujo/web/hub.py | RD supplement/job assets | same MAK module | WIN import/handler | local; Pillow optional | filesystem; Illustrator external | static import |
| rd-analysis | route-optional | flujo.analyze.colors and ocr | src/flujo/web/hub.py | upload palette/text hints | same MAK modules | probe PIL, pytesseract, fitz; hub colors/ocr | Pillow optional; OCR/PDF not base | OCR/PDF native uncertain | static sites; no upload |
| iskvw-portfolio | route-optional | portfolio catalog/static docs | hub.py; flujo_hub.html | /api/portafolio | MAK docs/assets and _get_portafolio | WIN iskvw/docs labels | no package; static/catalog data | local allowlisted roots | crosswalk; no HTTP |
| iskvw-show | route-optional | show-kit records | src/flujo/web/hub.py | /api/show-kit | MAK counterpart unresolved | WIN xio/show_kit and JSON | no declared req; evidence only | hardware/OSC likely external | route/source only |
| iskvw-svg | route-optional | SVG preview/index | hub.py; svg_visualizer.html | /visualizer; /api/list-svg-works; /api/svg-index | web/svg_preview.py and SVG roots | WIN SVG roots/tokens | cairosvg/vtracer candidates, not proven | filesystem + native rasterizer optional | static route/file inventory |
| cultura-view | dynamic | CULTURA view key | context/flujo_hub.html | UI cultura; no API | MAK cultura projects/docs | tapiz, tilde, psicosis, precursor; no API | no package/requirements entry | static allowlisted paths; not service | crosswalk; genealogy evidence |
| shared-intake | dynamic | intake.email_parser and pipeline | src/flujo/web/hub.py | parse pedido/upload actions | same MAK modules | WIN imports/handlers | local; requests not needed | local files; mutation boundary | AST; POST not called |
| shared-jobs | dynamic | jobs.job, dashboard, eventos.presets | src/flujo/web/hub.py | dashboard/job/preset APIs | same MAK modules | WIN source/imports | local; no extra | local workspace/jobs | import map; no creation |
| shared-serve | MAK-local | flujo.serve.server | src/flujo/serve/server.py | shared plano helper only | byte-identical MAK source | WIN/MAK SHA 8d38...6f13 | local package; no extra | stdlib; port 8777 only separate | hash/crosswalk; not launched |
| windows-launcher | Windows-only | abrir_hub.bat and launch-flujo.bat | WIN/flujo/abrir_hub.bat | double-click adapter | same-named MAK files, not Linux launcher | CRLF; cd /d; sibling batch | not in pyproject/requirements | Windows cmd only | diff/metadata; not executed |
| unresolved-render | unresolved | cairosvg, vtracer, pypdf, PyMuPDF/fitz | probe imports; render-adjacent modules | possible SVG/PDF/OCR branches | no route-level proof | candidates present in probe | absent from base requirements; optional/undoc | native wheels unknown | linkage unresolved |
| unresolved-heavy | unresolved | numpy, torch, bpy, mathutils, crawl4ai, psycopg | broad WIN scan, not direct hub path | none proven | no bounded MAK counterpart | tree-wide candidate/freeze imports | not base route deps | GPU/Blender/DB/network | excluded from slice |

## Vocabulario de búsqueda y riesgo residual

Se buscaron ASCII y variantes bilingües/accentuadas: RD, rd, Reduciendo,
Reduciendo Daño, reduciendo dano, reduc, ISKVW, iskvw, CULTURA, cultura,
Culture, Portafolio, Portafolio, Portfolio, hub, app, serve, visualizer,
visualizador, plano, rider, cotización, cotizacion, quote, show kit, show-kit,
SVG Studio, api, /rd, /iskvw, /cultura, más nombres de módulos y archivos.
Se revisaron imports AST, rutas literales, fetch, botones, raíces físicas y
requirements. Riesgo residual medio: el HTML está minificado, hay resolución
dinámica y imports.json mezcla todo WIN. Puede existir una dependencia activada
solo por payload o dato no nombrado; unresolved no significa innecesario.

## Slice vertical seleccionado: RD packs/tariff read-only

- Source path: WIN/flujo/src/flujo/web/hub.py,
  WIN/flujo/src/flujo/plano/packs.py y WIN/flujo/data/rd_packs.json.
- MAK destination/consumer: src/flujo/web/hub.py -> plano.packs y
  data/rd_packs.json, consumido por la tarjeta RD de context/flujo_hub.html.
- Dependency set: stdlib json/pathlib/HTTP handler, flujo.plano.packs,
  flujo.paths, fetch('/api/rd-packs') y JSON local. No GUI, OCR, red ni cairo.
- Interface/route: GET /api/rd-packs; JSON de packs/tarifa.
- Platform risks: resolución de paths, encoding y presencia del JSON; sin
  riesgo GUI/native wheel.
- Exact bounded validation command:
  PYTHONPATH=/home/mak/flujo/src python3 -c "import ast,pathlib,json; h=pathlib.Path('/home/mak/flujo/src/flujo/web/hub.py').read_text(); p=pathlib.Path('/home/mak/flujo/src/flujo/plano/packs.py'); d=pathlib.Path('/home/mak/flujo/data/rd_packs.json'); html=pathlib.Path('/home/mak/flujo/context/flujo_hub.html').read_text(); assert p.exists() and d.exists(); json.loads(d.read_text()); assert '/api/rd-packs' in h and '/api/rd-packs' in html; ast.parse(h); ast.parse(p.read_text()); print('RD_PACKS_STATIC_OK route=1 data=1 ast=2')"
- Expected output: RD_PACKS_STATIC_OK route=1 data=1 ast=2, exit 0.
- Rollback boundary: analysis-only now; a future code edit reverts only the
  changed hub.py/packs.py adapter and its focused test. No HTML, RD database,
  generated output or WIN evidence.
- Why this over one .py: proves hub lineage, RD UI consumer, route contract and
  real local data together; one module alone would not prove integration.

## Validation record and next action

Only the two PHASE27_ROUTE_DEPENDENCY_MATRIX files are created. Source checks
were read-only; no HTTP/API route, service, worker, cron, SSH or package
installation was used. Run the focused slice command before any source/runtime
edit. If it passes, authorize a separate adapter change; if it fails, keep
rollback bounded to RD packs.
