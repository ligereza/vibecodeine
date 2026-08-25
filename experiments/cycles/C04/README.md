# C04 — observación de medio y fuerza de evidencia

## Pregunta

C02 encontró que `ARICA.aep` declara `C:\ARICA\tottem_ojo.mp4` y que el
archivo existe. Eso permite sostener “el proyecto referencia este artefacto”
como candidato/apoyo, pero no “el proyecto lo generó”. C04 mide qué añade una
observación técnica real del medio y qué no añade.

```text
AEP fullpath declaration + local existence
    + hash / container / dimensions / streams / duration
    -> evidence for uses and artifact state
    -> generated/output role remains unknown without an export event
```

La forma no convencional del archivo se conserva como dato: `256×1536`, no se
normaliza ni se reescala.

## Insumos congelados

| rol | ruta | SHA-256 |
|---|---|---|
| native declaration | `/home/mak/curatoria_inbox/ARICA/ARICA.aep` | `99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460` |
| declared local artifact | `/home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4` | `b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776` |

La observación real conocida es un MP4 de 12,092,541 bytes, H.264/AAC, 44.627917
segundos, 1070 frames, con video `256×1536`, más streams de audio y data. Esa
observación no certifica que el `.aep` lo exportó.

## Reglas

- Leer, hashear y describir no modifica el medio ni el `.aep`.
- `declared_reference` y `media_observation` son hechos distintos.
- `uses` puede ser `supported` cuando la declaración nativa y la existencia
  local están documentadas.
- `generated`, `RENDERS_TO` y “obra final” permanecen `unknown` sin evidencia
  de actividad/exportación.
- Basename, extensión, fecha, dimensiones o coexistencia sólo generan
  candidatos; no son causalidad.
- Las dimensiones no se comparan contra formatos convencionales: se preservan.

## Salida

Un endpoint produce una observación real read-only del MP4. El segundo produce
un evaluador de niveles de evidencia sobre casos ciegos y adversariales. El
resultado integrado debe mostrar tanto la relación que sí puede sostenerse
(`uses`) como la que deliberadamente no puede sostenerse (`generated`/output).
