# Estado del repo

Ultima actualizacion: **2026-08-01, 03:55**.

Este archivo se lee en dos minutos o no sirve. Llego a 1.666 lineas apiladas y
nadie lo leia -- ni los agentes que lo editaban. La historia esta en
`docs/handoffs/archive/HANDOFF_hasta_20260801.md`; aca queda solo lo que hoy es
cierto.

**Como se mantiene:** se REESCRIBE, no se le agrega al final. Un hallazgo va a
su seccion y reemplaza lo que decia antes. Si algo dejo de ser cierto, se borra
-- una frase que describe un estado que ya no existe se lee como medicion, y esa
es la trampa que costo mas caro (ver "Lo que este repo aprendio", regla 1).

---

## 1. Lo que espera una decision TUYA

Ninguna la puede tomar un agente. Estan ordenadas por lo que cuesta no tomarla.

| Que | El numero que hace falta para decidir |
|---|---|
| **El reloj de IBM** | ~US$36/dia por TENER el plan. Todo el trabajo de dos dias costo US$0,56. Bajar a Lite se hace desde la consola, no por API. |
| ~~Degradar las ocurrencias encoladas~~ | **HECHO 2026-08-01 03:22.** 2.656 tareas de `ig` pasaron a `propuesta`; queda 1 pendiente real. Respaldo en `~/plataforma/material.jsonl.bak-20260801`. Lo despachado (155) no se toco. |
| **Consolidar las 1.354 fichas de watsonx** | `tipo_obra` 67%->100%, `materiales` 66%->99,6%. Pero **4.595 valores quedarian mas cortos** que los actuales. `tools/consolidar_fichas.py --aplicar`. |
| ~~Encender `nodo_glifo`~~ | **ENCENDIDA** en el PR #433: el nodo deja de ser circulo. Medido en la banda densa: gradientes 217->0, arcos 434->0. Apagarla es una llave en `datos/tablero.json`. |
| **Si los ensayos de MAK se publican en iskvw.cl** | Lo dejaste para debatir -- y **ya estan publicados** desde el 2026-07-31: el sustrato lleva 16 conceptos y 1 informe. La maquina tomo la decision por vos. |
| **La geometria del campo** | Dijiste que la pediste "mil veces" y **no esta escrita en ningun lado**: se busco en los 5 documentos, todo el repo, la historia de git en todas las ramas, `.remember/` y los issues. Se perdio en conversacion. Lo unico escrito es `iskvw/piel/campo/ASCII_REFERENCIA.md`. |
| **`patch_efectos` y `venue3d`** | Construidos y apagados en `datos/tablero.json`. Encenderlos es del artista. |
| **La direccion de iskvw como obra** | `iskvw/MAPA.md` la declara tuya y sigue vacia. |

---

## 2. Muros nombrados

Un muro nombrado es entrega valida. Estos no los resuelve mas trabajo.

1. **El micelio no llega al sitio.** El runner de CI no ve la caja MAK
   (`Connection refused`), asi que `gen_archivo_iskvw.py --fuente todo` omite sus
   vinculos y lo dice en el log. Las 479 piezas publicadas salen del material del
   repo.
