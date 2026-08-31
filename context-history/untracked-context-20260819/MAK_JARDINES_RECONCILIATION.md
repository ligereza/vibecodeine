# Reconciliacion MAK y Jardines interpretativos

Este documento es un crosswalk read-only. Las dos bases conservan
esquemas y responsabilidades distintas; no se fusionan tablas por
tener nombres parecidos.

## Identidad de la fuente

- fuente: `/home/mak/curatoria_inbox/funding-lab/JARDINES_INTERPRETATIVOS.md`
- titulo: Jardines interpretativos
- hash de Jardines: `a35070350df210568c9f33827cbaea4d7768d1582a033cf4fa68c21c285418cc`
- hash fisico actual: `a35070350df210568c9f33827cbaea4d7768d1582a033cf4fa68c21c285418cc`
- match con artifact MAK: **True**
- artifact MAK: `15057`
- integridad global: `ok`
- integridad Jardines: `ok`

## Conteo separado

| superficie | cantidad | funcion |
|---|---:|---|
| Jardines: fuentes URL | 40 | referencias capturables, aun no verificadas por red |
| Jardines: claims | 22 | afirmaciones/decisiones del documento |
| Jardines: entidades | 9 | entidades del modelo interpretativo |
| Jardines: relaciones | 4 | relaciones del modelo interpretativo |
| Jardines: semantica | 12 | discover a audit |
| MAK: residuos de esfuerzo | 4484 | senales cronologicas de Research |

## Herramientas y puente

- herramientas declaradas por Jardines: **12**
- nombres que coinciden con candidatos tool de MAK: **0**
- coincidencias: `ninguna`
- relaciones `possibly_consumed_by` desde Research: **0**

El cruce por nombre no promueve una herramienta: requiere etapa, entrada,
salida, licencia, plataforma, mantenimiento y consumidor probado. La
ausencia de `possibly_consumed_by` impide afirmar que un JSON de esfuerzo
sea consumido por una herramienta concreta.

## Decision

1. La fuente esta correctamente indexada en ambas capas y el hash coincide.
2. La base de Jardines permanece como modelo semantico especializado.
3. `mak_knowledge.db` permanece como inventario cronologico, procedencia
   fisica, imports, consumidores y residuos de esfuerzo.
4. El puente operativo es el router de Research y el gate Cultura, no una
   copia de tablas ni una fusion automatica.
5. La primera entidad que puede pasar a `review_ready` es el expediente
   de Jardines, porque tiene fuente, semantica, relaciones, restricciones
   y un dry-run de propuesta; aun no tiene captura web verificada ni FUP.

## Limites

- Las 40 URLs del documento siguen siendo referencias hasta una captura
  explicita; no se presenta su contenido como verificado.
- `review_ready` no significa publicable ni postulacion enviada.
- No se escribio ninguna de las dos bases durante esta reconciliacion.
