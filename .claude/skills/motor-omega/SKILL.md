---
name: motor-omega
description: "Protocolo Ω para arrancar cualquier proyecto/pieza nueva en flujo: solo desde una ⊕ heredada o pedido real, con condición de fracaso Ω11 declarada antes de producir. Usar cuando se proponga proyecto, obra, feature o pieza nueva."
---

# Motor Ω — protocolo de arranque para flujo

Adaptación del motor generativo de `idea_generativa/v2/MOTOR.md` a producción real
(código, piezas visuales, features, entregas). Ahí el motor produce obras desde
residuos fechados; acá produce lo mismo — cosas nuevas en flujo — con la misma
disciplina: nada arranca porque "sería buena idea", todo arranca desde algo que
ya existe y quedó pendiente, o desde un pedido real de alguien.

Esta skill se invoca ANTES de escribir la primera línea de una pieza/proyecto/
feature nueva, no después. Si ya está en marcha, releé esto igual: el paso 4
(Ω11) tiene que quedar declarado antes de exponer el resultado, no importa en
qué punto lo agarrés.

## Los 5 pasos, en orden, sin saltear

### (a) Semilla
Elegí una ⊕ viva de `puente/SEMILLAS.md`, o un pedido real que esté en `inbox/`
(correo, encargo, entrega pendiente). Está **prohibido** arrancar de "tengo una
idea buena" — eso no es una semilla, es inercia con disfraz. Si no hay ⊕ viva
que sirva y no hay pedido real en inbox, no hay paso (a): el motor se queda
apagado y eso es el resultado correcto, no un bloqueo a resolver.

Antes de seguir, nombrá en voz alta (o por escrito) cuál ⊕ o qué ítem de inbox
es el origen. Si no podés nombrarlo, todavía no hay semilla.

### (b) Precipitación
Usá los templates de `knowledge/` (`knowledge/templates/*.for_ai.json`, o los
de referencia en `knowledge/examples/`, `knowledge/logos/`, `knowledge/venues/`,
`knowledge/productoras/`) para bajarle el umbral a la semilla — no para
decorarla. La operación es: juntar la semilla con el material que ya existe y
generar variantes que compartan núcleo pero diverjan en superficie. Si el
resultado es una sola variante obvia, todavía no precipitó — falta cruce.

### (c) Sobre-narración
Empujá el material hasta que sostenga más de una lectura sin colapsar en la
primera ocurrencia. Si el proyecto lo pide, usá multi-agente (subagentes,
distintos roles) para forzar esa ambigüedad en vez de resolverla de una. El
criterio de parada es productivo, no exhaustivo: parás cuando las lecturas
divergentes siguen siendo defendibles, no cuando se te acaban las ideas.

### (d) Ω11 — declaración de fracaso, ANTES de producir
Antes de producir la pieza final (no después, no al entregar), escribí:
**"Esta pieza pierde si ______."**

La condición tiene que ser evaluable por alguien que no seas vos — un cliente,
un lector, un usuario, quien recibe la entrega. Una Ω11 que solo vos podés
juzgar ("pierde si no me convence") no cuenta: eso deja la pieza en suspenso
igual que dejó a OBRA_02 en `idea_generativa`. Escribí la Ω11 en el mismo lugar
donde vayas a registrar el resultado (ver paso e) para que quede fechada junto
con la semilla.

### (e) Registro
El resultado —éxito, indiferencia o fracaso— se fecha en `puente/SEMILLAS.md`,
en la misma tabla que las ⊕ existentes. Un fracaso **no se reinterpreta**: si
la Ω11 se cumplió, se anota como fracaso y punto, no se busca cómo en realidad
funcionó igual. Si la pieza deja un residuo nuevo (algo que no cruzó, algo que
quedó pendiente y es rastreable), esa es la ⊕ siguiente — entra a la tabla con
fecha y origen.

## Regla de freno

El descanso es un ancla del sistema (equivalente a F2/Q1 en `idea_generativa`),
no una pausa entre tareas. **No generás por inercia.** Si alguien pide un
proyecto/pieza/feature nueva "porque toca", "para no estar parado", o sin poder
señalar cuál ⊕ o cuál pedido real lo origina — eso viola el protocolo en el
paso (a). La respuesta correcta ahí no es forzar una semilla: es decir que no
hay semilla y parar.

## Estado vivo

Las semillas ⊕ vigentes están en `puente/SEMILLAS.md` — leelo siempre antes de
correr el paso (a); no asumas cuáles siguen vivas desde memoria. Al día de
escribir esto hay tres registradas (⊕₁, ⊕₂ bloqueada esperando lector humano,
⊕₃), pero esa tabla cambia y es la fuente de verdad, no esta skill.
