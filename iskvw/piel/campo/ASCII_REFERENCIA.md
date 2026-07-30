# Piel ASCII: la técnica, no la rama

> Extraído el 2026-07-30 de `rescate/ascii-campo` (commit `2d63fd6`), que quedó
> 33 commits atrás de `main`. Mergearla hoy **revertiría** la semilla
> reproducible y los vínculos por peso: su `index.html` son 206 líneas nuevas
> contra 354 borradas, y tiene 3 referencias a `semilla`/`VINCULOS` donde main
> tiene 12. Lo que vale de esa rama es la técnica; se guarda acá para que la
> decisión sea «¿me gusta esta piel?» y no «¿acepto perder lo de hoy?».

## Qué hace distinto

En vez de dibujar el trazo de cada obra como **contorno**, lo **muestrea** y lo
pinta como **patrón ASCII** sobre un canvas propio (`.obra-ascii`). La razón
está escrita en el propio código de la rama:

> *«en Safari los vectorizados se vuelven monótonos, y el svg tiene que ser la
> forma animada, ASCII como patrón, no una línea. Así que el trazo deja de
> dibujarse como contorno: se MUESTREA la forma.»*

Es una decisión estética con una causa técnica real: el contorno vectorizado
pierde carácter en un motor de render, y el muestreo lo recupera como textura.

## El código, tal como estaba

```css
#f-obra .obra-ascii{height:100%;width:auto;display:block;position:static;
    inset:auto;transform-origin:left center;
    transform:skewX(calc(var(--gesto,0) * -7deg)) scaleY(calc(1 + var(--gesto,0) * .06));
    transition:transform .12s linear}
```

```js
/* ── la obra como PATRON, no como linea ──
   El usuario, mirandolo en Safari: los vectorizados se vuelven monotonos, y el
   svg tiene que ser la forma animada, ASCII como patron, no una linea.

   Asi que el trazo deja de dibujarse como contorno. Se MUESTREA la forma -- los
   paths del SVG que MAK vectorizo -- y en cada punto se pone un glifo. La obra
   es lo que la nube de glifos deja ver.

   Y es GENERATIVO, no una animacion guardada: el glifo de cada punto sale de
   evaluar un campo que evoluciona (dos ondas incomensurables mas la distancia
   al centro), asi que el patron nunca se repite y nunca es igual entre dos
   obras. Lo que cambia por obra no lo elegi yo, sale de lo que el archivo ya
   mide: la densidad del trazo y su tilde.

   Canvas y no <text>: cientos de nodos de texto en el DOM es justo el patron
   que este repo ya midio y arreglo en el micelio de MAK. */
const RAMPA = ' .:-=+*#%@';        // de menos a mas materia
const _forma = new Map();          // id -> puntos muestreados, una sola vez
```

## Cómo se aplicaría hoy

Sobre el `index.html` actual de `main`, que ya trae la semilla (`#semilla=`) y
el dibujado de vínculos. La técnica es independiente de las dos: cambia CÓMO se
pinta cada obra, no qué se posiciona ni qué se une. No se mergea la rama; se
aplica esto encima.
