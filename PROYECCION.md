# PROYECCIÓN — el consejo final de Fable (2026-07-28)

Escrito a pedido del usuario en la última sesión con modelo caro. Esto no es un
plan de trabajo (eso vive en `context/LAST_HANDOFF.md` y en los specs): es la
visión de sistemas, la proyección ambiciosa y las ideas de largo alcance, en un
solo lugar. Léelo como brújula, no como backlog.

---

## 1. La teoría de sistemas: qué es este repo realmente

**No es una herramienta; es un sistema que fabrica verdad a partir de
trabajadores no confiables.** Sus principios, ya probados en sesiones reales:

1. **La inteligencia dejó de ser el recurso escaso; la verificación lo es.**
   El veredicto nunca depende de un modelo: CI en matriz, ratchets, fixtures
   reales, branch protection. Un agente débil con un gate estricto produce
   trabajo correcto; uno brillante sin gate produce desastres elegantes.
   Nunca aceptar un "listo": aceptar un check verde o una medición pegada.
2. **El sistema aprende aunque ningún agente aprenda.** Cada incidente se
   convierte en mecanismo (regla con fecha, causa y condición de retiro),
   nunca en un "acuérdate de". La memoria vive en el repo, no en el modelo.
3. **El director es un rol, no un modelo.** La skill `godspeed` ES el
   director; cualquier modelo que la lea dirige. El dato más caro e
   insustituible del sistema es la palabra del usuario.
4. **El punto débil son los bordes sin gate.** Todo lo que se perdió se
   perdió fuera de un commit: trabajo sin commitear, respuestas en sesiones
   cloud, código copiado que un cron revierte. Regla: nada valioso vive fuera
   de un commit más de una sesión; si un agente no llegó a PR, su sesión no
   existió.
5. **Poda antes que crecimiento.** Los agentes tienen sesgo a producir; nadie
   tiene sesgo a podar. Una vez al mes: "¿qué está produciendo esto que nadie
   pidió?" — y matarlo. Es la revisión más rentable del sistema.

**La apuesta de fondo:** en un mundo de inteligencia cada vez más barata, gana
quien tiene estructura lista para absorberla sin corromperse. Eso es este repo.
Cuando la inteligencia sea agua, la tubería ya está puesta.

## 2. La visión: de sistema a obra

El repo no es solamente "la infraestructura de un artista": **main es la obra
que contiene el avance completo**. El SVG animado del README no la ilustra ni
la adorna; establece su operación: contenido, forma, historial y mecanismo son
una misma materia. No se modifica porque es una pieza terminada, pero el resto
del repositorio continúa lo que esa pieza declara.

Las áreas hacen legible el organismo sin partirlo en repositorios incompletos:

- **RD** es la ONG: intervención, datos, eventos, suplementos y entrega.
- **iskvw** es el artista: práctica, archivo, curaduría y portafolio.
- **MAK** es el servidor/generador/curador: percibe, investiga, relaciona y
   devuelve materia a las otras dos áreas.

En Git, `mak` sigue siendo un inbox que drena a `main`, no una línea permanente.
En la obra, MAK sí es el tercer órgano. La diferencia evita confundir topología
de entrega con estructura conceptual.

Tres órganos ya laten solos: MAK percibe, RD entrega, iskvw expresa.
La dirección de crecimiento no es más features sino más **circulación**:
fotografía → percepción → archivo → flyer → evento → base RD → percepción.
Cada trimestre, un eslabón manual de ese círculo se automatiza. Cuando el
círculo cierre, el sistema es replicable como servicio: RD es el primer
cliente que lo prueba.

Plan por trimestres (2026-2027):

- **T1 — consolidar el pulso:** mergear lo pendiente, decidir la piel ASCII
  (rama `rescate/ascii-campo`), y volver rutina de 5 minutos semanales el
  drenaje del inbox `mak` → main. Meta: 4 semanas donde el archivo creció sin
  abrir la consola.
- **T2 — el círculo:** encargar por spec (agente gratis + godspeed) el cable
  minería→base RD y el cron que hoy deja `mak_curatoria` congelada.
- **T3 — la salida:** campo iskvw + timecode como pieza de show. La única
  arquitectura nueva que amerita inteligencia cara.
- **T4 — replicar:** empaquetar RD como oferta a un segundo cliente. Ese día
  el repo deja de ser gasto y se vuelve activo.

