# El motor semántico: un agente ciego que dibuja

> Para qué existe este documento: para que nadie vuelva a escribir esto desde
> cero, y para que nadie confíe en él más de lo que aguanta. Las mediciones son
> de la sesión que lo produjo (2026-07-28) y están puestas con su método, no
> como titular. Las fuentes, verbatim, en
> [`REFERENCIAS_MOTOR.md`](REFERENCIAS_MOTOR.md).

## El problema, que no es el que parece

Un modelo escribe `<path d="M60,47 L36,-6 L52,-6Z">` y **no tiene forma de saber
si eso es un rayo de sol o un enredo**. Tiene un modelo *estructural* de la
imagen, no *pictórico*. Escribe geometría a ciegas.

Lo importante no es que se equivoque: es *cómo* se equivoca. En dos rondas de
revisión visual sobre 16 íconos escritos a mano aparecieron 7 defectos y
**ninguno era de sintaxis**. El 100% fueron fallas visuales sobre archivos
perfectamente válidos: un ícono invisible en reposo, una multitud sin contraste
contra el fondo, texto desbordando la hoja, una etiqueta chocando con el borde,
una composición desbalanceada.

**La falla visual es silenciosa.** El XML roto grita; el círculo vacío no dice
nada, pasa todos los tests y llega al entregable. En un pipeline de varios
agentes sin supervisión, ése es exactamente el error que sobrevive hasta el
final.

## La tesis

**Si el agente sólo puede expresar significado, no puede producir geometría
rota.** La falla silenciosa deja de ser improbable y pasa a ser *inexpresable*.

El agente escribe intención, nunca coordenadas:

```json
{"slug":"berlin", "composicion":"confrontacion", "tono":"concreto",
 "capas":[{"rol":"lado_izq","figura":"muro","gesto":"desplazar_fuera"},
          {"rol":"lado_der","figura":"muro","gesto":"desplazar_fuera"},
          {"rol":"protagonista","figura":"onda","gesto":"emanar"}]}
```

Vocabulario cerrado: **22 figuras · 12 gestos · 9 tonos · 6 composiciones ·
5 ritmos**. Cualquier palabra fuera de las listas se rechaza *con las opciones
válidas en el mensaje de error*, que es lo que hace baratísima la reparación.
Con tres capas, el espacio combinatorio queda del orden de 10⁹: acotado no
significa pobre.

## Lo medido

| Métrica | Motor semántico | Escritura directa |
|---|---|---|
| Specs compilados | 9 de 10 (1 rechazo legítimo) | — |
| XML inválido | **0** | 0 |
| Invisibles en el frame 0 | **0** | 1 de 16 |
| Texto desbordado | **0** | 2 de 16 |
| Fallas de contraste | **0** (2 autocorregidas) | 1 de 16 |
| **Defectos visuales totales** | **~11%** | **~44%** |

El rechazo era real: a esa spec le faltaba la capa `protagonista`. Reproducible
hoy, con el motor ya landeado:

```
py -c "..."   # ver tests/test_motor_semantico.py
compilados 9 / rechazados 1 (XML valido en los 9)
vocabulario: 22 figuras, 12 gestos, 9 tonos, 6 composiciones, 5 ritmos
```

Los cuatro modos de falla quedan eliminados **por construcción**, no por
revisión: no existe forma de expresar «empieza en opacidad cero»; el texto se
mide antes de dibujarse; el contraste se calcula con WCAG y si falla se cambia
el rol de color avisando; el agente no concatena strings, así que `&`, `<` y `>`
se escapan solos.

## El hallazgo más instructivo: mi propio QA mentía

Primer render del motor: **9 de 9 en negro**. El diagnóstico fácil era «el motor
no sirve». La medición dijo otra cosa:

```
colores distintos SIN <style> : 386   <- la geometría estaba perfecta
colores distintos CON <style> :   1   <- el renderizador la borraba
```

Aislado: un `transform-origin` de CSS junto a un `transform=` como atributo hace
que **cairosvg blanquee el elemento. Los navegadores lo renderizan bien.**

El SVG era correcto y la herramienta de verificación estaba equivocada. La
solución fue estructural —grupos anidados: `translate` exterior, clase animada
en el medio, `scale` interior— y así rota y escala sobre el centro sin depender
de `transform-origin`. Funciona en navegador **y** en el rasterizador.

> **La lección, que vale más que el motor:** un QA automático que discrepa del
> destino real produce falsos negativos catastróficos. Hay que validar el
> validador contra el navegador antes de confiar en él.

Por eso `rasterizador.py` tiene dos backends y por eso el navegador gana si
alguna vez discrepan.

## Lo que el motor NO resuelve

