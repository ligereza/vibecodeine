# Memoria de dirección — iskvw / MAK / ingresos

> Destino sugerido: `cultura/mak_plataforma/MEMORIA_DIRECCION.md`
> Vive al lado de `RELEVO_MAK.md` y `GENESIS.md`: son los documentos de "quién
> lleva el timón". Este es el cuaderno del timón.
>
> Abierto el 2026-07-30. Español con diacríticos (lo lee un humano, no el parser).
> **No** reemplaza a `context/LAST_HANDOFF.md`, que es el checkpoint técnico y es
> ASCII-only.

---

## 0. Cómo se usa este archivo

Esto es **memoria**, no plan. Un plan se ejecuta y se vence; una memoria se
consulta y se poda.

**Una idea no entra acá sin las tres columnas:** por qué es real, qué hay ya
construido que la sirve, y cuál es la trampa. Una idea sin trampa identificada
no está pensada todavía — está entusiasmada.

Y lo que se descarta **se escribe en §5 con la razón**, igual que se cerró n8n en
`cultura/PLAN.md:76-84`. Una idea muerta sin acta se vuelve a intentar en seis
meses.

---

## 0.b Quién es MAK, qué quiere y qué rechaza

> Esta sección faltaba hasta el 2026-07-30 por la tarde y su ausencia era el peor
> defecto del archivo: doce ideas bien fundamentadas **sin la premisa que las
> ordena**. "Irse del país" tenía CERO menciones en 969 líneas. Sin esto, todo lo
> de abajo se lee como consultoría genérica.

### Qué tiene (el inventario real, no el currículum)

- **Artista visual. Tres años de VJ.** Ha ido a **mínimo un venue por ciudad** en
  Chile. **Sabe qué necesitan técnicamente, sabe las constantes y tiene los
  contactos.** La investigación de mercado ya está hecha; no hay que hacerla.
- **Ha recorrido VJ, música, tatuaje, iluminación y 3D**, y acumuló un **público
  diverso** que lo sigue a él y no a un rubro. Sus colegas tienen un perfil por
  oficio; él no. **Su fuerte es no separarse.**
  → Y eso **es la calificación**, no un desorden: alguien que sólo hace 3D no sabe
  qué necesita un rider. Va en el pitch, no escondido.
- **Es el primero de su escena en hacer colaboraciones triples de técnica
  múltiple.** "Menos compe más compas" no es un eslogan: tiene antecedentes.
- **Hace la parte legal él mismo.**
- **Es el diseñador de RD**, y no sólo de flyers: zonas de descanso, integraciones
  de servidores. RD es **el sustento de las herramientas**, no un cliente más.
- **Trabajó para la SCD** — cliente institucional con nombre reconocible. Es una
  credencial, no un trabajo más.
- **Fierros:** iPad Pro 12.9" 5ª gen (M1, con LiDAR) · notebook con RTX 4070 ·
  MAK, una Dell con **GTX 1650 de 4 GB** (el cuello de todo el organismo).

### Qué quiere

- **Irse del país, con su pareja.** Ella es **enfermera**.
  → Esto ORDENA las prioridades y es lo que se perdía al no escribirlo: enfermería
  está en listas de escasez profesional y **arrastra pareja**; un fondo artístico
  son US$5-20k por una vez y **no confiere residencia**. Ver §2.4.
- Crecer como VJ y como artista **ganando estatus**, no persiguiendo clientes.
- Que la gente **contribuya** al código y a la base de datos.
- Que MAK siga funcionando cuando el modelo fuerte no esté (la misión del README).

### Qué RECHAZA — y esto es lo que más se pierde si no queda escrito

- **"Necesito dinero, hago visuales y te limpio el piso."** Sus palabras. En su
  escena **pedir plata primero es negativo para el estatus**, y desde abajo el
  trabajo no llega.
- **Construir la app y después salir a buscar clientes que quieran justo eso.**
  Lo llamó "mal plan" y tiene razón: es un modelo de empuje y su mundo no funciona
  así.
- **Botones de contacto para comisiones.** No le sirven.
- **Separarse en perfiles por oficio.** Ver arriba: es su activo, no su problema.
- **Una hoja de precios fija.** "Si alguien comenta 'precio?', sea cual sea mi
  respuesta es errónea si no tengo un plan de acción según recursos" — y cada sala
  es distinta, así que un número fijo miente. Lo que corresponde es un
  **instrumento de cotización**, no un precio.
- **Cobrar dinero antes que herramientas.** *"No cobro dinero sino herramientas."*
  El vehículo es **"libre de lucro"** — no "sin fines de lucro": libre DE lucro.
- Ante el público general se para como **alguien que apoya lo gratuito de
  internet, con la base cultural de descargar pirateado.** Por eso el commons va
  con licencia share-alike: el copyleft es la forma pirata-compatible de mantener
  algo libre, no una traición.

### Las restricciones duras que no se negocian

```txt
1  Nada del corpus RD sale de la caja. Nunca.
2  En afters: geometria si, identidad no. No ser el que tiene la lista.
3  Descriptivo, nunca certificante (la tilde, RD, el rider: la misma regla).
4  La maquina lee y propone; el humano verifica y FIRMA. Lo que se vende es la firma.
5  Lo que un humano lee como producto va en espanol con tildes y eñes.
   "Reduciendo Daño" lleva Ñ.
```

---

## 1. La síntesis (lo único que hay que recordar si se pierde todo lo demás)

**Comunidad VJ, portafolios pagados y fondo público no son tres ideas. Son tres
salidas de una máquina que ya está construida.**

```txt
percepcion.py           lee un archivo DESORDENADO (OCR + vision + ffmpeg)
   |                    ~/curatoria/fichas/fichas.jsonl, schema unico por archivo
extraccion_db.py        consolida entidades canonicas (fuzzy >=0.82 / dudoso 0.70-0.82)
   |
corpus_a_micelio.py     lo indexa y lo hace consultable (memoria.py)
   |
gen_archivo_iskvw.py    genera sitio estatico
publicar_iskvw.yml      lo publica (sube SOLO la carpeta iskvw/)
```

Una corrida sobre el archivo de un colega produce, al mismo tiempo:

| Salida | Qué es | Quién paga |
|---|---|---|
| **Archivo público de la escena** | Registro curado de una práctica que hoy sólo existe como posteos efímeros | Un fondo (Fondart u similar) |
| **Directorio** | La comunidad en su forma útil | Nadie — es el bien público que justifica el fondo |
| **Portafolio individual completo** | El sitio propio del artista, con su dominio | El colega, en efectivo |

Tres modelos de ingreso que **no se canibalizan porque son capas del mismo
objeto**. Y la posición es defendible: nadie más en la escena tiene la máquina.

### El producto no es el sitio

El HTML es commodity — Cloudflare Pages es gratis y cualquiera lo hace.
Lo escaso: **no le pedís al cliente que curatore.**

Todo servicio de portafolio dice *"mandame tus 20 mejores piezas organizadas por
proyecto"*. Ese es exactamente el paso donde todos se frenan, y por eso los
colegas siguen con el trabajo tirado en Instagram.

> **La frase que es el negocio: "mandame la carpeta desordenada".**

Y lo que se vende no es diseño web: es **la lectura**. Alguien leyó 700 archivos
y te dice qué es tu obra. Eso además halaga al cliente, que es cómo se venden
servicios creativos.

---

## 2. Ideas vivas

Ordenadas por plata por unidad de trabajo nuevo. Cada una con el mismo esquema.

### 2.1 · Portafolios para colegas — LA LÍNEA PRINCIPAL

- **Por qué es real:** diseñadores 2D, VJs e iluminadores tienen su obra sólo en
  Instagram. Instagram es un *feed*, no un portafolio: no le podés mandar a una
  productora "mirá mi IG" y esperar que scrollee 300 posteos buscando el trabajo
  de LED. Todos lo saben y nadie lo arregla, porque armar un sitio es un proyecto.
