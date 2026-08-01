# Estado del repo

Ultima actualizacion: **2026-08-01, 10:31**.

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
| **Consolidar las 1.354 fichas de watsonx** | `tipo_obra` 67%->100%, `materiales` 66%->99,6%. Pero **4.595 valores quedarian mas cortos** que los actuales. `tools/consolidar_fichas.py --aplicar`. |
| **Si los ensayos de MAK se publican en iskvw.cl** | Lo dejaste para debatir -- y **ya estan publicados** desde el 2026-07-31: el sustrato lleva 16 conceptos y 1 informe. La maquina tomo la decision por vos. |
| **La geometria del campo** | Dijiste que la pediste "mil veces" y **no esta escrita en ningun lado**: se busco en los 5 documentos, todo el repo, la historia de git en todas las ramas, `.remember/` y los issues. Se perdio en conversacion. Lo unico escrito es `iskvw/piel/campo/ASCII_REFERENCIA.md`. |
| **La direccion de iskvw como obra** | `iskvw/MAPA.md` la declara tuya y sigue vacia. |

---

## 2. Muros nombrados

Un muro nombrado es entrega valida. Estos no los resuelve mas trabajo.

1. **El micelio no llegaba al sitio -- causa corregida y mecanismo construido
   (2026-08-01).** Este archivo mezclaba dos hechos independientes bajo "el
   runner de CI no ve la caja". Medido: el runner self-hosted `mak` SI esta
   offline (`gh api .../actions/runners`, muerto a mitad de un retry el
   2026-07-24 14:03:59Z, sin proceso ni unidad systemd) -- pero
   `publicar_iskvw.yml` corre en `ubuntu-latest`, y el propio workflow ya
   declaraba en su comentario que no alcanzar la caja es ESPERADO, no una
   caida: una maquina en la nube nunca iba a llegar a una IP de LAN privada,
   con ese runner vivo o muerto. Medido sobre lo publicado ese dia: 269
   vinculos, **0 de clase `semantico`** -- los 227 `obra` que si aparecen
   salen de `campo.json` + `obras.json` (219 + 8, commiteados a mano), nunca
   del micelio en vivo. Construido: `cultura/mak_plataforma/entregar_micelio.py`
   corre EN la caja, lee el micelio local y abre PR contra `mak` con
   `iskvw/datos/micelio.json` (mismo patron que `entregar.py`, hard-falla sin
   escribir nada si el micelio no responde o da 0 vinculos);
   `gen_archivo_iskvw.py --fuente todo` cae a ese snapshot cuando el micelio en
   vivo no responde. Probado real, no en seco: **PR #440, 1530 piezas, 4921
   vinculos, los 4921 de clase `semantico`**. Pendiente de un humano: #440
   (contra `mak`) y el PR de este mecanismo (contra `main`) siguen sin
   mergear -- el sitio publicado sigue en 269 hasta que ambos entren y
   `publicar_iskvw.yml` corra de nuevo.
2. **La rama `mak` no drena.** 33 utilidades autogeneradas en `mak`, **0 en
   main**. Su unica salida deberia ser un PR a main y ese PR nunca se abrio.
   **Correccion medida el 2026-08-01:** este muro decia "main las borro en
   #406" y es FALSO. `git show 7310956 --name-status -- cultura/mak_plataforma/utilidades/`
   no devuelve un solo archivo: #406 no toco esa carpeta. Nunca estuvieron en
   main -- no fueron rechazadas, no llegaron. Aparecen bajo `--diff-filter=D`
   solo por como el squash compara contra su padre, y contar ese filtro sin
   abrir el commit es lo que fabrico la frase. Importa porque cambia la
   decision entera: "main las evaluo y las tiro" manda a NO drenar; "nadie las
   miro nunca" manda a que alguien las abra. Leidas las 33 ese dia: 9 invocan
   subprocess (son ordenes operativas, no utilidades), ~10 son de sandbox y
   pesan menos de 1 KB, y 6 sirven de verdad -- `osc_encode.py` la mejor,
   porque todo Resolume/Chataigne/xio habla OSC.


3. **La triangulacion de RD produce cero fuentes primarias.** 70 informes vivos,
   46 dicen NO SE ENCONTRO y **0 de 70** tienen `verificacion.fuentes_primarias`
   con algo adentro.

---

## 3. Que corre hoy, medido

**El sitio.** `iskvw.cl` publica **479 piezas y 269 vinculos**. El workflow
GENERA `archivo.json` con `gen_archivo_iskvw.py --fuente todo` antes de subir y
recien despues verifica que exista; no es una copia congelada. La piel degrada a
`campo.json` solo si eso falla, y no falla desde el 2026-07-31.