Dicho sin adornos, porque un documento que sólo vende es un documento que
engaña:

- **El techo creativo es real y se ve.** Estos íconos son *correctos y
  genéricos*. No hay nada como «el muro que se parte y libera ondas» del
  conjunto escrito a mano, donde la metáfora estaba en la geometría específica.
  Acá la metáfora está en la *elección de piezas*, que es una expresividad
  menor.
- **El equilibrio compositivo sigue necesitando ojo.** Tras arreglar el render
  hubo dos rondas más de ajuste, todas decididas mirando: rayos de fondo
  compitiendo con el protagonista, muros solapando la onda central, una multitud
  demasiado grande. Ningún chequeo estático detectó eso.
- **El crítico perceptual premia lo convencional.** Mide seis propiedades sobre
  píxeles (tinta, centrado, dominancia, margen, legibilidad a 24 px, vida) y
  puntuó 95/100 al motor contra 72/100 a los hechos a mano. Es *parcialmente
  circular*: premia exactamente lo que el motor garantiza. Los íconos más
  expresivos son los que peor puntúan. **Es un filtro de primera pasada, no un
  juez de calidad**, y un sistema que optimice ciegamente ese número producirá
  trabajo correcto y sin riesgo — lo contrario de lo que un sistema de íconos
  sobre contracultura debería ser.
- **Nadie mide si la metáfora funciona.** Ni el crítico ni un CLIP score. Eso no
  se deduce de los píxeles ni del código.

Dos bugs propios encontrados midiendo, que explican por qué el crítico está
calibrado como está: marcaba «60 familias de color compiten» cuando **801 de 808
colores eran antialiasing de bordes**, y marcaba 8 íconos por «tocar el borde»
cuando eran **sangrados deliberados**. Se corrigieron descartando familias bajo
el 4% del contenido y midiendo qué fracción de cada borde está cubierta (banda
completa = diseño, punta suelta = error).

## La consecuencia arquitectónica

| | Escritura directa | Motor semántico |
|---|---|---|
| Falla silenciosa | ~44% | **~11%** |
| Techo creativo | **alto** | medio |
| Necesita ojo | sí, por pieza | sí, por **vocabulario** |
| **Costo del ojo** | **O(n)** | **O(1) amortizado** |

Esa última fila es todo el argumento. El ojo sigue siendo necesario, pero se
gasta **una vez al ampliar el vocabulario**, no en cada pieza.

**Conclusión: híbrido.** El motor como piso garantizado para el grueso;
escritura directa con revisión visual obligatoria para las tres o cuatro piezas
insignia donde la metáfora justifica el costo. Los 16 íconos del ensayo rave son
del segundo tipo y se quedan como están.

Y una consecuencia que sí es una decisión, no una medición: **el estilo no se
unifica**. Cada tema que se investigue pide su propia presentación, así que el
modo por defecto es `coro` (polifónico) y no `sistema` (unificado). Ver
[`FORMATO_ENSAYO.md`](FORMATO_ENSAYO.md).

## Lo que dice la literatura

La búsqueda confirmó las conclusiones y aportó una corrección. Detalle y citas
textuales en [`REFERENCIAS_MOTOR.md`](REFERENCIAS_MOTOR.md); lo que cambia
decisiones:

- **Nadie deja a un modelo escribir coordenadas libres.** Chat2SVG llegó a la
  misma solución textualmente: *«un sistema de prompts que dirige a los LLM a
  generar plantillas SVG usando primitivas geométricas básicas»*.
- **El diagnóstico está publicado.** SVGFusion: los modelos que generan SVG
  *«como una secuencia plana de tokens tienen mala comprensión estructural y
  acumulan errores»*. Es exactamente el 44%.
- **El estado del arte es mediocre**: SVGenius mide los mejores modelos en SSIM
  ~54%. No es un problema resuelto.
- **La advertencia central**, de una revisión de structured outputs: *«una
  respuesta garantizada como válida no es una respuesta garantizada como
  correcta, y el error más caro en producción es confundir las dos»*. Es
  literalmente lo que medimos: cero errores de validación y aun así dos rondas
  de corrección visual.
- **La corrección que aportó**: SVGFusion explica por qué el código SVG no es un
  buen espacio semántico — *«SVG sintácticamente distintos pueden ser
  visualmente similares»*, así que fusionan código con la imagen rasterizada.
  **El píxel es lo que ancla el significado**: confirmación independiente de que
  el render no es opcional.

## El puente que no era metáfora

Los vectores del SVG y los vectores semánticos **no son parientes: son
homónimos**. Mover un punto de `(60,58)` a `(61,58)` no significa nada
semánticamente.