- **Qué hay construido:** todo. Ver §1. Más `tools/portfolio/`,
  `gen_campo_iskvw.py`, `gen_capas_iskvw.py`.
- **Diferenciador:** la carpeta desordenada. Ver §1.
- **Precio:** paquete de alcance fijo, no barato-y-muchos. Se cobra la
  **curatoría**, no el HTML.
- **La trampa:** `triangular.py:17-20` — las fichas del 2026-07-23 se hicieron
  con un prompt que **nunca pedía headliners**. Si esto se vende, el prompt de
  percepción tiene que estar corregido ANTES. Una ficha con metadata equivocada
  llegando a un cliente es el problema "reduciendo ano" otra vez.
  → **El bloque D7-D10 de `PLAN_IBM_20D.md` deja de ser higiene interna y pasa a
  ser el control de calidad del producto.** El crédito de IBM está
  de-riskeando la línea de ingreso.
- **Caso cero:** la migración de iskvw.cl de Adobe Portfolio a estático propio.
  Hacerlo primero sobre uno mismo, en público, con antes/después. Ese es el
  activo de venta.
- **Siguiente paso concreto:** el día de §4.
- **Estado:** máquina lista, prompt sin corregir, sin precio publicado.

### 2.2 · Contenido LED / VJ como servicio con precio

- **Por qué es real:** las productoras necesitan contenido para pantalla, se paga
  en efectivo por evento, y está crónicamente mal atendido.
- **Qué hay construido:** `tools/vj_set`, `tools/tapiz_renderer.html`,
  `tapiz_three.html`, `TAPIZ_RESOLUME_SPEC.md`, `tapiz_live_loop.py`,
  pixel-mapping, totems. Blender a nivel de Geometry Nodes con Simulation Zones.
  Y **la lista de clientes**: `extraccion_db.py` + `gen_dashboard_productoras.py`
  vienen produciendo candidatos de productoras y venues del corpus de flyers.
- **La trampa:** falta lo aburrido — hoja de precios y página de portafolio. Sin
  eso cada trabajo se negocia de cero y se cobra mal.
- **Siguiente paso concreto:** la hoja de precios sale en el día de §4.
- **Estado:** capacidad técnica sobrada, comercialización en cero.

### 2.3 · Departamento vigía (scanner) — el de mayor impacto en la vida real

- **Por qué es real:** enfermería en empleospublicos se publica todos los días;
  becas, cursos y concursos tienen ventanas que se cierran. Revisar a mano no
  escala y olvidarse cuesta un plazo.
- **El insight central: no es un problema de LLM, es un problema de diff.** 90%
  del valor es bajar → normalizar → hashear → comparar con el estado anterior →
  notificar lo nuevo. Eso es `urllib` y un JSONL de IDs vistos. **Cero tokens,
  cero GPU, cero rate limits.** El modelo aparece sólo en el último tramo
  ("¿calza con este perfil?"), y hasta eso conviene pre-filtrar por palabras.
- **Corolario:** no compite por la GTX 1650 y no necesita un peso del crédito de
  IBM. Es el departamento más barato de construir.
- **Modelo a copiar:** `mak_lenguaje`. Es el único departamento que **nunca
  falló**, y es el único sin LLM, sin red y sin GPU. Stdlib, determinista,
  aburrido. Aburrido = en diciembre sigue corriendo.
- **Qué hay construido:** `cola.py` con `ntfy_publish()`, `red_watch.py` como
  molde de cron, `guardia.py` como gate de recursos, `memoria.py` para dedup
  semántico, `backlog.py` como molde de cosecha. Y **`tools/becas_calendario.py`
  ya existe** — mirar qué hay ahí antes de escribir de cero.
- **Las tres trampas, y las tres ya pasaron:**
  1. **El cero silencioso.** Si cambia el HTML, el parser devuelve 0 y el scanner
     reporta "nada nuevo" para siempre. Es lo que pasó con la corrida detenida el
     2026-07-23 (tres días parada sin que nadie se enterara) y con las fichas sin
     headliners. → **"0 resultados por primera vez en N días" es ERROR, no
     silencio.** Esa línea decide si el departamento sirve.
  2. **La cola compartida.** No colgarlo de `worker.py`: ese worker toma un
     `flock` exclusivo y serializa todo por la GPU de 4 GB. Un chequeo horario
     quedaría atrás de un research de 30 min y llegaría cada 4 horas. **Lock
     propio y cron propio** — es seguro porque no toca GPU ni modelo.
  3. **El destino.** La salida va a ntfy, no a un dashboard que hay que acordarse
     de abrir. Topic separado para la enfermera, en su propio teléfono.
     Construir para otra persona es otra barra: 40 notificaciones por día y lo
     silencia en una semana.
- **Buena práctica de red:** GET condicional (`If-Modified-Since` / `ETag`).
  Cuesta casi nada, es la forma respetuosa, y evita el baneo de IP que llega
  cuando se golpean 50 sitios por hora sin caché.
- **Estado:** no empezado. Es lo próximo después del día de §4.

### 2.4 · El reencuadre migratorio: la enfermera es la visa

- **Por qué es real:** un fondo artístico son ~US$5-20k por una vez y **no
  confiere residencia**. Enfermería está en listas de escasez de profesionales en
  varios países, y eso sí es una vía de residencia **que arrastra pareja**. La
  asimetría es enorme.
- **Consecuencia para el vigía:** si sólo puede vigilar una cosa bien, no es
  fondos.cl. Es **reconocimiento de títulos y reclutamiento de enfermería** en
  dos o tres países objetivo, más los plazos de examen y colegiatura, que son lo
  que realmente define el calendario.
- **Lo artístico entra por la segunda puerta:** **residencias con estipendio y
  fondos de movilidad**, donde el dinero y el permiso de estadía suelen ser el
  mismo instrumento — que es justo lo que un Fondart no da.
- **Regla de fuentes:** apuntar el scanner a **agregadores**, no a fondos
  individuales. El agregador lo mantiene alguien más; eso es trabajo que no se
  paga.
- **Pendiente:** verificar la lista concreta de agregadores y programas vigentes.
  **No copiar nombres de memoria** — cambian todos los años y un dato viejo
  cuesta un plazo.
- **Estado:** decisión estratégica tomada, investigación sin hacer.

### 2.5 · Fondo público: el archivo, no los portafolios

- **Por qué el encuadre obvio es débil:** "portafolios gratis" se lee como
  freelance subsidiado, y compite con la línea pagada de §2.1 (si el fondo los
  hace gratis, ¿quién paga?).
- **La versión fuerte:** el fondo paga **el archivo público**. Documentación y
  preservación de la práctica de visuales en vivo en Chile — una escena que hoy
  existe sólo como posteos efímeros y desaparece cuando alguien borra su cuenta.
  Patrimonio digital efímero sin registro institucional. Es colectivo (los fondos
  lo prefieren), produce un bien público, y **el portafolio de cada participante
  sale como subproducto de la misma corrida**. No compite con §2.1: la alimenta,
  porque el archivo es la vidriera.
- **Requisitos del día uno, no de después:**
  - **Consentimiento explícito por artista** para archivar obra ajena. No es
    trámite: es lo que hace creíble la postulación.
  - Las fotos de evento involucran **fotógrafos y venues como terceros**.
  - **El material de RD y este archivo nunca se tocan.** Misma frontera de datos
    que en `PLAN_IBM_20D.md`.
- **Estado:** idea encuadrada, nada escrito.

### 2.6 · Comunidad VJ: el piso de precios es el producto

- **Por qué es real:** "competencia desleal" en un mercado freelance creativo es
  **siempre precio**. Alguien cobra 50 lucas por una noche que vale 300 porque
  nadie sabe cuánto se cobra, y la productora vive de esa opacidad.
- **El artefacto que mueve el mercado:** **datos de tarifas anónimos, agregados y
  publicados.** Formulario anónimo → rangos por tipo de evento, duración y
  entregable → publicado. Es lo que hace que la gente se sume, porque todos
  quieren saber cuánto cobran los demás. Un grupo de WhatsApp amistoso no arregla
  nada.
