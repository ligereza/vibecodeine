# iskvw · la cara visible

El portafolio cambia seguido. Esta carpeta existe para que **cambiar el estilo
no signifique rehacer el sitio**.

```
  datos/obras.json     el contenido            <- no se toca al cambiar de estilo
  datos/ESQUEMA.md     qué hay en ese archivo
  CONTRATO.md          qué debe cumplir cualquier piel
  PROMPT_ESTETICA.md   lo que se le pasa a un agente para pedir una estética nueva
  piel/                cada estilo, en su propia carpeta. Se despegan y se cambian
```

## Para pedir un estilo nuevo

Pasale a un agente —Arena, Google AI Studio, el que sea— estos tres archivos:

    PROMPT_ESTETICA.md
    CONTRATO.md
    datos/ESQUEMA.md

Lo que devuelva va a `piel/<nombre>/`. No tiene que tocar `datos/` ni nada más.
Si para que funcione hay que editar el contenido, la propuesta no cumple el
contrato.

## Por qué así

Tres razones, y las tres son del autor:

- **El estilo se reemplaza entero, no se parchea.** Cada piel vive aparte; la
  anterior no se borra.
- **El sitio no puede mentir.** Ningún elemento afirma un dato que no tiene: es
  la regla que gobierna todo este repo.
- **No es un sitio con título y menú.** La interfaz puede ser parte de la obra.
  Está explicado en el contrato.
