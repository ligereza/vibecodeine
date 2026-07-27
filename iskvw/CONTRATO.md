# Contrato de la cara visible de iskvw.cl

Este documento existe para que **el estilo del portafolio se pueda reemplazar
entero sin tocar el contenido ni romper nada**. El portafolio cambia seguido;
lo que no cambia es lo que hay que mostrar y lo que no se puede mentir.

Se lo podés pasar completo a un agente externo (Arena, Google AI Studio, el que
sea) junto con `PROMPT_ESTETICA.md`, y lo que devuelva tiene que encajar acá sin
que nadie edite los datos.

---

## Las tres capas, y por qué están separadas

```
  datos/obras.json     CONTENIDO   -- no cambia cuando cambia el estilo
  CONTRATO.md          CONTRATO    -- qué hay que mostrar y qué no se puede mentir
  piel/<la-que-sea>/   PIEL        -- se despega y se reemplaza entera
```

La piel **consume** los datos y **cumple** el contrato. No los modifica, no
agrega campos, no inventa. Si una piel necesita un dato que no está en
`obras.json`, ese dato se agrega primero al contenido — nunca se hardcodea en
la piel, porque entonces deja de ser reemplazable.

---

## Qué recibe una piel

Un único archivo: `datos/obras.json`. Su forma está en `datos/ESQUEMA.md` y
cada campo dice si es obligatorio o puede faltar.

Nada más. Sin API, sin backend, sin build propio del contenido. Una piel es
HTML/CSS/JS (o un bundle) que lee ese JSON y lo dibuja.

---

## Lo que cualquier piel tiene que cumplir

Estas cinco no son estéticas: son las que hacen que el sitio no mienta y que se
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

## Cómo se cambia el estilo

1. Se le pasa a un agente `PROMPT_ESTETICA.md` + este contrato + `datos/ESQUEMA.md`.
2. Lo que devuelva se pone en `piel/<nombre-nuevo>/`.
3. Se abre. Si cumple las cinco reglas de arriba y se ve bien, se apunta ahí.
4. La piel anterior queda en su carpeta: cambiar de estilo no borra el anterior.

No hace falta tocar nada más. Ese es el punto.