2. **La rama `mak` no drena.** 33 utilidades autogeneradas en `mak`, **0 en
   main**. Su unica salida deberia ser un PR a main y ese PR nunca se abrio.
   **Correccion del 2026-08-01:** este muro decia "main las borro en #406", y
   es FALSO. `git show 7310956 --name-status -- cultura/mak_plataforma/utilidades/`
   no devuelve un solo archivo: #406 no toco esa carpeta. Las utilidades nunca
   estuvieron en main -- no fueron rechazadas, no llegaron. Aparecen bajo
   `--diff-filter=D` solo por como el squash compara contra su padre, y contar
   ese filtro sin mirar el commit es lo que fabrico la frase.
   Importa porque cambia la decision entera: "main las evaluo y las tiro"
   manda a NO drenar; "nadie las miro nunca" manda a que alguien las abra. Lo
   escribio una sesion de este mismo modelo cuatro horas antes (#432), y la
   sesion siguiente la cito como medicion para justificar automatizar el
   drenaje. Se cayo porque el usuario pregunto "y si es slop?", no porque
   alguien la verificara.
3. ~~El nodo-glifo no se puede medir.~~ **RESUELTO 2026-08-01.** Eran dos cosas
   distintas y una era un defecto real: el glifo se elegia sobre la posicion ya
   temblada por `Math.random()`, asi que el azar decidia el conteo. Corregido, el
   campo se lee en la posicion estable del nodo. Lo que quedaba -- que la cuenta
   se mueva entre cuadros -- es el patron generativo haciendo lo suyo, y el
   medidor ahora fija el PEOR cuadro y publica el rango en vez de exigir que
   todos sean iguales.
4. **La triangulacion de RD produce cero fuentes primarias.** 70 informes vivos,
   46 dicen NO SE ENCONTRO y **0 de 70** tienen `verificacion.fuentes_primarias`
   con algo adentro.

---

## 3. Que corre hoy, medido

**El sitio.** `iskvw.cl` publica **479 piezas y 269 vinculos**. El workflow
GENERA `archivo.json` con `gen_archivo_iskvw.py --fuente todo` antes de subir y
recien despues verifica que exista; no es una copia congelada. La piel degrada a
`campo.json` solo si eso falla, y no falla desde el 2026-07-31.

**La percepcion.** 3.138 fichas: 1.737 rd, 1.401 ig. La pasada de watsonx sobre
las ig termino (1.401/1.401, 0 errores) y esta en
`~/curatoria/pasadas/v4_watsonx_20260801/` en la caja, **sin consolidar**.

**La cola de MAK.** 2.812 tareas: 2.656 `propuesta`, 155 despachadas, 1
pendiente. Lo que nace de `oportunidad_codigo` y `linea_investigacion` nace como
`propuesta` y no se despacha; solo la triangulacion de RD sigue siendo trabajo.
El corte rige en la caja desde que sincronice main.

**La busqueda.** Funciona con `TAVILY_API_KEY` puesta en
`~/n8n-local/research.env` (permisos 600). Los cuatro motores generales de
SearXNG siguen tapados de forma intermitente; el sistema lo detecta y pausa en
vez de escribir un informe de memoria.

**El debate adversarial.** Tres modelos distintos, uno por papel: proponente
`mistral-medium-2505`, refutador `llama-3-3-70b`, juez `granite-4-h-small`. El
informe declara en su primera linea si hubo debate o no.

---

## 4. Lo que este repo aprendio, y cuesta caro olvidar

Cada una salio de un incidente medido. Estan en orden de cuantas veces volvio a
aparecer el mismo defecto.

1. **Una lista, un default, un comentario o un orden escritos a mano dejan de
   coincidir con la realidad, descartan en silencio lo unico que funcionaba, y
   el error culpa a otra cosa.** Aparecio siete veces en dos dias: la tupla de
   proveedores de `refutar.py`, el `_CODER_CHAIN_MAP` de codex, `CLAVES_VISION`
   tragandose `_motor`, el comentario del banco de vision diciendo 1024 donde
   produccion usa 1280, el requisito "nada" de `tapiz`, los tres cubos de
   `consolidar_fichas` cubriendo 1.879 de 17.602 decisiones, y la frase de
   `iskvw/MAPA.md` que caduco a las cuatro horas y media de escribirse.
   **Antes de depurar, preguntarse si el bug tiene esta forma.**

2. **NO DEPURES: CONTA.** Agrupar los fallos por su mensaje literal antes de
   abrir nada. Resolvio en un paso lo que llevaba una hora, tres veces.

3. **Un grep vacio no es evidencia de ausencia**, es evidencia de que la
   consulta fue estrecha. El 2026-08-01 se concluyo que nadie conectaba los
   conceptos de un ensayo con el motor de iconos, cuando `tools/iconos_conjunto.py`
   existe, tiene tests, produjo 16 iconos y **esta registrado en
   `CAPACIDADES.md`** -- un archivo editado cinco veces esa noche sin abrirlo.
   Antes de construir: leer el registro VIVO de `CAPACIDADES.md` y la tabla de
   `MAPA.md`, que estan generados y no se pudren.

4. **Contar es el metodo correcto para ENCONTRAR un defecto y el equivocado para
   declararlo resuelto.** Se midio `bing: 10 resultados` y se lo dio por bueno;
   mirando los resultados, eran basura no relacionada. Un conteo dice cuantos;
   solo mirar dice cuales.

5. **Nunca rellenar una ausencia con un valor plausible.** Un `or "ollama"`
   destruye el campo que existe para medir quien respondio.

6. **Una falsa alarma es tan grave como un descarte callado.** Manda a perseguir
   un fantasma y quema la credibilidad de la proxima alarma verdadera.

7. **Los comentarios de un archivo son su bitacora de incidentes: se leen ANTES
   de editarlo.**

8. **Compilar y `pyflakes` no son evidencia.** Corrida real y conteo comparado
   contra los numeros de antes. `pyflakes` si atrapa lo que `compileall` no ve
   (un `%` que quedo ligado al string equivocado).

9. **Inventar que hacer esta bien; decidirlo sin formato no** (palabras del
   usuario). Las tres preguntas que convierten una ocurrencia en tarea estan en
   `flujo.micelio.evaluar_propuesta`: quien lo va a usar, donde se busco que no
   exista ya, y como se sabe que salio bien.

10. **Lo que el usuario responde se escribe en la misma sesion o se pierde.** La
    geometria del campo se perdio asi.

---

## 5. El circuito micelio, para usarlo

Tu flujo: le pedis una semilla a un modelo web, la depositas, y si hay bug el
micelio te entrega un hongo; le pasas el hongo al modelo, que responde con un
nutriente; si el nutriente lo arregla, se crea un fruto.

```bash
py -m flujo micelio formato              # el texto que le pegas al modelo web
py -m flujo micelio validar sobre.json   # dice que le falta, en castellano
py -m flujo micelio depositar sobre.json --aplicar
py -m flujo micelio cosechar sobre.json  # -> fruto si crecio, hongo si no
```

El hongo lleva que criterios se pusieron rojos con su mensaje literal, cuales
pasaron, el pedido original y **el contenido real de los archivos** que el
criterio nombra. Sale con codigo 1 para que un script lo use como compuerta.

Probado de punta a punta el 2026-08-01: vuelta 1 ROJO (faltaba `normalizar` y la
prueba), vuelta 2 con un nutriente arreglo dos de tres en 71 segundos.
**Muro:** `codex generar` entrega UN archivo, asi que un criterio que pide un
segundo archivo en una ruta concreta no lo puede cumplir.

---

## 5b. El mes de conversacion, medido y sin leer

Las decisiones que se perdieron estan en las transcripciones y en ningun archivo
del repo. Medido el 2026-08-01 sobre `~/.claude/projects/c--IA-flujo/`:

```txt
122 sesiones, 2026-07-01 a 2026-08-01, 316,7 MB de JSONL
  turnos del usuario   4.264   3,0 MB   lo que decidio y se perdio
  turnos del asistente 9.844   4,6 MB   lo que prometio y dio por hecho
  lineas de error      3.005   0,2 MB   los fallos, agrupables por mensaje
  tool_result                 39,2 MB   el repo pegado de vuelta: no aporta
```

Se intento leerlo con watsonx y el usuario lo cancelo. **Lo que quedo aprendido
es el diseno correcto**, por si se retoma: no hay que pedirle las citas al
modelo -- las parafrasea, y una decision parafraseada deja de ser la decision,
que es justo el problema que se quiere arreglar. Hay que pedirle que diga QUE
TURNOS contienen una decision, y sacar la cita de la transcripcion por indice.
Textual por construccion, sin nada que verificar despues.

## 6. Para un agente que recien llega

Leer, en este orden: `CLAUDE.md`, este archivo, `MAPA.md`. Si vas a tocar iskvw,
tambien `iskvw/MAPA.md`. Si vas a construir una herramienta, **primero** el
registro VIVO de `CAPACIDADES.md`: 4 de las 45 entradas tienen como unico
consumidor su propio test, y agregar la 46a sin mirar es como se llego a eso.

El veredicto de un PR es su matriz de CI, nunca el pytest local.
