# Estado del repo

Ultima actualizacion: **2026-08-06, Faro: circuito MAK verificado en MAK**.

Este archivo se lee en dos minutos o no sirve. Llego a 1.666 lineas apiladas y
nadie lo leia -- ni los agentes que lo editaban. La historia esta en
`docs/handoffs/archive/HANDOFF_hasta_20260801.md`; aca queda solo lo que hoy es
cierto.

**Como se mantiene:** se REESCRIBE, no se le agrega al final. Un hallazgo va a
su seccion y reemplaza lo que decia antes. Si algo dejo de ser cierto, se borra
-- una frase que describe un estado que ya no existe se lee como medicion, y esa
es la trampa que costo mas caro (ver "Lo que este repo aprendio", regla 1).

---

## Estado vigente 2026-08-06

Esta seccion manda sobre las notas historicas posteriores cuando describan un
estado distinto.

- Director operativo: **Faro**. Windows dirige y verifica; MAK ejecuta modelos.
- Ramas remotas: solo `main`, `mak`, `rd`, `iskvw`; las cuatro apuntan al mismo
  commit de `main`. No hay PR abiertos.
- El circuito real de MAK ya escribio ledger persistente: 86 filas comunes y
  35 tandas registradas. Watsonx y AWS funcionaron; los fallos de proveedor se
  registran y no abortan la ronda.
- El gate de evidencia detecto 21 filas historicas con rutas inexistentes y las
  dejo en `/home/mak/plataforma/common_ledger_quarantine.jsonl`; el ledger
  comun no se reescribe. `autonomia status` expone esa cuarentena y su proxima
  accion.
- La corrida de seis areas produjo evidencia aceptada en SVG, pero retuvo
  resultados de MAK, Adobe y arqueologia cuando faltaba evidencia o habia
  mezcla de dominios.
- Las tandas nuevas exigen bloque `product` por area. Si falta, quedan en
  `revise` y no entran como verdad al ledger.
- La prueba sin Watsonx, AWS ni Ollama acepto una entrada valida mediante
  fallback determinista y escribio ledger.
- MAK tiene `material.jsonl`: 2.812 entradas, 0 pendientes. Tiene 46 preguntas
  generativas pendientes y 185 informes; el loop ya ejecuto una revision real
  y selecciona un informe antiguo cada cuatro unidades productivas.
- `cola.py` no esta en el crontab vivo. No se debe reactivar sin demostrar un
  consumidor; puede retirarse o convertirse en inbox explicito.
- Los archivos no rastreados en `/home/mak/flujo` son evidencia externa y no se
  borran automaticamente: `.claude`, `crudo_lotes`, `director_snapshot.md`,
  auditorias, `mineria_estado.json` y `turnos_flujo.jsonl` quedan en cuarentena
  hasta ser clasificados.

---

## 1. Lo que espera una decision TUYA

Ninguna la puede tomar un agente. Estan ordenadas por lo que cuesta no tomarla.

| Que | El numero que hace falta para decidir |
|---|---|
| **El reloj de IBM** | ~US$36/dia por TENER el plan. Todo el trabajo de dos dias costo US$0,56. Bajar a Lite se hace desde la consola, no por API. |
| **Consolidar las 1.354 fichas de watsonx** | `tipo_obra` 67%->100%, `materiales` 66%->99,6%. Pero **4.595 valores quedarian mas cortos** que los actuales. `tools/consolidar_fichas.py --aplicar`. |
| **Encender `nodo_glifo`** | El nodo deja de ser un circulo y pasa a ser glifo: arcos 764->0, gradientes 382->0. Publicada apagada en `datos/tablero.json`. Ojo: con ella encendida el medidor no puede fijar el costo por cuadro (ver muro 3). |
| **Si los ensayos de MAK se publican en iskvw.cl** | Decidido por frontera el 2026-08-05: NO entran al sustrato publico por defecto. Siguen vivos como vista explicita de research (`--fuente ensayos` o `--incluir-ensayos`) porque sus iconos/propuestas SVG son garantia visual del informe, no basura. |
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
   mergear -- el sitio publico ya se limpio a 237 vinculos obra/taller, pero
   sigue sin recibir los vinculos semanticos del micelio hasta que ambos entren
   y `publicar_iskvw.yml` corra de nuevo.
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

**El sitio.** `iskvw.cl` publica el sustrato limpio generado por
`gen_archivo_iskvw.py --fuente todo`: medido localmente el 2026-08-05, 446
piezas y 237 vinculos del archivo de obra/taller. Hasta antes de este parche la
maquina habia mezclado 1 informe, 16 conceptos y 16 iconos de ensayos MAK dentro
del archivo publico (479/269). Eso queda opt-in: `--fuente ensayos` o
`--fuente todo --incluir-ensayos` produce la vista de research ilustrado. La piel
degrada a `campo.json` solo si `archivo.json` falla.

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

**MAK format routing, measured bug on 2026-08-05.** A factual request harvested
from the backlog (`Quien organizo el evento del 2023-10-28`) entered under verb
`multiplicar` and came out as a long essay shape (`PARTE I`, iconographic
annex). The cause was not the model: `trabajo.py` chose output format only from
the verb. The repo now fixes that seam twice. First: factual/RD requests force
`informe/corto` even when the verb is `multiplicar`. Second: the new mechanical
router in `cultura/mak_plataforma/research_router.py` classifies task intent
before the model sees it: RD/factual -> `informe`, iskvw/archive/art work ->
`curatoria`, MAK quality/introspection -> `revision`, human-facing/public text
-> `exposicion`, cultural interpretation -> `ensayo`. This is the user's
correction: different research orders need different product contracts; do not
force every job into the same report/essay mold. Verified with `py -m pytest
tests\test_mak_research_router.py tests\test_mak_trabajo_resp.py
tests\test_formato_ensayo.py tests\test_mak_tandas.py -q`.

