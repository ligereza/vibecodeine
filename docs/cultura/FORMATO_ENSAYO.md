# FORMATO ENSAYO

> Qué es: el formato de salida largo del órgano research de MAK, un nivel por
> encima del informe. Existe porque el informe actual —`1. RESUMEN EJECUTIVO /
> 2. HALLAZGOS / 3. ANÁLISIS CRÍTICO / 4. LAGUNAS / 5. PRÓXIMOS PASOS`— produce
> un documento correcto que nadie lee dos veces: enumera, no argumenta, y no
> deja nada que se pueda mirar.
>
> El ejemplo canónico, y el que fijó el nivel, es
> [`ensayos/rave/ensayo.md`](ensayos/rave/ensayo.md) con su anexo de 16 íconos
> animados.

## Las siete exigencias

Un documento es un **ensayo** cuando cumple las siete. Si falla una, es un
informe, y está bien que lo sea — pero no se llama ensayo.

1. **Partes narradas, no secciones enumeradas.** «PARTE IV: EL ÁCIDO — La doble
   hélice del movimiento» dice de qué se trata y anticipa una tesis. «4.
   HALLAZGOS» no dice nada. Entre 5 y 8 partes, cada una con subsecciones
   numeradas para poder citarlas.
2. **Una tesis que se puede negar.** El ensayo afirma algo que un lector podría
   discutir, y lo sostiene. Ejemplo real: «la ilegalidad no fue un accidente
   sino, en distintos momentos, recurso, filosofía y obligación» — y después una
   tabla que separa esos tres.
3. **Al menos una tabla donde dos lecturas compiten.** No una tabla de datos:
   una tabla que *distingue*. «RAVE como CONCEPTO» contra «RAVE como CULTURA» en
   cinco filas hace un trabajo que tres párrafos no hacen.
4. **Una cronología.** Fechas con su hecho. Es lo que convierte el ensayo en
   material reutilizable: de ahí salen los posts, las fichas y las charlas.
5. **Un cierre que argumenta**, no que resume. La última línea del ensayo rave es
   una cita que reordena todo lo anterior. Un cierre que repite el resumen
   ejecutivo delata que no había tesis.
6. **Fuentes con URL, obligatorias.** Cada afirmación que un lector podría
   querer verificar dice de dónde viene. Si el ensayo entrecomilla, la cita
   tiene procedencia. **Cuando falten, se declara la deuda en la cabecera** —
   como hace hoy el ensayo rave. Lo que no se hace nunca es inventar una URL
   para tapar el hueco.
7. **Anexo iconográfico**: un ícono por concepto nombrable. Ver abajo, que es la
   parte que este repo puede verificar sola.

## El anexo iconográfico

**Un ícono por concepto nombrable con una frase nominal.** Si el concepto es «la
relación entre X e Y bajo Z», hay que partirlo o fundirlo. Cualquier tema cae
entre 6 y 24 conceptos a esa granularidad; el ensayo rave tenía 7 partes y ~25
subsecciones, y 16 fue donde cada cosa era nombrable.

El manifiesto es `iconos.json`, un objeto por concepto:

```json
{
  "n": "07",
  "archivo": "07-berlin-muro-techno.svg",
  "slug": "07-berlin-muro-techno",
  "titulo": "Berlín: cae el muro, sale el techno",
  "descripcion": "1989: búnkeres, centrales y fábricas de la RDA se vuelven catedrales de una religión secular sin puertas.",
  "estilo": "Brutalista concreto",
  "ancla": "### 2.5 Berlín: El Muro Cae, el Techno Emerge"
}
```

`ancla` no es decoración: **es el pasaje del ensayo que justifica el ícono.** El
texto es el órgano que justifica el contenido que sustenta la forma. Un ícono sin
ancla reclama un significado que el ensayo no le dio, y eso es exactamente lo que
la tesis doublecup prohíbe: *ningún elemento reclama un dato que no codifica*.
`tests/test_ensayo_rave.py` exige que cada `ancla` sea un título real del ensayo.

### El estilo NO se unifica

Decisión del usuario, 2026-07-30: **cada tema que se investigue es distinto, y
cada palabra carga un valor cultural de distinta presentación.** Así que el modo
por defecto es:

- **`coro`** (polifónico) — cada pieza con su propio lenguaje visual. Es el
  default para cualquier tema cultural. En el ensayo rave son 16 lenguajes
  distintos, y la heterogeneidad argumenta lo mismo que el contenido: un tema
  sobre marginalidad y sobre negarse a ser estandarizado no se ilustra con una
  grilla única.
