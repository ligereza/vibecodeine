"""Versión y changelog de flujo."""

__version__ = "0.52.0"
VERSION = __version__
__version_info__ = (0, 52, 0)


def get_version():
    return __version__


def get_changelog():
    return {
        "0.52.0": {
            "titulo": "Checkpoint limpieza total: reglas obsoletas + basura + estado fuerte/debil",
            "fecha": "2026-07-16",
            "highlights": [
                "limpieza: ~190M fuera (caches, _logs, egg-info, duplicado md5 76M en "
                "jobs/contraportadas); CSV Azure, doublecup.png y APKs xio preservados "
                "fuera del repo en C:/IA/_flujo_local",
                "git: ramas pr45 / worktree-magical-sparking-kite / "
                "claude/cultura-xio-mistral-20260715 borradas (diff 0 vs main) + "
                "worktree cultura-xio; quedan main, rama de trabajo y worktree MAK (PR #48)",
                "archivo via git mv a _archive/legacy_20260716_2000 (motivos en su "
                "README): xio/advplugins, briefs agente1/2, proposal mejoras 2026-06, "
                ".claude/commands push-all.md y README.md; NO archivados por dependencia "
                "viva: projects/flyer_eventos (src/flujo) y xio/actual (platform-tools)",
                "reglas: CLAUDE.md poda Gemini (pedir_a_gemini PARKED, caveat desktop, "
                "cultura=MAK); CONTRIBUTING.md rewrite (checkpoint.sh muerto fuera); "
                "DIRECTOR_PLAN.md marcado HISTORICO; PLAN_SIGUIENTE_AGENTE.md reescrito "
                "con FUERTE/DEBIL verificado + pendientes P1/P2/P3; SESSION_STATE.json "
                "comprimido",
                "seguridad: .gitignore cultura/.dev* -- cultura/.dev.limpio tenia keys "
                "vivas (Tavily/Groq/Cerebras/Azure) y era commiteable via git add -A",
                "verificacion: compileall OK, 394 tests verdes + 1 skip, flujo verify OK",
            ],
        },
        "0.51.0": {
            "titulo": "Checkpoint consolidado: flyer sin Photoshop + PACKS en Python + dossiers curados",
            "fecha": "2026-07-10",
            "highlights": [
                "CONSOLIDACION: las ramas claude/blender-node-compositing (composicion "
                "del flyer POR NODOS en RD.blend, sin Droplet de Photoshop; productoras "
                "wire-in a flyer-auto; commit_ai) y claude/plano-packs-alignment "
                "(src/flujo/plano/packs.py espejo de rdBrand.ts, costs.py a precio "
                "plano de pack, export_propuesta_pdf y api_plano_render en "
                "INFO/TESTEO/COMPLETO) mergeadas en un solo checkpoint; PRs #19/#20/#21 "
                "cerrados, ramas borradas, queda solo main",
                "eventos: blender_nodes.py compone FRAME2.png + flyer de productora con "
                "fit-width + fade a negro + recolor por hue, idempotente sobre el grafo "
                "guardado en RD.blend; flyer_auto.py usa nodos si hay RD.blend+FRAME2.png "
                "(el camino Droplet queda de fallback); GPU OptiX forzado en memoria",
                "productoras.py: identify() wired en flyer-auto (no fatal), PIL motor de "
                "color y Gemini solo semantica, primera entrada curada "
                "data/productoras/thegrid.json",
                "plano: la deuda under/base/mainstream cerrada -- packs.py unica fuente "
                "Python de PACKS RD (100k/300k/500k), proporciones siempre derivadas "
                "precio*pct/100; 9 tests nuevos; PlanoTool.tsx manda pack directo al "
                "backend (PACK_TO_BACKEND_PRESET eliminado)",
                "cultura: dossiers tilde/psicosis/precursor curados (seccion 'del "
                "dossier a la pieza/herramienta' al patron de tapiz.md) con spot-check "
                "web real de las fuentes citadas (Gemini no trajo grounding; cada fuente "
                "marcada VERIFICADA / NO ENCONTRADA / PARCIAL)",
                "ops: gh CLI instalado y autenticado en la maquina del usuario; skills "
                "nuevas teleport-sesion-web y verificar-antes-de-negar; "
                "tools/vibo_voz/commit_ai.py genera mensajes de commit/PR via Gemini "
                "(nunca commitea solo)",
            ],
        },
        "0.50.0": {
            "titulo": "Departamento Cultura + instrumento tapiz + medidor tilde",
            "fecha": "2026-07-10",
            "highlights": [
                "CULTURA: tercer workspace del hub (boton ambar junto a RD/Studio, "
                "CulturaPanel con las 4 lineas de arte-investigacion) y base cultural en "
                "projects/cultura/ (RAINSTORM del artista verbatim + dossiers "
                "tapiz/tilde/psicosis/precursor investigados via Gemini API con busqueda)",
                "tapiz reconciliado: vibecode/ansi.py primitivas compartidas (antes "
                "duplicadas 3x), spaces/void dentro del paquete, wrappers compat, y "
                "exportador SVG (--svg) con paleta flujo HEX real + SMIL opcional; "
                "16 tests nuevos",
                "tilde v0: desktop/tilde_meter.py standalone (supervivencia de marcas "
                "n~/acentos/apertura al comprimir ideas, palabras degradadas ano->ano, "
                "corpus JSONL gitignored); NO cableado a la GUI por decision del usuario",
                "tools/vibo_voz/investigar_cultura.py: runner Gemini+google_search que "
                "escribe findings en los dossiers; extrae groundingMetadata (URLs "
                "verificables) o marca ADVERTENCIA si el modelo no trajo grounding "
                "(las fuentes en texto pueden ser inventadas)",
                "Seguridad: config.json del desktop anclado al dir del script; "
                "permissions contents:read en ci/validar-piezas/render_piezas; scrub "
                "de pedir_a_gemini.py alineado (nvapi-, sk-or-v1-); denylist de "
                "local_tools.py ampliada (credentials.json/token.json/.aider.conf.yml/"
                "tilde_log.jsonl)",
                "desktop/gemini_client.py: cadena de modelos ampliada con gemini-2.5/2.0 "
                "(los modelos disponibles VARIAN POR KEY; gemini-3.x no existe para "
                "todas las keys -- verificado con ListModels real 2026-07-10)",
                "REGLA FIRME registrada: el README del repo es una creacion terminada "
                "del artista (double cup ASCII); no se le agrega nada",
            ],
        },
        "0.49.0": {
            "titulo": "PlanoTool: modelo de PACKS RD (100/250/500)",
            "fecha": "2026-07-09",
            "highlights": [
                "Reemplaza los presets UNDER/BASE/MAINSTREAM (costos calculados) por 3 PACKS de "
                "precio plano: Testeo o Informativo (2 vol) 100.000, Testeo y Informativo (6 vol) "
                "300.000, Servicio Completo (15 vol) 500.000 (m2/stands/inclusiones/proporciones "
                "por pack)",
                "buildElements() dibuja por pack sin solapes; corrige el bug de margen inferior del "
                "plano (PLANO_FRAME) y el default/clamp de la leyenda tecnica arrastrable",
                "Elimina el bloque JSX de impresion duplicado (viewBox 2970x2400, logo remoto); "
                "printRider()/buildPrintableMapSvg queda como unica fuente del PDF",
                "Cotizacion del Rider (seccion 5) muestra solo el pack seleccionado -- precio, "
                "voluntarios, m2/stands, inclusiones y proporciones si es el pack Completo -- "
                "en vez de la tabla comparativa de 3 presets",
                "web/src/rdBrand.ts: PACKS/calcCostos/formatCLP reemplazan el modelo de costos "
                "calculados; RD_PALETTE y RD_LOGO (dark/white) se mantienen sin cambios",
            ],
        },
        "0.48.5": {
            "titulo": "Chataigne template schema real",
            "fecha": "2026-06-30",
            "highlights": [
                "Ajusta el .noisette experimental al schema real exportado por Chataigne 1.10.3",
                "Reemplaza stateMachine por states top-level para que aparezcan las acciones",
                "Usa paths reales como /modules/soundCard/values/ltc/ltcTime y consequencesTRUE",
                "Mantiene XML/CSV como salidas estables y el .noisette como salida compatible en prueba",
            ],
        },
        "0.48.4": {
            "titulo": "Chataigne experimental layout visible",
            "fecha": "2026-06-30",
            "highlights": [
                "El .noisette experimental ahora incluye un layout explicito con Modules, Inspector y State Machine visibles",
                "Agrega paneles Logger, Sequences y Custom Variables para evitar que Chataigne abra en blanco",
                "README_CHATAIGNE indica usar View Default Layout / State Machine si la UI no enfoca las acciones",
                "Mantiene XML y CSV como salidas estables para auditar el mapeo OSC",
            ],
        },
        "0.48.3": {
            "titulo": "Resolume Chataigne sidecars y SVG Studio editable",
            "fecha": "2026-06-30",
            "highlights": [
                "Resolume automatizar ahora genera XML pre-flight, CSV OSC, README y .noisette experimental",
                "El CLI advierte que .noisette es experimental y recomienda template real de Chataigne para compatibilidad total",
                "SVG Studio convierte SVGs reales con rect/circle/line/text a elementos editables del Config Editor",
                "Mantiene fallback svg_image para SVGs vectorizados/path-heavy",
            ],
        },
        "0.48.2": {
            "titulo": "Hotfix SVG Studio svg_image editable",
            "fecha": "2026-06-30",
            "highlights": [
                "SVG Studio renderiza `svg_image` dentro del SVG editor en vez de overlay HTML fantasma",
                "Los SVG importados desde Galeria/Config Editor ahora se pueden seleccionar, mover, redimensionar y alinear",
                "PropEditor agrega controles X/Y/ancho/alto/opacidad para `svg_image`",
                "Alinea el limite del servidor stdlib de SVGs por grupo con el hub principal",
            ],
        },
        "0.48.1": {
            "titulo": "Operational agent workspace baseline",
            "fecha": "2026-06-30",
            "highlights": [
                "Squash de main a un baseline operacional limpio",
                "AGENTS.md queda como contrato operativo principal para agentes",
                "Airdrop queda estandarizado con _airdrop/, HANDOFF y LAST_HANDOFF",
                "Repo hygiene aplicado y raiz limpia de handoffs historicos",
                "Verificacion integral con compileall, pytest, health, version y hub smoke",
            ],
        },
        "0.47.13": {
            "titulo": "Rider PDF alineado al editor y SVG Studio configurable real",
            "fecha": "2026-06-30",
            "highlights": [
                "El PDF del rider vuelve a respetar colores, iconos tecnicos y posicion de la leyenda del editor",
                "Evita doble disparo de impresion y mantiene impresion directa por iframe",
                "Formato PDF vuelve a A4 natural, no forzado horizontal extremo",
                "Config Editor lista SVGs reales del repo y permite cargar SVG local",
                "El boton Configurar este SVG ahora pasa el SVG abierto al editor sin quedarse en demos",
            ],
        },
        "0.47.12": {
            "titulo": "PDF directo con color y puente Galeria→Config SVG",
            "fecha": "2026-06-30",
            "highlights": [
                "Imprimir Rider vuelve a abrir el dialogo directo usando iframe oculto, sin descargar HTML",
                "El plano imprimible recupera color de zonas y simbolos",
                "SVG Studio agrega boton Configurar este SVG dentro del modal de galeria",
                "Config Editor puede cargar el SVG seleccionado desde la galeria como documento editable base",
                "Mantiene Actualizar repo y Carpeta local para ubicar SVGs reales",
            ],
        },
        "0.47.11": {
            "titulo": "Hotfix PDF Plano/Rider en ventana imprimible aislada",
            "fecha": "2026-06-30",
            "highlights": [
                "Reemplaza la impresion React/Tailwind del rider por un HTML imprimible aislado",
                "El boton Imprimir Rider abre una ventana PDF limpia con 3 paginas: checklist, mapa y detalle",
                "El plano se renderiza como SVG autonomo dentro de la hoja de mapa para evitar que desaparezca",
                "Mantiene fixes de SVG Studio: cargar SVGs reales, Actualizar repo y Carpeta local",
            ],
        },
        "0.47.10": {
            "titulo": "Fix SVG previews reales y PDF multipagina Plano/Rider",
            "fecha": "2026-06-30",
            "highlights": [
                "SVG Studio ahora carga el contenido real de /svg desde la API y evita tarjetas con icono generico",
                "Agrega botones Actualizar repo y Carpeta local para refrescar o seleccionar SVGs manualmente",
                "Plano/Rider fuerza PDF multipagina A4 horizontal y separa portada/checklist, mapa y detalle",
                "El mapa imprimible escala dentro de la pagina para evitar recortes",
                "Se mantiene Plano/Rider estable y el Config Editor de SVG Studio",
            ],
        },
        "0.47.9": {
            "titulo": "SVG Studio y Hub web revisado sobre Plano/Rider estable",
            "fecha": "2026-06-30",
            "highlights": [
                "Integra las mejores mejoras web del airdrop externo sin reemplazar el Plano/Rider estable",
                "Convierte el visualizador SVG en SVG Studio con galeria, inspector, preview, descarga y export PNG",
                "Agrega Config Editor visual para config.json con drag, seleccion multiple, alineado, distribucion e import/export",
                "Mejora dashboard, sidebar, jobs, intake y comandos manteniendo fallback demo/local",
                "Mantiene build single-file para context/flujo_hub.html, plano_demo.html y svg_visualizer.html",
            ],
        },
        "0.47.8": {
            "titulo": "Plano/Rider integrado: capas estables, mezcla aditiva y knowledge operativo",
            "fecha": "2026-06-30",
            "highlights": [
                "Integra hotfixes pendientes de Plano/Rider sobre el repo web remoto actual",
                "Seleccionar elementos ya no reordena capas; se agrega ordenamiento base explicito",
                "Auto ordenar respeta prioridad de capas y distribuye simbolos en grilla compacta",
                "Zonas solapadas usan mezcla visual tipo screen para evitar acumulacion opaca",
                "Sincroniza checklist y mapa en ambos sentidos, preservando color, posicion y tamano de simbolos",
                "Mejora exportacion/impresion con leyenda tecnica debajo del mapa y schema knowledge operativo",
            ],
        },
        "0.47.0": {
            "titulo": "QA operativo para rider/plano y SVGs de suplementos",
            "fecha": "2026-06-29",
            "highlights": [
                "Agrega validacion CLI para eventos antes de imprimir/exportar rider y plano",
                "Completa simbolos tecnicos del Plano/Rider y sincroniza los 17 items del checklist al mapa",
                "Agrega validador tecnico de SVGs de suplementos y contraportadas para detectar placeholders y tamano incorrecto",
                "Documenta comandos Windows-first y mantiene entrega por airdrop",
            ],
        },
        "0.46.0": {
            "titulo": "Post Fiesta Flyer creation + complete 8-flyer master generation run",
            "fecha": "2026-06-28",
            "highlights": [
                "Agrega la ficha de contenido individual y la generacion de Post Fiesta en el JSON maestro",
                "Soporta la creacion del 8vo flyer de suplementos con renderizado automatico editable y vectorizado",
                "Bumpea la version del sistema a 0.46.0 y empaqueta el entregable unificado en airdrop_v0.46.0.zip",
            ],
        },
        "0.45.0": {
            "titulo": "Plano element resizing + direct label editing + automated flyer generator run",
            "fecha": "2026-06-28",
            "highlights": [
                "Permite modificar el tamano (ancho y alto en px) de los elementos en el editor de propiedades del Plano SVG",
                "Permite editar de forma directa el texto interno / nombre de los elementos del plano",
                "Ejecuta de forma automatizada la creacion y renderizado maestro de los 7 flyers vectorizados de suplementos de la ONG",
                "Bumpea la version del sistema a 0.45.0 y empaqueta el entregable unificado en airdrop_v0.45.0.zip",
            ],
        },
        "0.44.0": {
            "titulo": "Rider requirements restore 17 items + icons + layer ordering + export",
            "fecha": "2026-06-28",
            "highlights": [
                "Rider restaurado a 17 requerimientos con iconos Lucide y live-sync al plano SVG",
                "Fondo de pantalla oscuro para el canvas del plano en modo de diseño",
                "Alinea el viewBox de SVG a las proporciones de 2970x2100 px del catalogo de la ONG",
                "Soporta persistencia de checklist en impresion y exportacion a Markdown (.md)",
                "Ordenamiento de capas con traer al frente y color picker para zonas y simbolos",
                "Corrige boton de navegacion Ir al Plano conectandolo con inyeccion automatica de elementos",
            ],
        },
        "0.43.2": {
            "titulo": "Fix CI health check – ignore node_modules/web",
            "fecha": "2026-06-28",
            "highlights": [
                "flujo_health ignora web/tsconfig.json (JSONC)",
                "CI render_piezas_vectoriales verde",
            ],
        },
        "0.43.1": {
            "titulo": "Contraportadas suplementos con automatizacion y CLI",
            "fecha": "2026-06-28",
            "highlights": [
                "Automatiza generacion de contraportadas SVG cuando se crea un job de suplementos en el hub",
                "Agrega soporte en CLI para contraportadas con el flag --brief para sobreescribir beneficios",
                "Soporta busqueda dinamica de los 11 suplementos de la linea RD uniendo config y spec JSON",
                "Corrige bug critico de layout en el reemplazo de texto de nombres de suplementos multilinea",
                "Agrega documentacion de operacion y guias pre-prensa en docs/CONTRAPORTADAS_SUPLEMENTOS_OPERATIVO.md",
                "Integra especificaciones tecnicas de contraportadas en la linea_editorial v4.1",
            ],
        },
        "0.43.0": {
            "titulo": "Rider Pro + Cotizacion + Flyers Techno",
            "fecha": "2026-06-28",
            "highlights": [
                "Rider Pro: Requerimientos + Plano imprimible",
                "Iconografia tecnica sin emojis",
                "Configuracion persistente ONG/precios",
                "Cotizacion operativa Presets + Items Manuales",
                "Flyers v4.1 Techno-Elegant layout",
            ],
        },
        "0.42.1": {
            "titulo": "Example ingest templates",
            "fecha": "2026-06-28",
            "highlights": [
                "Agrega templates `knowledge/templates/*.for_ai.json` para analisis visual por IA",
                "Knowledge ingest ahora crea `manifest.json`, `for_ai.json` y `README.md`",
                "Soporta templates para cartelera digital, flyer 10x14, supplement flyer y logo source",
                "Ordena el flujo para que una IA con vision devuelva `analysis.json` reutilizable",
            ],
        },
        "0.42.0": {
            "titulo": "Knowledge base skeleton",
            "fecha": "2026-06-28",
            "highlights": [
                "Agrega `knowledge/` con productoras, venues, logos y examples",
                "Registra Creamfields, The Grid, template Rave Under y Espacio Riesco",
                "Agrega comandos `py -m flujo knowledge list/show/classify/ingest-example/logo-source`",
                "Documenta Agent Visual Director para generar JSON desde ejemplos reales",
            ],
        },
        "0.41.2": {
            "titulo": "Demo jefe y cotizacion base",
            "fecha": "2026-06-28",
            "highlights": [
                "Agrega vista React de Cotizacion con preset UNDER/BASE/MAINSTREAM",
                "Agrega `/api/cotizacion/render` para cotizacion referencial local",
                "Agrega ACTIVE_PLAN, SESSION_STATE y demo jefe para continuidad anti-interrupcion",
                "Documenta roadmap AI Memory para productoras, venues, logos, ejemplos reales e internet enrichment",
            ],
        },
        "0.41.1": {
            "titulo": "Presets EVENTOS e intake con metadata",
            "fecha": "2026-06-28",
            "highlights": [
                "Agrega presets UNDER, BASE y MAINSTREAM para estimar rider/plano desde flyers de eventos",
                "PlanoTool permite seleccionar preset y enviarlo a `/api/plano/render`",
                "El parser sugiere `event_preset` para correos de eventos, rider, cartelera e Instagram",
                "Create job draft guarda `intake.json` y resumen de metadata parseada cuando existe",
            ],
        },
        "0.41.0": {
            "titulo": "Hub React operativo unificado",
            "fecha": "2026-06-28",
            "highlights": [
                "Convierte `flujo_hub.html` en la misma app React single-file usada por Plano y SVG",
                "Agrega AppShell, HubDashboard, JobsPanel, IntakePanel y CommandPanel conectados a APIs reales con fallback",
                "El build `npm run build:context` genera `flujo_hub.html`, `plano_demo.html` y `svg_visualizer.html`",
                "Agrega endpoints livianos de jobs/intake al servidor stdlib para que `hub serve` no quede inutil",
            ],
        },
        "0.40.5": {
            "titulo": "SVG Visualizer conectado a SVG reales",
            "fecha": "2026-06-28",
            "highlights": [
                "`SvgVisualizer` carga `/api/list-svg-works` y usa los SVG reales del repo con fallback demo",
                "Agrega alias `/api/svg-index` y soporte de endpoint en `flujo hub serve`",
                "Renombra el build web principal a `npm run build:context` manteniendo `build:plano` como alias",
                "Sirve `/svg/...` desde el servidor stdlib y agrega checks Node al CI",
            ],
        },
        "0.40.4": {
            "titulo": "React SVG Visualizer integrado",
            "fecha": "2026-06-28",
            "highlights": [
                "Integra `SvgVisualizer.tsx` and `svgIndex.ts` en la capa `web/`",
                "El build single-file ahora actualiza `context/plano_demo.html` y `context/svg_visualizer.html`",
                "Agrega navegacion React Plano/SVG manteniendo uso diario con `py -m flujo app`",
                "Mantiene Node como capa local/gratis de desarrollo UI y Python como backend operativo",
            ],
        },
        "0.40.3": {
            "titulo": "Frontend React/Vite para Plano Pro",
            "fecha": "2026-06-28",
            "highlights": [
                "Agrega `web/` como capa Node/React local y gratis para avanzar mas rapido en UI",
                "Compila con Vite single-file y copia el resultado a `context/plano_demo.html`",
                "Integra PlanoTool React con canvas editable, checklist, capas, export SVG e impresion",
                "Agrega boton Motor Python para usar `/api/plano/render` cuando se abre via `py -m flujo app`",
            ],
        },
        "0.40.2": {
            "titulo": "Plano/Rider Pro integrado al hub vanilla",
            "fecha": "2026-06-28",
            "highlights": [
                "Reemplaza `context/plano_demo.html` por una herramienta util de plano, rider y costos sin React ni build",
                "Integra ideas del prototipo PlanoTool: requerimientos, checklist, capas, zonas arrastrables, grilla, zoom y leyenda",
                "Mantiene conexion real a `POST /api/plano/render` y fallback demo local para doble clic",
                "Agrega export SVG, JSON, copiar rider/costos e impresion desde la UI",
            ],
        },
        "0.40.1": {
            "titulo": "Fix dispatcher y addons hub",
            "fecha": "2026-06-28",
            "highlights": [
                "Restaura `py -m flujo` para delegar en la CLI Typer principal sin ocultar comandos vivos",
                "Registra `serve`, `index` y `route` bajo el namespace seguro `py -m flujo hub ...`",
                "Corrige continuidad operacional: version, handoff activo y documentacion de comandos hub",
                "Mantiene airdrop Python-only con validacion, backup, checks y checkpoint",
            ],
        },
        "0.35.13": {
            "titulo": "EVENTOS palette y preview Blender",
            "fecha": "2026-06-24",
            "highlights": [
                "Revision Gmail automatica cambia a cada 8 horas",
                "`eventos flyer-auto` genera `palette_ig.png` and `palette_ig.json` desde la imagen descargada",
                "Agrega soporte `--render-blender` para renderizar frame 1 de `cartelera.blend` a `preview_cartelera.png`",
                "Agrega soporte `--open-blender` para abrir `cartelera.blend` con autorizacion humana",
            ],
        },
    }
