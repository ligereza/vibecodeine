# Triage de las 813 divergencias

Fuente congelada: `/_archive/merge-20260831/fused/projection3/MANIFEST.json`.
Su SHA-256 es `8240dfe69e854d09155ea274c0aed414a207fc07a3afeb3286cbe92e49229850`.
La matriz completa por ruta está en `divergence-triage.json`.

| Grupo | N | Lectura operativa |
|---|---:|---|
| Consenso byte a byte en 2 de 3 orígenes | 712 | 653 conservan el baseline activo; 59 tienen el baseline activo como outlier y son prioridad manual |
| Sólo dos fuentes o conflicto de tipo | 73 | revisión manual; incluye archivo↔symlink |
| Tres contenidos únicos | 28 | revisión manual obligatoria |

No se hizo fusión semántica automática: el manifiesto no contiene una base
común de tres vías. El consenso de bytes es evidencia para decidir, no prueba
de equivalencia funcional. Orden de trabajo: `active_outlier` (59),
`three_unique` (28), y finalmente los 73 conflictos restantes.
