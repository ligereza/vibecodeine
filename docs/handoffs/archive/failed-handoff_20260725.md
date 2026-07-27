# failed-handoff -- sesion 2026-07-25 (tarde/noche)

Cierre parcialmente fallido, por orden del usuario. El failed-handoff anterior
(sesion de la manana, mismo dia) fue absorbido por ORQUESTACION_SUCESOR.md y
las promociones de hoy; queda integro en el historial de git de este archivo.

Que fallo NO es el trabajo tecnico (eso aterrizo con CI verde, seccion 2).
Fallo la DIRECCION: el asistente se descarrilo varias veces persiguiendo
tareas derivadas en vez del encargo, midio de mas, y disenio el portafolio
sobre una referencia vieja. El usuario tuvo que interrumpir y corregir
repetidamente.

---

## 1. Modos de falla de esta sesion (para que el proximo no los repita)

1. PERDIDA DE NORTE POR TAREA DERIVADA. Encargo: dividir/ordenar el repo.
   El asistente se desvio a limpiar telefonos de relleno de suplementos y a
   micro-mediciones. Cita del usuario: "te volviste a descarrilar por una
   tarea insignificante".
2. RITMO EQUIVOCADO. Revisar/commitear/testear en pasos de bebe. Ordenes
   explicitas del usuario que quedan como regla: "es preferible avanzar y
   revisar cada avance grande que revisar cada paso de bebe"; "basta de
   revisar si ya sabes"; "no mides nada, solo haz un plan".
3. ANTI-TEAMWORK. El asistente escribio "pendiente que es tuyo, no mio".
   Regla del usuario: orientar o pedir, nunca deslindar. Si el entorno
   bloquea algo (ej. borrar ramas con 403), se construye el canal (se hizo:
   workflow podar_ramas) o se deja el comando exacto listo.
