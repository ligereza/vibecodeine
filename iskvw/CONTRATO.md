# Contrato de la cara visible de iskvw.cl

Este documento existe para que **el estilo del portafolio se pueda reemplazar o
cambiar en vivo sin tocar el contenido ni romper nada**. El portafolio cambia
seguido; lo que no cambia es el conjunto que se muestra y lo que no se puede
mentir.

Se lo podés pasar completo a un agente externo (Arena, Google AI Studio, el que
sea) junto con `PROMPT_ESTETICA.md` y `ESQUEMA_ARCHIVO.md`, y lo que devuelva
tiene que encajar acá sin que nadie edite los datos.

`datos/obras.json` conserva sólo el respaldo pequeño de herramientas del repo.
La fuente publicada se genera como `datos/archivo.json` y el manifiesto que le
fija selección y orden es `datos/portafolio.json`. Los ensayos de research son
una vista explícita, no el default.

---

## Las cuatro capas, y por qué están separadas

```
  datos/archivo.json       CONTENIDO   -- piezas y vínculos
  datos/portafolio.json    FORMATO     -- selección completa, orden y pieles
  CONTRATO.md              CONTRATO    -- qué hay que mostrar y qué no se puede mentir
  piel/<la-que-sea>/       PIEL        -- representación intercambiable
```

El manifiesto `datos/portafolio.json` se genera junto con `archivo.json`. Incluye
todos los ids de ese archivo, incluso cuando una pieza no tiene posición,
decisión o metadata completa. Su orden es determinista: posición medida cuando
existe; id estable cuando todavía no existe. Eso permite crear y mostrar un
portafolio completo sin convertir cada ausencia en `unknown` ni en una revisión
manual obligatoria.

Una piel de portafolio **consume** el manifiesto y los datos y **cumple** el
contrato. No los modifica, no agrega campos, no inventa. Si necesita un dato
que no está en `archivo.json`, ese dato se agrega primero al contenido — nunca
se hardcodea en la piel, porque entonces deja de ser reemplazable. La vista
geométrica SCD no es una piel: es una herramienta especializada de FLUJO en
`tools/venue3d/`, con su propio registro de venue y cadena de geometría.

---

## Qué recibe una piel

Una piel de portafolio recibe dos archivos generados: **`datos/portafolio.json`** y
**`datos/archivo.json`**. El primero fija la selección completa, orden, piel
por defecto y pieles disponibles; el segundo tiene dos listas, `piezas` y
`vinculos`. Su forma está en `ESQUEMA_ARCHIVO.md` y cada campo dice si es
obligatorio o puede faltar.

`datos/obras.json` y `datos/campo.json` siguen existiendo y son RESPALDOS: el
runtime común los pide sólo si `archivo.json` no está. Una piel nueva se
escribe contra el formato común; que degrade a los otros es opcional y se
declara.

Nada más para una piel de portafolio. Sin API, sin backend, sin build propio
del contenido. Una piel es HTML/CSS/JS (o un bundle) que lee ese JSON y lo
dibuja.

---

## Lo que cualquier piel tiene que cumplir

Estas reglas no son estéticas: son las que hacen que el sitio no mienta y que se
pueda cambiar sin miedo.

1. **Ningún elemento afirma un dato que no tiene.**
   Si una obra no tiene año, no se inventa ni se pone "2026" de relleno: se
   omite o se dice que falta. Un contador que dice "12 obras" muestra 12. Una
   barra de progreso que no mide nada no va.
   *Causa: es la regla que gobierna todo este repo, y ya arruinó piezas antes.*

2. **Todo texto visible en español correcto, con acentos y eñes.**
   "Diseño", no "diseno". Esto se le muestra a gente.

3. **Abre sin internet.**
   Sin CDN, sin fuentes remotas, sin analytics. Lo que necesite viaja adentro.
   *Causa: el sitio tiene que poder mostrarse desde un disco, en un evento, sin red.*

4. **Funciona en un teléfono.**
   No hace falta que se vea igual: hace falta que se pueda ver.

5. **La piel se puede borrar y poner otra sin tocar `datos/`.**
   Si para cambiar el estilo hay que editar el contenido, el contrato se rompió.

6. **Una clase de pieza o de vínculo que no conocés no se descarta ni se
   asimila.** El archivo crece: el sustrato público hoy trae `obra` y
   `pieza_grafica`; la vista explícita de research puede traer `concepto` e
   `informe`. Una piel que sólo dibuja lo que su autor conocía deja de mostrar
   el archivo sin avisar. Dibujala de la forma más neutra que tengas y decilo.
   *Causa: es el defecto que este repo encontró cinco veces en dos días — una
   lista escrita a mano que dejó de coincidir con lo que existe.*

7. **Las pieles de portafolio consumen la misma proyección.** El selector puede
   cambiar `campo` o `terminal` conservando query y hash; cambiar la piel cambia
   la lectura visual, no el archivo ni la selección. La vista geométrica SCD es
   una herramienta de venue en FLUJO, no una piel ni una lista de obras.

---

## Lo que NO tiene que ser

Esto es dirección, y viene del autor:

- **No es un sitio con título y menú de ventanas.** Nada de encabezado +
  navegación + secciones apiladas. Eso es lo convencional y es justo lo que no
  se quiere.
- **La interfaz puede ser la obra.** La referencia que dio el autor no es un
  documento con un menú: es un instrumento corriendo — un lienzo generativo vivo
  de fondo, secciones que se conmutan, una barra de estado que reporta lo que
  realmente pasa. Si la piel es un lienzo que se puede tocar, mejor.
- **El archivo es el tema.** Es un archivo de obra, no un currículum. No hay que
  vender: hay que dejar ver.

---

## Cómo se cambia la piel

1. El generador crea `datos/archivo.json` y su compañero
   `datos/portafolio.json`.
2. `campo` y `terminal` cargan ambos mediante `piel/lib/skin_runtime.js`; si el
   manifiesto todavía no está, conservan el orden del archivo y degradan a los
   respaldos. `sala` usa el mismo runtime para el selector, pero su contenido
   es el registro geométrico declarado por su `piel.json`.
3. El selector superior cambia entre las pieles declaradas y conserva query y
   hash. La raíz publicada abre `campo`; `terminal` comparte el conjunto.
4. Para agregar una piel de portafolio se pone en `piel/<nombre>/`, se declara
   en su `piel.json` y se pasa la batería. Las pieles anteriores no se borran.

La reemplazabilidad de archivos y la conmutación en ejecución son dos garantías
distintas: ahora ambas están conectadas y verificadas.

No hace falta tocar nada más. Ese es el punto.
