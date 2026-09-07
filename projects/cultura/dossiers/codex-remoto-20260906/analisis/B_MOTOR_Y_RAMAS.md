# Análisis B — Un motor, tres ramas: cultural, comunitaria y privada

Fecha: 2026-09-06.

## 1. ARTE–VISIÓN–COMPUTACIÓN–ORDEN, como mecanismo y no como lema

El encargo pedía convertir la fórmula en algo comprensible con un ejemplo real
del archivo. Aquí está, con datos que se pueden abrir en la máquina ahora mismo.

### El ejemplo: una pieza del archivo

Tomo la pieza `00dfbf29763b-17963390141716156` de `~/iskvw/datos/campo.json`,
que existe tal cual se transcribe:

```json
{"id": "00dfbf29763b-17963390141716156",
 "x": -0.8773, "y": -0.1102,
 "colores": ["naranja", "verde", "azul"],
 "estilo": "Surrealismo, Psicodelia",
 "tipo": "obra",
 "percibido": "Una ilustración digital de una mujer en una bañera con elementos surrealistas y psicodélicos.",
 "archivo": "posts/17963390141716156.mp4",
 "tilde": {"marcas": 3, "por_cien": 3.23, "cuales": {"ó": 1, "ñ": 1, "é": 1}}}
```

### Las seis estaciones

| Estación | Qué es aquí, concretamente |
|---|---|
| **Entrada** | `posts/17963390141716156.mp4`: un archivo real de la carpeta `posts`. De 697 candidatos, **478 fueron filtrados** y 219 quedaron. El filtro está declarado en `campo.json.meta.filtro`, no oculto. |
| **Criterio** | La pregunta que se le hace al archivo. Aquí fue: *¿qué colores, qué estilo y qué se ve?* Podría ser otra —qué se repite, qué está sin fechar, qué no se mostró nunca— y el orden resultante sería otro. **Ese es el punto de "dimensiones" en plural.** |
| **Transformación** | ARTE se convierte en VISIÓN: una lectura de máquina produce `colores`, `estilo` y `percibido`. 219 de 219 piezas la tienen. Y una lectura del texto produce `tilde`: cuántas tildes hay y cuáles. Es una medida deliberadamente menor y no universal — mide algo del castellano escrito de este archivo en particular. |
| **Vista** | VISIÓN se convierte en ORDEN: `x = -0.8773`, `y = -0.1102`. Un punto en un plano donde lo parecido queda cerca. Y el sistema **declara cuánto miente**: `vecindad_conservada = 0.4855`. Poco menos de la mitad de la vecindad original sobrevive a la proyección. Un mapa que publica su propia distorsión. |
| **Decisión** | El artista abre `curaduria.json` y escribe `mostrar: false`, o cambia el `titulo` a su voz con sus tildes, o le pone una `serie`, o una `nota`. Lo que no escribe, no cambia nada. **Hoy hay 0 decisiones registradas.** El instrumento está afinado y nadie lo ha tocado. |
| **Formato final** | Aquí se acaba. La única salida es un `.json` que el navegador descarga. **No hay portafolio.** Esta casilla vacía es el proyecto. |

### La frase corta que resume el motor

> El archivo entra como materia, la máquina lo mira y propone un orden, el orden
> declara cuánto pierde, la persona corrige, y del acuerdo sale una forma pública.

**Y la parte incómoda que hay que decir:** el orden automático perfecto no existe
y este sistema no finge lo contrario — `0.4855` es la confesión escrita en el
propio archivo de datos. Un proyecto que promete "ordenar automáticamente un
archivo" está prometiendo algo que su propia métrica desmiente.

### Una elección de sentido que la documentación no resuelve

Hay una decisión que es del artista y no mía. La capa `tilde` cuenta tildes por
pieza. En `~/iskvw/datos/archivo.json` hay una obra llamada *"VOLÁ · lo visible y
lo invisible"* cuya nota dice: *"El nombre lleva su propia tilde — volá / vola
decide quién vuela."* La tilde no es metadato ahí: es la obra.

Entonces, ¿qué es la capa `tilde` en las tres postulaciones?

- **Opción 1 — es una métrica.** Un indicador de densidad diacrítica, útil para
  agrupar. Sobria, defendible, y desperdicia lo que ya está escrito.
- **Opción 2 — es una obra dentro del instrumento.** La marca que distingue
  quién escribe de quién transcribe, en un archivo donde una máquina describe lo
  que ve. Más ambiciosa, y exige sostenerla en el texto.
- **Opción 3 — no se nombra** en las postulaciones y se conserva como capa interna.

Los expedientes de este paquete usan la **opción 1** por defecto, porque es la
que no necesita defensa. La opción 2 está preparada y anotada en
`RESOLUCIONES_EXTERNAS.md` ítem R-6: es un cambio de dos párrafos si el artista
la elige. La autoría del sentido es suya.

## 2. Qué se reutiliza, qué se adapta, qué se financia

| Componente | Estado hoy | Ama Amoedo | Creación | Formativas |
|---|---|---|---|---|
| Corpus propio (2.034 piezas) | existe | se ordena | se usa como demostración | se usa como ejemplo |
| Percepción visual (219 obras) | existe | se reutiliza | se reutiliza | se reutiliza |
| Proyección con métrica de pérdida | existe | se reutiliza | se reutiliza | **se enseña** |
| Contrato de curaduría reversible | existe, 0 usos | **se ejerce** | se ejerce en público | se ejerce con terceros |
| Normalización del vocabulario visual | pendiente | **se financia** | — | — |
| Exportación a portafolio | **no existe** | **se financia** | — | — |
| Superficie pública / instalada | **no existe** | — | **se financia** | — |
| Mediación y accesibilidad | no existe | — | **se financia** | se reutiliza el protocolo |
| Programa formativo y guía | no existe | — | — | **se financia** |
| Modo multiusuario / servicio | no existe | no se promete | no se promete | no se promete |

