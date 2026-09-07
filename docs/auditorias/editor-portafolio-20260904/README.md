# Auditoría del editor y portafolio

Paquete curado de la investigación del editor/portafolio. Contiene evidencia estructural, contratos, riesgos y propuestas que vale la pena versionar junto al repositorio MAK.

La auditoría completa permanece fuera del repositorio como archivo de trabajo. Este paquete no contiene snapshots operativos completos, inventarios masivos de archivos, respuestas raw de proveedores ni scripts auxiliares de generación.

## Qué contiene

- superficies, controles del editor, campo/atlas, frontera de publicación y glosario;
- matriz de mutaciones, reconciliación de árboles y planes de reparación;
- procedencia, reproducibilidad y validación;
- límites de red, headers, observabilidad, integridad de mutaciones, proxy y contrato de errores;
- retención de datos y propuestas priorizadas.

## Convenciones

Las rutas locales fueron convertidas a referencias portables:

- `MAK/`: árbol MAK;
- `FLUJO/`: worktree FLUJO;
- `RUNTIME/`: datos y procesos locales, no incluidos en este paquete;
- `source-audit/`: referencia al archivo de auditoría original, fuera del repo;
- `TEMP/`: salidas temporales usadas en pruebas aisladas.

Los hashes y timestamps son evidencia de la medición realizada; no significan que la publicación haya sido ejecutada. Las propuestas son read-only: no autorizan por sí mismas cambios de código, deploy, commit o push.

## Archivos deliberadamente excluidos

Se dejan en el archivo local `07_recuperables_v2.json`, `13_superficie_artifacto_publico.json`, los snapshots runtime de gran tamaño, `16_sonda_deploy_externo.json`, los JSON históricos duplicados y `_generate_*.py`/`_resolve_07.py`. Contienen inventarios voluminosos, rutas de máquina, estado efímero o herramientas de trabajo que no aportan valor proporcional a un commit documental.

La copia curada fue creada sin detener procesos y sin alterar la carpeta original de auditoría.
