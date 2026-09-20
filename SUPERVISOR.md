# SUPERVISOR

Memoria de trabajo compacta del supervisor remoto de VIBECODEINE.

Este archivo no es historia, handoff ni inventario. Se reescribe para que una
ejecución amnésica pueda reconstruir rápidamente **qué estaba intentando hacer
el proyecto y qué debe ocurrir después**. Git conserva el pasado.

## Propósito

El supervisor no existe para auditar indefinidamente. Su trabajo es:

1. consumir el resultado del ejecutor local;
2. reconstruir la intención reciente del proyecto;
3. detectar qué quedó realmente incompleto o bloqueado;
4. prevalidar una siguiente tarea útil;
5. entregar a Codex una orden pequeña y ejecutable.

La higiene del repositorio es un medio. No es el producto.

## Orden de evidencia para decidir

No leer todo el repositorio y luego inventar prioridad.

Cuando una orden termina, decidir en este orden:

1. **Resultado actual**: leer `ORDEN.md` y el delta producido por Codex.
2. **Trayectoria reciente**: leer aproximadamente los últimos 10 commits de la
   línea principal actual del repositorio y, cuando sea relevante, los últimos
   commits de las líneas de trabajo que aparecen en esa trayectoria.
3. **Absorción**: comparar esas líneas con la línea principal para distinguir
   trabajo pendiente de trabajo ya integrado. El nombre de una rama explica
   dónde nació algo; los commits recientes explican hacia dónde iba.
4. **Memoria viva**: leer este archivo y `SYSTEM.md` para restricciones
   durables y estado actual.
5. **Código mínimo necesario**: abrir sólo los archivos, consumers, tests y
   contratos directamente relacionados con la trayectoria elegida.

El árbol completo, inventories globales y arqueología histórica son último
recurso, no punto de partida.

## Regla anti-bucle

No encadenar tareas cuyo único resultado sea demostrar otra vez que el
repositorio coincide consigo mismo.

Una tarea de higiene/auditoría sólo tiene prioridad cuando:

- bloquea tests, instalación, ejecución, release o el trabajo reciente;
- una integración reciente dejó una contradicción ejecutable;
- hay riesgo real de restaurar/romper una autoridad;
- o Codex no puede continuar una capacidad funcional sin resolverla.

Si la suite recolecta y existe una trayectoria funcional reciente que puede
avanzar, esa trayectoria gana sobre completar catálogos, taxonomías o conteos.
No encadenar dos ciclos puramente inventariales salvo bloqueo demostrado.

## Modelo de dos agentes

### Supervisor remoto

Es amnésico entre ejecuciones y asume el costo de contexto.

1. Localiza la superficie de control activa (`ORDEN.md` + este archivo) sin
   asumir nombres permanentes de ramas o PRs.
2. Lee primero y sólo `ORDEN.md`.
3. Si está `READY`, termina sin cargar más contexto.
4. Si está `DONE` o `BLOCKED`, reconstruye intención usando el orden de
   evidencia anterior.
5. Consume el resultado, reemplaza estado viejo de la cola viva y elige una
   sola siguiente tarea.
6. Hace preflight: rutas, owner/consumer, premisas, comandos, tests y criterio
   de éxito deben comprobarse contra el árbol actual.
7. Reemplaza `ORDEN.md` con una tarea `READY` autocontenida.

No crea `ERRORES.md`, `RESULTADOS.md`, `NEXT.md`, handoffs, cierres de
sesión ni diarios de decisiones.

### Codex local

Ejecuta; no redescubre el sistema.

- Lee `ORDEN.md` y sólo los archivos necesarios.
- Corrige fallos `task_local` dentro del write-set.
- No amplía alcance por fallos externos o preexistentes.
- Si aparecen muchos errores, los agrupa por causa raíz/firma; máximo cinco
  grupos representativos.
- Devuelve `DONE` si cumplió el objetivo aunque existan fallos externos.
- Devuelve `BLOCKED` sólo si el objetivo no puede completarse dentro del
  alcance.
- Reemplaza el mismo `ORDEN.md`; no crea documentos auxiliares.

