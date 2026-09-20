# SUPERVISOR

Parte de misión temporal de la rama `SUPERVISOR`.

Este archivo existe para explicar la operación de limpieza a un agente que llega
después. No es contexto durable del sistema y no debe convertirse en un nuevo
handoff permanente.

> **No reconstruyas `main` dentro de esta rama. `SUPERVISOR` es una auditoría
> reductiva de `main`. Una ausencia puede ser el resultado correcto. Antes de
> restaurar algo, demuestra un consumidor actual o una pérdida funcional.**

## 1. Propósito de la rama

`SUPERVISOR` nació desde `main` para revisar el árbol integrado después de
fusiones y restauraciones mecánicas que recuperaron trabajo válido, pero también
resucitaron documentación, wrappers, runtimes, copias y contratos ya retirados.

La misión no es "dejar menos archivos" por sí misma.

La misión es:

1. reducir superficie operativa falsa o supersedida;
2. conservar código, evidencia, investigación y contenido real;
3. concentrar contexto durable en `SYSTEM.md`;
4. reemplazar estado narrado por medición reproducible;
5. eliminar referencias que puedan volver a resucitar autoridades retiradas;
6. demostrar que cada pieza que queda tiene razón de existir.

## 2. Qué representa el diff

El diff grande contra `main` no debe leerse como una lista de funciones
eliminadas.

Gran parte de las eliminaciones pertenece a categorías como:

- handoffs y cierres de sesión;
- `NEXT`, memorias, proyecciones y roadmaps ya cumplidos;
- reportes de fase e inventarios regenerables;
- contratos documentales reemplazados por código/registry;
- wrappers pre-Typer o herramientas supersedidas;
- copias de sistemas cuya autoridad vive fuera de este repo;
- piezas explícitamente retiradas que reaparecieron por integración mecánica;
- historia operativa que Git ya conserva.

La ausencia de un archivo no constituye por sí sola una regresión.

## 3. Autoridades después de la limpieza

Para conocer el sistema actual:

1. leer `SYSTEM.md`;
2. medir Git: rama, HEAD, diff, dirty state y procedencia;
3. ejecutar `python tools/contexto_repo.py --json`;
4. si importa el MAK físico, ejecutar `python tools/mak_status.py --json`;
5. consultar `python -m flujo --help`;
6. revisar consumidores, tests y workflows del área afectada;
7. acudir a historia Git sólo cuando el presente sea contradictorio.

`SYSTEM.md` contiene invariantes durables. No contiene el estado dinámico de
esta operación.

Este archivo, `SUPERVISOR.md`, contiene únicamente la intención y protocolo de
esta rama.

## 4. Decisiones que no deben revertirse accidentalmente

No restaurar sólo porque el nombre aparezca en historia o en `main`:

- Airdrop y sus superficies retiradas;
- la copia completa de XIO dentro de VIBECODEINE;
- `AGENTS.md` como contrato de entrada;
- handoffs persistentes;
- `NEXT.md` y documentos equivalentes de sesión;
- Watsonx como runtime activo;
- `tapiz_live_loop` como daemon sin consumidor medido;
- contratos `CAPACIDADES_*.md` reemplazados por superficies ejecutables.

Una retirada explícita prevalece sobre una reaparición mecánica mientras no
exista una decisión posterior explícita de reactivación.

## 5. Qué sí debe preservarse

"Un solo contexto" no significa "un solo Markdown".

No eliminar por extensión, antigüedad o tamaño.

Se preservan cuando tienen valor propio:

- código vigente;
- datos y evidencia;
- investigación;
- dossiers y postulaciones;
- obra y assets;
- contratos técnicos consumidos por código/tests;
- documentación de producto con conocimiento humano no reproducible desde
  schemas o código;
- herramientas manuales con uso real aunque no tengan invocador automático.

## 6. Regla para restaurar algo

Antes de restaurar un archivo eliminado, responder con evidencia:

