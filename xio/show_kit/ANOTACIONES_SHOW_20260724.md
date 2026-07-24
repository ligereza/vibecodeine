# Anotaciones show DREF CHOCOLATE -- 2026-07-24 (en vivo)

Registro pasivo. NO altera el setlist corriendo (xio 10.134.166.149) ni Chataigne.
Documenta cambios de ultimo momento para reconciliar despues del show.

## Tema agregado en vivo: "Random Friends" (con invitado)

- **Posicion:** entre `A Fuego` (idx 15) y `Misionar` (idx 16) del setlist DREF.
- **Anclaje por timecode:**
  - A Fuego  -> cue `07:30:00:00`
  - **Random Friends (invitado) -> ocurre aqui, despues de A Fuego, antes de la cue 08:00**
  - Misionar -> cue `08:00:00:00`
- **TC vivo al momento de anotarlo:** `07:33:56:29` (val 27236.97 s)
- **Nota:** no se inyecto al engine en vivo (correria indices y romperia panel/cues).
  Reconciliar post-show en `setlist_festival_sentir.txt` + `setlist_durations_dref.json`
  (nueva linea entre A Fuego y Misionar; asignar visual/duracion o null si sin visual).

_Autor: Cauce (fallback pasivo). Config del show intacta._

## Observacion: transicion intro -> "Ultimo Dia" no avanza por duracion

- **Sintoma (usuario):** no pasa a "Ultimo Dia"; el calculo entre la duracion del
  clip de intro (~1 min) y la llegada a Ultimo Dia no cuadra.
- **Lectura:** el avance del setlist es por CUE de timecode, no por duracion de clip.
  - intro show -> cue `00:00:00:00` (clip real ~`00:01:11`, 71.2 s)
  - Ultimo Dia -> cue `01:00:00:00`
  - Entre el fin del clip (~00:01:11) y la cue de Ultimo Dia (01:00:00:00) hay un
    hueco enorme: el panel se queda en intro hasta que el TC llega a 1:00:00:00.
- **TC vivo al anotar:** `00:02:24:00` (aun en intro, next = Ultimo Dia).
- **Reconciliar post-show:** revisar el anclaje de cues del setlist -- si la intencion
  es avanzar por fin-de-clip, la cue de Ultimo Dia deberia caer cerca de ~00:01:11,
  no en 01:00:00:00. NO se toca en vivo.
