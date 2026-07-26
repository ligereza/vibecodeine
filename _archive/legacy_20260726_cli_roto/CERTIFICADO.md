# Retirado el 2026-07-26: dos caminos de la CLI que no funcionaban

No se archivaron por viejos. Se archivaron porque **estaban rotos** y la CLI los
seguía ofreciendo como si funcionaran. Medido ejecutándolos, no leyéndolos.

## `portal.py` — comando `flujo portal`

Exportaba un HTML estático para jefatura, con los estados de los jobs y links a
GitHub Issues, planteado como alternativa gratuita a monday.com.

**Cómo falla:** `py -m flujo portal -o salida.html` termina en
`AttributeError: 'dict' object has no attribute 'replace'`.

Además, aunque se arreglara, hoy choca con dos cosas del repo:

- el panel **Trabajos** de la app ya muestra el estado de cada job, en vivo;
- los GitHub Issues son un **canal de entrada** (Gmail -> issue -> render), no un
  tablero de tareas. Decisión del usuario, 2026-07-26.

Último commit que lo tocó: 2026-06-30, el commit inicial del repo.

## `app_gradio.py` (era `scripts/app.py`) — opción `flujo serve --legacy`

Una segunda interfaz web, en Gradio, anterior al hub.

**Cómo falla:** `--legacy` importaba `flujo.web.editor`, un módulo que **no
existe** en el paquete. Al fallar caía por `except` a ejecutar `scripts/app.py`,
o sea una tercera interfaz. Y `gradio` no está declarado en `pyproject.toml`, así
que en cualquier instalación limpia el camino ni siquiera arrancaba.

Último commit que lo tocó: 2026-06-30.

Con esto retirado, `flujo serve` y `flujo app` hacen exactamente lo mismo: lanzar
el hub. Se dejaron los dos nombres a propósito, porque los dos están en la
memoria y en la documentación; `app` llama a `serve`.

## Los tests pasaban mientras el comando reventaba

`test_portal_jefe.py` (archivado acá también) corría sobre un workspace vacío:
sin ningún job, el código nunca llegaba a la línea que falla. El
`AttributeError` aparece con jobs reales. O sea que la suite estaba en verde
sobre un comando roto, que es exactamente el defecto que describe `CLAUDE.md`:
un test que no ejercita el comportamiento real da falsa seguridad.

Si alguien revive el portal, el primer test tiene que ser con un job de verdad.

## Un cuarto punto de entrada

Al archivar `scripts/app.py` se cayó un test de `scripts/flujo.py`, que resultó
ser **otro despachador** con su propia lista de comandos armada desde la carpeta
`scripts/`. Ese test exigía que existiera un comando `app` que venía justamente
de la interfaz Gradio muerta, aunque su propio docstring decía que verificaba un
comando que funciona. Se corrigió la expectativa, no el comando.

La entrada real a la app es `py -m flujo app`.

## Si algo de esto hace falta de nuevo

Los archivos están acá completos y con su historia en git (`git mv`, no
borrado). El de portal necesita, antes que nada, que se arregle el
`AttributeError` y que se decida qué relación tiene con el panel de Trabajos,
que hace lo mismo mejor.
