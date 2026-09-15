# REPOS

Mapa descriptivo de los repositorios y espacios de código presentes en MAK.
El nombre conceptual y el nombre del repositorio no siempre coinciden: MOSAIK
antes aparecía como VJ y KINO corresponde al proyecto externo
`datos-de-azar`, cuyo núcleo matemático fue integrado en MAT-SI.

## Mapa general

```text
VIBECODEINE / MAK ── estación de integración y núcleo MAK

FLUJO ── repositorio autónomo: motor, datos, operaciones, cultura,
          portafolio, RD e ISKVW
        └── XIO (repo externo) ── campo móvil: RD y FOH

VIBECODEINE / MAK mantiene sus propios dominios y no es el padre Git de FLUJO.
MOSAIK, WACHUMA e IRIS son repositorios separados.

FARMAKSIA ── laboratorio de hipótesis, representación y procedencia
      ├── VIZZ ── visión, geometría, calibración y percepción
      ├── PUPILA ── asociación de acciones, capacidades y propuestas
      └── LUCIDA ── traducción entre intención humana e interfaces

MAT-SI ── matemática, falsación, evaluación y estados
      └── KINO ── núcleo de selección finita, incertidumbre y aprendizaje

bucle ── experimentación visual vectorial y formas generativas
```

## Repositorios de proyecto

### VIBECODEINE / MAK

- Ruta: `/home/mak`
- Remoto: `ligereza/vibecodeine`
- Estado conceptual: estación de trabajo y núcleo de integración. Reúne el
  entorno MAK, el código compartido, el Hub, los departamentos de cultura,
  investigación y operaciones, además de la base común que conecta los demás
  proyectos.
- Idea: convertir trabajos heterogéneos —archivos, eventos, investigaciones,
  herramientas y sesiones— en superficies relacionables y reproducibles.
- Relación: es el espacio superior del sistema. FLUJO es otra extracción o
  checkout del mismo origen, con foco en el motor operativo y de conocimiento.

### FLUJO

- Ruta: `/home/mak/flujo`
- Remoto nuevo: `ligereza/flujo`
- Rama permanente: `main`
- Estado Git: separación autónoma completada; el worktree legado de
  VIBECODEINE se conserva como `/home/mak/flujo-vibecodeine-legacy-20260914`;
  la ruta activa ya es el clone autónomo.
- Estado conceptual: motor portable de workflow, CLI, workspace web, datos,
  cultura, portafolio, RD e ISKVW. No contiene el runtime XIO ni el Hub de
  MAK.
- Idea: hacer que una acción práctica deje un registro interpretable y que los
  objetos de trabajo puedan proyectarse a distintas superficies: Hub, HTML,
  SVG, base de datos, dossier o servicio.
- Relación: FLUJO intercambia contratos y `source_ref` con MAK y XIO. XIO-RD
  consume el contexto RD revisado; XIO-FOH consume el contexto ISKVW/VJ. Las
  pestañas RD e ISKVW son perfiles de la aplicación, no ramas de Git.
- Cableado local RD: la SQLite no se versiona en FLUJO. En esta instalación la
  única proyección canónica es `/home/mak/data/rd.db`; el Hub autónomo usa
  `FLUJO_RD_DB` y el launcher XIO host la recibe por `MAK_RD_DB`/`XIO_RD_DB`.

### XIO

- Ruta: `/home/mak/XIO`
- Remoto: `ligereza/XIO`
- Rama activa: `integration/xio-field-20260911`
- Estado conceptual: sistema móvil y local-first para operar fuera de la
  estación fija.
- Idea: combinar cámara, red local, servidor, sensores, registro temporal,
  evidencias y herramientas de evento en un dispositivo transportable.
- Superficies: `projects/rd-field` para RD y `projects/foh-monitor` junto al
  plugin FOH para operación de espectáculo. RD se orienta a observación de
  terreno, espacios, materiales y comunidad; FOH a señales de show, cues,
  timecode, Art-Net, sACN, OSC y contexto de operación.
- Relación: es el capturador móvil de datos y estados. FLUJO/MAK puede
  recibir sus registros; VIZZ puede aportar geometría o medición visual;
  MOSAIK puede aportar contexto de performance; MAT-SI puede estudiar las
  series y estados sin convertirlos automáticamente en afirmaciones.

### FARMAKSIA

- Ruta: `/home/mak/FARMAKSIA`
- Remoto: `ligereza/FARMAKSIA`
- Rama activa: `fix/provenance-integrity`
- Estado conceptual: laboratorio de investigación computacional, artística y
  matemática.
- Idea: trabajar con hipótesis, representaciones, analogías, límites,
  procedencia y experimentos reproducibles. Sus resultados se expresan como
  estados verificables, no como verdades artísticas, químicas o humanas.
- Relación: es el espacio semántico y experimental que conecta VIZZ, PUPILA,
  LUCIDA, IRIS y CODE-INE. Sus experimentos ya contienen puentes entre
  representación visual, experiencia, interacción y evidencia.

