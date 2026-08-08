# LAST_HANDOFF — Faro

Actualizado: 2026-08-08

## Estado real

- Director: Faro/Codex en Windows; MAK es la caja Linux y ejecuta los modelos.
- Ramas canónicas: `main`, `mak`, `rd`, `iskvw`. No crear ni conservar ramas de trabajo remotas.
- Rama local actual: `mak`; ultimo commit publicado en `origin/mak`: `1a63f70`.
- No hay tags útiles declarados para este ciclo.
- No usar Downloads como destino de artefactos.

## Cambios de esta sesión

- Contrato `mak-work-v1` en Capataz, tandas y ledger; entradas sin identidad quedan `legacy_unknown`.
- Guardia de curatoria y cron destructivo pausados en MAK; no se relanza producción sin contexto válido.
- Hub MAK activo y editor de portafolio conectado a inbox, tableros, triangulación, copilot y rescate legado.
- La interfaz mantiene separadas búsqueda, bandeja de asociación, tableros y triangulación.
- `/api/research/rescue` expone el rescate adjudicado sin promoción automática.
- Watsonx revisó 23 candidatos legacy: 12 `rescue`, 11 `review`.
- AWS hizo la segunda lectura: coincidencia con Watsonx en 12 casos.
- Ningún informe fue borrado ni promovido al ledger.
- Diez semillas creativas permanecen como `creative_reinterpretation`, fuera del conocimiento factual y del micelio público.

## MAK comprobado

- `mak-hub.service`: activo.
- AWS funciona desde `/home/mak/plataforma/.venv`.
- Watsonx funciona desde la configuración existente en MAK.
- El servidor Ollama es un servicio del sistema; no es requisito para el rescate terminado.
- El archivo de adjudicación vive en:
  `/home/mak/plataforma/director_runs/faro-report-action-queue-20260808/RESCUE_ADJUDICATED.json`.
- La instancia Gemma puede quedar cargada por el servicio Ollama; no confundirla con una tanda activa de Faro.

## Decisiones aplazadas

- Las decisiones visuales del usuario en el editor quedan aplazadas; no bloquean el trabajo factual.
- Los 12 `rescue` son candidatos, no verdad pública: requieren gate posterior antes del ledger.
- Los 11 `review` deben conservar su incertidumbre y no pueden rellenarse por inferencia.

## PR y limpieza resueltos

- PR #511 paso todos los checks y fue integrado a `main` como `e8f67c0`.
- PR #512 sigue cerrado; su utilidad aislada no se reincorporo al nucleo.
- `origin` conserva solo `main`, `mak`, `rd` e `iskvw`; no se borraron ramas canonicas.
- El ultimo bloque de identidad fue publicado en `origin/mak` como `1a63f70`.
- La caja debe avanzar su checkout `mak` a `origin/mak` en la proxima sincronizacion operativa.

## Limpieza 2026-08-08

- Windows quedó limpio en la rama `mak`; `origin` conserva solo `main`, `mak`, `rd` e `iskvw`.
- `/home/mak/flujo` esta limpio en `mak`; su checkout debe alinearse con el ultimo `origin/mak`.
- Los cambios locales que estaban en la caja se conservaron en
  `/home/mak/quarantine/flujo-20260808-cleanup/`; no se eliminaron silenciosamente.
- Los tags locales antiguos de la caja se inventariaron en esa cuarentena y se eliminaron; `origin` no tenía tags publicados.
- El despliegue operativo vive separado en `/home/mak/plataforma`; `mak-hub.service` sigue activo.

## Regla de continuidad

No añadir otra base ni otro framework. Toda tarea nueva debe conservar `work_id`, propósito, lane, formato, evidencia, proveedor, estado y siguiente acción. La promoción pública requiere evidencia y gate; las semillas creativas no se convierten en informes por accidente.

## Cierre positivo — 2026-08-08