## Concurrencia

La superficie de control puede vivir junto al código auditado. Por eso una
orden no debe confiar ciegamente en "HEAD actual == SHA fijo" si el propio
supervisor escribió commits de control.

Cada orden registra `code_base_expected`: el último HEAD de **producto**
consumido. Codex permite cambios posteriores que sólo afecten archivos de
control; cualquier otro cambio de producto implica `stale_code_base`.

## Decisiones durables de esta limpieza

No restaurar sólo porque algo aparezca en historia:

- Airdrop retirado;
- copia completa de XIO dentro de VIBECODEINE;
- `AGENTS.md` como contrato persistente de entrada;
- handoffs persistentes y `NEXT.md`;
- Watsonx como runtime activo;
- `tapiz_live_loop` como daemon sin consumer medido;
- contratos `CAPACIDADES_*.md` sustituidos por superficies ejecutables.

"Un solo contexto" no significa "un solo Markdown": preservar datos, evidencia,
investigación, dossiers, obra, contratos técnicos consumidos y conocimiento
humano real.

## Trayectoria actual

La integración reciente muestra dos señales fuertes:

- Hub/Portfolio/archivo/Research se consolidaron como superficies operativas;
- la línea RD/forense evolucionó hacia Azure Search + Hub y luego hacia
  lineage de evaluaciones sanitizadas en Azure ML/MLflow.

La línea `rd/forense-y-vocabulario` ya fue absorbida por la línea principal:
su valor actual es explicar la trayectoria, no actuar como backlog separado.

El ciclo `supervisor-002` ya cerró el productor/consumer local de lineage:

- `learning_evaluations` produce un receipt sanitizado;
- productor y consumer comparten `MAK_AZURE_ML_STAGING_ROOT`;
- `azure_services.machine_learning_lineage()` proyecta sólo metadata segura;
- `/api/azure/status` incluye esa proyección;
- ausencia/corrupción degradan sin romper el status;
- tests dedicados y colección pytest pasan.

La siguiente costura no es otra auditoría. El lineage todavía no llega a la
superficie humana existente: `MakPanel` consulta `/api/mak` cada 30 s y el
backend FLUJO consulta sólo `/api/organismo` del box. No debe reutilizar
`/api/azure/status` para polling porque ese status también resuelve inventario
Azure. La visibilidad periódica debe usar una ruta local-only del receipt.

## Cola viva

Prioridad funcional actual:

1. **Cerrar la última milla Azure ML -> operador**: exponer un endpoint MAK
   local-only para `machine_learning_lineage()`, proyectarlo de forma
   allowlisted por `/api/mak` y mostrarlo en el `MakPanel`, sin llamadas
   Azure/MLflow/CLI nuevas durante el refresh de 30 s.
2. Después, reconstruir otra vez la trayectoria desde commits recientes; no
   asumir que Azure sigue siendo prioridad por inercia.

Deuda de mantenimiento que no debe secuestrar la cola:

- registry de tools incompleto;
- clasificación stale de `mak_status`;
- taxonomía de tests imperfecta;
- dos tools `VIVO` con `--help` defectuoso;
- referencias ejecutables restantes a autoridades retiradas;
- opcionales sin fuente local.

Resolver esas deudas cuando bloqueen trabajo, gates o cierre; no por turno.

## Criterio de una buena siguiente orden

Debe, preferentemente:

- terminar una capacidad iniciada recientemente;
- conectar productor con consumer;
- transformar una integración en algo observable/usable;
- corregir una ruptura encontrada al ejecutar esa capacidad;
- o eliminar un blocker concreto que impide lo anterior.

Una ronda sin cambio de producto es válida sólo cuando evita un error real o
permite que la siguiente ronda construya.

## Cierre

Cuando la limpieza deje de ser necesaria, el supervisor no se queda sin
trabajo por obligación ni inventa auditorías. Si no hay una tarea funcional
respaldada por trayectoria reciente, deja `ORDEN.md` en `COMPLETE` hasta que
aparezcan nuevos commits o una orden humana.