- **Activo propio:** "menos compe más compas" funciona porque hay antecedentes —
  las colabs triples de técnica múltiple son un hecho documentado, no un eslogan.
  **La comunidad debe ser la institucionalización de algo que ya se hace.**
- **Las tres trampas:**
  1. **El orden.** La comunidad va **después** del producto pagado, no antes. Con
     el servicio primero, la comunidad se forma alrededor de los usuarios. Con la
     comunidad primero, se es administrador no pago de 80 personas que piden
     favores. Organizar es infinito, político y gratis.
  2. **La curatoría de personas.** El día que se decide quién entra al
     directorio, uno define quién es "VJ de verdad" en Chile: poder que no se
     pidió y enemigos que no se ganaron. **Inscripción abierta; criterio sólo
     sobre presentación, nunca sobre quién.**
  3. **El piso estadístico.** La encuesta necesita ~15-20 respuestas antes de
     publicar. Abajo de eso el anonimato es falso, y publicar con 6 quema la
     confianza para siempre.
- **Estado:** posicionamiento claro, ejecución postergada a propósito.

### 2.7 · Aviso de vencimiento de dominios → trabajo web chico

La versión legítima de la idea de dominios vencidos (ver §5.1 por qué la otra
no). **La señal es real: alguien se descuidó y hay urgencia.** El activo estaba
mal elegido.

- **El movimiento:** el scanner encuentra el vencimiento y **se le avisa al
  dueño, gratis.** "Tu dominio vence en 11 días" es un mensaje bienvenido que
  abre conversación con un negocio que acaba de descubrir que no tiene a nadie
  cuidando su presencia web. Misma búsqueda, polaridad invertida: **construye
  reputación en vez de gastarla.**
- **La lista de prospectos ya existe:** `extraccion_db.py` y
  `gen_dashboard_productoras.py` producen candidatos de productoras y venues con
  nombres canónicos fuzzy-matcheados. Son exactamente los negocios con dominio
  abandonado y cero capacidad técnica interna. **El corpus de curatoría es una
  lista de clientes.** Cruzarlo contra estado de dominios es un script de una
  tarde.
- **Prueba de competencia:** la propia migración de iskvw.cl.
- **Estado:** no empezado. Depende del vigía (§2.3).

### 2.8 · Escribir postulaciones para otros

- **Por qué es real:** la temporada de Fondart es un cuello de botella anual y la
  gente paga por ayuda.
- **Qué hay construido:** `gen_propuestas_rd.py`, `gen_propuesta_directiva.py`,
  `tools/becas_calendario.py`.
- **Acá sí se justifica el crédito de IBM** (volumen de tokens con calidad).
- **Estado:** maquinaria parcial, sin oferta.

### 2.9 · Base de datos de venues y riders — EL MEJOR CLIENTE

- **Por qué es real:** toda producción le pregunta al venue "¿tienes plano?" y el
  venue manda un PDF de 2014 que no coincide con la realidad. El documento ya se
  pide, ya existe, y está disperso y viejo.
- **Quién paga: el VENUE, no los artistas.** Los artistas no tienen plata y no van
  a pagar una base de datos. Los venues tienen presupuesto de documentación
  técnica y, más importante: **un render 3D con rider exacto es herramienta de
  venta** — lo mandan a las productoras para ganar fechas. Eso lo mueve de "costo
  de documentación" a "gasto de marketing": otro presupuesto, otra disposición a
  pagar.
- **El flywheel (y es raro que exista uno real):** los artistas aportan
  correcciones —"el truss está a 6,2 m, no a 7"— **gratis**, porque les conviene
  la exactitud. La exactitud hace valioso el documento del venue. El venue paga.
  → **El aporte de la comunidad es el foso; el documento del venue es el
  producto.**
- **Qué hay construido:** `PLANO.png`, `plano rider.pdf`, `RIDER-01.svg`,
  `src/flujo/plano`, `tools/sala3d`, `tools/piezas_vectoriales`. Ya se estuvo
  haciendo esto sin llamarlo negocio.
- **LA TRAMPA, y es de las serias — responsabilidad:** un rider técnico es un
  **documento de seguridad**. Si alguien cuelga un truss según el render y la
  carga está mal, eso no es un error de diseño: es una persona debajo de una
  estructura que cae.
  > **El render describe, nunca certifica.** Cargas, capacidades de rigging,
  > límites eléctricos y vías de evacuación se **citan** de la documentación
  > certificada del propio venue, con fuente y fecha, o van marcados
  > explícitamente como **no verificados**. Nunca se publica una medición propia
  > como si fuera un certificado.

  Es la regla §6.4, tercera aparición del mismo patrón.
- **Lo bueno de la trampa:** **medir bien es el trabajo facturable.** Una pasada
  de fotogrametría o medición láser es la razón por la que esto es un servicio y
  no un scraper — nadie lo commoditiza con un script.
- **Estado:** insumos dispersos, sin oferta, sin esquema de datos.

#### 2.9.1 · El intake: la tercera opción (no foro, no API ajena)

Falso dilema a evitar: "armar un foro" vs "usar la API de una red existente".

- **Por qué no un foro:** no es un problema de API, es de **arranque en frío**.
  Un foro necesita masa crítica el día uno o es una sala vacía, y una sala vacía
  mata la credibilidad.
- **Por qué no la API de Reddit:** técnicamente **sí** lo permite (tier gratis con
  rate limits bajos, uso comercial ~US$0,24 por 1.000 llamadas, términos que
  restringen almacenamiento y redistribución). El problema no es el permiso: es
  que **Reddit ya hizo exactamente esto en 2023** — mató el acceso gratuito de un
  día para otro y fundió a los terceros que dependían de él. Es cambiar arranque
  en frío por **dependencia**, la cosa contra la que está organizado todo el repo.
- **La tercera opción:** **la comunidad no necesita sede; la base de datos
  necesita intake.** Los técnicos y VJs ya viven en Instagram y WhatsApp — moverlos
  es arranque en frío *más* migración, dos problemas duros por cero ganancia.

```txt
formulario (nativo de celular)  ->  issue  ->  validacion contra schemas/
                                                  ->  merge  ->  sitio estatico
```

- **Ya está todo construido:** `gmail_to_github_issues.gs` (el intake está
  resuelto), `puente_issues.py`, `bridge_issue_render.py`, `inbox/`, `schemas/`,
  `publicar_iskvw.yml`.
- **Por qué gana:** un formulario es nativo de celular, un foro no. Cero
  dependencia de plataforma, cero arranque en frío, y la base es **un JSONL
  versionado y propio**. Misma razón por la que `index.jsonl` es una virtud y no
  una deuda.

#### 2.9.2 · Decisiones técnicas de captura (verificado 2026-07-30)

Detalle operativo en `tools/sala3d/PROTOCOLO_CAPTURA_VENUE.md`. Acá quedan sólo
las decisiones y por qué.

**Las cámaras Hikvision 2MP/2,8 mm: el problema no era el 2MP.** En orden de
probabilidad: (1) se estaba tirando del **sub-stream** —`/Streaming/Channels/102`
es sub, `101` es main; el sub suele ser 640×480 a ~512 kbps—, (2) **bitrate**, no
resolución: el perfil de fábrica está afinado para 30 días de grabación, subir a
8-16 Mbps CBR e I-frame a ~1× fps, (3) **H.264+/H.265+ prendido**, que congela el
fondo y mete fantasmas —apagar para uso en vivo—, (4) espiral
**ruido→compresión** en sala oscura, limitar ganancia y usar DNR, (5) WDR/BLC/HLC
en automático peleando con las luces, todo a manual, y (6) **2,8 mm es ultra gran
angular (~100-110°)**: la blandura es **resolución angular sobre el sujeto**, no
del sensor.
→ **No comprar más megapíxeles. Comprar más milímetros.** Un 6 o 12 mm en el mismo
sensor se ve dramáticamente mejor sobre gente.