La sesión avanzó de forma real: MAK dejó de producir a ciegas, Watsonx y AWS trabajaron como lectores externos, y sus resultados quedaron trazables en vez de entrar directamente como verdad. El rescate de 23 informes produjo 12 candidatos `rescue` y 11 `review`, sin borrar ni publicar nada. También quedó conectada la interfaz de portafolio con la triangulación y el rescate, separando búsqueda, asociación y promoción.

Lo aprendido para la siguiente sesion: no confundir una tarea externa con una decision del usuario; las 23 adjudicaciones pueden seguir sin bloquear la curaduria visual. La higiene del repositorio tambien es parte del sistema: un archivo de usuario en un log puede romper CI, y una rama o tag local puede parecer trabajo vigente cuando no lo es. El PR #511 ya esta integrado; el siguiente foco es la trazabilidad operativa y no repetir auditorias cerradas.

## Reanudación — 2026-08-08

El PR #511 revelo dos fallos de higiene, no fallos del circuito: `tools/construir_mapa_visual.py` no estaba registrado en `CAPACIDADES.md`, y el runner de idioma detecto la docstring espanola del adjudicador. Ambos fueron corregidos en `7a98c13`; los checks finales pasaron y el PR se integro en `main` como `e8f67c0`. La correccion se verifico por compilacion y `git diff --check`.

## Autonomía combinada — 2026-08-08

Se unieron las dos rutas sin crear otro framework: la columna vertebral conserva
`mak-work-v1`, decisiones humanas y ledger append-only; el editor ahora convierte
selecciones, exclusiones y relaciones aceptadas/rechazadas en señales trazables.
Los tableros registran sus nuevas parejas como feedback contextual, sin publicar
ni convertir una hipótesis en hecho. El copiloto aplica un perfil acotado por
faceta (`artist`, `venue`, `event`, `date`, `client`, `collab`, `period`), respeta
el alcance explícito del tablero y evita mezclar candidatos fuera de él.

La superficie `/api/portfolio/copilot/learning` expone el aprendizaje resumido
al editor. Las sugerencias siguen siendo candidatas; Watsonx/AWS pueden
proponer hipótesis y la decisión humana modifica el ranking futuro, con pesos
limitados para impedir que una tanda pequeña se convierta en dogma. Tests
focalizados de copilot, Capataz y enrutamiento pasan (`46 passed`). PR #511
esta integrado en `main`; no se mezclo este bloque con PR #512.

## Fase 1 ejecutada — 2026-08-08

La primera tanda cerro la columna vertebral sin crear otro framework:

- `mak-identity-v1` viaja dentro de `mak-work-v1` con kind, source_id, parent_id,
  entidades, fecha de evento y fecha de publicacion.
- Las entidades iniciales son artist, username, client, collab, event, festival,
  venue, location y source. Se mantienen separadas; no se deduce un artista desde
  un username ni un venue desde un evento.
- Los informes historicos sin sobre de identidad permanecen `legacy_unknown` y
  no se reescriben.
- Los briefs de tandas ya declaran identidad; la ingesta rechaza un sobre invalido
  antes del juez local y del ledger.
- La reparacion de formato conserva el work completo; antes podia perder identidad
  al reconstruir el objeto `product`.
- Las decisiones del juez ahora heredan el mismo work e identidad, por lo que una
  revision negativa no queda desconectada del lote que la produjo.
- Se hizo una tanda Watsonx acotada sobre calidad de MAK. El juez determinista la
  rechazo por evidencia insuficiente; quedo como memoria de rechazo, no como verdad.
- Tests focalizados Windows: `90 passed`; compilacion y `git diff --check` pasan.
- En MAK: `py_compile` y `mak-hub.service` activo. No se ejecuto pytest alli porque
  esa caja no tiene pytest instalado; no se instalo una dependencia temporal.

## Proximo bloque

Sin domain ni barrido masivo: sincronizar el checkout `mak`, cerrar un circuito
vertical aceptado con identidad, y luego iniciar la segunda tanda sobre el corpus
visual. Watsonx/AWS solo reciben lotes con source_id y evidencia acotada.
