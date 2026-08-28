# MAK: teoría maestra reconciliada

## Tesis

MAK no es una tarea de ordenar carpetas ni un generador de portafolios. Es un
sistema operativo de conocimiento para archivos artísticos: observa un mundo
físico, conserva memoria temporal, propone y refuta relaciones, reconstruye
unidades prudentes, cruza la práctica con el mundo cultural, compila productos
coordinados y aprende de consecuencias externas verificadas.

Su unidad de generalización es el archivo de una persona o artista con años de
obra terminada, procesos, versiones, proyectos nativos, exports, publicaciones,
documentos y episodios. ARICA, MYRA, RAYU, ISKVW y Fondart son casos que enseñan
al sistema; nunca deben aparecer como reglas de la arquitectura reusable.

El resultado humano no es un informe sobre el archivo. Es un conjunto de
productos útiles y trazables —portfolio, dossier, postulación y research— que
puede crecer autónomamente sin inventar autoría, intención, identidad de obra,
publicación ni readiness.

## Síntesis de las seis perspectivas

Las seis lecturas no compiten; describen planos distintos del mismo sistema:

1. **Responder saludo** define el propósito intelectual: operating world,
   supervisión natural, representación antes que clasificación, curaduría como
   compilación y aprendizaje por episodios.
2. **Observar archivos MAK** define la ontología material: identidad física,
   identidad de contenido, estados por snapshot, replay, relaciones, unidades y
   portabilidad.
3. **Auditar capacidades MAK** define el criterio operativo: una herramienta
   existente no equivale a capacidad integrada; una capacidad integrada no
   equivale a conocimiento; y ninguno equivale a producto verificable.
4. **LUNA-ARCHIVE** define las leyes de conservación: ninguna transformación
   puede perder identidad, procedencia, incertidumbre o significado.
5. **LUNA-CONTROL** define gobierno y actuación: departamentos, órganos,
   capacidades y owners son proyecciones diferentes; plan, ejecución y
   consecuencia externa deben permanecer separados.
6. **LUNA-WORLD** define el acoplamiento externo: Vigía descubre, capture
   registra, Research triangula, evidence return propone y el controlador
   decide cuándo recomputar o detenerse.

La dirección maestra agrega una séptima función: ordenar esas perspectivas en
una causalidad única y obligarlas a terminar en un producto medible antes de
abrir otro piso.

## Modelo del sistema

En el tiempo `t`, el estado de MAK puede representarse como:

```text
X_t = (A_t, M_t, H_t, K_t, W_t, Q_t, P_t, E_t, C_t)
```

- `A_t`: artefactos físicos y sus estados observados.
- `M_t`: memoria temporal append-only y replayable.
- `H_t`: hipótesis de relaciones, unidades y programas con alternativas.
- `K_t`: conocimiento apoyado por evidencia y sus unknowns.
- `W_t`: modelo versionado del mundo externo y sus oportunidades.
- `Q_t`: frontier de preguntas priorizadas por valor de información.
- `P_t`: plan común y productos derivados.
- `E_t`: episodios con decisión, observación y outcome separados.
- `C_t`: política de control finita, inicialmente plan-only.

Cada transición válida conserva un conjunto de invariantes. Si una proyección
no puede demostrar qué conservó, no es una transición del sistema: es sólo una
salida conveniente.

## Las cuatro conservaciones

### Identidad

`archive_id + artifact_ref` representa una localización física; `content_id`
representa bytes. Dos paths con bytes iguales siguen siendo dos artefactos.
Un path con bytes nuevos conserva continuidad física y cambia de estado. Una
unidad provisional, un proyecto o una obra no se deriva automáticamente de
ninguno de esos IDs.

### Procedencia

Toda relación, claim, requirement, texto y asset debe poder retroceder hasta
una observación o receipt. Un producto derivado no sustituye la evidencia que
lo originó. Una base, índice, embedding o manifest también es una proyección y
debe declarar productor, schema, fuente y consumidor.

### Incertidumbre

`candidate`, `unknown`, `abstain`, `contradicted` y `rejected` son estados
productivos. Permiten compilar lo apoyado y convertir lo importante que falta
en una sonda finita. `Rejected` es monotónico dentro de una evaluación: un gate
posterior que abstiene no puede revivirlo.

### Significado

Un `.blend` no prueba obra; un export no prueba publicación; una fuente oficial
no prueba la práctica del artista; una narrativa fluida no crea un claim; y un
outcome exitoso no prueba mérito artístico. Cada tipo de evidencia conserva su
alcance semántico.

