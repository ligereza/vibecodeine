# Revisión de enfoque — 2026-09-11

## Decisión de esta iteración

La evidencia del código mostró una diferencia real: la APK nativa ya agrupaba
por productora y exigía logo cargado, mientras que la PWA HTTP de XIO mostraba
un selector plano. También FLUJO era responsive por CSS, pero no declaraba qué
vista estaba usando el navegador.

Se eligió un parche directo y reversible sobre esas dos superficies, más un
placeholder honesto para el venue más repetido. No se eligió rediseñar el hub,
crear otra APK, agregar puertos, ni delegar la tarea: esas opciones ampliarían
el alcance y podían romper el despliegue existente.

## Riesgo que se evitó

- No se mezclan eventos sin logo ni se inventa un evento desde el teléfono.
- La PWA y la APK quedan bajo la misma política de catálogo del host.
- El venue “más repetido” no se afirma hasta conectar el conteo real de
  `triangular.py`.
- FLUJO conserva una sola aplicación; sólo declara visualmente celular o
  escritorio según el viewport.

## Señales de verificación

1. Comprobar sintaxis de ambas copias de `rd_field/static/app.js`.
2. Ejecutar typecheck y builds de FLUJO.
3. Ejecutar las pruebas existentes de bridge/plugin de XIO.
4. Revisar diff y estado Git antes de cualquier commit; no incluir cambios
   ajenos.

## Supuestos visibles

- `logo_loaded` es la señal que el bridge actual publica para que la APK pueda
  seleccionar una productora.
- El orden de eventos debe conservar el orden del catálogo del host; no se
  presenta como ordenamiento cronológico.
- La base de datos sigue perteneciendo al proceso que corre el servidor: XIO
  en Xiaomi para operación offline, o el PC cuando éste es el host. El cliente
  del Xiaomi sólo consume la superficie HTTP del host.