**Una cámara IP es la herramienta equivocada para vivo.** Existe para topología de
vigilancia: PoE largo, muchas cámaras, grabación continua. Su costo es compresión
y **latencia** (200 ms - 2 s de decodificación RTSP), fatal si se corta en el beat.
- **Vivo a Resolume** → HDMI limpio o USB-UVC a una capturadora. Un dongle
  HDMI→USB barato le gana en todo menos largo de cable.
- **Grabar para procesar después** → la IP está bien; la latencia no importa y se
  puede poner el bitrate al máximo.
- Si igual se usa RTSP en vivo: `-fflags nobuffer -flags low_delay -probesize 32
  -analyzeduration 0`, GOP = 1× fps, y como capa de ambiente, no sincronizada.

**El infrarrojo: excelente contenido, mala reconstrucción.** Como estética
—monocromo plano, ojos retrorreflejando, aire de vigilancia— es **firma** y hay
que seguir. Como insumo de fotogrametría **no sirve**, por tres razones
independientes: las cámaras fijas **no dan paralaje** (se necesitan decenas de
puntos de vista de una cámara en movimiento; cuatro esquinas es matemáticamente
insuficiente), **el IR se mueve con la cámara** y rompe el supuesto de que una
superficie se ve igual desde ángulos distintos, y monocromo + gran angular +
comprimido es el peor insumo para detección de features.

**DESCARTADO: pedir acceso al CCTV del venue.** Ver §5.8.

**LiDAR para lo medible, fotogrametría/splats sólo para que se vea lindo.** La
fotogrametría es **ambigua en escala** salvo que se ponga una referencia de tamaño
conocido; **el LiDAR viene métricamente escalado**. Para un rider, escala
equivocada = documento equivocado = el problema de la regla §6.4. Los Gaussian
Splats se ven muy superiores a la malla en interiores pero **no se miden**.

**El iPad captura y exporta, nada más.** El error anterior no fue el precio de las
suscripciones: fue usar la app como pipeline completo, *"el render corriendo por la
misma app sin capacidad de configurarlo"*. Exigirle a la app: OBJ/PLY/USDZ **más el
set de imágenes crudas**, sin nube obligatoria, pago único. Verificar términos
actuales antes de pagar. Confirmar que el iPad sea **Pro 2020+** (el LiDAR está
sólo en los Pro); si no, el plan cambia a fotogrametría + medidor láser para dar
escala.

**Un medidor láser (~$30-40) es lo más barato que convierte el escaneo en
documento.** Diez cotas a mano son la verdad de referencia que valida el escaneo y
los números que van en el rider. Tres niveles de confianza en un entregable: el
escaneo **describe**, las cotas a mano son lo que se **afirma**, las cargas se
**citan** de la documentación certificada del venue.

**Todo el proceso en casa y gratis:** Meshroom (AliceVision) o COLMAP,
Blender para modelar limpio encima, splatting con CUDA. **En el notebook con la
RTX 4070, no en MAK** — la 1650 de 4 GB ya tiene su trabajo. Misma división que
`bridge_issue_render.py` ya establece.

**El flujo propuesto era correcto y además es el modelo de negocio:** visita al
venue → captura → proceso en casa. La visita es el evento facturable, el proceso
corre en fierro propio a costo marginal cero. **Lo único que lo rompe es volver dos
veces**, y por eso la captura es checklist y no improvisación.

#### 2.9.3 · La lección del SCD: invertir el generador (2026-07-30)

Revisión completa en `tools/sala3d/REVISION_PLANO_TEATRO.md`. Lo que queda como
decisión:

**El diagnóstico del trabajo SCD: no faltó información, el modelo imponía una
geometría que el edificio no tiene.** `referencia_plano_teatro.py` declara en su
propio subtítulo *"Geometría Radial · Simétrica"*, y el SCD Plaza Egaña era una
construcción readaptada al lugar físico. Las medidas estaban bien; el modelo no
cerraba. Y como el dibujo salía perfecto igual, la conclusión fue "me falta info"
→ se buscó al arquitecto en vez de confiar en la huincha. **El generador mintió en
silencio**, que es justo lo que `memoria.py` se niega a hacer con las dimensiones
de embedding.

**Requisito nuevo:** la herramienta **reporta su propio residuo**. Si el mejor
ajuste deja un muro 40 cm afuera del arco, lo dice. Un dibujo limpio y falso es peor
que uno con nota de discrepancia — regla §6.4 otra vez.

**NO generalizar el generador: invertirlo.** Un generador (parámetros → forma) sirve
sólo para venues que siguen un tipo; las discotecas —"arquitectura sin propósito",
ex-stripclubs, casas antiguas— no lo van a hacer nunca. Lo que generaliza es
**modelo de datos + renderer**: el venue es un JSON de polilíneas medidas, alturas,
artefactos, citas y **residuos**, con un campo `confianza` por dato
(`medido | ajustado | citado | no_verificado`). El generador de teatro pasa a ser
**un ayudante de entrada** que escribe ese JSON rápido para las salas radiales.

> **CORRECCIÓN 2026-07-30 (misma tarde): el esquema no se inventa — se exporta a
> MVR.** El formato ya existe y es norma publicada: **MVR (My Virtual Rig) =
> DIN SPEC 15801:2023-12 v1.6**, y **GDTF = DIN SPEC 15800**. MVR no lleva sólo
> luminarias: lleva **escena completa** — trusses, pantallas, objetos de escena,
> capas, clases, grupos. Lo leen grandMA3, Vectorworks Spotlight, Capture. Y las dos
> piezas que lo vuelven propio: **BlenderDMX** importa **y exporta** MVR desde
> Blender, y **`pymvr` / `pygdtf`** son librerías Python.
>
> **La diferencia es comercial, no técnica:** un render es una imagen que el venue
> mira; **un MVR es un archivo que el diseñador de iluminación carga en su consola.**
> Lo segundo le ahorra trabajo a la persona que contrata, y por eso se paga.
> El JSON propio sigue existiendo como fuente (lleva cotas a mano, citas, residuos y
> `confianza`, que MVR no modela); **MVR es la salida.**
>
> Y lo que **no** existe: el lado venue. Todo lo que hay —ArtistRider, RiderForge,
> guías de stage plot— es **del lado del artista**. As-built de sala, cotado y
> exportable, no apareció. Ese es el hueco, y requiere estar en el lugar.
> Léxico completo y términos de búsqueda en `POSICIONAMIENTO_Y_LEXICO.md` §4.

→ **La base de datos de §2.9 no son renders: son estos JSON en `schemas/`, en git.**
Los planos y renders son derivados regenerables. Un colaborador corrige una cota y
todo se regenera. Ahí el flywheel funciona.

**Dejar de exportar imágenes para Blender; exportar coordenadas.** Un SVG es un
dibujo (matplotlib con `bbox_inches='tight'` sale en escala arbitraria y hay que
reescalar a ojo, que es donde se pierde la precisión métrica que es todo el valor).
Un DXF o un JSON de polilíneas en metros es geometría: veinte líneas de Python en
Blender lo leen a escala exacta para siempre. PNG/PDF/SVG siguen existiendo como
**lámina para el cliente**, no como transporte de geometría.

**Bug que hay que arreglar ya:** la tabla "Configuración Manual por Fila - Planta
Baja" **no hace nada** — la rama exige `not align_radial`, y `align_radial` está
fijo en `True` sin control en la UI. El usuario la llena y el dibujo la ignora. El
balcón sí funciona, así que además es inconsistente.

**El prototipo ya existe: el caso SCD.** Publicarlo, y presentarlo como
**documento, no como imagen** — plano + render + estructura del rider, mostrando
los tres niveles de confianza. El valor no es que el render esté lindo: **SCD es un
cliente institucional con nombre reconocible** y eso abre puertas que ningún
portafolio de imágenes bonitas abre.

### 2.10 · ReD: el box del stand (XIO aplicado a reducción de daños)

- **La idea:** un servidor local en el stand de RD. La gente se conecta desde su
  teléfono en la zona de descanso: información, preguntas anónimas, riesgos de
  interacción. **Sin extracción de datos.**
