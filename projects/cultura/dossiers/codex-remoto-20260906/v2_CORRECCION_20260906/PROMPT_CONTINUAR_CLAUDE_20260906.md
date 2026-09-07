# Prompt de continuación para Claude Code

Retoma el paquete documental vigente en `/home/mak/CODEX REMOTO/v2_CORRECCION_20260906/`. La v1 histórica está congelada en `../v1_ENTREGA_20260906_AUDITADA/`; no la modifiques. Lee primero:

- `LEEME_CIERRE.md`
- `REPORTE_AUDITORIA_20260906.md`
- `REPORTE_TRABAJO_REALIZADO_20260906.md`
- `RESPUESTA_AUDITORIA.md`
- `MATRIZ_REQUISITOS.md`
- `DEPENDENCIAS_HUMANAS.md`
- `ORDEN_TRABAJO_CLAUDE_20260906.md` y `FORMATO_ENTREGA_CLAUDE_20260906.md` — son el encargo operativo y el formato obligatorio de esta continuación.

## Estado que debes conservar

La recomendación vigente es: Ama Amoedo + Fondart Regional Difusión + Fondart Regional Actividades Formativas. `ALTERNATIVA_CREACION/` sustituye a Difusión si el titular prefiere una obra exhibible; no se deben enviar Creación y Difusión como dos versiones del mismo contenido.

La evidencia MAK distingue dos universos: el editor tiene decisiones humanas persistidas (87 selecciones en 14 sesiones, 103 clasificaciones y 123 asientos de ledger del dominio `iskvw` al corte 6/9/2026), mientras `curaduria.json` del otro universo tiene 0 decisiones. El editor descarga datos; no existe aún una pieza integrada que convierta inventario + decisiones en un portafolio público. Las mejoras Windows de IRIS/PUPILA no están integradas ni auditadas en MAK y no deben presentarse como terminadas.

## Trabajo restante, en orden

La orden ejecutable tiene prioridad operativa: produce los tres archivos que exige su criterio de aceptación, incluido el dry-run estático y el paquete de acción del titular. No cierres la tarea con una refutación narrativa si esos archivos aún no existen.

1. No inventes identidad, región, Perfil Cultura, CV, portfolio, epígrafes, estudios ni firmas. Cuando el titular los entregue, actualiza sólo campos por fuente y regenera conteos con `python3 postulaciones/generar_texto_por_campo.py`.
2. Mantén la separación de requisitos: Ama Amoedo exige identidad, CV y portfolio al postular; cuenta bancaria sólo para adjudicación/pago. Fondart exige Perfil Cultura y FUP al postular; documentos de convenio se preparan para después.
3. Si el usuario aporta región, actualiza fecha/territorio en todos los campos Fondart y verifica de nuevo la resolución aplicable. Si no la aporta, conserva escenarios condicionados; no incrustes RM.
4. Para Formativas, conserva la guía manual como vía real de transferencia y deja la instalación del software como prueba futura. Reúne sólo si el titular puede hacerlo: antecedentes de estudios, compromiso de espacio y al menos 15 compromisos de asistentes. No conviertas proveedores puntuales en equipo para evitar cartas.
5. No cambies totales para agotar topes. Después de cada cambio ejecuta `verificador/verificar_presupuestos.py`, `verificador/pruebas_negativas.sh` y `verificador/comprobacion_cruzada.py`.
6. Si llegan artefactos nuevos de IRIS/PUPILA, audítalos con ruta, fecha, prueba reproducible y relación con la evidencia MAK antes de cambiar claims o presupuesto. No toques sus repositorios desde este encargo.
7. Actualiza `LEEME_CIERRE.md`, `DEPENDENCIAS_HUMANAS.md` y este registro sólo cuando el estado cambie. Deja una manifestación SHA-256 final de la v2 y confirma que el sello de v1 sigue pasando.

## Criterio de cierre

El paquete queda listo para que el titular complete y envíe sólo cuando los campos humanos, adjuntos obligatorios y región estén presentes, los textos no tengan marcadores, los presupuestos y conteos pasen las pruebas y se conserve la evidencia de versión. No envíes, no firmes, no registres cuentas, no contactes terceros y no modifiques repositorios o servicios.