1. ¿Cuál es su owner actual?
2. ¿Cuál es su consumer actual?
3. ¿Qué capacidad real se rompe sin él?
4. ¿Existe una superficie nueva que ya reemplaza esa capacidad?
5. ¿Fue retirado explícitamente antes de reaparecer?
6. ¿Hay un test, workflow o runtime actual que lo necesite?

Si sólo existen menciones históricas, wrappers legacy llamando wrappers legacy,
o documentación antigua, eso no basta para restaurarlo.

## 7. Trabajo de revisión que todavía importa

La limpieza no se considera cerrada sólo porque el árbol sea menor.

El revisor debe buscar especialmente **referencias colgantes y contratos
ejecutables que todavía modelen el mundo anterior**.

Hallazgos ya medidos en esta rama que requieren reconciliación antes del cierre:

### Registry de herramientas

`data/tool_registry.json` debe representar el conjunto real de
`tools/*.py`.

Se observó que herramientas presentes no aparecen en el registry y que al menos
una herramienta eliminada sigue declarada allí. No solucionar esto inventando
vigencia: cada estado debe tener evidencia suficiente.

### Estado del sistema

`src/flujo/knowledge/system_status.py` todavía modela `AGENTS.md` como parte
de su contrato y usa una frase exacta antigua para reconocer su ausencia
intencional.

Debe alinearse con `SYSTEM.md` y con la política actual sin volver a crear
`AGENTS.md`.

### Fallback de diagnósticos

`src/flujo/diagnostics.py` conserva rutas de fallback hacia autoridades
retiradas como `AGENTS.md` y `context/LAST_HANDOFF.md`.

El fallback también debe representar el sistema actual; no basta con que el JSON
principal esté correcto.

### Contrato README

`SYSTEM.md` declara que `arte-ascii-readme.svg` es el README raíz y que
`README.md` no debe recrearse.

Cualquier metadata, herramienta o test que todavía requiera `README.md` debe
reconciliarse con esa decisión. No resolver el problema recreando
`README.md`.

### Documentación de sesión restante

Rutas como `docs/session_learning/` y `docs/system_learning/` deben evaluarse
por consumo y contenido, no borrarse en bloque.

Un plan fechado de sesión que sólo reproduce estado antiguo puede retirarse.
Conocimiento durable único debe preservarse o absorberse antes.

## 8. Orden para el agente MAK

Cuando se pida "revisa la rama SUPERVISOR":

1. no empieces reconstruyendo la historia completa;
2. lee `SYSTEM.md` y este archivo;
3. mide `main...SUPERVISOR`;
4. ejecuta las superficies de contexto/estado actuales;
5. revisa consumidores, tests y workflows afectados;
6. clasifica cada problema como:
   - regresión real,
   - referencia colgante,
   - historia legítima,
   - contenido legítimo,
   - eliminación intencional;
7. corrige referencias colgantes y regresiones reales;
8. no restaures piezas retiradas sin demostrar necesidad actual;
9. corre los gates relevantes;
10. deja el árbol explicable sin agregar otra capa de documentos de sesión.

## 9. Criterio de salida

La rama queda lista para integrar cuando:

- las eliminaciones importantes pueden explicarse por categoría;
- no quedan consumidores actuales apuntando a autoridades retiradas;
- los registries reflejan el árbol real;
- tests y workflows relevantes representan la topología actual;
- las ausencias deliberadas no generan falsos errores;
- no se perdió evidencia/contenido real por una limpieza mecánica;
- `SYSTEM.md` basta como contexto durable después del merge.

## 10. Destino de este archivo

`SUPERVISOR.md` es deliberadamente temporal.

Debe permanecer durante la auditoría y revisión del PR para que cualquier agente
entienda la intención del diff.

Antes de cerrar definitivamente la operación, sus decisiones durables que no
estén ya en `SYSTEM.md` deben absorberse allí y este archivo debe eliminarse en
un commit de cierre.

Git conservará este parte de misión como historia de la operación.