- **Por qué es la mejor idea de la tanda:** el **anonimato deja de ser una
  promesa y pasa a ser una propiedad de la topología.** Sin internet no hay
  registros en un ISP, no hay analítica, no hay IPs saliendo del dispositivo. Si
  el dato no existe, no hay nada que filtrar ni nada que requerir.
- **Bonus de UX:** en un festival la red celular está saturada. Un AP local es
  **mejor experiencia**, no una concesión. Y es nativo de celular por
  construcción — resuelve del todo el requisito "sin necesitar PC".
- **Qué hay construido:** `xio/` y el patrón del `xio_puente` (GET-only). Es el
  mismo molde.

#### 2.10.1 · Contexto legal vigente — Ley 21.817 (verificado 2026-07-30)

> **Esto caduca. Revisar cuando salga el reglamento (~noviembre 2026).**
> La parte legal la lleva MAK (el humano). Acá quedan sólo las consecuencias de
> diseño.

Aprobada en marzo, **publicada el 23 de mayo de 2026**, modifica la Ley 20.000:

1. **Cambia la lógica de clasificación:** de cantidad a "peligrosidad
   toxicológica". El reglamento que define qué sustancias entran está
   **PENDIENTE** (seis meses desde la publicación).
2. **Tres agravantes nuevas, de 5+ a 10+ años.** Dos importan acá:
   - cuando las sustancias están **adulteradas o mezcladas**
   - cuando el tráfico se hace **usando aplicaciones tipo WhatsApp, Telegram o
     Instagram**
3. **Impugnación en el TC** presentada el 13 de abril por 37 diputados
   (encabezados por Gazmuri): alega que la ley no excluye actos preparatorios del
   consumo personal permitido y que vulnera proporcionalidad y privacidad.
   **Sin resolver.**

**Consecuencias de diseño, no opiniones legales:**

- **La agravante de "aplicaciones" es el argumento fuerte a favor del box local.**
  Un AP local **no es una aplicación de mensajería**: no hay cuentas, no hay
  mensajes, no hay transporte que un fiscal pueda caracterizar. El mismo servicio
  por WhatsApp o DM de Instagram operaría en un canal que la ley **acaba de
  nombrar explícitamente**. El instinto era correcto; ahora tiene razón técnica.
