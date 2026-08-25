# C04 media observer — LUNA A

## Resultado

Se implementó un observador técnico read-only para el artefacto real
`/home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4`. El runner calcula SHA-256 y
bytes antes y después de una consulta `ffprobe`; sólo si el digest previo
coincide ejecuta la consulta. Si falta `ffprobe`, vence el límite o devuelve
un código distinto de cero, la respuesta JSON queda en `status=blocked` y el
runner termina con código `2`.

El JSON normal conserva el formato no convencional exactamente como fue
observado: dimensiones `256x1536`, sin intercambio ni normalización a un
formato convencional. La sanitización conserva únicamente campos técnicos
consultados; descarta tags y disposition del contenedor/streams. La ruta
absoluta se reemplaza por `<artifact>` dentro del comando emitido.

## Archivos producidos

- `media_observer.py` — hash, consulta `ffprobe`, sanitización y contrato JSON.
- `runner.py` — CLI sin archivo de destino ni operaciones de escritura.
- `tests/test_media_observer.py` — seis pruebas stdlib `unittest`, incluyendo
  la observación real y fallos explícitos.

## Evidencia real

| campo | observado |
|---|---|
| SHA-256 esperado y antes/después | `b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776` / coincide / coincide |
| bytes | `12092541` |
| contenedor | `mov,mp4,m4a,3gp,3g2,mj2` — `QuickTime / MOV` |
| streams | `0 video`, `1 audio`, `2 data` |
| codecs | video `h264`, audio `aac`, data sin codec declarado |
| duración | formato/video `44.627917 s`; audio `44.693333 s` |
| dimensiones | video exacto `256x1536` |
| frames | video `1070`; audio declarado `2095`, leídos `2093`; data `1` |

## Comandos ejecutados y códigos

La consulta exploratoria real, ejecutada antes de implementar el parser, fue:

```text
ffprobe -v error -count_frames -print_format json -show_format -show_streams -show_entries 'format=format_name,format_long_name,duration,size,bit_rate,nb_streams:stream=index,codec_type,codec_name,codec_long_name,profile,width,height,avg_frame_rate,r_frame_rate,duration,nb_frames,nb_read_frames,channels,sample_rate,channel_layout' /home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4
exit code: 0
```

Pruebas ejecutadas después de la implementación:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s /home/mak/flujo/experiments/cycles/C04/media_observer/tests -p 'test_*.py' -v
exit code: 0
resultado: Ran 6 tests; OK
```

Runner real ejecutado:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -B /home/mak/flujo/experiments/cycles/C04/media_observer/runner.py /home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4
exit code: 0
resultado: JSON sanitizado en stdout; status=ok; probe exit_code=0; hash antes/después coincidente
```

También se verificó el bloqueo de `ffprobe` ausente en la suite con el mismo
artefacto real: el caso produjo `status=blocked`, `block_reason=ffprobe_unavailable_or_timed_out`,
`probe.exit_code=null` y hash posterior coincidente.

## Ausencia de relaciones de procedencia

El payload JSON no contiene claves ni valores `generated`, `RENDERS_TO` u
`output`; una prueba serializa todo el documento y falla si aparece cualquiera
de esos términos. Esa ausencia es intencional: observar hash, contenedor,
streams, codec, duración, dimensiones y frames demuestra estado técnico del
medio, pero no demuestra causalidad, evento de exportación ni rol de salida.

## Límites

- Sólo se lee el archivo indicado por argumento; no se enumeran carpetas.
- SHA-256 se calcula en bloques de `1048576` bytes y se valida antes y después.
- `ffprobe` tiene un límite de `120` segundos y se usa sólo para metadata JSON.
- No se escribe el MP4, no se renderiza, no se transcodifica y no se abre
  navegador o reproductor.
- La observación no consulta `.aep`, catálogos, red ni eventos de exportación.
- Un código `0` certifica la consulta técnica y la integridad del archivo en
  esos dos puntos; no certifica procedencia o autoría.
