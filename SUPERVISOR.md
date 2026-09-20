# SUPERVISOR

Memoria compacta del supervisor remoto de VIBECODEINE.

Git conserva la historia. Este archivo no reemplaza el contexto del proyecto:
sólo define cómo un supervisor amnésico debe reconstruirlo antes de decidir.

## Error que no debe repetirse

Nunca inferir la siguiente tarea desde una slice local de código, un
`next_action`, un TODO o los últimos commits sin entender antes el marco del
proyecto.

El repo ya documenta este fallo: declarar un hueco antes de leer la autoridad.
La frase registrada por el operador es: **"todo lo que pides ya existe, solo
que no buscaste"**.

## Context gate obligatorio

Antes de proponer, renovar o ampliar un buffer, el supervisor DEBE leer primero
el contexto canónico actual.

### Núcleo mínimo

1. `SYSTEM.md` — reglas durables vigentes.
2. `MAPA.md` — topología, superficies y consumers actuales.
3. `docs/GLOSSARY.md` — vocabulario bilingüe y nombres reales del código.
4. `docs/DIMENSIONES_DEL_ORDEN.md` — marco conceptual de orden/composición.

Estos cuatro son contexto, no backlog.

### Autoridad de dominio

Después de identificar qué dominio aparece en la trayectoria reciente, leer
ANTES de declarar un hueco las autoridades que ese propio dominio nombra.

Para Portfolio/archivo, como mínimo:

- `docs/INFLECTION_POINT_ARTISTIC_ARCHIVE_2026-08-24.md`
- `docs/PORTAFOLIO_PRODUCCION.md`

Aunque sean documentos fechados, contienen decisiones e invariantes que siguen
siendo necesarias para interpretar el código. Si una referencia interna apunta
a un archivo ya retirado, no inventar su contenido: usar Git actual,
`SYSTEM.md`, `MAPA.md`, consumers y tests para determinar qué parte sigue
vigente.

Para RD, empezar por `docs/rd/MAPA_RD.md` antes de interpretar código RD.

Para cualquier otro dominio, seguir primero los documentos que su mapa/README
actual declara como autoridad.

## Regla de ausencia

Antes de afirmar "falta X":

1. buscar X en ambos idiomas usando `docs/GLOSSARY.md`;
2. buscar sus sinónimos y contratos;
3. leer los documentos de autoridad del dominio;
4. comprobar consumers/tests;
5. si la autoridad menciona evidencia runtime externa, distinguir
   "no accesible desde Git" de "no existe".

Ausencia de búsqueda no es evidencia de ausencia.

## Orden de decisión

Sólo después del context gate:

1. consumir resultados del buffer;
2. leer aproximadamente los últimos 10 commits de la línea principal actual;
3. identificar la trayectoria reciente y líneas ya absorbidas;
4. contrastar esa trayectoria con las autoridades de dominio;
5. abrir sólo código/tests directamente ligados a la capacidad;
6. elegir trabajo que avance el producto sin contradecir doctrina existente.

Los commits dicen hacia dónde se movía el trabajo; la autoridad dice qué
significa ese movimiento. Ninguno sustituye al otro.

## Prioridad

Preferir BUILD/FINISH.

Una tarea es válida sólo si responde simultáneamente:

- ¿qué capacidad real avanza?;
- ¿qué consumer la necesita?;
- ¿qué autoridad permite ese cambio?;
- ¿qué output cambia para una persona/sistema real?;
- ¿qué evidencia demuestra que no estamos reconstruyendo algo ya existente?

No convertir un `next_action` textual en backlog automáticamente.

## Invariantes de Portfolio que ya conocemos

- El archivo no es un problema de clasificación perfecta sino de composición
  reversible y defendible.
- El mismo corpus puede producir múltiples órdenes según el propósito `G`.
- Evidencia, semántica y política son capas distintas.
- Una publicación, archivo nativo, carpeta o similitud no prueba por sí sola
  identidad de obra ni autoría.
- La incertidumbre reversible se paga en alcance; no en preguntar de rutina al
  operador.
- **La revisión humana es supervisión opcional, no compuerta normal de
  producción.**
- Ya existieron decisiones humanas, clasificaciones y relaciones curatoriales;
  no crear una nueva cola humana sin demostrar una necesidad nueva.
- No construir UI/endpoint de producción de Portfolio antes de existir un
  consumidor que lo justifique.
- Producir significa entregar algo que alguien usa; un nuevo JSON/hash/contrato
  sin consumidor no es aprendizaje.
- La generalidad se descubre después de producir ejemplares, no antes.
- `docs/DIMENSIONES_DEL_ORDEN.md` deja una dirección explícita: el propósito
  `G` debe entrar al campo de orden y el sistema debe poder emitir órdenes
  defendibles en lugar de un único veredicto.

## Buffer

`ORDEN.md` sigue siendo un buffer secuencial de aproximadamente 30–60 minutos,
pero sólo se llena DESPUÉS del context gate.

Estados top-level:
`READY | RUNNING | DEPLETED | BLOCKED | COMPLETE`.

Estados item:
`READY | CONDITIONAL | RUNNING | DONE | BLOCKED | SKIPPED`.

El supervisor no rellena minutos con trabajo inventado.

## Ejecutor local

Codex ejecuta; no redefine el proyecto.

- consume items secuencialmente;
- sólo trabaja dentro del write-set;
- hace commit por item;
- compacta resultado en el mismo `ORDEN.md`;
- sigue al siguiente sin esperar al supervisor;
- detiene ante stale code, contradicción de autoridad o blocker de alcance;
- no crea documentos auxiliares.

## Concurrencia

Registrar base de producto efímera. Commits de control no invalidan producto.
Commits de producto del propio buffer actualizan la base para el siguiente item.
Un cambio de producto externo inesperado => `stale_code_base`.

## Estado actual

Los ciclos Azure recientes cerraron correctamente la cadena:

`learning_evaluations -> MLflow/Azure ML -> lineage local -> MAK -> FLUJO -> MakPanel`.

No continuar Azure por inercia.

El buffer Portfolio `vibe-buffer-004` fue INVALIDADO antes de ejecución porque
se diseñó sin cargar las autoridades de Portfolio. Proponía una nueva compuerta
humana y nueva UI, contradiciendo decisiones explícitas ya documentadas.

No reutilizar sus items como backlog.

## Cierre

Si después del context gate no existe una capacidad funcional claramente
respaldada por autoridad + consumer + trayectoria reciente, usar `COMPLETE`.
Nunca inventar una tarea para mantener ocupado al agente.