- **La agravante de "adulteradas o mezcladas" es una mina debajo de la función de
  combinaciones.** No hace ilegal informar, pero pone contenido que se lea como
  *orientación para combinar* al lado de una figura agravada específica.
  → **Riesgo de interacción y señales de alarma sí. Cualquier cosa que se lea
  como cómo-combinar, no.** La línea de CLAUDE.md ("reducción de daños, no guía de
  consumo") deja de ser principio y pasa a ser estructural.
- **El reglamento pendiente significa que el contenido caduca.** Lo exacto en
  agosto puede estar mal en diciembre. Obliga a contenido **versionado, fechado y
  con fuente visible en pantalla** — que es lo que da un bundle estático en git y
  lo que nada generativo puede dar.
- **El TC abierto** significa que hay un argumento constitucional vivo sobre
  proporcionalidad y privacidad en este dominio exacto. El terreno está en
  disputa, no cerrado: el diseño conservador y la documentación son el mejor
  activo.

#### 2.10.2 · Reglas de diseño del box (no negociables)

1. **CONTENIDO: lo provee un organismo de reducción de daños establecido, citado y
   versionado. NADA de generar información de sustancias con un modelo.** Es lo
   más seguro y lo único creíble ante una autoridad sanitaria. Un bundle auditable
   es un activo de cumplimiento, no un trámite.
2. **Sin logs, por arquitectura y no por política.** Sin access log, sin
   analítica. Si algo se guarda, en RAM y se borra al desarmar. La afirmación de
   anonimato es verdadera sólo si es una propiedad, no una promesa.
3. **Las preguntas anónimas son un almacén de datos si se guardan.** La versión
   más simple y más segura: la pregunta llega a una tablet que sostiene el equipo
   de RD y **la responde una persona**. El aparato sólo saca la vergüenza de
   preguntar en voz alta. Nunca toca disco.
4. **Nada de dosis.** Interacción, riesgo y "buscá ayuda si" es reducción de
   daños. Dosis es guía de consumo. La línea ya está en CLAUDE.md.
5. **Frontera de datos:** el material de RD no se mezcla con el archivo público
   de la escena (§2.5) ni sale de la caja. Misma regla que `PLAN_IBM_20D.md`.

- **La conexión que cierra el embudo:** RD ya era la puerta a las productoras. Con
  la ley nueva y su ambigüedad, un productor que puede mostrar **presencia
  documentada de reducción de daños** tiene una posición defendible. → **El box
  deja de ser sólo la puerta y pasa a ser un valor cotizable.**
  `RD -> productoras -> venues -> riders -> contenido LED` es **un solo embudo**,
  no cinco ideas.
- **Y es financiable:** acceso a información de salud pública con anonimato por
  diseño es una postulación mucho más fuerte que "portafolios gratis".
- **Estado:** idea encuadrada, contexto legal verificado, nada construido.

### 2.11 · Afters: la puerta de luces, y separar geometría de identidad

- **El encuadre comercial es correcto:** se vende **diseño de luces y visuales
  automatizadas**, el LiDAR sale de paso en la visita técnica, y el rider se propone
  después si quedó contento. No se presenta nunca como "te hago un 3D del local".
- **Por qué el iPad es mejor que pedir cámaras, y no es sólo lo práctico:** pedir
  acceso al CCTV es tocar un sistema que **graba a todo el mundo, todo el tiempo, y
  lo guarda 30 días**. Entrar con el iPad captura **sólo geometría, una vez, sólo lo
  que se apunta**, y el que decide qué se borra es uno. El iPad es la opción que
  protege.
- **EL RIESGO REAL NO ES LA PRESENTACIÓN, ES EL ARTEFACTO.** Un escaneo LiDAR de un
  local irregular es un mapa preciso con sus salidas, probablemente
  **geolocalizado** (muchas apps escriben GPS en el EXIF), con fecha y hora, en los
  dispositivos y en el repo. Si eso se filtra, se pierde o lo piden, se produjo el
  documento más útil posible sobre gente que confió.

#### 2.11.1 · La regla que hace que la idea sobreviva: geometría ≠ identidad

Lo **técnico** es valioso y **anónimo**: la sala mide 12×8, cielo a 3,2, una columna
a un tercio, acometida 32A monofásica, tiro de proyección 9 m.
Lo **identitario** —qué local, dónde, de quién— es lo peligroso **y no se necesita**.

- [ ] **EXIF de GPS afuera, siempre.** Verificar en la app antes de la primera visita.
- [ ] Sin dirección ni nombre en el archivo. Un id que no mapea a nada guardado.
- [ ] **Para afters no se conserva la nube de puntos.** Se entrega el showfile, se
      guardan las cotas y notas técnicas anonimizadas, **se borra el escaneo**. La
      nube es el artefacto peligroso; los números son el útil.
- [ ] La regla "sin gente" del protocolo vale doble acá, y además **es lo que
      construye la confianza**: *"vengo a medir la sala vacía, no saco fotos de
      nadie, no guardo la dirección"* es literalmente lo que desactiva el miedo a
      estar siendo registrado.

> **No ser el que tiene la lista.** Con una planilla de afters uno es un objetivo y
> un pasivo. Con **tipologías anónimas** uno es un ingeniero con datos de
> referencia.

Y estratégicamente la versión anónima es **más valiosa**: lo que se reutiliza es
*"esta es la tercera sala de 12×8 con columna y sin puntos de cuelgue, acá está el
plot que funcionó"*. Eso es una **biblioteca de tipologías**. Una lista de locales
sólo sirve para revenderle a ese local, y para afters no se puede publicitar igual.

- **Estado:** encuadre y reglas definidas, nada construido.

### 2.12 · Ordenador de archivos — EL INGRESO RECURRENTE

- **Por qué es real:** para un artista el desorden es el peor síntoma y el problema
  de "mañana". `percepcion.py` ya **lee y describe** una carpeta desordenada; falta
  el paso siguiente: **actuar sobre ella**.
- **La frase que tiene todo el valor: "según las app que llaman a esa carpeta."** No
  es orden genérico, es **estructura consciente del software** — y es difícil justo
  donde está el valor: mover un archivo que un proyecto referencia lo rompe. Los
  `.aep` y `.prproj` guardan rutas; Resolume referencia clips por path; los `.blend`
  tienen rutas relativas y absolutas de texturas y links.
  → **La herramienta no mueve archivos: lee los archivos de proyecto para saber qué
  assets se usan de verdad, y después reordena reescribiendo las referencias.**
- **La función que se vende sola: "¿qué puedo borrar?"** Assets que ningún proyecto
  referencia, duplicados por hash, renders superados por versiones posteriores. Para
  alguien con el disco lleno eso vale plata, y nadie lo hace porque exige leer
  formatos de proyecto.
- **Orden de implementación, de seguro a peligroso:**
  1. **Inventario + dedup por hash.** Trivialmente seguro, valor inmediato. Las
     fichas ya existen.
  2. **Grafo de referencias:** parsear proyectos por rutas de assets. Blender es el
     más fácil (API de Python, ya se scriptea), Resolume es XML, AE/Premiere son los
     duros.
  3. **Reporte de huérfanos.** Sólo lectura, sin mover nada. **Esto ya es vendible
     como informe.**
  4. Recién después proponer movimientos — **nunca mover sin reescribir referencias,
     nunca sin dry-run y sin un manifiesto reversible.**
- **La trampa:** romperle los proyectos al archivo de un cliente es daño de
  confianza irrecuperable. Que `retencion.py` sea dry-run por default es el mismo
  instinto — ya está, hay que aplicarlo acá.
- **Por qué importa comercialmente:** **el portafolio es una vez; "ordeno tu archivo
  y te digo qué borrar" es anual.** Y la misma corrida de `percepcion.py` deja
  montado el inventario. **Portafolio = la puerta. Higiene de archivo = el abono.**
- **Estado:** `percepcion.py` describe, nada actúa. El paso 3 es la primera venta.

---

## 3. Deudas técnicas que bloquean plata

No son higiene: cada una está entre una idea de §2 y el primer peso.

| Deuda | Dónde | Qué bloquea |
|---|---|---|
| Prompt de percepción sin headliners | `triangular.py:17-20` | §2.1 — es el QA del producto |
| `buscar()` en Python puro, O(N·768) | `memoria.py:283-299` | §2.1, §2.5 — el archivo consultable. Gratis de arreglar; el grafo ya tiene numpy (`_aristas_numpy():340`) |
| Vectores como 768 floats de texto por línea | `index.jsonl` | idem. A `.npy` baja ~6× y carga instantáneo |
| VCD-03: el sandbox que no es sandbox | `codex_lib.py:13-40`, 4/6 evasiones pasan | Escalar `generar.py`. Mientras tanto: escalar `agente_libre.py`, que entrega sin ejecutar |
| `:8890`/`:8891`/`:8900` sin auth | `DEPLOY_OPEN.md` | Seguro **sólo** porque es LAN. Tailscale es lo que permite mantener esa decisión y ver los órganos desde el teléfono. Sin él, la alternativa es exponer puertos sin auth |
| `azure` en el default de `LLM.__init__` | `research_lib.py:396`, `interfaz.py:1027` | Retirado el 2026-07-28 pero sigue firmando por default y comiendo 90 s de timeout |
| Timeouts desalineados | `FALLBACK_FINDINGS.md:59` | Worker research 1800 s / codex 900 s vs proveedores 60-300 s |
| Tabla manual por fila muerta | `referencia_plano_teatro.py:457` + `:69` | §2.9.3 — la UI miente hoy |
| Grosor de pared es un trazo, no geometría | idem `:254`, `:372` | El espesor no se exporta a Blender |
| Escala arbitraria en el export | idem `:602` (`bbox_inches='tight'`) | La precisión métrica se pierde al reescalar a ojo |
| **SIN COMPUERTA DE CALIDAD DE FUENTE** | `research_lib.py` (`fetch_url:591`, etapa de análisis) | **§3.c — el defecto más grave encontrado.** Bloquea confiar en cualquier informe |
| Nombre del servicio = nombre de artista | `iskvw.cl` | §3.d — la presentación B no puede vivir ahí |

---

## 3.c El defecto más grave: el research afirma sin fuente (hallado 2026-07-30)

**Caso:** `docs/rd/informes/ley_20000_marco_legal.md` (2026-07-22).

Sus tres fuentes, según su propio `meta:`:

```txt
eesppnsrmadrededios.edu.pe/libros/1.pdf        escuela de pedagogia PERUANA
mriuc.bc.uc.edu.ve/.../tomo3.pdf               Universidad de Carabobo, VENEZUELA
dokumen.pub/estructura-social-de-chile...      agregador de libros pirateados
```

**Ninguna es fuente sobre derecho chileno.** Y el informe afirma, con estructura
impecable: *"El ISP autoriza a ONG a realizar pruebas de composición química bajo
condiciones de bioseguridad"*, *"Resultados de análisis deben remitirse al ISP"*,
*"ONG pueden ofrecer RDS con autorización del Ministerio de Salud"*. Atribuido a un
PDF de pedagogía peruano. **Casi con certeza inventado.**

Segunda capa: el informe es del 22 de julio, **dos meses después** de que se
publicara la **Ley 21.817** (23 de mayo, ver §2.10.1) — y no la menciona. **Sin
fuente Y desactualizado en el hecho más importante.**

**Por qué es peor que el bug del plano:** un arco mal dibujado hace que alguien
vuelva a medir. Esto dice "podés hacer análisis de pureza si reportás al ISP" y
alguien puede actuar en consecuencia.

**El diagnóstico está en el contraste.** `docs/becas/informes/2026...fundaciones-internacionales...md`
se portó **bien**: dijo *"no se localizan anuncios explícitos de convocatorias"* y
listó las lagunas. **Falló ruidosamente.** El legal **falló en silencio.** Misma
máquina, dos comportamientos → el problema no es el modelo, es que **no hay
compuerta de fuente**. `fetch_url` devuelve 4000 chars de lo que dé Tavily y la
etapa de análisis trata cualquier PDF como autoridad.

> **El sistema mide TILDES (93/100) pero no mide si las fuentes son del tema.**

### Los dos arreglos, y los dos son baratos

1. **Lista blanca por jurisdicción** para preguntas legales/regulatorias:
   `bcn.cl`, `leychile.cl`, `diariooficial.interior.gob.cl`, `ispch.gob.cl`,
   `minsal.cl`. **Cero fuentes de la lista → el informe se marca `SIN FUENTE
   PRIMARIA` y no afirma nada.** ~15 líneas. Es la diferencia entre un órgano de
   research y un generador de texto plausible.
2. **`refutar.py` ya existe y no se aplicó.** Una pasada adversarial —"dadas estas
   fuentes, qué afirmaciones NO están respaldadas"— mataba ese documento. **Es
   cableado, no código nuevo.** Y es exactamente donde rinde el crédito de IBM: una
   refutación por informe cuesta centavos y hoy no se hace por rate limits (el
   propio `meta:` de ese informe registra dos `429` de Cerebras).

### Acción inmediata

- [ ] **Marcar `ley_20000_marco_legal.md` como NO CONFIABLE** antes de que alguien lo
      cite. Es el informe más peligroso del repo **justamente porque es el mejor
      escrito**.
- [ ] Auditar los otros 13 informes commiteados: revisar el campo `sources` de cada
      `meta:` y preguntar *"¿estas fuentes son del tema?"*. Es lectura, no código.

**Lo bueno que hay que preservar:** ese `meta:` es la mejor instrumentación del repo
—`iterations`, `queries`, `findingsCount`, `sources`, `llmCalls` por proveedor,
`providerOrder`, `errors` con los 429 reales, `ms`— y el encabezado ya dice
*"Revisión humana pendiente"*. La disciplina está; falta la compuerta.

---

## 3.d El dominio: iskvw es buen nombre de artista y mal nombre de servicio

**iskvw funciona como nombre artístico precisamente porque es opaco.** Una vocal,
cuatro consonantes, impronunciable en español, no se explica solo. Eso es lo que
hacen los nombres de artista: dicen "esto es una práctica, no un producto".

**Y es letal para la presentación B.** Un administrador de sala que recibe *"el rider
está en iskvw.cl"* no puede escribirlo tras escucharlo por teléfono, no puede
decírselo a un colega, no lo recuerda a la semana, y no lo encuentra buscando. Peor:
**lee como proyecto de arte** en el momento exacto en que hay que leer como el
profesional que firma.

> **No se reconsidera iskvw. Se reconsidera si el servicio vive ahí. No vive ahí.**

Es el mismo corte A/B de `POSICIONAMIENTO_Y_LEXICO.md` §3 — la pregunta del dominio
ya estaba contestada por ese marco.

Y **protege a iskvw también**: un rider técnico colgado en el dominio de artista
diluye la práctica. Corta para los dos lados.

- **Renovar iskvw.cl sigue siendo correcto** y no cambia: es la firma, tiene
  historia, y dejarlo caer significa que alguien puede tomar el nombre de artista.
- Un segundo `.cl` son ~$10 mil más al año. **Dos dominios siguen siendo menos de dos
  cafés al año.** No era una restricción de plata, era una confusión de propósito.
- **Criterios del dominio de servicio** (lo elige MAK, el humano): pronunciable en
  español al primer intento · escribible tras escucharlo una vez por teléfono · que
  diga lo que hace o sea una palabra real · `.cl` · que quepa en una firma de correo
  y al pie de un documento.

---

## 3.b El orden (2026-07-30)

```txt
1  iskvw.cl                        horas. Sigue pendiente.
2  SCD publicado como caso          el activo YA existe; es la credencial
3  esquema venue-JSON en schemas/   sin esto cada venue es una GUI a medida
4  reporte de huerfanos (2.12 p1-3) solo lectura, seguro, vendible como informe
5  puerta de luces en afters, upsell de rider, base de datos
```

Nada del 5 antes del 3: sin el esquema, cada venue nuevo vuelve a ser trabajo
artesanal y el negocio no escala.

---

## 4. El día uno (un día de trabajo full)

El día correcto es el que **renueva el dominio, publica el portafolio propio con
la máquina, y produce el activo de venta** — porque ese único día desbloquea
§2.1, la credibilidad de §2.6 y la prueba de concepto de §2.5, todo junto.

```txt
00:00  RENOVAR iskvw.cl en nic.cl. Considerar 2-5 anios por el descuento.
       A nombre propio (RUT propio), no de un tercero.               [15 min]
       Es lo unico del dia que no puede fallar. Va primero.

00:15  Instalar Tailscale en la caja y en el telefono.               [20 min]
       Gana su lugar: permite mirar la corrida de percepcion desde
       el telefono en vez de quedarse sentado al lado del box.

00:35  Lanzar percepcion.py --solo-fuente ig sobre el archivo propio,
       CON el prompt de headliners corregido.                        [lanzar]
       Corre solo el resto de la maniana. No esperarlo mirando.

01:00  DNS de iskvw.cl a Cloudflare Pages. Conectar publicar_iskvw.yml
       (ya sube solo la carpeta iskvw/).                             [60 min]
       Mientras propaga: no es trabajo, es espera. Seguir.

02:00  Hoja de precios, una pagina. Tres paquetes, alcance fijo,
       precio visible. Contenido LED (2.2) y portafolio (2.1).       [90 min]
       Escribir el precio. Un precio escrito se cobra; uno pensado se negocia.

03:30  ---- almuerzo ----

04:30  Revisar la salida de percepcion. Generar el sitio con
       gen_archivo_iskvw.py y PUBLICAR.                              [120 min]
       Salida del pipeline TAL CUAL.

06:30  Un posteo en Instagram: antes/despues del portafolio +
       "hago esto para colegas, mandame la carpeta desordenada".     [45 min]
       Ese posteo es el activo de venta y la primera prueba de demanda.

07:15  Anotar en esta memoria: que se publico, que se rompio,
       cuanto tardo de verdad cada bloque.                           [30 min]

07:45  Cerrar. No abrir nada nuevo.
```

> **La única forma de que este día fracase es ponerse a diseñar.** El pipeline ya
> genera; se usa la salida tal cual. **Nada de estilos ese día.** Un sitio feo
> publicado vale infinitamente más que uno lindo en la cabeza. El diseño es otro
> día, y recién cuando haya un cliente que lo pague.

Lo que **no** entra al día uno, aunque tiente: el scanner, la comunidad, el
fondo, cualquier red social nueva, y tocar MAK más allá de la corrida de
percepción.

---

## 5. Descartado con razón (para que no se vuelva a intentar)

### 5.1 · Comprar dominios vencidos para revender — CERRADO

Tres capas, la tercera es la que decide:

1. **La carrera está perdida de antemano.** El drop-catching es industria madura:
   DropCatch, SnapNames, Pool corren cientos de conexiones de registrador y
   disparan miles de requests en el instante de la liberación. Una caja en Chile
   con internet residencial pierde el 100% de las veces para cualquier dominio
   que valga algo. Los que sí se agarran son, por definición, los que nadie quiso.
2. **El mercado .cl es chico.** Menos industrializado que .com, así que hay algo
   más de aire, pero vender exige encontrar *un* comprador chileno que quiera ese
   string exacto. Volumen bajo, ciclo lento. No es un ingreso.
3. **El problema serio no es económico.** El modelo es encontrar a alguien que se
   descuidó, registrar su nombre, y vendérselo de vuelta con un margen que existe
   *porque* se equivocó. Registrar con la intención primaria de revender al dueño
   previo es el patrón de hechos que persigue la doctrina de registro de mala fe
   — o sea, un negocio cuyo acto central es la cosa que después habría que
   defender. Y sobre todo: **un artista con nombre público y una ONG de reducción
   de daños al lado no puede tener una línea de ingreso que consista en tener la
   identidad de negocios chicos como rehén.** Un posteo enojado y se le queda
   pegado a iskvw para siempre.

→ **La señal era buena. Ver §2.7 para la versión con la polaridad invertida.**

### 5.2 · Expandirse a varias redes sociales — DESCARTADO

Es la forma clásica de sentirse productivo sin mover nada. Los clientes son
productoras y colegas: están en Instagram y WhatsApp. El descubrimiento ya está
resuelto (IG con antecedentes); **lo que falta es conversión, y eso es el sitio.**
Sumar redes suma descubrimiento que no se necesita.

Única excepción con lógica: **repostear renders que ya existen** en formato
video-nativo, porque el producto es movimiento. Pero eso es distribución
automatizada de material existente — la parte mecánica a automatizar — no una
estrategia de contenido.

### 5.3 · Del md de findfree.org

| Descartado | Razón |
|---|---|
| **Shotstack como desahogo de GPU** | Mal diagnóstico. El cuello de render no es capacidad en la nube: es que Blender/AE corren en **Windows** vía polling de issues. Una API de video no evalúa un árbol de Geometry Nodes |
| **Degoo / Internxt como remotos rclone** | El storage consumer de tier gratis es donde mueren los backups: cambios de ToS, borrado por inactividad, APIs inestables. Y 20 GB contra un corpus RD de 57 GB no es backup de nada |
| **Pollinations.AI en el pipeline de flyers** | Generación gratis, sin registro, con procedencia y licencia poco claras, alimentando **piezas que llegan a clientes** y material de RD. Si "reduciendo ano" no puede llegar al cliente, una imagen sin derechos comerciales claros tampoco |
| **Poliigon como fuente principal** | La sección gratuita es chica. Para trabajo comercial, quedarse con **CC0**: Kenney, 3Dassets.one |
| **Subdominios gratis (`us.kg`, `pp.ua`)** | Registros con historial de suspensiones (caso Freenom). No para la firma propia |

**Lo que sí vale de ese md, y es poco:** Tailscale (por la razón de §3, no por
comodidad), Cloudflare Pages, Freesound, y OpenRouter como un eslabón más de la
cadena de `research_lib.py` (~8 líneas, igual que watsonx).

**Error de hecho a corregir en ese md:** dice *"MAK trabajando autónomo (render
Blender por GPU en box casero)"*. **Falso.** El render corre en Windows —
`bridge_issue_render.py:33`, `BLENDER_EXE = C:\Program Files\Blender
Foundation\Blender 4.5\blender.exe`. La GPU de MAK hace `gemma3:4b` y
`nomic-embed-text`. Es el mismo tipo de error que la línea "el organismo vive
fuera del repo" que, según `RELEVO_MAK.md`, hizo trabajar horas contra la premisa
equivocada.

