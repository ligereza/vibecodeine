# LAST_HANDOFF — Faro

Actualizado: 2026-08-08

## Estado real

- Director: Faro/Codex en Windows; MAK es la caja Linux y ejecuta los modelos.
- Ramas canónicas: `main`, `mak`, `rd`, `iskvw`. No crear ni conservar ramas de trabajo remotas.
- Rama local actual: `mak`; cambios consolidados en `ec6cfed` y publicados en `origin/mak`.
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

## PR y limpieza pendientes

- Consolidar los cambios locales en `mak`, ejecutar tests focalizados y hacer push.
- PR #511 contiene el bloque actual; no mezclarlo con el PR #512.
- Cerrar el PR #512 y eliminar su rama remota porque es una utilidad autogenerada sin relación con el núcleo.
- Tras comprobar CI de #511, decidir promoción a `main`; no hacer merge automático con checks rojos.
- Sincronizar la caja MAK con el commit publicado y verificar servicio, rama y archivos desplegados.

## Limpieza 2026-08-08

- Windows quedó limpio en la rama `mak`; `origin` conserva solo `main`, `mak`, `rd` e `iskvw`.
- `/home/mak/flujo` quedó limpio en `main` y alineado con `origin/main`.
- Los cambios locales que estaban en la caja se conservaron en
  `/home/mak/quarantine/flujo-20260808-cleanup/`; no se eliminaron silenciosamente.
- Los tags locales antiguos de la caja se inventariaron en esa cuarentena y se eliminaron; `origin` no tenía tags publicados.
- El despliegue operativo vive separado en `/home/mak/plataforma`; `mak-hub.service` sigue activo.

## Regla de continuidad

No añadir otra base ni otro framework. Toda tarea nueva debe conservar `work_id`, propósito, lane, formato, evidencia, proveedor, estado y siguiente acción. La promoción pública requiere evidencia y gate; las semillas creativas no se convierten en informes por accidente.

## Cierre positivo — 2026-08-08

La sesión avanzó de forma real: MAK dejó de producir a ciegas, Watsonx y AWS trabajaron como lectores externos, y sus resultados quedaron trazables en vez de entrar directamente como verdad. El rescate de 23 informes produjo 12 candidatos `rescue` y 11 `review`, sin borrar ni publicar nada. También quedó conectada la interfaz de portafolio con la triangulación y el rescate, separando búsqueda, asociación y promoción.

Lo aprendido para mañana: no confundir una tarea externa con una decisión del usuario; las 23 adjudicaciones pueden seguir sin bloquear la curaduría visual. La higiene del repositorio también es parte del sistema: un archivo de usuario en un log puede romper CI, y una rama o tag local puede parecer trabajo vigente cuando no lo es. La próxima sesión debe revisar el resultado final del PR #511, no repetir auditorías ya cerradas, y sincronizar MAK solo después de una promoción comprobada a `main`.

## Reanudación — 2026-08-08

El PR #511 reveló dos fallos de higiene, no fallos del circuito: `tools/construir_mapa_visual.py` no estaba registrado en `CAPACIDADES.md`, y el runner de idioma detectó la docstring española del adjudicador. Ambos fueron corregidos en `7a98c13` y enviados a `mak`; CI debe repetir ahora la verificación. La suite focalizada de higiene tarda más de dos minutos en Windows y fue detenida para no dejar un proceso costoso colgado; la corrección se verificó por compilación y `git diff --check`.