Pero hay una conexión real. Las *Vector Symbolic Architectures* construyen
estructuras con dos operaciones —binding (rol ⊗ relleno) y superposición (⊕)— y
el spec del motor ya tenía esa forma exacta:

```
BERLÍN = (lado_izq ⊗ muro ⊗ desplazar_fuera)
       ⊕ (lado_der ⊗ muro ⊗ desplazar_fuera)
       ⊕ (protagonista ⊗ onda ⊗ emanar)
```

Sin buscarlo, el motor semántico es una VSA simbólica. Eso habilita álgebra
sobre el significado, implementada en `algebra.py`: analogía
(`BERLÍN − muro + grilla` = «la vigilancia que se parte y emite»), transferencia
de estilo, interpolación (camino mínimo entre dos conceptos, cada paso un SVG
válido) y distancia semántica (`d(TAZ, ACID) = 6`, una métrica sobre conceptos y
no sobre píxeles).

El spec vive en un espacio discreto composicional y el compilador es una función
determinista spec→geometría; por lo tanto **operar algebraicamente sobre el
significado produce operaciones predecibles sobre la forma**. El puente está en
el spec, no en el path.

## Dónde vive y cómo se usa

| Pieza | Ruta |
|---|---|
| El motor (Python, corre en la caja dentro de codex) | `cultura/mak_codex/motor_semantico/` |
| El modo de codex que lo invoca | `cultura/mak_codex/iconos.py` (modo `iconos`) |
| El gemelo de navegador, sobre thi.ng | `docs/cultura/lib/compilador.js` |
| El vocabulario exportado como datos | `docs/cultura/lib/vocabulario.json` (lo genera `tools/gen_vocabulario_motor.py`) |
| Un conjunto de íconos: validar y construir su galería | `tools/iconos_conjunto.py` |

```bash
# compilar una spec a mano
py cultura/mak_codex/motor_semantico/compilador.py spec.json salida.svg

# el vocabulario cerrado, tal como se le entrega al modelo
py -c "import sys; sys.path.insert(0,'cultura/mak_codex'); from motor_semantico import esquema; print(esquema.resumen_para_prompt())"

# en la caja: brief -> spec -> SVG
python3 iconos.py "el muro que se parte y libera ondas"
```

**Dos implementaciones, una sola fuente de verdad.** La geometría no se portó a
mano al navegador: se **exporta** desde `vocabulario.py` como datos, y
`gen_vocabulario_motor.py --verificar` falla si el JSON quedó viejo. Portarla a
mano habría creado dos fuentes divergiendo, que es el defecto que ya costó caro
acá (los ids del micelio y los del campo se formaban en dos lugares: 1004 piezas
y 0 posiciones).

## thi.ng: qué usa, qué no, y por qué

El estado real —con las candidatas y sus prioridades— está en la sección 6 de
[`CAPACIDADES.md`](../../CAPACIDADES.md), que es el índice que un agente lee
*antes* de escribir un generador desde cero. Lo específico de este motor:

- **`@thi.ng/hiccup` + `@thi.ng/hiccup-svg` — en uso** en el compilador de
  navegador. Retiran la concatenación de strings: el árbol SVG se arma con
  `svg/group/rect/text` y se serializa. Es la #5 de la recomendación externa y
  la que de verdad se solapa con este motor.
- **`@thi.ng/color` — en uso** en el mismo compilador: el contraste WCAG lo
  calcula la librería en vez de repetir la fórmula de luminancia relativa.
- **`@thi.ng/geom` — candidata sin medir.** Se solapa con las 22 figuras, que
  hoy son geometría escrita a mano. Adoptarla es un trabajo real y quedaría
  justificado si el compilador de navegador demuestra ser el camino principal.
- **Por qué no entra al motor Python**: son TypeScript. Dentro de codex no hay
  runtime de Node garantizado, así que el motor Python queda como está y thi.ng
  paga donde no hay Python — el navegador, que además es el norte del repo
  (mejorable sin PC).

## La arquitectura de agentes que esto habilita

| Agente | Hace | Prohibido |
|---|---|---|
| **Curador** | fuente → conceptos con slug, título y *brief visual* | dibujar |
| **Director de arte** | asigna tono y composición, evita colisiones entre vecinos | dibujar |
| **Ilustrador ×N** | brief → spec semántica | decidir significado |
| **QA / integrador** | esquema → crítico → render → rechazo con motivo | corregir en silencio |

El paralelismo real está en el ilustrador; los otros tres son cuellos de botella
deliberados. Y la granularidad no es «un ícono por sección» sino **un ícono por
concepto nombrable con una frase nominal**: si es «la relación entre X e Y bajo
Z», hay que partirlo o fundirlo. Cualquier tema cae entre 6 y 24 a esa
granularidad.
