# Orden de ejecución para Claude — producir, no debatir

Trabaja sobre `/home/mak/CODEX REMOTO/v2_CORRECCION_20260906/`. La v1 está congelada y no se modifica.

## Rol y regla principal

Actúas como ejecutor documental y de control de calidad. La auditoría ya fijó los hallazgos y las decisiones vigentes. No debes reabrirlas, defenderte, refutarlas ni escribir otro informe argumentativo. Si encuentras un error nuevo, corrígelo en el archivo afectado, regenera lo necesario y registra sólo la evidencia concreta.

El resultado se juzga por archivos útiles creados o corregidos, no por la calidad de la explicación.

No enviar, no firmar, no registrar cuentas, no contactar terceros, no inventar datos y no tocar repositorios o servicios.

## Secuencia obligatoria

### 1. Preparar y comprobar

Lee `LEEME_CIERRE.md`, `DEPENDENCIAS_HUMANAS.md`, `MATRIZ_REQUISITOS.md` y este encargo. Ejecuta la integración actual antes de modificar. Conserva estas decisiones ya cerradas:

- Ama Amoedo + Difusión + Formativas es la recomendación vigente.
- Creación es alternativa de Difusión, nunca una postulación simultánea del mismo contenido.
- La evidencia distingue decisiones humanas persistidas en MAK de los universos sin decisiones; no vuelvas a afirmar “cero decisiones” sin especificar el universo.
- En Formativas, la guía manual es la vía real; no afirmes autonomía de software ni instalación en 16 equipos.
- El conteo correcto del verificador es 1 control positivo + 14 defectos inyectados.

### 2. Producir artefactos operativos

Debes crear o corregir estos archivos, en este orden:

1. `DRY_RUN_ENVIO_20260906.md`: una tabla ejecutable por expediente (Ama, Difusión, Formativas y Creación alternativa) que indique campo, fuente, estado real, dato faltante, archivo destino y bloqueo. Debe resolver cada expediente como `PUEDE PASAR A CUENTA` o `NO PUEDE PASAR A CUENTA`; no uses “enviable” si faltan datos del titular.
2. `PAQUETE_DE_ACCION_TITULAR_20260906.md`: ficha copiable con región, identidad, RUT/edad, Perfil Cultura, cuenta Ama, CV, identidad, portfolio y epígrafes, estudios para Formativas, decisión Difusión/Creación, asistentes y espacio. Cada campo indica el archivo exacto que se actualizará y qué bloqueo elimina.
3. `postulaciones/BORRADORES_SIN_FIRMA/FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv`: plantilla de 15 filas, sin nombres, RUT ni firmas inventadas, con encabezados útiles y validables.
4. `postulaciones/BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md`: texto listo para copiar y enviar a un espacio, sin enviarlo y sin fingir que existe una cotización.
5. `verificador/revision_ids_y_gastos.py` o equivalente reproducible: comprueba IDs únicos, gastos comunes duplicados y exclusión simultánea de Creación/Difusión. Ejecútalo y deja el resultado.

No crees un artefacto sólo para describir que otro debería existir. Los archivos anteriores deben contener material utilizable.

### 3. Verificar y cerrar

Ejecuta:

```bash
bash VERIFICAR_INTEGRIDAD.sh
python3 verificador/verificar_presupuestos.py
bash verificador/pruebas_negativas.sh
python3 verificador/comprobacion_cruzada.py
python3 postulaciones/generar_texto_por_campo.py
```

Si la regeneración cambia archivos del manifiesto, regenera `MANIFIESTO_v2.sha256` y repite toda la integración. Debe quedar v1 30/30, v2 coincidente, presupuestos OK, control positivo 1 y 14 defectos detectados.

### 4. Escribir el recibo final

Sólo después de crear y probar los artefactos, crea `REPORTE_EJECUCION_CLAUDE_20260906.md`, máximo una página. Debe contener únicamente archivos creados/corregidos, resultado de cada comando, bloqueos humanos restantes y confirmación de que no hubo acciones externas. No incluyas una defensa de la auditoría ni un ensayo sobre quién tenía razón.

## Criterio de aceptación

La tarea falla si falta cualquiera de los cinco artefactos operativos, si el CSV no tiene 15 filas vacías, si la solicitud de espacio no está lista para copiar, si el verificador no se ejecuta, si Creación y Difusión aparecen como simultáneas, o si el cierre consiste principalmente en explicar/refutar.

La tarea termina sólo cuando los artefactos existen, son utilizables sin inventar datos, las pruebas pasan y el reporte breve demuestra su existencia.