### VIZZ

- Ruta: `/home/mak/VIZZ`
- Remoto: `ligereza/VIZZ`
- Estado conceptual: motor de visión y geometría perceptual.
- Idea: representar cámara, pantalla, rayos, calibración, plano de pantalla,
  ojo y condiciones de observación sin declarar profundidad métrica cuando no
  existe evidencia de calibración.
- Relación: aporta medición visual, geometría y calidad de observación a
  FARMAKSIA, XIO, espacios de venue y posibles experiencias VJ. No equivale
  por sí mismo a identificación química, interpretación artística ni
  aprendizaje supervisado.

### PUPILA

- Ruta: `/home/mak/PUPILA`
- Remoto: `ligereza/PUPILA`
- Estado conceptual: sistema pequeño de asociación y propuestas.
- Idea: relacionar rol, acción, etiqueta, modalidad, capacidad y precondición
  para producir candidatos explicables.
- Relación: funciona como capa de asociación entre una situación observada y
  una posible acción o interfaz. Sus integraciones con FARMAKSIA y LUCIDA
  modelan adaptación y aprendizaje de uso sin depender de una aplicación
  concreta.

### LUCIDA

- Ruta: `/home/mak/LUCIDA`
- Remoto: `ligereza/LUCIDA`
- Estado conceptual: capa de traducción entre eventos de interacción,
  intención operativa y superficies de software.
- Idea: transformar `EngineEvent` en un estado reducido, un `RenderPlan` y un
  `OverlayFrame`, con adaptadores para dialectos como Adobe, Resolume y otras
  interfaces.
- Relación: es el puente de interfaces del sistema. PUPILA puede proponer o
  asociar acciones; LUCIDA puede expresarlas para una herramienta concreta;
  MOSAIK representa el dominio VJ donde esa traducción tiene uso directo.

### IRIS

- Ruta: `/home/mak/IRIS`
- Remoto: `ligereza/IRIS`
- Rama activa: `postulacion/fondart-regional-2027`
- Estado conceptual: repositorio de propuesta y documentación; no es el
  runtime de IRIS.
- Runtime vigente: la aplicación IRIS/Atlas vive en MAK, en
  `cultura/mak_plataforma/copilot.py` y el Hub `:8900`, sobre el corpus privado
  de Portafolio suministrado por el artista.
- Idea: transformar materiales dispersos en una estructura legible de
  antecedentes, decisiones, fuentes, vacíos y propuestas; el artista/usuario
  es el contexto común declarado, no una autoría inferida.
- Relación: FLUJO aporta contratos y consumidores de conocimiento; XIO puede
  aportar capturas RD o FOH/ISKVW. Este repositorio conserva la propuesta IRIS
  y no debe originar un segundo Hub, base, corpus o definición de obra.

### WACHUMA

- Ruta: `/home/mak/WACHUMA`
- Remoto: `ligereza/WACHUMA`
- Estado conceptual: investigación cultural, histórica, botánica y visual
  alrededor de Echinopsis pachanoi y sus contextos relacionados.
- Idea: combinar investigación documentada, relaciones de linaje,
  representación espacial y geometría procedural.
- Componentes: PostgreSQL/PostGIS para relaciones espaciales, escenas GLB,
  Three.js/R3F y adaptadores de Blender para geometría reproducible.
- Relación: conecta cultura, investigación y 3D. IRIS puede ensamblar su
  evidencia; FARMAKSIA puede estudiar sus representaciones; FLUJO puede
  transportar los registros; XIO puede funcionar como superficie de captura
  de observaciones en terreno.

### MOSAIK

- Ruta: `/home/mak/mosaik`
- Remoto: `ligereza/mosaik`
- Estado conceptual: repositorio de trabajo VJ y performance audiovisual.
- Idea: preparar, organizar, probar y proyectar materiales para shows,
  incluyendo Resolume, Titan, media, cues, iluminación semántica y replay.
- Relación: es la especialización de eventos visuales. LUCIDA traduce eventos
  y acciones hacia interfaces; XIO aporta contexto móvil o FOH; FLUJO
  conserva datos de show; VIZZ aporta geometría y observación de superficies.

### MAT-SI

- Ruta canónica: `/home/mak/MAT-SI`
- Ubicación física actual: `/home/mak/Escritorio/MAT-SI`, expuesta mediante
  el enlace canónico anterior.
- Remoto: `ligereza/MAT-SI`
- Estado conceptual: laboratorio matemático de representaciones, evaluación,
  falsación y transferencia entre dominios.
- Idea: estudiar cuándo una estructura, regla, estado o representación se
  conserva, se rompe, se reutiliza o queda indeterminada.
- Relación: es el núcleo de evaluación transversal. Puede recibir estados de
  XIO, estructuras de FLUJO, resultados de FARMAKSIA o registros de KINO sin
  afirmar que una correlación equivale a aprendizaje válido.

