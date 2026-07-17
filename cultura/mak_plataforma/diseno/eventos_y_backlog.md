# Diseño: eventos, pausa-en-error, backlog (contrato, no código)

> Una pagina. Escrita antes de tocar codigo porque el schema de eventos es un
> contrato con 3 consumidores derivados (hub, visor, reanudador) -- el unico
> punto donde equivocarse cuesta triple.

## 1. Schema de evento (`~/<depto>/eventos.jsonl`, append-only, uno por job_id)

`job_id`: acunado al lanzar el job (no existe hoy -- `jobs.jsonl` solo tiene
texto+timestamp). Formato: `<stamp()>-<4 hex random>`. Viaja desde `_lanzar()`
hasta el proceso/hilo que corre el trabajo real.

Tipos de evento (un JSON por linea, campo `tipo` obligatorio):

```json
{"tipo":"node_start","job_id":"20260717-160000-a3f1","fase":"buscar","detalle":"iteracion 1/2: idioma quechua","ts":1784318400}
{"tipo":"llm_result","job_id":"20260717-160000-a3f1","fase":"buscar","proveedor":"groq","resumen":"encontro: Introduccion a la lengua y cultura quechuas (books.google)","ruta_completa":null,"ts":1784318412}
{"tipo":"error","job_id":"20260717-160000-a3f1","fase":"escribir_codigo","tipo_error":"timeout","contexto":"deepseek-coder:6.7b: timed out","ts":1784318430}
{"tipo":"human_gate","job_id":"20260717-160000-a3f1","motivo":"error","acciones":["reintentar","editar_input","saltar","abortar"],"ts":1784318430}
{"tipo":"node_end","job_id":"20260717-160000-a3f1","estado":"listo","ts":1784318441}
```

Reglas: `resumen` siempre 1 linea (<=140 chars), texto real (que encontro, que
dijo el modelo) -- NUNCA contador de pasos ("iteracion 2/2" va en `detalle`,
no en `resumen`). `ruta_completa` apunta al archivo final si existe (el .md/.py
ya guardado), null si aun no se persistio. Escribir el evento tras CADA
`print("STATUS: ...")` existente -- ese punto de enganche ya esta en
research.py/generar.py, no se inventa un mecanismo nuevo.

## 2. Maquina de estados del workflow

```
en_cola -> corriendo -> listo
              |     \-> bloqueado_esperando_humano -> corriendo (resume)
              |                                     \-> abortado
              \-> FALLO (solo si el error ocurre FUERA de un nodo, ej. guardia)
```

`corriendo -> bloqueado_esperando_humano` dispara SIEMPRE que: (a) un proveedor
lanza excepcion Y no quedan mas en la cadena, o (b) el output no valida
(sandbox bloqueado, syntax error). Nunca esperar al timeout del workflow
completo para notificar -- el evento `human_gate` se emite en el momento del
fallo del nodo, no al final.

Acciones humanas permitidas en `bloqueado_esperando_humano` (las 4, sin mas):
- **reintentar**: mismo nodo, mismo input, siguiente proveedor de la cadena.
- **editar_input**: mismo nodo, input modificado por el humano, reintenta.
- **saltar**: marca el nodo como omitido, sigue al siguiente si el workflow lo permite.
- **abortar**: `node_end` con `estado=abortado`, libera el lock del departamento.

## 3. Schema del backlog (`~/plataforma/backlog.jsonl`, un depto o compartido)

```json
{"id":"bl-a1b2","pregunta":"como influye el quechua en la musica andina contemporanea","origen_informe":"20260717-151714-idioma-quechua.md","linaje":["bl-0000"],"score":0.0,"estado":"pendiente","fecha":"2026-07-17"}
```

- `linaje`: lista de ids padres, **profundidad maxima 3** (pregunta de
  pregunta de pregunta -> corta ahi, no sigue).
- Poblado: al cerrar cada informe, parsear la seccion "LAGUNAS DE INFORMACION"
  (ya existe en el formato actual, no hay que inventar el parser desde cero),
  una pregunta por bullet, dedup por hash del texto normalizado contra
  backlog+informes ya existentes.
- **3 reglas de poda** (sin esto la cola crece sin limite y quema tokens en
  deriva -- lo que Fable llamo "model collapse" del backlog):
  1. Maximo N preguntas derivadas por informe (tope duro, ej. 3).
  2. Profundidad de linaje capada en 3 (arriba).
  3. Cada K ciclos autonomos, un pase "curador": un LLM barato rankea el
     backlog pendiente y descarta lo redundante/trivial (marca
     `estado=descartado`, no borra -- el historial queda).
- `trabajo.py` hace `pop` del backlog (mayor score, mas viejo primero como
  desempate) antes de caer a las listas fijas de `roles.py` (que pasan de ser
  el motor a ser la semilla de arranque cuando el backlog esta vacio).

---

*Contrato completo. Con esto fijo, cada pieza (emisor de eventos, pausa,
lector del hub, backlog+poda) se implementa y prueba por separado.*