### 5.4 · n8n — CERRADO 2026-07-15

Ya estaba cerrado en `cultura/PLAN.md:76-84`. Se repite acá para que no vuelva:
el bloqueador fue el timeout de 300 s del task-runner de Code. **No reintentar.**

### 5.5 · El scanner como servicio para terceros — TRAMPA, no idea

Parece escalable y no lo es: cada usuario quiere un filtro distinto y se termina
dando soporte gratis a diez personas por dos lucas. Construirlo para uno y para
la enfermera. Si después alguien insiste en pagarlo, cobrarlo caro y como setup
único.

### 5.7 · Foro propio, y base de datos sobre API de red ajena — DESCARTADOS AMBOS

Ver §2.9.1 por el detalle. En una línea cada uno:

- **Foro propio:** arranque en frío. Sala vacía el día uno = credibilidad muerta.
- **Reddit (o cualquier plataforma) como backend:** sí lo permite —tier gratis con
  rate limits bajos, comercial ~US$0,24/1.000 llamadas, términos que restringen
  almacenamiento y redistribución— pero **ya cortó el acceso unilateralmente en
  2023**. Es cambiar arranque en frío por dependencia.
- **Lo que se hace en cambio:** formulario → issue → schema → git → sitio
  estático. Toda la maquinaria ya existe.