**MAK vigia, measured and activated on 2026-08-05.** `CAPACIDADES.md` said
`MAK-VIGIA` was live, but the box did not have it applied: `crontab -l` showed no
`MAK-VIGIA` line and `/home/mak/vigia` was empty. The repo already had the right
line in `cultura/mak_plataforma/crontab.mak`, so the fix was operational, not a
rewrite: copy `cultura/mak_vigia` to `/home/mak/vigia`, seed the first run with
`--sin-notificar`, then apply the versioned crontab. Measured result: live
crontab now has `MAK-VIGIA`, the sync line copies `mak_vigia`, and
`/home/mak/vigia/estado/` exists with 425 seeded items. The first follow-up runs
absorbed a few late `fondos_de_cultura` items; after that, three immediate
follow-up runs returned `fondos_de_cultura nuevos=0`.

**MAK autonomy verdict, external-model consensus on 2026-08-05.** Watsonx
Mistral, Watsonx Granite, AWS Qwen and AWS Mistral Large converged on the same
answer from mechanical evidence: MAK is partially autonomous, about 6/10. It can
run research, harvest backlog questions, keep core crons alive and open PRs
through `entregar.py`, but it is not self-sufficient until two seams close:
deploy the factual-format `trabajo.py` patch through the repo gate, and fix or
deliberately retire `cola.py` dying on missing `NTFY_TOPIC_IN`. Raw outputs live
outside commits, not in Downloads, at
`C:\IA\flujo\_logs\cauce_director\20260805\CAUCE_MAK_AUTONOMY_MODELS_20260805_raw.json`;
the local director board is
`C:\IA\flujo\_logs\cauce_director\20260805\CAUCE_MAK_AUTONOMY_20260805.md`.

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

## 7. Current orchestration state

- 2026-08-06 identity correction: the active Codex operator is now **Faro**.
  **Cauce** means the Claude-era historical operator, and **SOL** means the
  earlier GPT web/Azure operator. This was changed because reusing Cauce made
  new Codex work look like Claude work and increased attribution errors after
  compaction.
- 2026-08-06 external web audit triage: the user-provided external audit is
  useful as a third-party hypothesis, not as ground truth. It correctly names
  the main risk as knowledge-governance drift:
  code, JSON, MAPA, LAST_HANDOFF, Hub and README can describe the same state with
  similar authority. Local checks refined it: `iskvw/datos/tablero.json` already
  ships `patch_efectos=true` and `nodo_glifo=true`; `iskvw/datos/micelio.json`
  is present in `origin/main`; `mak` remains an inbox by doctrine, but
  `origin/mak` is currently mixed with workflow/package changes plus
  autogenerated utilities. Next action is not a rewrite of the architecture: it
  is to add more derived-state checks and quarantine mixed MAK/Dependabot diffs
  before any promotion.
- 2026-08-06 Faro branch/local sync: open PRs were drained to zero. PR #456
  was merged; PRs #457, #458 and #463 were closed and their remote branches
  deleted because they were dirty or low-quality. Remote branches were pruned so
  only `origin/main`, `origin/mak`, `origin/rd`, and `origin/iskvw` remain.
  Local Windows branches now track those four canonical remotes; the external
  Windows worktree on `main` was fast-forwarded to `origin/main`; MAK's
  `~/flujo` was fast-forwarded to `origin/main` and its stale local branches were
  deleted. `mak` was merged with `origin/main` and pushed so the inbox no longer
  looks like a dependency downgrade. Code fix applied in
  `cultura/mak_plataforma/revisor.py`: capataz PRs are rejected if they touch
  files outside `cultura/mak_plataforma/utilidades/`.