### KINO / `datos-de-azar`

- Estado: ya no es un repositorio activo independiente.
- Estado físico: fuente archivada en `/home/mak/archive/windows-sync-20260914/`.
- Integración: `/home/mak/MAT-SI/src/matsi/kino/`
- Idea original: análisis temporal de Kino/Loto, selección latente,
  distribuciones exactas sobre conjuntos finitos, transiciones, mezclas,
  fronteras de confianza, estados y caché prequential.
- Relación actual: sus herramientas matemáticas forman una subcapa de MAT-SI.
  La aplicación web, scrapers, secretos y entornos locales no forman parte de
  la integración. El núcleo aporta estructuras para experimentar con
  incertidumbre, fuga temporal, selección y reutilización de estados.

### bucle

- Ruta: `/home/mak/bucle`
- Remoto: `miskirabit/bucle`
- Estado conceptual: espacio visual de iteración vectorial.
- Idea: producir, comparar y visualizar formas SVG y variaciones generativas,
  incluyendo bocas, dientes, referencias y previsualizaciones.
- Relación: comparte con VIBECODEINE, FLUJO y WACHUMA el interés por convertir
  estructuras en superficies visuales. Su nombre expresa el problema de los
  ciclos sin avance, pero el repositorio funciona principalmente como
  laboratorio de formas y previews.

## Repositorios auxiliares y de contexto

### `mwb-linux`

- Ruta: `/home/mak/src/mwb-linux`
- Remoto: `lucky-verma/mwb-linux`
- Idea: cliente Linux compatible con Mouse Without Borders de PowerToys,
  con transferencia de teclado, mouse y portapapeles entre MAK y Windows.
- Relación: es infraestructura de conexión entre estaciones, no un módulo
  semántico de los proyectos creativos o de investigación.

### `ml-mobileclip`

- Ruta: `/home/mak/src/ml-mobileclip`
- Remoto: `apple/ml-mobileclip`
- Idea: modelos MobileCLIP y MobileCLIP2 para clasificación imagen-texto
  eficiente, inferencia móvil, entrenamiento y evaluación.
- Relación: es una referencia de visión/deep learning que puede dialogar con
  XIO y VIZZ como motor visual liviano. No constituye actualmente el modelo
  común entrenado de los repositorios propios.

### `XIO-IMPORT`

- Ruta: `/home/mak/curatoria_inbox/XIO-IMPORT`
- Remoto: `ligereza/XIO`
- Estado conceptual: extracción, snapshot y revisión histórica de XIO.
- Relación: duplica gran parte de XIO y conserva documentación, pruebas y
  material de procedencia. No representa una idea distinta de XIO.

### `DIMENSIONES DEL ORDEN`

- Ruta: `/home/mak/curatoria_inbox/DIMENSIONES DEL ORDEN`
- Estado Git: repositorio inicializado sin commits.
- Idea: catálogo y observación del desorden de archivos, proyectos,
  herramientas y representaciones; incluye paneles, análisis de interfaces,
  simulaciones y materiales de la idea de un ordenador que aprende formatos a
  partir del caos.
- Relación: es el antecedente conceptual de VIBECODEINE, MAT-SI y el interés
  por descubrir estructuras, pero no es actualmente un motor integrado.

### Temas del sistema Zorin

- Rutas: `/home/mak/Escritorio/zorin-desktop-themes` y
  `/home/mak/Escritorio/zorin-icon-themes`
- Idea: temas visuales del entorno Linux.
- Relación: infraestructura estética del escritorio MAK, sin dependencia
  conceptual con los repositorios de investigación, eventos o visión.

## Relaciones transversales

| Eje | Repositorios relacionados | Tipo de relación |
|---|---|---|
| Estación, datos y proyección | VIBECODEINE, FLUJO, IRIS | Registro, composición y salida a distintas superficies |
| Campo y evento móvil | XIO, FLUJO, MOSAIK | Captura de contexto, operación y replay |
| Visión y geometría | VIZZ, XIO, WACHUMA, MOSAIK, bucle | Cámara, calibración, rayos, formas, layouts y visualización |
| Interfaces y aprendizaje de uso | PUPILA, LUCIDA, MOSAIK, FLUJO | Asociación de acciones y traducción entre herramientas |
| Investigación y evidencia | FARMAKSIA, MAT-SI, IRIS, WACHUMA | Hipótesis, procedencia, falsación, archivo y presentación |
| Deep learning y visión móvil | ml-mobileclip, XIO, VIZZ | Modelos visuales, inferencia local y medición perceptual |
| Estructuras e incertidumbre | MAT-SI, KINO, FARMAKSIA, DIMENSIONES DEL ORDEN | Estados, selección, límites, representación y aprendizaje de formatos |

El punto común no es una aplicación única ni una interfaz única. Es la
transformación de una situación —archivo, evento, imagen, interacción,
espacio o investigación— en una representación con procedencia, y luego su
proyección hacia otra herramienta o dominio.