- **`sistema`** (unificado, una grilla, una paleta) — sólo para temas técnicos,
  y **sólo si la elección queda justificada por escrito** en la cabecera del
  ensayo. No es un default, es una excepción argumentada.

El vocabulario del motor semántico se **amplía por tema**: ahí es donde se gasta
el ojo humano, una vez, en vez de gastarlo pieza por pieza.

### El artefacto es una animación, y es editable

No es un ícono estático. Cuatro consecuencias, que son reglas:

1. **SVG animado con CSS**, con la paleta y las velocidades declaradas como
   variables al inicio del archivo. Cambiar un color o un ritmo no puede romper
   la animación, porque la apariencia está separada del motor de animación.
2. **Una capa por elemento, con nombre.** Todo grupo del compilador sale como
   `<g id="capa-2-protagonista" data-rol data-figura data-gesto data-ritmo>` con
   su `<title>`. Eso hace dos cosas: se abre en Illustrator o Inkscape como capa
   con nombre —se edita en diseño y se vuelve a integrar— y **cada elemento
   responde por lo que codifica** sin que nadie tenga que mirarlo.
3. **Nada rígido.** Los 16 del ensayo rave están escritos a mano y se editan a
   mano; los que compile el motor se editan igual, porque salen con la misma
   estructura de capas nombradas.
4. **La verificación es un GIF, no un PNG.** Un cuadro suelto no distingue
   *quieto* de *animado*: valida algo que no es lo que se construyó.
   `py tools/iconos_conjunto.py animar` rasteriza cuadros a lo largo del ciclo y
   **cuenta cuántos son distintos**. Medido el 2026-07-30 sobre los 16: los
   dieciséis dan 10 de 10. La regla que lo sostiene es de coherencia y no un
   umbral: **un ícono que declara `@keyframes` tiene que moverse dentro de su
   propio ciclo**, y el ciclo se le pregunta al archivo en vez de suponer una
   ventana fija. La primera medición dio un falso positivo —un ícono acusado de
   estático— y el defecto era del instrumento, no de la pieza. Los GIF no entran
   al repo: son instrumento de medición, no entregable.

### Los comandos

```bash
# el conjunto no está roto (7 clases de error, incluida la var(--x) sin declarar)
py tools/iconos_conjunto.py validar   --raiz docs/cultura/ensayos/<tema>

# regenerar la galería desde iconos/ + iconos.json (incluye el taller del motor)
py tools/iconos_conjunto.py construir --raiz docs/cultura/ensayos/<tema>

# ¿de verdad se mueve? cuadros distintos por ícono
py tools/iconos_conjunto.py animar    --raiz docs/cultura/ensayos/<tema> --salida <scratchpad>
```

`galeria.html` es **generada**: no se edita a mano. Trae además un *taller* que
compila una spec semántica en el navegador, así que el lector puede cambiar una
palabra y ver la forma cambiar sin instalar nada.

## Cómo lo produce MAK

```bash
# en la caja
python3 research.py "<tema>" --formato ensayo [--iteraciones N] [--densidad largo]
```

`--formato ensayo` cambia dos cosas: el prompt del documento final (las siete
exigencias van en el prompt, no en la esperanza) y una salida extra
`<stamp>-<slug>.conceptos.json` con los conceptos nombrables que detectó, ya en
la forma que consume el modo `iconos` de codex.

El contrato vive en `cultura/mak_research/formato_ensayo.py` como módulo aparte y
testeado, no como un string dentro de `research.py`: ese archivo tiene su propio
prompt del 2026-07-20 y la regla de esta sesión es no parchear a ciegas nada de
más de una semana.

Después, un ícono por concepto:

```bash
python3 iconos.py "<brief visual del concepto>"     # modo iconos de codex
```

El ilustrador escribe **significado** —vocabulario cerrado, sin coordenadas— y el
compilador determinista hace la geometría. El porqué, con sus mediciones y sus
límites honestos, está en [`MOTOR_SEMANTICO.md`](MOTOR_SEMANTICO.md).

## Dónde vive un ensayo

```
docs/cultura/ensayos/<tema>/
  ensayo.md            el documento
  iconos/*.svg         la FUENTE de los íconos, editable
  iconos.json          el manifiesto: un concepto nombrable por entrada
  GUIA-DE-EDICION.md   qué se puede tocar y con qué cuidado
  galeria.html         GENERADA
```

Un ensayo es material del que salen cosas: un post de RD, una ficha, una pieza
del portafolio. No es el final de la cadena.