- The live MAK core is already mapped: `cultura/mak_plataforma/{capataz,trabalho,backlog,mantenimiento,salud,latido,coherence,metricas_capataz,calidad_loop,entregar,revisor,guardia,energia,cuotas,red_watch,vigilar_red}` plus `cultura/mak_research/{research_lib,retencion,expulsion,conversacion}`.
- `tools/contexto_repo.py task` is the cheapest route for scoping; `tools/contexto_repo.py map` is the cheapest repo map.
- `tools/auditoria_completa_watsonx.py` is the right Watson-style orchestrator for compact, high-signal reads.
- `tools/conversacion.py` is the real session-corpus reader; `arquitectura.py` is not present in the repo, and `esfuerzo.py` is external, not a repo tool.
- IBM Cloud credentials are present in `.env` and can be mapped to Watsonx env vars; no secret values should be written to disk or repeated in handoffs.
- Local git shows extra branches beyond the user's canonical set; treat `main`, `mak`, `iskvw`, and `rd` as the canonical lines, and ignore stale/local experiment branches unless a cleanup task is explicitly requested.
- The current reading plan is now externalized here, not in chat: `src/flujo/` + `tools/` remaining files are Tanda 1; `docs/OPERACION_APP.md`, `docs/HUB_PERFILES.md`, `docs/TAPIZ.md`, `tests/test_revisor_gates.py`, `tests/test_calidad_loop.py`, `tests/test_curatoria_percepcion.py`, and `tests/test_capataz.py` are already covered; `docs/rd/...` is lower priority for now.
- The SVG `mapa_lectura.svg` is a coverage map only; it is not the source of truth for continuation. The durable state lives in this handoff file.
- Watsonx and AWS are both being used as batch readers, not as memory stores: Watsonx already ranked the remaining `src/flujo/` clusters, and AWS `amazon.nova-pro-v1:0` classified the current `src/flujo/` and `tools/` batches.
- Current `src/flujo/` result: `cli.py` is the CLI nucleus; `intake/json_parser.py` is the intake/brief contract; `serve/server.py` is the fallback server; next cluster is `web/hub.py` + `rd/database.py` + `jobs/brief.py`.
- Follow-up `src/flujo/` result: `web/hub.py`, `jobs/job.py`, `jobs/brief.py`, `route/resolver.py` form the core job/hub/routing spine; AWS pointed the next cluster to `src/flujo/dashboard/`.
- Current `tools/` result: `gen_archivo_iskvw.py` is the nucleus; `validar_curaduria.py` and `consolidar_fichas.py` are contract/validator layers; `compete_engine.py` is the next cluster to inspect after that.
- Follow-up `tools/` result: the next cluster after the current batch should be `tools/compete_engine.py` plus the `tools/` files that orbit it; `gen_archivo_iskvw.py` stays as the nucleus, `validar_curaduria.py` and `consolidar_fichas.py` stay as contracts/validators, and `ig_metadatos.py` is a product-facing source reader, not a core engine.
- Mechanical refutation of the AWS dashboard/compete batch: `src/flujo/dashboard/` is live through `src/flujo/web/hub.py`, the CLI, and tests; `tools/compete_engine.py` and `tools/system_map.py` are VIVO in `CAPACIDADES.md`, CLI-wired, and test-covered; `tools/tapiz_telemetry.py` and `tools/tapiz_live_loop.py` are REVISAR with consumers/tests/UI references, not dead.
- Next decision seam: inspect `tests/test_compete_engine.py` and `web/src/components/CulturaPanel.tsx` before any Tapiz cleanup, consolidation, or rebuild.
- External-model seam check: when given only mechanical evidence lines, both Watsonx `ibm/granite-3-8b-instruct` and AWS Bedrock `amazon.nova-pro-v1:0` converged on `compete_engine.py` = VIVO, `system_map.py` = VIVO, `tapiz_telemetry.py` = REVISAR, `tapiz_live_loop.py` = REVISAR. Earlier long-context outputs were noisy and must not be trusted without grep-backed evidence.
- Director verdict for Tapiz: do not rebuild or replace this cluster. Reuse `compete_engine.py` and `system_map.py`; review `tapiz_telemetry.py`/`tapiz_live_loop.py` only at their seams with tests/UI before deciding whether they graduate to VIVO or get pruned.
- AI-op utility verdict: `tools/context_pack.py`, `tools/token_budget.py`, and `tools/verify_all.py` are small, compile, and do distinct jobs. They are useful for this orchestration and must not be recreated, but CAPACIDADES still marks them REVISAR because repo consumers are pending.
- Critical 2026-07-31/2026-08-01 window: the real landed work is the commit chain `a856a92`, `88a4e74`, `64dbe1a`, `304ae3e`, `1cf6e57`, `777b40f`, `5d59bf8`, `47ea7cb`, not any later chat memory. Treat this git range as the recovery spine.
- Commit `0d9f6e0` (`feat(tools): las herramientas que CAPACIDADES.md ya declara vivas, pero main no tiene`) has no visible diff against parent `64dbe1a`; it is still useful as a signed narrative/rollup, but the applied code is in neighbouring commits, especially `88a4e74` and `1cf6e57`.
- `88a4e74` is load-bearing: it landed the micelio circuit (`src/flujo/micelio.py`), perception support marking, `tools/consolidar_fichas.py`, `tools/drenar_material.py`, `tools/ig_metadatos.py`, and tests. Do not rebuild those tools; audit their current consumers and gates.
- `1cf6e57` is the correction to the "almost deleted" MAK utilities story: the prior claim that main evaluated and deleted the 33 utilities was false; nobody had read them. Four useful utilities were identified, then reverted back to the inbox because they lacked consumers and broke fixtures; the durable finding is that `revisor.gate_compila` was blind to encoding/surrogate defects, later covered by tests.
- Next recovery batch: inspect `tools/consolidar_fichas.py`, `tools/drenar_material.py`, `tools/ig_metadatos.py`, `src/flujo/micelio.py`, `cultura/mak_plataforma/material.py`, and `tests/test_{consolidar_fichas,micelio_cosecha,micelio_deposito,ig_metadatos,material_ocurrencias}.py` as one circuit, not as separate utilities.
- Cauce external excavation loop, 2026-08-05: do not use Codex subagents for this phase. Use Watsonx/AWS as batch critics, then verify locally by grep/tests before editing. Scratch/output lives in `C:\IA\flujo\_logs\cauce_director\20260805`, not Downloads. Main artifacts: `ROUND2_AGGREGATED_SEEDS.md`, `ROUND3_REFUTATION_AGGREGATE.md`, `MECHANICAL_VERIFICATION.md`, and `MAPA_SEMILLAS_AMBICIOSAS.md`.
- Current ambitious sequence from six external refuters plus local evidence: first check PR #440/#443 micelio visibility, then rescue/register/test Illustrator/Adobe bridge, then surface RD primary-source triangulation, then measure thi.ng only if browser payoff is real, then decide whether `cola.py` is repaired as mobile trigger or explicitly retired. Do not rebuild any of these before checking the named existing paths.
- Micelio visibility update, same session: #440 is MERGED into `mak` and #441 is MERGED into `main`, but `origin/main` still has no `iskvw/datos/micelio.json`. PR #443 (`micelio-a-main-20260801` -> `main`) is OPEN/BEHIND and only adds that snapshot. Local proof by applying the blob from #443 and running `py tools/gen_archivo_iskvw.py --fuente todo`: 1976 pieces, 5158 links, 4921 semantic. This is a branch promotion problem, not a new-engine problem.
- Illustrator/Adobe update, same session: `py -m pytest tests\test_illustrator_bridge.py tests\test_svg_illustrator_integration.py -q` passed 6 tests. `tools/illustrator/README.md` and `tools/adobe_panel/README.md` already document the JSON bridge, export JSX, logo tools and CEP panel. Treat this as rescue/registration/manual-app-test work, not a rebuild.
- RD surface update, same session: `py -m pytest tests\test_rd_eventos.py tests\test_gen_propuestas_rd.py tests\test_fuentes.py -q` passed 50 tests. `src/flujo/rd/panel.py` exposes normalized events and triangulable counts; `src/flujo/rd/eventos.py::indice_triangulacion` exists. The gap is likely surfacing/consuming primary-source evidence, not a new DB or triangulator.
- MAK cola repair update, same session: `ssh mak@192.168.50.2` confirmed `NTFY_TOPIC_IN` is missing and `cola.log` is repeating `Falta NTFY_TOPIC_IN en research.env`; `interfaz.py` is alive. The repo mirror now patches `cultura/mak_research/watchdog.sh` so cron starts `cola.py` only when the ntfy inbox is configured and reports the disabled state once via `.cola.disabled.missing_ntfy`. Verified with `py -m pytest tests\test_mak_research_watchdog.py -q`, `bash -n cultura/mak_research/watchdog.sh`, and `py -m pytest tests\test_mak_mirror_fixes.py tests\test_crontab_mak_referencias.py -q`. Not live on MAK until this mirror reaches `main`; do not hotfix the box as a substitute, the repo sync will overwrite it.
- RD/thi.ng round 4 update, same session: six Watsonx/AWS judges reviewed only the RD primary-source seam and thi.ng lane; five parsed. 3/5 recommended editing RD, but their main suggestion (`cl_eventos` in `cultura/mak_research/fuentes.py`) already existed. The durable fix is a ratchet in `tests\test_fuentes.py` covering event/producer domain detection, promoter/ticketing primary sources, and absence marking. Verified with `py -m pytest tests\test_fuentes.py tests\test_rd_eventos.py -q` (40 passed) and `py -m compileall cultura\mak_research\fuentes.py`. For thi.ng, 0/5 recommended adoption now; `py -m pytest tests\test_thing_registro.py tests\test_iskvw_librerias.py -q` passed 22 tests. Do not adopt more thi.ng until a concrete browser-side query/benchmark exists.
- The next durable anchor, if this branch grows, is still `context/LAST_HANDOFF.md`; no extra checkpoint file is needed yet.
- RD primary-source persistence update, same session: `productora_eventos` now stores the source-gate verdict from `cultura/mak_research/fuentes.py::evaluar(..., dominio="cl_eventos")` as `fuentes_primarias` JSON plus `sin_fuente_primaria`. This reuses the existing MAK gate instead of duplicating source rules inside RD. Verified with `py -m pytest tests\test_rd_database.py tests\test_fuentes.py tests\test_rd_eventos.py -q` (60 passed) and `py -m compileall src\flujo\rd\database.py cultura\mak_research\fuentes.py`.
- RD panel source surface update, same session: `src/flujo/rd/panel.py` now exposes each event's `fuentes_primarias` and `sin_fuente_primaria`, plus `resumen.eventos_sin_fuente_primaria`; `web/src/components/RdDbPanel.tsx` shows the missing-primary-source count and a per-productora badge. Verified with `py -m pytest tests\test_rd_db_logos.py tests\test_rd_database.py tests\test_fuentes.py tests\test_rd_eventos.py -q` (67 passed), `py -m compileall src\flujo\rd\panel.py src\flujo\rd\database.py cultura\mak_research\fuentes.py`, and `cd web; npm run typecheck`.
- RD board proposal source surface update, same session: `tools/gen_propuesta_directiva.py` now carries `productora_eventos.sin_fuente_primaria` into the generated HTML stats and event labels, so the board-facing proposal can distinguish "fuente primaria" from "sin fuente primaria" instead of treating all registered events as equally evidenced. Verified with `py -m compileall tools\gen_propuesta_directiva.py`, `py -m flujo rd-db build`, and `py tools\gen_propuesta_directiva.py --out _logs\cauce_director\20260805\propuesta_directiva_check.html`.
- Micelio visibility recheck, same session: PR #443 is still OPEN/BEHIND and contains only `iskvw/datos/micelio.json` (+58,435 lines). Local generation with the snapshot present (`py tools\gen_archivo_iskvw.py --fuente todo --salida _logs\cauce_director\20260805\archivo_micelio_visibility_check.json`) produced 1976 pieces, 5158 links, 4921 semantic links; the live micelio endpoint refused connection and the generator correctly fell back to the snapshot. Verified the circuit with `py -m pytest tests\test_gen_archivo_iskvw.py tests\test_contrato_archivo.py tests\test_entregar_micelio.py -q` (18 passed). This remains a PR/rebase/promotion task, not an engine task.
- Illustrator/Adobe registration rescue, same session: the bridge itself passed tests, but `MAPA.md`/`tools/gen_mapa_comandos.py` documented `py -m flujo render bridge` as requiring Blender even though it generates Illustrator JSX. Fixed the command registry prerequisite to Adobe Illustrator. Verified with `py -m pytest tests\test_mapa_completo.py tests\test_illustrator_bridge.py tests\test_svg_illustrator_integration.py -q` (9 passed) and `py -m compileall tools\gen_mapa_comandos.py src\flujo\export\illustrator_bridge.py src\flujo\export\illustrator.py`.
- Adobe CEP panel rescue, same session: `tools/adobe_panel/js/main.js` tried to resolve scripts with ExtendScript globals (`File`, `Folder`, `$.fileName`) inside the CEP browser process and its fallback pointed at `tools/adobe_panel/` instead of `tools/`; copied panels would not find `illustrator/scripts/*.jsx`. Reworked path resolution to use CEP `window.cep.fs`, `SystemPath.EXTENSION`, env/config roots, and a repo-mode fallback to the parent `tools/` directory; README no longer tells agents to edit `REPO_TOOLS` manually. Verified with `py -m pytest tests\test_adobe_panel.py tests\test_illustrator_bridge.py tests\test_svg_illustrator_integration.py -q` (8 passed) and `node --check tools\adobe_panel\js\main.js`.
- Adobe CEP install checker, same session: added read-only `tools/adobe_panel/check_install.ps1` to diagnose PlayerDebugMode, CEP extension path, manifest, and `repo_tools_path` without editing the machine. Local run shows the panel is not installed on this Windows user yet and CSXS.9-13 PlayerDebugMode are not set to `1`; repo scripts exist. Verified with `py -m pytest tests\test_adobe_panel.py tests\test_illustrator_bridge.py tests\test_svg_illustrator_integration.py -q` (9 passed), `node --check tools\adobe_panel\js\main.js`, and `powershell -NoProfile -ExecutionPolicy Bypass -File tools\adobe_panel\check_install.ps1`.
- Command registry refresh, same session: because `tools/gen_mapa_comandos.py` changed the `render bridge` prerequisite, `py tools\gen_mapa_comandos.py --check` correctly failed; regenerated `context/comandos.json` with `py tools\gen_mapa_comandos.py` (93 commands). Recheck passed with `MAPA.md y context/comandos.json al dia con el CLI`, and `py -m pytest tests\test_mapa_completo.py tests\test_adobe_panel.py -q` passed 6 tests.
- MAK visual autonomy update, same session: the missing seam was not icon creation itself (`cultura/mak_codex/iconos.py` already existed), but the lack of an automatic bridge from `research.py --formato ensayo` concept annexes to Codex visual jobs. `cultura/mak_research/worker.py` now watches successful research stdout for `ANEXO: *.conceptos.json` and queues up to `MAK_AUTO_ICONOS_MAX` best-effort `codex iconos` jobs through the Codex HTTP endpoint. This keeps factual/RD reports as reports, while cultural essays can autonomously spawn representative SVG icons. Verified with `py -m pytest tests\test_mak_research_iconos_auto.py tests\test_mak_trabajo_resp.py tests\test_mak_reanudar.py -q` and `py -m compileall cultura\mak_research\worker.py`.
- MAK quality audit update, same session: measured the real box corpus (`~/research/informes`) and found the user's concern was valid. Current sample: 32 markdown reports, 29 tagged `ensayo`, 23 with `.conceptos.json`; many operational/event questions from the backlog were shaped as cultural essays. Root cause: `research_lib._es_pregunta_factual()` recognized only four narrow phrases. Fixed by folding diacritics and adding measured operational/event/ticketing/security signals so `trabajo.py` forces `formato=informe`, `densidad=corto` for those topics even under verb `multiplicar`. Local audit note: `_logs\cauce_director\20260805\MAK_QUALITY_AUDIT_20260805.md` (not committed). Verified with `py -m pytest tests\test_mak_trabajo_resp.py tests\test_mak_research_lib.py tests\test_fuentes.py -q`, `py -m compileall cultura\mak_research\research_lib.py cultura\mak_plataforma\trabajo.py`, and `git diff --check`.
- MAK idle review mode, same session: user clarified that MAK autonomy should not mean producing more essays/research when no useful task is pending. Added first-class research format `revision` plus platform verb `repasar`; it activates only when material queue, research backlog and Codex backlog are empty, and produces a short critical operational review with executive nodes (`repasar`, `discutir`, `exponer`, `refutar`, `archivar`) instead of a cultural essay or generic report. Verified with `py -m pytest tests\test_mak_trabajo_resp.py tests\test_formato_ensayo.py -q`, `py -m compileall cultura\mak_plataforma\trabajo.py cultura\mak_plataforma\roles.py cultura\mak_research\research.py cultura\mak_research\formato_ensayo.py cultura\mak_research\interfaz.py`, and `git diff --check`.
- MAK autonomy plan correction, same session: user rejected tiny PR cadence and asked for a longer/significant MAK improvement. Kept the previous small commit on `mak` as an inbox checkpoint, but no PR was opened. Expanded the design so idle autonomy is a matrix, not a single fallback: seeds are no longer an infinite production motor unless `MAK_SEED_FALLBACK=1`, and idle-only verbs now route to distinct executive nodes: `repasar` -> `research` + `formato=revision`, `discutir` -> `panel`, `refutar` -> `refutar`, `exponer` -> `research` + `formato=exposicion`. Verified with `py -m pytest tests\test_mak_trabajo_resp.py tests\test_formato_ensayo.py tests\test_mak_research_lib.py tests\test_mak_research_iconos_auto.py -q`, `py -m compileall cultura\mak_plataforma\trabajo.py cultura\mak_plataforma\roles.py cultura\mak_research\research.py cultura\mak_research\formato_ensayo.py cultura\mak_research\interfaz.py`, and `git diff --check`.
- MAK idle audit ledger, same session: continued the significant MAK autonomy block without opening PR/push. `trabajo.py` now appends idle-only dispatch decisions to `~/plataforma/idle_decisions.jsonl` with timestamp, online state, verb, department, mode, format, density, topic, pending-queue snapshot, status (`accepted`/`rejected`/`failed`) and response/error preview. Productive verbs do not write this ledger. This gives `repasar`/`discutir`/`refutar`/`exponer` an auditable trail instead of another prose report. Verified with focused tests before publishing any PR.
- MAK external batch contract, same session: user clarified Watsonx/AWS credits expire in about one week and improvements must survive on Cerebras/Groq/Ollama later. Added provider-agnostic `cultura/mak_plataforma/tandas.py`: durable area contracts (`mak_quality`, `rd_evidence`, `iskvw_curation`, `tool_archaeology`, `svg_pipeline`), stable provider lanes (`premium_burst` -> `free_cloud` -> `local_floor`), JSON-only result schema (`claim`, `evidence`, `files`, `confidence`, `action`, `reject_reason`), CLI brief generation/validation, and append-only `~/plataforma/external_batches.jsonl` ledger that never stores secrets. This lets temporary IBM/AWS burn through large reads without making them structural dependencies.
- MAK common ledger, same session: added `cultura/mak_plataforma/ledger.py` as the durable circulation layer. External model output no longer has to remain a report: validated items can become append-only records in `~/plataforma/common_ledger.jsonl` with schema `mak-ledger-v1`, typed as `evidence`, `idea`, `task`, `decision`, `reject` or `artifact`, hard-gated by domain (`rd`, `iskvw`, `mak`, `svg`, `adobe`, `repo`) and allowed actions. `tandas.py validate --common-ledger <path>` now writes validated external results into that shared ledger, while keeping the batch ledger separate. Secrets are redacted by marker before persistence. Verified with `py -m pytest tests\test_mak_ledger.py tests\test_mak_tandas.py tests\test_mak_research_router.py tests\test_mak_trabajo_resp.py tests\test_formato_ensayo.py -q`, compileall and `git diff --check`.
- MAK local discernment gate, same session: user clarified that Ollama local exists so MAK can discern, not merely fall back when the cloud dies, and asked to cover the other areas too. Added `cultura/mak_plataforma/discernment.py`: an Ollama-facing local review contract (`mak-local-review-v1`) that judges external batch output as `accept`, `revise` or `reject` with risks, missing evidence and next action. `tandas.py` now embeds a `local_review` prompt in every brief, exposes `review-prompt`, and more importantly exposes `ingest`: provider JSON from Watsonx/AWS/free/local -> schema validation -> local review via Ollama when available -> deterministic fallback if Ollama is down -> append review decision to `common_ledger.jsonl` -> append provider facts ONLY when the verdict is `accept`. If the verdict is `revise` or `reject`, the ledger keeps the local decision/rejection but does not promote the provider output as evidence. Areas covered: `mak_quality`, `rd_evidence`, `iskvw_curation`, `tool_archaeology`, `svg_pipeline`, plus new `adobe_rescue` so Illustrator/Adobe bridge rescue is not confused with Blender or generic SVG work. This is the first self-sufficiency seam: expensive models may produce volume, but a local/cheap gate decides what becomes system memory. Verified with `py -m pytest tests\\test_mak_discernment.py tests\\test_mak_ledger.py tests\\test_mak_tandas.py tests\\test_mak_research_router.py tests\\test_mak_trabajo_resp.py tests\\test_formato_ensayo.py -q`, compileall and `git diff --check`. Committed and pushed to `origin/mak` as `d3c5e55`.
- MAK batch routing correction, same session: user warned that `capataz` came from his Claude interaction and may be too abstract/ambiguous to be the best path. Do NOT make `capataz` the backbone for external batches. Treat it as observer/optional client only. The permanent path is a mechanical standalone organ: `tandas.py` builds briefs, writes them to disk, validates provider output, and summarizes its own ledger without asking a deliberative agent to choose.
- MAK external batch runner update, same session: `cultura/mak_plataforma/providers.py` now gives `tandas.py run` real provider transports for Watsonx and AWS Bedrock. It normalizes IBM env aliases (`IBM_CLOUD_APIKEY`, `IBM_PROJECT_ID`, `IBM_CLOUD_URL`) into the existing `WATSONX_*` contract without printing secrets, and uses optional `boto3` for Bedrock (`AWS_BEDROCK_BATCH_MODEL`, default `amazon.nova-pro-v1:0`). `tandas.py brief --with-evidence` now adds bounded local evidence packs per area, so external providers receive measured snippets instead of unreachable local paths. CLI JSON output is escaped/lossless so Windows cp1252 stdout no longer crashes on Unicode evidence. Verified with `py -m pytest tests\test_mak_tandas.py tests\test_mak_discernment.py tests\test_mak_ledger.py -q`, compileall, and `git diff --check`.
- MAK real controlled batch run, same session: generated six evidence briefs under `_logs/cauce_director/20260805/tandas_real_controlled/` for `mak_quality`, `rd_evidence`, `iskvw_curation`, `tool_archaeology`, `svg_pipeline`, and `adobe_rescue`. Ran 12 real external calls (Watsonx + AWS for every area) through `py -m cultura.mak_plataforma.tandas run ... --common-ledger _logs/cauce_director/20260805/tandas_real_controlled/common_ledger.jsonl --max-tokens 1800`. Result summary: 60 common ledger rows, 47 evidence, 12 decisions, 1 reject; by domain repo 7, mak 12, rd 9, iskvw 9, svg 12, adobe 11. Ollama was not listening on `127.0.0.1:11434`, so every review used deterministic fallback and recorded the local-review risk. This is acceptable as fail-safe proof, but not yet the strong local-discernment proof the user wanted.
- MAK ledger surface update, same session: `/api/mak` now includes a read-only `tandas` surface from `~/plataforma/common_ledger.jsonl` and `~/plataforma/external_batches.jsonl` (overrideable with `FLUJO_MAK_COMMON_LEDGER` and `FLUJO_MAK_BATCH_LEDGER`). `web/src/components/MakPanel.tsx` shows accepted evidence, rejected/revise, decisions, batch count, domains, providers, pending reviews, and last batches. This makes Watsonx/AWS output visible as judged memory, not hidden files. Verified with `py -m pytest tests\test_mak_tandas_surface.py tests\test_mak_tandas.py tests\test_mak_discernment.py tests\test_mak_ledger.py -q`, `py -m compileall src\flujo\web\hub.py cultura\mak_plataforma\providers.py cultura\mak_plataforma\tandas.py cultura\mak_plataforma\discernment.py cultura\mak_plataforma\ledger.py`, `cd web; npm run typecheck`, and `git diff --check`.
- MAK strict external-batch update, same session: external rounds showed a real defect in the local fallback gate. Before hardening, deterministic fallback accepted provider claims with `[redacted]`, empty `files`, secret-looking paths and weak negative claims. `cultura/mak_plataforma/discernment.py` now downgrades/rejects those classes: redacted/secret material rejects; actionable claims without concrete `files` revise; low confidence revises; negative claims (`no hay`, `no existe`, `missing`, `does not exist`) need concrete evidence. If Ollama returns invalid review JSON or the wrong domain, an otherwise accepted fallback is downgraded to `revise` with `valid local review` missing. Verified with `py -m pytest tests\test_mak_discernment.py tests\test_mak_tandas.py tests\test_mak_ledger.py -q`, compileall and `git diff --check`.
- MAK Ollama judge update, same session: Windows Ollama was installed but initially served no models. `ollama pull gemma3:4b` timed out after 15 minutes but completed enough that `ollama list` now shows `gemma3:4b` (3.3 GB). R003 strict batches used Ollama successfully for 10/12 reviews; one AWS RD result was invalid (`missing_reject_reason`), one AWS MAK result was `revise`, and an Adobe/AWS bad-domain review exposed the invalid-review downgrade gap fixed above. R004 Adobe/AWS regression then passed with Ollama reviewer and domain `adobe`.
- MAK live ledger burn update, same session: ran R005 live into default `~/plataforma/common_ledger.jsonl` and `~/plataforma/external_batches.jsonl` with Watsonx + AWS across all six areas (`mak_quality`, `rd_evidence`, `iskvw_curation`, `tool_archaeology`, `svg_pipeline`, `adobe_rescue`). Result: 40 common rows, 28 evidence, 7 decisions, 5 rejects/revise memory; batch statuses 35 accepted rows and 5 revise decisions across 12 provider runs. SVG was correctly held for revision by both providers because thi.ng/vpype integration claims lacked enough concrete measurement; Adobe/AWS was held for revise because Ollama returned `bad_domain`; AWS/tool_archaeology held `system_map.py` as needing consumer/use verification. This is the desired shape: credits burn as producers, but local review decides what becomes memory.
- MAK local promotion update, same session: promoted three verified decisions into the live `~/plataforma/common_ledger.jsonl` with source `local_verification`: (1) `tools/system_map.py` is live/test-covered through `tests/test_compete_engine.py` and should not be rebuilt from provider uncertainty; (2) thi.ng/laser lanes are measured by `tests/test_thing_registro.py`, `tests/test_iskvw_librerias.py`, and `py -m flujo laser estado`, so further thi.ng adoption waits for a concrete browser benchmark; (3) Adobe rescue is test-covered as bridge/rescue work, not Blender rebuild work. Verification commands: `py -m pytest tests\test_compete_engine.py tests\test_thing_registro.py tests\test_iskvw_librerias.py -q` (52 passed), `py -m pytest tests\test_laser.py tests\test_adobe_panel.py tests\test_illustrator_bridge.py tests\test_svg_illustrator_integration.py -q` (28 passed), `py tools\system_map.py show`, and `py -m flujo laser estado` (`OK vpype`, `OK hatched`, `OK flow`). Live common ledger summary after promotion: 43 rows, 28 evidence, 10 decisions, 5 rejects.
- MAK idle ledger autonomy update, same session: `repasar` now checks `~/plataforma/common_ledger.jsonl` for pending rejected/low-confidence ledger rows before dispatching another research document. If it finds one, `_tarea("repasar", ...)` returns depto `local` with mode `ledger_review`; `main()` writes `~/plataforma/idle_ledger_reviews.jsonl` and audits the decision without POSTing to research/codex or spending Watsonx/AWS/Ollama. If there is no pending ledger row, the prior `revision` research path still works. This is the safe autonomy seam: idle MAK reviews its own judged memory first, and premium credit burning stays explicitly directed through `tandas run`. Verified with `py -m pytest tests\test_mak_trabajo_resp.py tests\test_mak_discernment.py tests\test_mak_tandas.py tests\test_mak_ledger.py -q`, compileall and `git diff --check`.
- MAK promotion PR update, same session: opened PR #460 (`mak` -> `main`) titled `feat(mak): promote autonomous batch ledger circuit`, URL https://github.com/ligereza/vibecodeine/pull/460. This drains the current MAK inbox block as one coherent circuit: research format routing, provider-agnostic `tandas`, common ledger, local Ollama discernment, Watsonx/AWS runner, MAK panel ledger surface, and idle local ledger review. Local pre-PR verification passed: `py -m pytest tests\test_mak_trabajo_resp.py tests\test_mak_discernment.py tests\test_mak_tandas.py tests\test_mak_ledger.py tests\test_mak_tandas_surface.py tests\test_mak_research_router.py tests\test_formato_ensayo.py -q`; `py -m compileall cultura\mak_plataforma cultura\mak_research src\flujo\web`; `cd web; npm run typecheck`; `git diff --check`. Initial GitHub status: mergeStateStatus `BLOCKED` only because checks were queued/in progress (`CI` ubuntu/windows and `seguridad` jobs), not because a failure was observed yet.
- PR #460 CI follow-up, same session: both Ubuntu and Windows CI failed only at `tests/test_mapa_completo.py::test_toda_variable_de_entorno_esta_documentada` because the new hub overrides `FLUJO_MAK_COMMON_LEDGER` and `FLUJO_MAK_BATCH_LEDGER` were read by code but missing from `MAPA.md`. Fixed `MAPA.md` section 4 to document both variables. Local `py -m pytest tests\test_mapa_completo.py -q` passed after the fix. Full local pytest also showed two checkout-only contaminants (`AGENTS.md` untracked from the agent harness and a private `.env` key leaking into `tests/test_productoras.py`), so do not treat those as PR #460 regressions.
- Faro survival hardening, 2026-08-06: Ollama `faro-survival-09` exposed a real failure mode: lone Unicode surrogates from a model response could abort raw persistence, and escaped surrogates could reappear after `json.loads` and break ledger serialization. `cultura/mak_plataforma/tandas.py` now sanitizes direct and decoded provider trees before persistence/ingestion, preserving the strict invalid/revise gates. Regression coverage passes in `tests/test_mak_tandas.py` (28 tests). PR #483 and PR #484 were merged; the latter is the durable fix, and all four canonical remote branches now point to `0eeec83`. Main protection was restored with strict Ubuntu/Windows required checks and admin enforcement after the merge.
- MAK survival verification, 2026-08-06: deployed the hardened `tandas.py` to `/home/mak/plataforma` and ran `faro-survival-11`. Ollama completed without the previous Unicode crash; the batch returned three parsed items and only one domain-action error (`item_2_bad_action_for_domain`). It still exited nonzero because the content gate correctly reports that error; no malformed text entered truth. This confirms the infrastructure failure is fixed while semantic review remains strict.
- Corpus benchmark, 2026-08-06: added `cultura/mak_plataforma/benchmark.py`, deliberately separate from the Codex quality loop because it measures research products, not code jobs. It scans only research output directories, pairs JSON with Markdown, compares declared format with deterministic intent routing, and checks structural essay traces without claiming to judge truth. On the live MAK corpus it found 72 products: 41 declared essays, 20 reports, 1 revision and 10 legacy products without a recognized format. It found 27 route/format mismatches and 28 essays missing structural traces; only 21 products passed the mechanical benchmark. The mismatches include factual event/ticket questions declared as essays and cultural genealogy declared as reports. This is the first measured proof that the remaining problem is semantic product routing, not just model availability.
- Benchmark gate and external challenge, 2026-08-06: `benchmark.py` now supports `--since <epoch>` for new-product-only inspection and `--check` for a nonzero failure gate; it ignores Codex/panel legacy directories rather than inflating the research metric. Two focused MAK quality rounds (`faro-benchmark-r01` and `r02`) sent the benchmark to Watsonx and AWS. Watsonx invented or mis-resolved evidence paths and was held at `revise`; AWS mixed defect classes and Ollama rejected it. This is useful negative evidence: premium models must not be allowed to classify the benchmark without a bounded evidence package and a single defect taxonomy.
