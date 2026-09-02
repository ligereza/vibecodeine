# Matriz de integración — 2026-08-10

Esta matriz distingue capacidades comprobables de superficies paralelas. Las
integraciones de esta ronda viven dentro del Hub, el contrato `mak-work-v1` y
el editor GTM/mapa existentes.

| Recurso | Capacidad concreta | Archivos existentes reutilizables | Integración propuesta | Riesgo de duplicación | Coste de mantenimiento | Decisión | Siguiente acción |
|---|---|---|---|---|---|---|---|
| Ascii-Motion | Coalescer mutaciones visuales con refs, callbacks directos y `requestAnimationFrame` | `Ascii-Motion/src/contexts/CanvasContext/CanvasProvider.tsx`, `Ascii-Motion/src/hooks/useFrameSynchronization.ts`, `Ascii-Motion/src/components/common/AsciiMotionLogo.tsx` | Trasladar el patrón, no React ni el repositorio: agrupar cámara/popover y medir frames en `iskvw/mesa_montaje.js` | Bajo; no agrega estado global ni frontend | Bajo; patrón local y acotado | Integrar | Mantener scheduler y degradación en el editor existente |
| Flow / aplicación | Router y superficies de Hub, visualizador, mapping y show kit | `web/src/App.tsx`, `web/src/components/MappingTool.tsx`, `web/public/mapping.html`, `web/src/components/ShowPanel.tsx` | Usar como referencia de superficies ya existentes; no montar un segundo frontend | Medio si se copia `mapping.html` | Medio | Conservar como referencia / adaptar | Reutilizar solo contratos y patrones cuando una integración futura lo necesite |
| Flow / parser XIO | Lectura existente de setlist, cues, fps y registros de show | `src/flujo/web/hub.py::_get_show_kit()` | Mantener la fuente común `xio/show_kit`; el adaptador MAK devuelve átomos separados y usa el contrato común | Medio; evitar importar otra aplicación al Hub | Bajo | Adaptar | Compartir archivos fuente y validar salida contra el show kit |
| XIO show kit | Evidencia real de evento, fecha, cues y timecode | `xio/show_kit/cue_map_dref.json`, `xio/show_kit/setlist_durations_dref.json`, `xio/show_kit/DIA_DEL_SHOW.md`, `xio/show_kit/ANOTACIONES_SHOW_20260724.md` | Crear `cultura/mak_plataforma/xio_evidence.py` como adaptador read-only y exponer `xio_evidence` en la escena existente | Bajo; no crea ledger ni base | Bajo | Integrar | Mantener campos desconocidos explícitos y enlace humano pendiente |
| `mak-work-v1` / ledger | Envelope común con identidad, evidencia, proveedor, estado y siguiente acción | `cultura/mak_plataforma/ledger.py`, `cultura/mak_plataforma/tandas.py`, `cultura/mak_plataforma/contrato_archivo.py` | Construir el envelope de cada show/evidencia XIO con `ledger.build_work_envelope` | Bajo | Bajo | Integrar | Validar el envelope en pruebas focalizadas; no escribir decisiones automáticas |
| Hub MAK / portfolio | Escena, copilot, feedback y fallback existentes | `cultura/mak_plataforma/hub.py`, `cultura/mak_plataforma/copilot.py`, `cultura/mak_plataforma/visual_index.py` | Agregar la evidencia XIO como canal separado y conservar la ruta de fallback metadata | Bajo si se amplía la escena existente | Bajo | Integrar | Verificar endpoint y servicio sin cargar torch/FAISS |
| Editor GTM/mapa | Pieza activa, navegación, revisión humana y relaciones visuales | `iskvw/editor.html`, `iskvw/mesa_montaje.js` | Mostrar un bloque de evidencia XIO declarada/no vinculada dentro de la pieza activa; conservar GTM/mapa | Bajo | Bajo | Integrar | Probar con escena real y sin índice visual |
| `cultura/mak_xio_puente` | Monitor read-only de estado operativo XIO | `cultura/mak_xio_puente/monitor.py`, `cultura/mak_xio_puente/staged/mak_link.py` | No usarlo como evidencia artística; conservarlo para salud/telemetría | Alto si se confunde estado operativo con autoría/evento | Medio | Conservar como adaptador | Mantener separación entre estado del dispositivo y evidencia del show |
| `xio/new/plugins` | Arquitectura histórica de plugins | `xio/new/`, `xio/new-plugins/`, `xio/new/plugins/` | No introducirla en MAK: hay una copia stale y no es necesaria para el contrato actual | Alto | Alto | Retirar de la ruta activa (preservar histórico) | No copiar ni activar; documentar si vuelve a ser requerida |
| SVG / GLSL / 3D | Motores y superficies de mapping/render ya existentes | `tools/tapiz_three.html`, `tools/tapiz_renderer.html`, `tools/sala3d`, `tools/venue3d_*.mjs`, `web/src/data/trazador.ts`, `web/src/data/planoSimbolos.ts` | Conservar como motores visuales y referencias; no incrustar otro renderer en el editor | Alto | Medio/alto | Conservar como referencia | Evaluar por una necesidad visual concreta, no por inventario |
| Bridges Blender | Puente de archivos y temporizadores para Blender | `tools/blender/bridge_blender.py`, `tools/blender/inspect_blend.py` | Mantener como adaptador de producción; fuera de esta integración de catálogo | Bajo en esta ronda | Medio | Conservar como adaptador | Usar solo para un job visual explícito con contrato propio |
| Bridges Adobe | Panel CEP y scripts JSX para Illustrator/Photoshop/AE | `tools/adobe_panel/README.md`, `tools/adobe_panel/js/main.js`, `tools/illustrator/*.jsx` | Mantener como adaptador de producción; no convertirlo en backend del portfolio | Bajo en esta ronda | Medio | Conservar como adaptador | Reusar solo cuando una exportación humana lo solicite |
| thi.ng gestures/hiccup/color | Gestos y generación declarativa ya vendorizados | `iskvw/piel/lib/gestos.js`, `iskvw/piel/campo/index.html`, `docs/cultura/lib/compilador.js` | No agregar dependencias; conservar sus patrones para superficies que ya los usan | Medio | Bajo | Conservar como referencia | No tocar el editor hasta que exista una necesidad medible |
| thi.ng tsne/graph | Experimentos de proyección/grafo sin valor probado para esta ruta | referencias en `iskvw`, `cultura/mak_plataforma` y documentación histórica | No introducirlos: la reducción y el grafo existentes ya tienen rutas deterministas | Alto | Alto | Retirar de la ruta activa (preservar histórico) | Mantener la decisión registrada, sin instalación ni copia |
| `tools` de render y proyectos Tapiz | Mutación algorítmica y superficies artísticas | `projects/tapiz/`, `projects/cultura/`, `tools/svg/`, `projects/cultura/doublecup/svg/sistema` | Conservar la lectura artística; no usar como reemplazo del editor de archivo | Medio | Medio | Conservar como referencia | Integrar solo mediante una pieza o exportación explícita |
| Rutas Adobe/Blender raíz | Directorios raíz no presentes | `C:\IA\flujo\adobe` (ausente), `C:\IA\flujo\blender` (ausente), bridges bajo `tools/` | No inventar rutas ni copiar repos; la capacidad comprobable está en `tools/` | Bajo | Bajo | Descartar como fuente inexistente | Usar únicamente los bridges comprobados |

## Integraciones seleccionadas

1. **Rendimiento/visualización**: `mesa_montaje.js` adopta el patrón de
   coalescencia por frame de Ascii-Motion para cámara y popover, con una
   lectura de calidad de render y degradación visual acotada. No cambia el
   servidor, el ledger, el frontend ni la fuente de medios.
2. **Evidencia artística**: `xio_evidence.py` lee el show kit comprobable,
   conserva evento/fecha/timecode como átomos separados, deja
   artista/venue/productora como desconocidos cuando la fuente no los declara,
   y construye el envelope `mak-work-v1`. La escena actual y el editor lo
   presentan como evidencia XIO disponible, no como relación automática con la
   pieza activa.

## Sustituciones y límites

- No se necesitó sustituir XIO: existen archivos locales reales y pequeños que
  contienen setlist, cues, fecha y observaciones de timecode.
- El monitor `mak_xio_puente` no sustituye al show kit: informa estado operativo,
  no autoría ni evidencia del evento.
- Watsonx/AWS solo puede recibir una tanda posterior y aislada de unidades con
  abstención/conflicto ya identificadas por el índice local; sus resultados no
  podrán promocionarse al ledger sin revisión humana.