## Dos autoridades y una unión tipada

El sistema mantiene dos memorias que nunca se fusionan por parecido:

```text
archivo + receipts internos -> practice evidence
fuentes oficiales versionadas -> opportunity evidence
```

Sólo se encuentran en `requirement_id -> evidence_refs`. Este binding permite
afirmar que cierta evidencia apoya o contradice cierto requisito. No permite
afirmar autoría, intención o valor. La validez temporal es previa al fit:
`observed_local`, `unknown` y `stale` abstienen; `expired` e `ineligible`
fallan; sólo `current_verified` confirmado abre la puerta temporal.

## Research, scraping y triangulación

Scraping no es acumulación de páginas. Es un sensor de un mundo que cambia.
Vigía detecta candidatos; un gate bounded registra una sola versión con URL,
hashes, fecha, backend y licencia; un compilador identifica qué requirements
cambiaron; y Research formula la pregunta mínima capaz de cerrar un gap.

Triangular no significa contar URLs. Exige grupos de origen realmente
independientes, conserva contraevidencia y debe fallar cerrado ante pares
`job_id + requirement_id` inesperados. Su salida es una propuesta aditiva,
nunca una escritura directa en la práctica del artista.

Hay dos bucles:

- **Rápido:** gap -> job -> capture -> triangulation -> proposal -> explicit
  ingestion -> selective recompute.
- **Lento:** decisión de producto -> outcome externo -> episodio validado ->
  holdout por identidad -> comparación shadow -> política candidata.

Ambos terminan cuando no cambia el hash, se agota el valor de información, se
cumple el presupuesto o falta una autoridad necesaria.

## Curaduría y producto

Curaduría no es poner una etiqueta verdadera a cada archivo. Es optimizar una
vista útil sobre evidencia incompleta. Genera programas posibles, intenta
refutarlos y selecciona secuencias por cobertura, diversidad, coherencia,
contradicción, riesgo, costo y requisitos del consumidor.

Portfolio, dossier, postulación y research brief son vistas del mismo
`common product plan`. Comparten claims, assets, requirements, privacidad,
licencia, gaps y provenance. Un dossier puede ser útil mientras una postulación
permanece bloqueada y Research continúa abierto. Esa combinación es salud del
sistema, no fracaso.

El primer producto real de MAK no debe inventarse aparte del pipeline: debe ser
el dossier/portfolio interno que la cadena compila desde el archivo. Su valor se
mide por trazabilidad, utilidad y reducción causal de gaps, no por optimismo.

## Base de datos y memoria

MAK no necesita una base universal que trague todos los departamentos. Necesita
memorias con autoridades claras:

- memoria física y temporal del archivo;
- Project IR como intercambio provisional;
- estados de práctica y oportunidad separados;
- ledger de episodios y outcomes;
- stores departamentales cuando tienen consumidores propios.

Las bases existentes se conectan mediante contratos y refs, no mediante copias
masivas ni joins por nombre. DuckDB, SQLite, índices o vectores pueden acelerar
consultas y representación; no elevan el estatus epistemológico de sus filas.

### Topología física reconciliada — 2026-08-27

La limpieza operativa de MAK no significa reducir el número de archivos a la
fuerza. Significa que cada store tiene una sola clase y un camino legible:

```text
archivo/indexes -> archive memory -> Project IR -> mak_knowledge.db
fuentes Vigía   -> source captures -> constraints/fit -> Research + MAK memory
RD catálogo     -> rd.db -> RD/serve/departments
RD privado      -> rd_datos.db -> intake privado aislado
flyers          -> flujo.db -> index/flyer consumers
MAK memory      -> intake/product projections -> Portfolio/Postulación/Research
```

`data/mak_knowledge.db` es la memoria transversal activa de MAK, no un depósito
para absorber las soberanías de RD ni los snapshots de Research. `data/rd.db`,
`data/rd_datos.db` y `data/flujo.db` siguen siendo stores separados porque sus
consumidores, privacidad y políticas de escritura son distintos. Las bases en
`labs/`, `research/corpus/`, `research/intake/`, `experiments/pilots/` y
`out/archaeology/` son snapshots, capturas o evidencia histórica; se conectan
por hashes, contratos y referencias, nunca por una copia que borre su origen.

