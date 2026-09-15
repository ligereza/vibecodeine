# REPOS

Mapa descriptivo de los repositorios y espacios de código presentes en MAK.
El nombre conceptual y el nombre del repositorio no siempre coinciden: MOSAIK
es el proyecto VJ y KINO corresponde al proyecto externo
`datos-de-azar`, cuyo núcleo matemático fue integrado en MAT-SI.

Corte Git verificado: `2026-09-15`; los estados operativos detallados y la
contabilidad completa de cambios locales se mantienen en `STATUS.md`.

Validación canónica del mismo corte: `/home/mak/flujo` pasó `1572` pruebas de
FLUJO, omitió `59` por entorno y dejó `202` fuera del marcador; `/home/mak/XIO`
pasó `37` pruebas pytest más `69` suites directas de
showcontrol. Las copias `src/flujo` y `xio/` dentro de VIBECODEINE no son la
fuente de esos resultados.

## Mapa general

```text
VIBECODEINE / MAK ── estación de integración y núcleo MAK

FLUJO ── repositorio autónomo: motor, datos, operaciones, cultura,
          portafolio, RD e ISKVW
        └── XIO (repo externo) ── campo móvil: RD y FOH

VIBECODEINE / MAK mantiene sus propios dominios y no es el padre Git de FLUJO.
FLUJO se separó y hoy es un repositorio hermano autónomo; no comparte ramas
ni depende de un worktree del monorepo. MOSAIK, WACHUMA e IRIS también son
repositorios separados.

La línea de venues de FLUJO está separada del portafolio ISKVW: el registro
fuente vive en `data/venues/*.json`, la referencia 2D en
`tools/venue2d/referencia_plano_teatro.py`, la proyección en
`tools/venue_geometria_scd.py` y el primer visor 3D en `tools/venue3d/`. No se
debe crear una tercera piel ni enlazarlo como una obra del portafolio.

X-ANA-X ── repositorio integrador de motor común y superficies
      ├── core ── estado canónico, relaciones, misiones y verificación
      ├── PUPILA ── asistencia y representación perceptual
      ├── FARMAKSIA ── investigación, evidencia y experimentos
      └── LUCIDA ── integración de aplicaciones y superficies VJ/Adobe

FARMAKSIA ── laboratorio de hipótesis, representación y procedencia
      ├── VIZZ ── visión, geometría, calibración y percepción
      ├── PUPILA ── asociación de acciones, capacidades y propuestas
      └── LUCIDA ── traducción entre intención humana e interfaces

MAT-SI ── matemática, falsación, evaluación y estados
      └── KINO ── núcleo de selección finita, incertidumbre y aprendizaje
```

## Alcance operativo de MAK en este corte

El trabajo activo de este equipo se limita a `FLUJO` y `XIO`. `MAK` conserva
el Hub, los contratos y la coordinación, pero no absorbe el código de los
repositorios hermanos. `X-ANA-X`, `LUCIDA`, `PUPILA`, `FARMAKSIA`, `MAT-SI` y
`WACHUMA` se inspeccionan sólo como fuentes externas para detectar
mejoras, duplicados o conflictos. Una mejora de esas fuentes sólo entra a
FLUJO o XIO mediante un contrato, un commit de origen y una prueba propia.

### Fronteras físicas que no son autoridades duplicadas

Hay dos snapshots de compatibilidad dentro de este checkout padre:
`/home/mak/src/flujo` y `/home/mak/xio`. No son los runtimes activos ni deben
ser la primera fuente para editar. El runtime de FLUJO se ejecuta desde
`/home/mak/flujo/src`; el runtime de XIO se mantiene en
`/home/mak/XIO/xio`. Las copias del padre sobreviven porque la suite histórica
de VIBECODEINE todavía las inspecciona y porque conservan procedencia local;
una diferencia allí sólo se transporta después de comparar contrato, hash y
prueba contra el checkout autónomo. Esta regla evita que un agente convierta
un snapshot de pruebas en una segunda autoridad.

La ruta Git se expresa siempre con ambos datos: ruta local y remoto. La
colaboración disponible no cambia la autoridad del repositorio ni autoriza
mezclar ramas. Por instrucción del usuario, `miskirabit` cuenta con permisos
de colaboración en el espacio Git relevante y puede colaborar por el remoto
correspondiente; no se delega trabajo ni se hace merge automático en este
corte.

## Repositorios de proyecto

### VIBECODEINE / MAK

- Ruta: `/home/mak`
- Remoto: `ligereza/vibecodeine`
- Rama operativa: `main` → `vibecodeine-legacy/main` (`0/0`); HEAD local y
  publicado `2ce9a5c2` (`docs(status): audit deep learning runtime`).
- Estado conceptual: estación de trabajo y núcleo de integración. Reúne el
  entorno MAK, el código compartido, el Hub, los departamentos de cultura,
  investigación y operaciones, además de la base común que conecta los demás
  proyectos.
- Idea: convertir trabajos heterogéneos —archivos, eventos, investigaciones,
  herramientas y sesiones— en superficies relacionables y reproducibles.
- Relación: mantiene la cara MAK, el Hub `:8900` y las integraciones. FLUJO es
  un repositorio hermano autónomo, con foco en el motor operativo y de
  conocimiento; su estado Git detallado vive en `STATUS.md`.

### FLUJO

- Ruta: `/home/mak/flujo`
- Remoto: `ligereza/flujo`
- Rama permanente: `main`
- Estado Git actual: `0/0` frente a `origin/main`, HEAD publicado `48ca1d4`;
  worktree limpio. La separación venue/ISKVW ya está publicada en FLUJO.
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
- Estado Git actual: `0/0` frente a `origin/integration/xio-field-20260911`;
  worktree limpio en HEAD `6e8fa28`.
- Estado conceptual: sistema móvil y local-first para operar fuera de la
  estación fija.
- Idea: combinar cámara, red local, servidor, sensores, registro temporal,
  evidencias y herramientas de evento en un dispositivo transportable.
- Superficies: `projects/rd-field` para RD y `projects/foh-monitor` junto al
  plugin FOH para operación de espectáculo. RD se orienta a observación de
  terreno, espacios, materiales y comunidad; FOH a señales de show, cues,
  timecode, Art-Net, sACN, OSC y contexto de operación.
- Modos de host: `XIO_HOST_DOMAIN=rd` carga `rd_field` (por defecto en
  Termux); `XIO_HOST_DOMAIN=foh` carga `foh_monitor`. Son modos excluyentes del
  runtime Python, no ramas Git; la APK FOH puede usar su listener `:5100`.
- Relación: es el capturador móvil de datos y estados. FLUJO/MAK puede
  recibir sus registros; VIZZ puede aportar geometría o medición visual;
  MOSAIK puede aportar contexto de performance; MAT-SI puede estudiar las
  series y estados sin convertirlos automáticamente en afirmaciones.

### X-ANA-X

- Ruta: `/home/mak/X-ANA-X`
- Remoto: `ligereza/X-ANA-X`
- Rama activa: `LUCIDA` → `origin/LUCIDA` (`0/0`); worktree limpio, HEAD
  `0619057`.
- Ramas canónicas: `main` para el núcleo, `PUPILA`, `FARMAKSIA` y `LUCIDA`
  para sus superficies. No son ramas acumulativas ni sustituyen los repos
  separados de cada dominio.
- Estado conceptual: motor integrador que transforma misión, estado, relación,
  propuesta y verificación; su código canónico de superficies vive bajo la
  rama correspondiente de este repositorio.
- Verificación local: el motor Python de LUCIDA pasa 176 pruebas y
  `LUCIDA/XIO_LAYER` pasa 65. El núcleo C# queda sin verificar en esta máquina
  porque `dotnet` no está instalado.
- Relación: recibe trabajo seleccionado de PUPILA y FARMAKSIA, y proyecta a
  LUCIDA. No es todavía consumidor activo de FLUJO, MAT-SI ni WACHUMA; esas
  transferencias requieren un contrato y una prueba propios.

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
  LUCIDA, IRIS y VIBECODEINE / MAK. Sus experimentos ya contienen puentes entre
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
| Visión y geometría | VIZZ, XIO, WACHUMA, MOSAIK | Cámara, calibración, rayos, formas, layouts y visualización |
| Interfaces y aprendizaje de uso | PUPILA, LUCIDA, MOSAIK, FLUJO | Asociación de acciones y traducción entre herramientas |
| Investigación y evidencia | FARMAKSIA, MAT-SI, IRIS, WACHUMA | Hipótesis, procedencia, falsación, archivo y presentación |
| Deep learning y visión móvil | ml-mobileclip, XIO, VIZZ | Modelos visuales, inferencia local y medición perceptual |
| Estructuras e incertidumbre | MAT-SI, KINO, FARMAKSIA, DIMENSIONES DEL ORDEN | Estados, selección, límites, representación y aprendizaje de formatos |

El punto común no es una aplicación única ni una interfaz única. Es la
transformación de una situación —archivo, evento, imagen, interacción,
espacio o investigación— en una representación con procedencia, y luego su
proyección hacia otra herramienta o dominio.