**El campo genera durante la navegacion, y tiene bloom laser (2026-08-01).**
Dos pedidos del artista sobre el mismo archivo. (1) El glifo por-nodo
(`nodo_glifo`, encendido desde #433) tenia su densidad topada al 55% mientras
se navegaba: el piso lo ponia `E.despliegue`, que solo sube quieto 5s (2% por
cuadro) y cae en ~8 cuadros al primer gesto. Sacado el piso: el glifo usa su
rango completo SIEMPRE; quedarse quieto sigue revelando algo distinto (la
ficha y el tamano de la forma resuelta), nunca la densidad del glifo. De paso,
`ctx.font` quedaba sin inicializar para un visitante que solo navega y nunca
resuelve una obra (`F` arranca en 0 exacto): corregido. (2) Vinculos y glifos
ahora se pintan con doble trazo -- halo ancho y tenue debajo, nucleo fino y
brillante encima -- en `globalCompositeOperation='lighter'`, para que los
cruces SUMEN luz en vez de taparse. Sin llave nueva en el tablero: va directo,
como los vinculos-siempre-visibles del 2026-07-30, porque es un pedido
explicito del artista y no una propuesta a decidir. Medido:
`grep -cE "shadowBlur|bloom|glow|globalCompositeOperation" iskvw/piel/campo/index.html`
0->7 (4 ocurrencias de codigo real); peor caso de segmentos por frame
(`archivo.json`, 269 vinculos) 107->214 -- exactamente el doble, cada vinculo
sigue siendo el mismo, 5,6x bajo el techo de 1200. `tests/test_iskvw_piel_medir.py`
re-pineado con los numeros reales; `tools/iskvw_piel_smoke.mjs` extendido para
que `globalCompositeOperation` y `lineWidth` dejen firma en la traza (antes el
banco era ciego al modo de mezcla, igual que antes lo fue al radio y a la
fuente). Suite completa + smoke + medir en verde. PR: rama
`laser-bloom-campo-genera`.

**La percepcion.** 3.138 fichas: 1.737 rd, 1.401 ig. La pasada de watsonx sobre
las ig termino (1.401/1.401, 0 errores) y esta en
`~/curatoria/pasadas/v4_watsonx_20260801/` en la caja, **sin consolidar**.

**La cola de MAK.** 2.812 tareas y **ninguna pendiente**: 2.656 en `propuesta` y 156 en `despachada`. Medido el 2026-08-01 leyendo
`material.jsonl` en la caja y confirmando contra `material.pop_pendiente`,
que filtra por `estado == "pendiente"` -- o sea, la cola entera esta
inerte y `atender` devuelve None en cada tick.

Esto corrige DOS frases que este archivo traia como pendientes y ya no lo
eran. La primera pedia una decision tuya: "degradar las ocurrencias
encoladas, `python3 material.py --degradar-ocurrencias --aplicar`". Ya
esta aplicada. La segunda decia que "solo la triangulacion de RD (116)
sigue siendo trabajo", y **esas 116 tambien estan en `propuesta`**: la
degradacion se llevo por delante el unico trabajo real que quedaba, junto
con las ocurrencias que apuntaba a frenar.

La consecuencia se ve en el log: `atender` no tiene de donde sacar nada,
asi que el organismo corre su modo autonomo -- `multiplicar` sobre el
backlog -- que es lo que produce un informe cada 30 minutos. Reactivar las
116 de RD es cambiar un estado, no borrar nada.

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

### El prompt, listo para correr

No se le piden citas al modelo: se le piden NUMEROS de turno. La cita sale de la
transcripcion por indice, textual por construccion.

MAPA (`ibm/granite-3-8b-instruct`, 23 llamadas de ~95k tokens):

```txt
SISTEMA
Sos un clasificador de turnos de conversacion. Recibis turnos NUMERADOS de una
persona hablando con asistentes de IA sobre su repositorio. Devolves SOLO un
objeto JSON, sin explicaciones ni markdown.

USUARIO
Clasifica cada turno. NO copies ni cites el texto: ya lo tengo. Devolve el
NUMERO del turno y una etiqueta.

{"marcados": [{"n": 1234, "tipo": "decision|orden|correccion|queja",
               "sobre": "de que trata, MAXIMO 6 palabras"}]}

REGLAS:
- `decision`: elige entre opciones, define como debe ser algo, cierra un debate.
- `orden`: pide que se haga algo concreto.
- `correccion`: le dice al asistente que se equivoco.
- `queja`: repite algo con fastidio, o reclama que no se hizo.
- Un turno que no es ninguna de las cuatro NO se incluye. Una lista corta y
  cierta vale mas que una larga e inflada.
- `sobre` es una ETIQUETA para agrupar despues, no un resumen.
- Si dudas entre incluir y no incluir, no incluyas.

TURNOS:
[0001] ...
```

REDUCCION (`openai/gpt-oss-120b`, 1 llamada):

```txt
Estas son etiquetas de turnos clasificados a lo largo de un mes. Agrupa las que
hablan de LO MISMO y ordena por cuantas veces aparece.

{"temas": [{"tema": "...", "veces": N, "turnos": [1234, 5678],
            "primera_fecha": "...", "ultima_fecha": "...",
            "tipos": {"decision": N, "queja": N}}]}

REGLAS:
- Un tema que aparece muchas veces con `queja` o `correccion` es algo que la
  persona tuvo que repetir porque nadie lo anoto. Ese es el hallazgo.
- No recomiendes nada. No priorices. Conta.
```

Por que asi vale la pena: la salida son numeros y etiquetas de seis palabras,
asi que el tope de tokens deja de ser un recorte callado; el hallazgo es el
CONTEO, no la prosa; y lo unico que el modelo redacta es la etiqueta, de manera
que si se equivoca agrupa mal pero no inventa una decision.

Los estratos ya estan extraidos: `tools/leer_mes_watsonx.py` se borro por no
tener consumidor, pero su parte util era `estratos_del_mes()`, que separa
usuario / asistente / lineas de error de los `.jsonl` de
`~/.claude/projects/c--IA-flujo/`. La llave de watsonx vive solo en la caja
(`~/n8n-local/research.env`), asi que se extrae en la maquina del usuario y se
corre alla.

## 6. Para un agente que recien llega

Leer, en este orden: `CLAUDE.md`, este archivo, `MAPA.md`. Si vas a tocar iskvw,
tambien `iskvw/MAPA.md`. Si vas a construir una herramienta, **primero** el
registro VIVO de `CAPACIDADES.md`: 4 de las 45 entradas tienen como unico
consumidor su propio test, y agregar la 46a sin mirar es como se llego a eso.

El veredicto de un PR es su matriz de CI, nunca el pytest local.
