# SUPERVISOR

Memoria compacta del supervisor remoto de VIBECODEINE. Git conserva la historia.

## Objetivo

El supervisor paga el contexto caro y mantiene un buffer secuencial de trabajo útil para Codex local.
Meta de abastecimiento: aproximadamente 30-60 minutos de trabajo prevalidado, no un número fijo de tareas.
Si sólo existen dos tareas buenas, deja dos. Nunca rellenes el buffer con auditorías inútiles.

## Orden de evidencia

Cuando el buffer se agota o bloquea:
1. consume sus resultados;
2. descubre la línea principal actual y lee aproximadamente sus últimos 10 commits;
3. identifica líneas recientes y si ya fueron absorbidas;
4. lee este snapshot y SYSTEM.md;
5. abre sólo código, consumers, tests y contratos relacionados;
6. preflight de cada item antes de meterlo al buffer.

No recorrer todo el árbol para encontrar anomalías al azar.

## Prioridad

Preferir BUILD/FINISH. La higiene sólo entra si bloquea una trayectoria funcional, pruebas necesarias, ejecución o release.
No encadenar inventarios, taxonomías o conteos por sí mismos.

## Buffer

ORDEN.md es el único buzón reemplazable.
Estados top-level: READY, RUNNING, DEPLETED, BLOCKED, COMPLETE.
Estados de item: READY, CONDITIONAL, RUNNING, DONE, BLOCKED, SKIPPED.

Un item CONDITIONAL sólo se ejecuta cuando sus dependencias están DONE y su condición es verdadera.

## Ejecutor local

Codex consume el buffer secuencialmente en la misma sesión:
1. git fetch origin;
2. toma el primer item READY;
3. valida su guard;
4. marca RUNNING;
5. ejecuta sólo su write-set;
6. corre pruebas;
7. hace commit de producto;
8. compacta el resultado de ese item dentro de ORDEN.md;
9. promueve el siguiente CONDITIONAL si corresponde y continúa inmediatamente;
10. al agotar el buffer deja state: DEPLETED.

No espera al supervisor entre items.
Se detiene ante stale_code_base, blocker de alcance, contradicción de owner/consumer o decisión humana no autorizada.
Muchos errores se agrupan por causa raíz, máximo cinco grupos.
No crear ERRORES.md, RESULTADOS.md, NEXT.md, handoffs ni diarios.

## Concurrencia

El buffer registra base_product_head. Commits posteriores que sólo tocan SUPERVISOR.md u ORDEN.md son control-plane.
Codex conserva el último commit de producto que creó. Antes de cada item vuelve a hacer fetch.
Si aparece un cambio de producto ajeno posterior a ese HEAD, detiene el buffer con stale_code_base.

## Trayectoria consumida

Los últimos ciclos cerraron:
- learning_evaluations -> MLflow/Azure ML;
- lineage local seguro;
- MAK -> FLUJO -> MakPanel visible sin polling a Azure.

Azure queda cerrado por ahora; no continuar por inercia.

La trayectoria reciente de main también consolidó Hub/Portfolio/archivo y dejó:
direction-context -> work-packet -> work-preview -> human review before execution.

El sistema ya previsualiza una de cuatro tareas, pero no tiene una transición explícita y trazable desde preview a revisión humana solicitada/confirmada.

## Límite del buffer actual

Avanzar sólo hasta donde exista autoridad segura:
1. hacer explícita la solicitud de revisión humana;
2. permitir confirmación/rechazo idempotente sin ejecutar;
3. producir readiness para structural_order sólo si la confirmación existe y el ejecutor estructural ya tiene autoridad comprobable.

No fabricar autorización humana ni ejecutar una operación artística o semántica.

## Deuda no prioritaria

Registry incompleto, clasificación stale, taxonomía de tests, dos tools VIVO con --help defectuoso, referencias retiradas y opcionales ausentes.
Sólo volver a ellas si bloquean trabajo real.

## Cierre

Cuando el buffer quede DEPLETED, el supervisor reconstruye trayectoria reciente y lo reemplaza.
Si no puede prevalidar más trabajo funcional, usa COMPLETE.