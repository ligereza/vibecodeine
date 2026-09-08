# Codigo y datos - Jardines

Snapshot de la infraestructura que respalda el borrador de investigación.

- `interpretive_garden_workflow.py`: crea el esquema, registra fuentes,
  claims, relaciones, estados, restricciones y eventos de auditoría; exporta
  los CSV del paquete.
- `reconcile_garden_knowledge.py`: crosswalk de solo lectura entre la base
  global de MAK y la base especializada de Jardines.
- `jardines_interpretativos.sqlite`: base especializada, copiada sin cambios.
- `jardines_interpretativos_correlations.csv` y
  `jardines_interpretativos_process_semantics.csv`: exportaciones para lectura
  y revisión rápida.

Fuente original: `/home/mak/research/jardines_interpretativos/` y
`/home/mak/tools/`. El código depende del árbol original de MAK; esta carpeta
no es un paquete ejecutable aislado ni una prueba de trabajo de campo.