El inventario físico, los conteos, los hashes y las conexiones están en
`docs/system_learning/master/inventory.json` bajo `database_registry`; el
mapa causal de sus consumidores está en `hashmap.json`. Esa pareja es la
referencia única para distinguir autoridad, proyección, fixture y legado.

## Deep learning en el lugar correcto

Los años de trabajo contienen supervisión natural: proyectos nativos, exports,
versiones, sidecars, manifests, publicaciones, decisiones y outcomes. Pero esa
supervisión debe construirse después de separar identidad y congelar holdouts.

El orden lógico es:

1. reglas e invariantes;
2. baselines deterministas;
3. representaciones y features congeladas;
4. modelos pequeños con split por persona/archivo/proyecto;
5. aprendizaje shadow de ranking, atención, VOI y query selection;
6. modelos complejos sólo si superan el baseline sin leakage.

El sistema nunca entrena verdad, autoría, identidad o valor artístico desde sus
propios drafts. El deep learning sirve para priorizar relaciones, sondas y
selecciones; los gates independientes conservan la autoridad.

## Organización y control

Los departamentos representan ownership. Los órganos representan pasos del
flujo. Copilot representa capacidades seleccionables. El mapa owner-consumer
representa implementación y uso. No son cuatro arquitecturas rivales.

El crosswalk correcto es:

```text
capability -> owner -> interface -> validator -> consumer -> receipt
```

Conductor sólo puede ejecutar una acción cuando ese recorrido existe y la
acción está allowlisted, presupuestada, idempotente, observable y reversible.
Hasta entonces la autonomía selecciona planes; no publica, postula, entrena ni
muta fuentes.

## Cómo se evita el loop de bugs

El loop aparece cuando el objeto de trabajo es “el repositorio” o “todos los
bugs”. El objeto correcto es una causalidad vertical con un consumidor real.

El director mantiene un solo corte activo:

```text
input real -> primera frontera rota -> reparación mínima -> gate focalizado
-> mismo replay -> delta explicable -> producto -> siguiente dependencia
```

Un fallo se arregla si corta esa causalidad. Los demás se registran y esperan.
Una fase no termina por cantidad de tests sino cuando el consumidor puede usar
la salida y cada delta se explica por evidencia nueva.

## Estado empírico al transferir la dirección

El full observation de ARICA ya es durable: 12.332 artefactos, 12.015 archivos,
128 observaciones y snapshot estable. La captura oficial Fondart ya existe y
declara `current_verified`, `confirmed=true`, con vigencia hasta 2026-09-10.
Los receipts de práctica ya tienen cuatro bindings físicos exactos.

Sin embargo, el replay enriquecido todavía no es aceptable. Una edición en
`product_episode.py` dejó `program_requirement_ids` fuera de `_validate_plan`;
las diez pruebas focalizadas del episodio fallan. Los manifests actuales de
`full-baseline/` y `enriched/` son evidencia histórica de intentos, no una
comparación causal final.

Esta observación cambia el norte inmediato: ya no hay que buscar más evidencia
ni diseñar otro piso. Hay que restaurar una sola arista, repetir baseline y
enriched desde el mismo snapshot, verificar hashes en disco y medir qué cambió.

## Teorema operativo de mejora

MAK mejora en una iteración sólo si se cumplen simultáneamente:

1. iguales inputs normalizados producen iguales outputs;
2. todo delta tiene una cadena causal a evidencia nueva o código versionado;
3. disminuyen gaps relevantes o aumenta la precisión de su abstención;
4. aumenta la utilidad de al menos un producto real;
5. no crecen las promociones falsas ni los efectos externos implícitos;
6. la misma lógica sobrevive a un archivo holdout sin reglas por caso.

Más archivos clasificados, más embeddings, más tests o más documentos no son
por sí solos mejora de sistema.

## Rol del director siguiente

La sesión **Responder saludo** recibe la dirección porque conserva el contexto
intelectual más amplio. Su función no es implementar todo personalmente ni
abrir tareas ilimitadas: mantiene misión, causalidad activa, autoridad,
write-sets, gates y condición de salida; asigna slices bounded cuando convenga;
reconcilia los resultados contra evidencia física; y no abre un piso hasta que
el anterior produzca un artefacto útil y un delta aceptado.

El plan único y su primer comando están en `action_plan.md`. El inventario de
agentes, componentes, hashes y gaps está en `inventory.json`; las relaciones,
bucles, invariantes y frontera rota están en `hashmap.json`.
