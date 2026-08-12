# Universo ampliado de entidades RD

## Decisión de alcance

La base ya no se limita a las filas y columnas de la matriz ni a las sustancias que tienen un reactivo. Todo elemento relevante entra al universo y queda clasificado:

- sustancia;
- familia de sustancias;
- derivado o análogo;
- nombre de mercado o mezcla variable;
- medicamento;
- adulterante o contaminante;
- metabolito o precursor;
- sustancia contextual.

El archivo máquina-legible es:

[rd_universo_entidades_2026-08-11.json](C:/Users/issvk/claude_sesiones_recuperadas/rd_universo_entidades_2026-08-11.json)

## Qué cambió

La matriz contiene 14 entidades iniciales, pero el contenido público de RD menciona muchas más. Entran ahora MDA, DMT, 5-MeO-DMT, DET, 2C-B, NBOMe, DOx, catinonas, mefedrona, MDPV, a-PVP, benzofuranos, derivados disociativos de ketamina, opioides, fentanilo, xilazina, PMA, PMMA, DXM, levamisol, lidocaína, fenacetina, cafeína y medicamentos vinculados a interacciones o chemsex.

## Tres niveles que no se deben mezclar

```text
entity_universe
  = everything relevant that appears in RD material or linked evidence

integration_view
  = selected entities for one product, post, matrix, or interface

public_claim
  = the narrower statement that passed human review
```

Que una entidad exista en el universo no significa que tenga una ficha publicada, un test doméstico disponible o una conclusión clínica.

## Estados de testeo

La ausencia de test es un dato, no un motivo de exclusión:

- `colorimetric_reagent`: hay material de reactivos, pero debe conservarse como señal presuntiva;
- `specific_strip`: existe una tira específica, como fentanilo, xilazina o benzodiacepinas;
- `specific_non_colorimetric_test`: existe una prueba que no es un gotario colorimétrico, como el test de GHB en bebidas;
- `laboratory_only`: no se debe convertir en una guía doméstica;
- `no_known_test_in_scope`: RD declara que no distribuye o no tiene un método aplicable;
- `not_reviewed`: la entidad entra en la base, pero todavía no hay una conclusión de testeo.

## Casos importantes

### Tusi

No se registra como una molécula única. Se guarda como nombre de mercado o mezcla variable. Puede relacionarse con 2C-B, MDMA, ketamina, cocaína, catinonas, benzodiacepinas y otras entidades, pero esas relaciones no deben inferirse automáticamente desde el nombre.

### MDA

Tiene ficha propia, contenido de comparación con MDMA y reactivos relacionados. Es el primer candidato para incorporarse a la matriz como nueva entidad, pero esa decisión debe mantenerse separada de la base universal.

### Poppers

Entra como familia de nitritos de alquilo y no como una única sustancia. RD señala que no tiene actualmente un test colorimétrico aplicable a esta familia; esa ausencia debe mostrarse como información.

### GHB / GBL

Entra como familia y conserva su relación con alcohol y ketamina. La guía de RD distingue el test específico para bebidas de los reactivos colorimétricos comunes; no se debe registrar “sin reacción” como un resultado de seguridad.

### Adulterantes

Levamisol, lidocaína, fenacetina, cafeína, PMA, PMMA, fentanilo y xilazina no son notas al pie: son entidades propias que pueden aparecer como relación de adulteración, riesgo, test o investigación.

### Medicamentos

Viagra/sildenafil/tadalafil/vardenafil, ritonavir, cobicistat, PrEP, PEP y doxyPEP entran con `entity_kind=medication`. No se convierten automáticamente en sustancias equivalentes a las de uso recreativo; su función principal en el sistema puede ser interacción, tratamiento, prevención o contexto clínico.

## Próximo paso

Ahora corresponde construir el grafo relacional, no seguir agregando filas a mano. Cada relación deberá decir qué tipo de vínculo existe:

```text
interaction
comparison
adulterant_of
test_for
test_limit_of
market_name_for
derivative_of
medication_interaction
contextual_relation
```

La matriz visual será solo una vista filtrada de ese grafo. El post `MDMA vs MDA`, por ejemplo, usará dos nodos de sustancia, tres o más relaciones de testeo, sus límites y la evidencia disponible; no tendrá que cargar todo el universo.