4. REFERENCIA VIEJA. El portafolio iskvw.cl se disenio 2 veces sobre notas
   del failed-handoff anterior (3 mundos, terminal sci-fi, doublecup). El
   usuario las declaro viejas. Se midio el sitio vivo (archivo digital, 6
   secciones: Obra/Dibujo/Reactiva/Proyectos/Basurero/Sobre; "imagen como
   residuo, no como producto") pero TAMPOCO era eso: las referencias reales
   las mando el usuario EN OTRAS SESIONES cloud, y los contenedores son
   efimeros -- no llegan a esta sesion ni estan en el repo.
   LECCION DURA: toda referencia que el usuario comparta se commitea al repo
   EN LA MISMA SESION (p.ej. bajo la linea iskvw) o se pierde.
5. PLANES AL NIVEL EQUIVOCADO. Primer plan = lista de limpieza (rechazado:
   "revisar eliminar actualizar y testear"). Segundo = arquitectura nueva
   (rechazado: "no estoy abriendo ninguna obra nueva"). El nivel correcto
   aparecio recien al tercer intento: entregables concretos por area.

## 2. Lo que SI aterrizo hoy (en main, CI verde ubuntu+windows)

- Consolidacion en 3 lineas: promociones #303 (rd), #306 (poda CRT),
  #305 (mejoras: mecanismo de retiro + poda + manual). `mejoras` retirada.
- Fix real que destrabo #305: la poda habia borrado _cffi_download de
  ig/download.py (la via de descarga IG en Linux/MAK) y su test importaba un
  simbolo inexistente. Restaurada como via secundaria; imginn sigue muerto.
- App dividida en 3 mundos (#308): main / rd / iskvw + rd-plano oculto, con
  migracion de ids viejos (localStorage y ?perfil=).
- MAPA.md (#309): entrada universal; tabla de comandos generada desde el CLI
  (tools/gen_mapa_comandos.py) + tests/test_mapa_completo.py que exige todo
  comando y toda env var documentados. $FLUJO_RD_ROOT reemplaza C:\rd
  cableado. CLAUDE.md con topologia de 3 lineas y entrada via MAPA.md.
- tests/test_higiene_docs.py: ninguna doc viva afirma totales de suite,
  rangos de invariantes ni versiones que contradigan lo medido.
- PR #310 ABIERTO: workflow podar_ramas (Actions, desde el telefono, dry-run
  por defecto, escribir BORRAR para ejecutar; protege main/rd/iskvw).
- Verificacion de la auditoria externa recibida: hallazgos confirmados; su
  auditor rechazado como herramienta (conclusiones hardcodeadas). Detalle en
  LAST_HANDOFF.

## 3. En vuelo (rama iconos-plano-configurables-20260725, esta rama)

HECHO y verificado (typecheck + build:context): fallback de simbolo
personalizado con INICIALES DEL NOMBRE (antes "?" o iniciales de la key
interna) en las 3 vias de render de PlanoTool.tsx -- canvas
(renderSymbolGlyph), leyenda en pantalla y print SVG (symbolIconMarkup,
ambos call sites). Un elemento symbol con key desconocida ya se dibuja bien
en todas las vistas.

FALTA (revertido a proposito para no dejar variables muertas; era estado sin
UI): el catalogo de simbolos personalizados con alta/baja desde el editor.
Spec cerrada para retomarlo:
1. Constante PLANO_CUSTOM_SYMBOLS_KEY + tipo CustomSymbol {key,label,color}
   + loader defensivo de localStorage (~20 lineas).
2. Estado customSymbols + useEffect de persistencia.
3. addCustomSymbol(): key `custom-<slug>`, elemento con label/color propios
   (los elementos ya portan su data; el render fallback ya funciona).
4. UI en el panel "Simbolos Tecnicos": chips de los custom (click agrega al
   plano, x lo saca del catalogo) + form nombre + color + boton crear.
5. Ratchet: round-trip (crear -> aparece en canvas/leyenda/print -> borrar
   del catalogo no rompe elementos ya colocados).
CRITERIO DEL USUARIO (textual): "la jefa puede agregar un icono? si no, no
es configurable".

## 4. Ordenes del usuario de esta sesion que siguen vigentes

- Division por area main / rd / iskvw: HECHA (app y ramas).
- RD: presentacion web con la DB y tools ya creadas; plano/rider se extrae
  para la jefa de eventos; el resto se monta en la propuesta directa a la
  ONG. Sin fecha comprometida con nadie (el asistente invento urgencia y fue
  corregido).
- iskvw: portafolio automatizado y NO convencional en iskvw.cl, armado NUEVO
  en este repo. BLOQUEADO hasta tener las referencias del usuario
  (pedirselas y COMMITEARLAS, ver 1.4).
- F4 (panel suplementos en la app): INNECESARIO, palabra del usuario ("los
  flyers los presentan"). No reabrir.
- SIN INFO PERSONAL EN EL REPO (orden textual: "no debe haber info
  personal"): los campos contacto_label/qr_text de suplementos_config.py
  (7 telefonos +1-809 de relleno) y su uso en export/illustrator.py quedan
  PENDIENTES de poda bajo esa orden. No construir nada encima de ellos.
- Premisa central textual: "construir la estructura con capacidad de ser
  configurable (los datos constantes y variables, o agregar nuevos items, o
  eliminarlos) Y que todo sea intuitivo, flujo app ya lo tiene".

## 5. Los dos planes fallidos (condensados fieles; el proximo decide que
rescatar -- NO ejecutarlos por autoridad)

### Plan A -- "Separar el motor del contenido" (RECHAZADO)

Idea: el dominio esta compilado dentro del programa (suplementos = dict
Python, linea editorial = md suelto con refs rotas). Propuesta: contrato
schemas/workspace.schema.json + cargador src/flujo/workspace/ + fixture de
una organizacion inventada cuyo test exige generar piezas sin codigo nuevo +
trinquete de acoplamiento (refs de dominio en src/flujo solo pueden bajar).
6 fases estranguladas, orden fisico de carpetas al final.
Rechazo textual: "no estoy abriendo ninguna obra nueva, simplemente pedi
dividir el repo por area". Rescatable: la observacion del acoplamiento es
cierta, y el camino de datos YA existe como fallback en get_suplemento().

### Plan B -- "De repo a tres productos" (RECHAZADO EN PARTE: el producto 3
estaba diseniado sobre referencia vieja)

P1 App configurable: catalogos editables desde la app (iconos del plano ->
   suplementos -> textos institucionales orgTexts -> paleta unica web+py),
   con test de round-trip alta/baja. El test de la jefa manda.
P2 RD: (a) plano_rd.html standalone para la jefa CON iconos custom, sin
   contactos; (b) propuesta a la directiva REGENERABLE por comando sobre
   docs/rd/presentacion_db.html + tools/gen_presentacion_db.py (existentes).
P3 Portafolio: INVALIDO como estaba diseniado (referencias viejas). Solo
   sobrevive lo independiente de la estetica: pipeline obra-en-carpeta ->
   catalogacion -> build -> publicacion automatica (watcher/Action propio;
   n8n descartado, no reintentarlo), deploy a Pages o a portfolio-auto
   cuando el usuario agregue ese repo.
Cierre: merge #310 + poda desde Actions + archivar WALKTHROUGH.md
(redundante con MAPA.md) + handoff.

## 6. Verificacion al cierre de esta rama

- cd web && npm run typecheck && npm run build:context: OK
- py -m compileall src/flujo: OK (python no tocado en esta rama)
- Suite completa y flujo verify: verdes en main al momento de las
  promociones; esta rama solo toca web y context. Veredicto final = CI del
  PR.
