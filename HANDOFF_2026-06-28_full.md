HANDOFF - FLUJO airdrop completo (v0.40)
========================================
Fecha: 2026-06-28
Estado: aplicado y verificado de punta a punta. Listo para airdrop.

QUE ES
- Paquete unico con TODO: hub corregido + serve (backend) + index + route + doctor.
- Vanilla + stdlib. Sin frameworks, sin dependencias, sin build.
- Nada mueve/borra archivos del usuario (index/route/serve son solo-lectura).

NUEVO EN ESTE AIRDROP
- src/flujo/__main__.py : dispatcher  py -m flujo <serve|index|route|doctor|version>
- src/flujo/serve/      : servidor local (http.server) que sirve el hub y expone /api
    GET  /api/health/stats        (lee jobs/ o demo)
    GET  /api/materials           (lee context/data/materials.json o demo)
    GET  /api/materials/<id>/download
    GET  /api/index/brief         (resumen del index_rd.json si existe)
    POST /api/plano/render        {evento} -> {layout, rider, costos, total}
- flujo doctor : chequeo de entorno (hub + rutas + python)
- context/data/materials.json : datos editables que alimentan el visualizer
- instalar.bat / abrir_hub.bat : instalacion y arranque de 1 clic
- docs/INTEGRACION_CLI.md : como enchufar los subcomandos a un dispatcher existente

YA INCLUIDO (de sesiones previas)
- Hub: flujo_hub.html (portada NUEVA) + plano_demo.html + svg_visualizer.html
  con :root unico en shared/flujo.css y utilidades en shared/flujo.js.
  Bugs P0/P1/P2 corregidos (vars CSS, XSS escapeHTML, event global, tags,
  estados loading/empty/error, a11y tabs+modal, toasts, responsive).
- index : indexa C:\rd para agentes (build/stats/find/versions/dupes/cleanup/agent-brief).
- route : resuelve donde esta/va cada pieza (where/cuna/doctor), no mueve nada.

VERIFICADO (pruebas reales)
- py -m flujo doctor  -> OK (5 archivos hub + 2 areas de rutas).
- py -m flujo serve   -> GET / 302, hub 200, css mime ok, 3+1 endpoints responden,
                         path-traversal bloqueado, CSP enviada.
- POST /api/plano/render -> {layout(6 zones), rider, costos, total} correcto.
- /api/materials -> sirve los 7 items de context/data/materials.json.
- py -m flujo index build --from-inventory -> 1615 arch / 52.7 GB; stats por area OK.
- py -m flujo route where ... -> rutas correctas.
- JS de los 3 HTML: node --check OK. 0 event global, 0 alert(), 0 vars CSS huerfanas.

COMO USAR
- Demo sin servidor:  doble clic en context/flujo_hub.html
- Modo real:          py -m flujo serve --open   (http://127.0.0.1:8777)
- Instalar al repo:   instalar.bat C:\ruta\a\vibecodeine

INTEGRACION
- Si tu repo ya tiene dispatcher (app/health/portal), NO reemplaces __main__:
  registra serve/index/route/doctor junto a los tuyos (docs/INTEGRACION_CLI.md).

REGLAS RESPETADAS
- Windows + py. ASCII-only. Sin tokens. Sin dependencias. <script src> clasico (no ES modules).
  Sin CDN (offline-friendly). Server escucha solo en 127.0.0.1.
- Airdrop:
    py scripts/validate_airdrop.py
    py scripts/run_airdrop_checks.py "feat: flujo serve + hub pro + index + route (v0.40)"

PROXIMOS PASOS SUGERIDOS (opcional)
- Conectar /api/materials a un indexado real de material (hoy lee JSON editable).
- Tema claro/oscuro conmutable en el hub.
- Autenticacion simple si el server se expone fuera de localhost.