### 5.8 · Pedir acceso al CCTV de los venues — DESCARTADO (técnico y legal)

La idea era usar las cámaras de seguridad del venue —que ya están instaladas y
tienen infrarrojo— como insumo para reconstruir el 3D. **No sirve por dos vías
independientes, y cualquiera de las dos alcanza:**

**Técnica:** las cámaras fijas no dan paralaje, y el IR montado en la cámara rompe
el matching. Ver §2.9.2. No es "poca calidad": es insuficiente por construcción.

**Legal, y con fecha:** la **Ley 21.719 entra en plena vigencia el 1 de diciembre
de 2026**. Acceder al CCTV de un venue convierte al que accede en **encargado** de
tratamiento de sus datos personales: contrato escrito con cláusulas obligatorias,
medidas de seguridad, limitación de finalidad, notificación de incidentes. Imágenes
de público identificable son datos personales; lo biométrico es **categoría de
protección reforzada** con consentimiento explícito. Multas hasta 20.000 UTM.
→ Desde diciembre, ningún venue con asesoría dice que sí a la ligera. Sería un
servicio cuyo pedido central se vuelve una carga legal justo al lanzarlo.

**Lo bueno: la restricción empuja a la técnica que además es mejor.** Escanear el
venue **vacío** con equipo propio no contiene **ningún dato personal** — sin
consentimiento, sin contrato, sin exposición — y da mejor geometría. El camino que
cumple y el camino correcto son el mismo, lo cual es raro.
→ Y después de diciembre es **argumento de venta**: *escaneo sin gente, sin datos
personales*, contra cualquiera que intente la ruta CCTV.

### 5.6 · Otras que no

Agencia genérica de IA. Vender MAK.

---

## 6. Las tres reglas que ordenan todo lo anterior

1. **El producto pagado va primero; la comunidad y el fondo van detrás.** Al
   revés se termina siendo administrador no pago de una escena.
2. **Nada de RD sale de la caja, y RD nunca se mezcla con el archivo público.**
   Misma frontera que `PLAN_IBM_20D.md`.
3. **El indicador de éxito sigue siendo el del README:** cuánto necesita el repo
   al modelo fuerte —y ahora también al crédito, y al director— una vez que no
   están. Todo lo de acá arriba se juzga con esa regla.
4. **Descriptivo, nunca certificante.** Es la misma regla tres veces: la tilde no
   puede llegar mal al cliente, RD **describe** y no prescribe, y un rider
   **informa** y no certifica carga. Cuando un dato que uno publica puede lastimar
   a alguien si está mal, se cita la fuente certificada con fecha o se marca como
   no verificado. **Nunca se publica una medición propia como si fuera un
   certificado.**
5. **La sede no se construye, el intake sí.** Ni foro propio ni plataforma ajena:
   formulario → git → estático. Vale para la base de venues, para el directorio y
   para el archivo público. Lo único que se posee de verdad es el repo.
6. **La máquina lee y propone; el humano verifica y firma.** Lo que se vende es la
   firma, no la lectura — y los tres niveles de confianza existen para que el error
   quede **del lado correcto de la firma**. Consecuencia práctica: la presentación
   para clientes **no menciona IA ni MAK**, no por ocultar, sino porque al comprador
   le da igual y le siembra duda. Desarrollo en
   `POSICIONAMIENTO_Y_LEXICO.md`.
7. **Los datos abiertos, la firma paga.** Los datos abiertos no canibalizan el
   servicio: lo publicitan. Y el alcance es **Chile, las salas a las que se llega
   caminando** — la autoridad viene de haber estado en la sala, y eso no se scrapea.

---

## 7. Fuentes de los datos fechados de este archivo

Los datos con fecha caducan. Cuando se revisen, se revisan contra la fuente.

- Ley 21.817 y las tres agravantes nuevas:
  [El Mostrador, 2026-06-03](https://www.elmostrador.cl/unidad-de-investigacion/2026/06/03/modificaciones-a-la-ley-de-drogas-todos-estan-cagaditos-de-miedo/)
- Estado de la impugnación en el TC (13-04-2026, 37 diputados):
  [El Planteo](https://elplanteo.com/chile-aprobo-penas-mas-duras-para-el-cannabis-el-tribunal-constitucional-podria-anularlas/)
- Guía legal de drogas de la Biblioteca del Congreso:
  [BCN Ley Fácil](https://www.bcn.cl/api-leyfacil/servicio/ObtenerGuiaPublicadaHTML?uri=drogas)
- Precios y límites de la API de Reddit (2026):
  [SocialCrawl](https://www.socialcrawl.dev/blog/reddit-data-api-2026) ·
  [Prowlo](https://prowlo.com/blog/reddit-api-pricing)
- Precio del `.cl` en NIC Chile: ver `recursosiskvw.md` §3
- Ley 21.719 (protección de datos), plena vigencia **1-12-2026**, sanciones y
  categorías reforzadas:
  [Recording Law](https://www.recordinglaw.com/es/world-laws/world-data-privacy-laws/chile-data-privacy-laws/) ·
  [BCN / Gobierno Digital](https://wikiguias.digital.gob.cl/datos-personales/guia-practica-implementacion-nueva-ley-datos-personales)
- Apps de escaneo LiDAR en iPad (verificar términos y precios **antes de pagar**,
  cambian seguido): [3D Scanner App](https://apps.apple.com/us/app/3d-scanner-app/id1419913995) ·
  [Polycam](https://apps.apple.com/us/app/polycam-3d-scans-floor-plans/id1532482376) ·
  [KIRI Engine](https://www.kiriengine.app/features/lidar-scan)

---

*Memoria viva. Abierta el 2026-07-30, segunda pasada el 2026-07-30
(venues/riders, ReD, contexto Ley 21.817). Se poda, no se acumula.*