**Regla que sostiene la tabla:** cada casilla "se financia" aparece **una sola
vez** en toda la fila de convocatorias. Nada se paga dos veces.

## 3. Ramas posteriores, sin inventar mercado

El encargo advierte, con razón, que un nombre de producto no demuestra un
mercado. Lo que sigue son **hipótesis con su validación pendiente escrita al
lado**, no un plan de negocios.

### Rama cultural (la financiada)
Instrumento libre para que un artista ordene su archivo y produzca portafolio.
*Validación pendiente:* que alguien distinto del autor lo use y le sirva. Los
talleres de Formativas son, literalmente, ese experimento.

### Rama comunitaria
Colectivos, archivos de barrio, agrupaciones que tienen material acumulado y
ninguna forma de recorrerlo. *Hipótesis de cliente:* organizaciones culturales
con archivo y sin catalogador. *Validación pendiente:* que el problema exista
fuera de la cabeza del artista. **Esto no se declara como diagnóstico del sector
en ninguna postulación** — se formula como necesidad a validar y desde la
experiencia propia, que es lo que las bases admiten.

### Rama privada / institucional (PUPILA y afines)
*Hipótesis de cliente:* instituciones con fondos documentales, editoriales,
estudios de diseño, licitaciones de patrimonio digital.
*Validación pendiente, y es mucha:* que exista presupuesto asignado a este
problema, que se prefiera esta forma de trabajar a un catalogador tradicional, y
que alguien pague por reversibilidad y procedencia explícita.
**Estado real:** PUPILA y XANAX **no existen en MAK**. Se buscaron y no están
(ver `evidencia/MAPA_DE_FUNCIONES.md` §1). Todo lo que se sabe de ellos es cita
del traspaso. Por eso ninguna postulación los nombra como capacidad, y este
documento no les atribuye ninguna.

**Regla de sostenibilidad que se respeta en los tres expedientes:** la rama
privada aparece únicamente como continuidad posible en la sección de
sostenibilidad. Nunca como el objetivo financiado. El fondo cultural paga la
rama cultural.

## 4. Servicios que podrían sostener el instrumento después

Ordenados de menos a más especulativos, con lo que cada uno exige:

1. **Talleres pagados** tras los gratuitos del laboratorio. Exige: que el
   laboratorio gratuito demuestre demanda.
2. **Preparación de portafolios por encargo** para artistas y postulantes a
   fondos. Exige: que la exportación exista y produzca algo presentable.
3. **Ordenamiento de archivos institucionales** por proyecto. Exige: modo
   multiusuario y control de acceso, ninguno de los cuales existe hoy.
4. **Licenciamiento** de una versión privada. Exige todo lo anterior más una
   decisión de licencia.

## 5. Licencias y derechos, desde los textos verificados

- **Fondart, las tres líneas.** Las bases no reclaman la propiedad intelectual de
  los resultados. Obligan a cumplir la ley 17.336, a obtener autorización previa
  cuando se usen obras de terceros, y a acompañar esas autorizaciones en el
  informe final si aparecen después de firmar convenio. También exigen adjuntar
  un medio de verificación al informe final, que *"quedará en el expediente del
  proyecto, sin que sea devuelto"* y que el Ministerio **no podrá usar para otro
  fin que la verificación** salvo autorización expresa. Esa cláusula es favorable
  y conviene conocerla: entregar el verificador no cede derechos.
- **Consecuencia práctica para IRIS:** el corpus es del artista, luego no hay que
  pedir autorización a nadie. Si en un taller un participante trae su archivo, el
  archivo **no** entra al proyecto — así está escrito en los tres expedientes,
  y así se evita generar una obligación de autorización que nadie quiere.
- **Ama Amoedo.** Las bases no mencionan cesión de derechos. Obligan a firmar un
  acuerdo previo al pago y a enviar informes de uso durante 12 meses. Excluyen
  fines comerciales — lo que confirma que **la rama privada no puede aparecer
  como objetivo** de esa postulación.
- **Licencia del instrumento:** las bases no la fijan. Es una decisión libre del
  artista y está en `RESOLUCIONES_EXTERNAS.md` ítem R-7. Lo único que este
  paquete afirma es lo que se puede sostener: que el resultado quede disponible
  para uso de artistas, sin comprometer una licencia específica que nadie ha
  elegido todavía.

## 6. Qué queda después del financiamiento

Respondido en los términos que pedía el encargo:

- **Qué queda funcionando:** un instrumento que ordena un archivo propio, muestra
  cuánto pierde al ordenarlo, admite corrección reversible y produce un
  portafolio. Corriendo, con datos reales, en la máquina de su autor.
- **Quién lo usa:** primero el artista, todas las semanas, porque resuelve un
  problema que tiene. Después, los participantes del laboratorio.
- **Qué problema concreto resuelve:** un archivo grande —2.034 piezas— no se
  recorre con una lista. La lista te deja encontrar lo que ya sabes que buscas.
  El instrumento sirve para lo otro: ver qué hay, qué se repite, qué quedó suelto.
- **Cómo se mantiene:** el costo real de continuidad es hosting y dominio, no un
  equipo. El resto es el trabajo que el artista ya hace con su propio archivo. Si
  las ramas de servicio no prosperan, el instrumento sigue funcionando localmente
  igual que hoy, porque hoy funciona sin financiamiento alguno.