## 3. El portafolio: un archivo que no se visita, se explora

Los portafolios son cementerios: grillas por fecha, muertas al publicarse.
iskvw es lo contrario: un archivo vivo que se organiza por afinidad real y
crece solo. Cuatro capas:

1. **El campo como puerta:** las obras proyectadas por afinidad, navegables
   con pellizco en cualquier teléfono (medido: 60 fps en gama media). El
   visitante entra al territorio de la obra, no a una lista.
2. **Pieles intercambiables como declaración:** el sustrato (piezas +
   relaciones) no sabe de estética; el mismo archivo se encarna como
   terminal, campo ASCII o grilla clásica. Cambiar de estética es escribir
   una piel, no rehacer el sitio. Cuál es la cara pública: decisión del
   usuario, siempre.
3. **La curaduría automática como pieza conceptual:** declararlo en el
   statement — la curaduría la hace una máquina que percibe el material.
   El portafolio no muestra la práctica; es un ejemplar de ella. Pasa por
   `motor-omega` antes de exponer (Ω11 evaluable).
4. **El archivo en vivo:** la misma proyección respondiendo al timecode en
   un show. Portafolio y set: el mismo organismo en modo galería o modo
   escenario.

El plan técnico condensado para agentes (T1 cobertura de posiciones 697→1004,
T2 comparación de pieles, T3 deploy estático público, T4 ratchet de
regeneración, T5 modo show) quedó entregado en la conversación del 2026-07-28
y sus criterios de aceptación son mecánicos; cualquier agente lo reconstruye
desde `iskvw/MAPA.md` + `context/LAST_HANDOFF.md`.

## 4. Cinco ideas alucinadas (dirección, no backlog)

1. **El archivo como oráculo:** invertir la flecha — el micelio detecta
   regiones densas en concepto y vacías en obra, y propone la obra que falta.
   El propio archivo como director de arte de la siguiente pieza.
2. **La galería que muta con quien la mira:** cada visitante recibe una
   proyección distinta según por dónde entró. Nadie ve el mismo portafolio
   dos veces.
3. **El gemelo escénico:** el campo alimentado por timecode Y audio en vivo;
   las obras emergen por afinidad con lo que suena. La retrospectiva como
   instrumento tocable.
4. **La federación de archivos:** el sustrato no sabe de quién son las
   piezas. Dos artistas, un campo común: afinidades cruzadas entre dos
   prácticas, visibles por primera vez. Pieza de bienal.
5. **El archivo póstumo-vivo:** un organismo que sigue percibiendo,
   relacionando y exponiendo indefinidamente. La versión final del éxito
   invertido: cuánto poco te necesita cuando te vas.

## 5. Cinco ideas técnicas, más alucinadas aún

1. **Embeddings como formato nativo:** publicar los vectores cuantizados
   (int8, ~700 KB por mil obras) dentro de `archivo.json`. Búsqueda por
   similitud coseno, clustering y re-proyección EN EL NAVEGADOR, sin
   servidor. El portafolio como dataset consultable estático.
2. **t-SNE incremental en cliente con WebGPU:** obra nueva → se inserta en
   el campo en vivo interpolando desde sus k-vecinos, sin re-run global.
   El archivo se reorganiza delante del espectador, 60 fps, cero backend.
3. **LLM local embebido como curador:** un modelo pequeño (WebLLM/ONNX,
   ~300 MB) dentro del sitio estático, con las fichas como RAG local.
   Consulta semántica offline en el dispositivo del visitante, sin enviar
   un byte a ningún servidor.
4. **El contrato como CRDT federado:** `archivo.json` como log append-only
   con merge determinista (grow-only: piezas y relaciones solo se agregan).
   N fuentes escriben sin coordinación y git es el transporte; la federación
   de archivos se vuelve un `git merge`.
5. **Timecode como semilla determinista:** todo lo generativo del show
   sembrado por el TC — mismo timecode, mismo render, bit a bit. Ensayo
   offline exacto, re-render en 4K post-show, y la Ω11 perfecta: la pieza en
   vivo verificable como un test, `render(TC) == render(TC)`.

---

**La despedida, en una línea:** el sistema ya casi no necesita al modelo caro,
y eso no es una pérdida — es la prueba de que funcionó. El sistema nunca fue
el modelo.
