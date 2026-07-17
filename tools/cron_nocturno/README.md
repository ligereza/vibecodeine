# Pieza MANIFIESTO #6 -- CRON NOCTURNO CON BORRADO

Parte de la serie motor-omega (`projects/tapiz`, dossier
`projects/cultura/dossiers/tapiz.md`). Motor local: no usa red, no usa la
API de Claude/Anthropic. Solo stdlib de Python + la libreria real
`projects/tapiz/vibecode/loom.py` (se importa como libreria, no se
reescribe).

## Concepto

- `generate`: cada noche produce UNA variante SVG nueva usando el motor
  loom real. El motivo (loom mode: `field`/`border`/`medallion`/`mihrab`
  o uno de los 16 motifs-plugin de `vibecode/motifs/`, 20 en total) y el
  caracter de relleno se derivan deterministicamente de la fecha: el mismo
  dia siempre produce la misma pieza; un dia distinto casi siempre produce
  un motivo distinto. La fuente digerida es el propio `loom.py` -- el
  motor se teje a si mismo cada noche.
- `purge`: una vez por semana (dia configurable, default domingo), si hay
  2 o mas variantes acumuladas, borra UNA. La variante condenada se elige
  con un hash SHA-256 del numero de semana ISO -- nunca con el modulo
  `random`. Es auditable a mano (cualquiera puede recalcular el hash y
  verificar cual toca) pero ciego (nadie mira contenido, edad ni "valor"
  de las piezas antes de decidir).

## Omega11 (condicion de fracaso, declarada por el director)

La pieza PIERDE si el borrado es reversible (papelera, backup, copia
oculta) o si requiere una decision humana (confirmacion, revision antes de
borrar). Por eso:

- `purge()` usa `os.remove()` -- borrado real de filesystem. No hay
  papelera, no hay copia previa, no hay paso de "estas seguro?".
- La eleccion del archivo condenado es una funcion pura de la fecha (hash
  del numero de semana ISO), no un `input()` ni una revision manual.
- El proceso completo corre desatendido via Task Scheduler / cron (ver
  abajo): nadie lo dispara a mano ni lo mira antes de que corra.
- Sin llamada a red ni a la API de Claude: todo el motor es stdlib local.

## Uso

    py tools\cron_nocturno\nocturno.py generate
    py tools\cron_nocturno\nocturno.py purge

Overrides utiles (los mismos que usan los tests, ver
`tests/test_cron_nocturno.py`):

    py tools\cron_nocturno\nocturno.py generate --out C:\ruta\otra --date 2026-07-16
    py tools\cron_nocturno\nocturno.py purge --out C:\ruta\otra --lapidas C:\ruta\lapidas.log --weekday 6 --min-variants 2

Variables de entorno equivalentes (se usan si no se pasa `--out` /
`--lapidas`):

    CRON_NOCTURNO_SALIDAS   directorio de salidas (default: salidas/)
    CRON_NOCTURNO_LAPIDAS   ruta de lapidas.log (default: lapidas.log)

## Salidas (gitignoradas)

    tools/cron_nocturno/salidas/

El director debe agregar esa linea a `.gitignore` (este modulo no lo edita
por su cuenta, ver instrucciones de la tarea).

`lapidas.log` SI se versiona: es el registro/evidencia de que la pieza
corrio y borro algo real (fecha + nombre de archivo, nunca contenido), no
un artefacto generado descartable.

## Instalar el cron nocturno

### Windows: Task Scheduler (`schtasks`)

Generar cada noche a las 23:50, y purgar cada domingo a las 23:55 (ajustar
la ruta de `py` y del repo si difieren de `C:\IA\flujo`):

    schtasks /create /tn "flujo_cron_nocturno_generate" /tr "py C:\IA\flujo\tools\cron_nocturno\nocturno.py generate" /sc daily /st 23:50

    schtasks /create /tn "flujo_cron_nocturno_purge" /tr "py C:\IA\flujo\tools\cron_nocturno\nocturno.py purge" /sc weekly /d SUN /st 23:55

Verificar que quedaron creadas:

    schtasks /query /tn "flujo_cron_nocturno_generate"
    schtasks /query /tn "flujo_cron_nocturno_purge"

Desinstalar (si hace falta):

    schtasks /delete /tn "flujo_cron_nocturno_generate" /f
    schtasks /delete /tn "flujo_cron_nocturno_purge" /f

### Termux (Android, cron via `cronie`)

    pkg install cronie
    crontab -e

Agregar (ajustar la ruta del repo clonado en el telefono):

    50 23 * * * cd ~/flujo && python tools/cron_nocturno/nocturno.py generate >> tools/cron_nocturno/cron.log 2>&1
    55 23 * * 0 cd ~/flujo && python tools/cron_nocturno/nocturno.py purge >> tools/cron_nocturno/cron.log 2>&1

Termux no arranca el demonio de cron solo, hay que habilitarlo:

    sv-enable crond
    crond

## Archivos

- `nocturno.py` -- motor `generate`/`purge` (stdlib + import de
  `projects/tapiz/vibecode/loom.py` como libreria).
- `salidas/` -- variantes SVG generadas (gitignorado, ver arriba).
- `lapidas.log` -- registro de borrados (fecha + nombre de archivo, nunca
  contenido; se crea la primera vez que `purge()` borra algo).
