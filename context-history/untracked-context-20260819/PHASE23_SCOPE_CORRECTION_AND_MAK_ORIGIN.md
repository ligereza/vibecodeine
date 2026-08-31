Identity: LUNA-25 (principal)

# Phase 23 — corrección de alcance y origen histórico de MAK

## Corrección recibida

El objetivo no es reparar ni reconstruir MAK. MAK es el equipo Linux Debian 12
que conserva un entorno de trabajo con bugs y mejoras pendientes. El objetivo
principal es migrar desde `/home/mak/WIN` las herramientas de la aplicación
FLUJO que antes corrían en Windows con `flujo serve`, dentro de un hub dividido
en `RD`, `ISKVW` y `CULTURA`, y hacerlas funcionar correctamente en MAK.

La semántica correcta es:

```text
WIN / FLUJO APP / flujo serve / hub / RD + ISKVW + CULTURA
                         |
                         v
              migración y adaptación a MAK Linux
```

Las revisiones anteriores de MAK-plataforma siguen siendo evidencia de
dependencias, consumidores y riesgos, pero no deben convertir a MAK en el
objeto de una reingeniería ni elegir un `.py` aislado como objetivo principal.

## Evidencia en `historia git.odt`

El resumen estratégico identifica `/home/mak/WIN` como archivo Windows y
material fuente pre-migración, y `/home/mak`/`/home/mak/flujo` como superficie
Linux operativa e integración. Su autoridad también indica que Git solo sirve
para orientación histórica y que la realidad actual la determinan los árboles
físicos.

La primera señal explícita de la idea MAK integrada con la herencia WIN es:

| Fecha | Commit | Sujeto |
|---|---|---|
| 2026-07-17 17:22 -04:00 | `6a2b147097e169d42fdc3defe9f0e160de52cc41` | `feat(cultura): cierre organismo MAK -- WIN LLM provider, hub DOM+SVG, emisor de eventos (#48)` |

El `key_path_journeys` del documento marca ese commit como primer evento para
varios componentes MAK, entre ellos `cultura/mak_research/interfaz.py`,
`cultura/mak_codex/interfaz_codex.py`, `cultura/mak_research/research.py`,
`cultura/mak_research/research_lib.py`, `cultura/mak_research/worker.py` y
`cultura/mak_plataforma/backlog_codex.txt`. Esto muestra la aparición del
organismo MAK dentro del flujo histórico, no la prueba de que cada componente
fuera una migración completa desde WIN.

La secuencia inmediata refuerza la lectura:

- `f3cf06cf2b56`: `tools/mak: implement delegar bridge to MAK Linux peer`.
- `3f40b0959c5f`: `feat(mak): sistema generativo VIVO -- backlog de lagunas + matcher RD + works.json`.
- `cdda30ee106a`: `release: v0.55.0 -- pausa-en-error MAK vivo + workship Win-MAK probado`.
- `62dc9a687f4d`: `fix(mak): trabajo.py detecta rechazo de /run + emisor HALLAZGO ...`.

La interpretación más fuerte es que WIN era el punto de partida de la
aplicación y MAK fue el organismo/entorno Linux que se construyó alrededor de
la migración, no un reemplazo que debamos volver a ordenar desde cero.

## Confirmación física: WIN contiene la genealogía MAK

La inspección de `/home/mak/WIN/flujo` confirma que el archivo no es solo una
versión Windows anterior. Contiene simultáneamente:

- el entrypoint `src/flujo/cli.py`, con `flujo serve`, `flujo app` y comandos
  RD/knowledge/autonomía;
- `src/flujo/web/hub.py`, `src/flujo/serve/server.py` y
  `context/flujo_hub.html`;
- `cultura/mak_codex`, `mak_conductor`, `mak_curatoria`, `mak_lenguaje`,
  `mak_plataforma`, `mak_post`, `mak_research`, `mak_vigia` y
  `mak_xio_puente`;
- `tools/mak`, `tools/mak_ops`, `src/flujo/rd`, `iskvw` y `projects/cultura`.

Por tanto, el crosswalk debe tener una dimensión de generación:

```text
FLUJO APP original
    -> hub RD / ISKVW / CULTURA
    -> nacimiento de MAK dentro del mismo árbol
    -> adaptaciones Windows/Linux y recuperaciones posteriores
    -> destino actual en MAK
```

La fecha de creación del filesystem no sirve para ordenar esa genealogía:
53.095 de 53.103 archivos tienen birth date 2026-08-13 y 53.092 tienen ctime
2026-08-13, correspondiente a la importación del archivo. `mtime` sí varía y
se conserva como señal auxiliar, pero debe cruzarse con contenido, ruta del
hub, consumidor y commit histórico.

## Consecuencia operativa

- Pausar la adopción de `discernment.py`; su prueba aislada queda como
  evidencia secundaria, no como siguiente integración.
- Rehacer la ruta principal como un crosswalk físico WIN → MAK para el
  entrypoint `flujo serve`, hub y departamentos `RD`, `ISKVW`, `CULTURA`.
- Para cada herramienta heredada identificar origen WIN, destino MAK, función,
  consumidor del hub, dependencias Windows, adaptación Linux necesaria,
  estado real y prueba de funcionamiento.
- Mantener intacta la casa MAK existente; solo cambiarla cuando una herramienta
  WIN tenga un destino concreto y una prueba de integración.
- No interpretar los 167 registros no adoptables de la triage de MAK como
  basura de WIN. Esa clasificación responde a otra pregunta y no autoriza
  borrar ni excluir herramientas heredadas.

## Archivos y cambios

Solo se creó este informe de corrección. No se modificaron source, runtime,
WIN, datos, servicios, cron, Git ni artwork.
