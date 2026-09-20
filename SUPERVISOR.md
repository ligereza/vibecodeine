# SUPERVISOR.md — protocolo autónomo ChatGPT ↔ Codex

Este archivo define el canal de coordinación para la rama `SUPERVISOR` de
`ligereza/vibecodeine`.

## Objetivo

Mantener un único Codex local trabajando sin depender de prompts humanos
adicionales. ChatGPT actúa como supervisor remoto una vez por hora. GitHub es
el único canal entre ambos.

El trabajo no se planifica desde memoria de conversación. Cada actor reconstruye
el estado desde el repositorio.

## Jerarquía de lectura

Siempre:

1. `AGENTS.md`
2. `REAL_INFO.md`
3. `SUPERVISOR.md`
4. `ORDEN.md`
5. `CODEX_STATE.md`
6. sólo después, código/tests/documentos específicos de la fase activa

`HISTORICO.md` se abre únicamente para arqueología.

## Propiedad de archivos

### ChatGPT supervisor escribe

- `ORDEN.md`

Codex **no edita `ORDEN.md`**.

### Codex local escribe

- código, tests y documentación necesarios para la fase
- `CODEX_STATE.md`

ChatGPT **no edita `CODEX_STATE.md`**.

### Compartidos pero estables

- `AGENTS.md`
- `REAL_INFO.md`
- `SUPERVISOR.md`

Sólo se modifican si una fase lo exige de forma explícita.

Esta separación evita conflictos Git y hace posible auditar afirmaciones del
agente contra evidencia independiente.

## Rama

Todo el ciclo autónomo ocurre en:

```text
SUPERVISOR
```

No hacer push directo a `main`. No mergear automáticamente `main`. El
supervisor puede abrir/actualizar PRs cuando sea útil, pero la rama
`SUPERVISOR` es el cuaderno de trabajo operativo.

## Estados de ORDEN

- `READY`: hay trabajo disponible.
- `RUNNING`: existe una fase activa confirmada por evidencia reciente.
- `DEPLETED`: Codex consumió la cola; el supervisor debe reponerla.
- `BLOCKED`: no se puede producir una fase segura sin una decisión externa.
- `COMPLETE`: objetivo global cerrado; Codex debe detenerse.

El supervisor puede cambiar el estado. Codex sólo reporta su propio estado en
`CODEX_STATE.md`.

## Unidad de trabajo

Una fase debe caber aproximadamente en 30–60 minutos de trabajo concentrado y
tener:

- ID estable;
- objetivo;
- alcance;
- evidencia de aceptación;
- condición de parada.

`ORDEN.md` mantiene **exactamente 10 fases pendientes/activas** siempre que
haya diez acciones útiles y seguras disponibles.

Una fase no es “investigar el repo”. Debe nombrar la pregunta o cambio concreto.

## Bucle de Codex

Antes de CADA fase:

1. `git fetch origin`
2. incorporar `origin/SUPERVISOR` sin pisar trabajo local;
3. releer `ORDEN.md`;
4. comprobar que el ID que va a ejecutar sigue en la cola;
5. marcar en `CODEX_STATE.md` el ID como `RUNNING`.

Durante la fase:

- trabajar sólo el alcance indicado;
- buscar antes de crear otra implementación;
- no usar documentos históricos como estado;
- no modificar `ORDEN.md`;
- no esconder fallos de tests o checks.

Al cerrar la fase:

1. ejecutar la evidencia exigida;
2. actualizar `CODEX_STATE.md` con resultado, archivos, comandos y SHA;
3. commit;
4. `git pull --rebase origin SUPERVISOR`;
5. resolver sólo conflictos que entienda;
6. push a `origin/SUPERVISOR`;
7. volver a leer `ORDEN.md` y tomar la primera fase pendiente vigente.

Si la cola queda vacía, marcar `DEPLETED` en `CODEX_STATE.md`, hacer push y
esperar una nueva generación de `ORDEN.md`. Si el entorno permite mantener la
sesión, consultar `origin/SUPERVISOR` periódicamente; si la sesión termina,
el repo debe quedar suficientemente explícito para reanudar sin reconstrucción.

## Bucle del supervisor horario

En cada auditoría, ChatGPT debe:

1. leer los cinco archivos del orden obligatorio;
2. leer el HEAD de `SUPERVISOR`, commits desde la auditoría anterior y diff
   relevante;
3. contrastar cada afirmación de `CODEX_STATE.md` con commits, archivos,
   tests y CI disponibles;
4. aceptar, rechazar o devolver una fase a reparación;
5. conservar una fase realmente `RUNNING` salvo que haya evidencia de que su
   premisa quedó obsoleta;
6. retirar de la cola lo ya aceptado;
7. reordenar por dependencia/riesgo;
8. rellenar hasta 10 fases accionables;
9. actualizar `ORDEN.md` en `SUPERVISOR`;
10. dejar en `ORDEN.md` el HEAD auditado y una nota corta de la auditoría.

El supervisor no debe crear trabajo sólo para llenar diez casillas. Si quedan
menos de diez acciones justificables, mantiene las reales y explica la razón.

## Evidencia mínima de una fase

Una fase sólo se considera aceptada cuando existe, según corresponda:

- commit SHA;
- lista de archivos modificados;
- comandos de verificación y resultado;
- CI/checks si aplica;
- explicación del límite de lo no verificado.

“Listo”, “parece bien”, un documento narrativo o el propio
`CODEX_STATE.md` no son evidencia suficiente.

## Replanificación

El supervisor puede reemplazar fases futuras cuando:

- el código demuestra que la premisa era falsa;
- una fase anterior resolvió varias posteriores;
- aparece un fallo más fundamental;
- CI demuestra una regresión;
- el usuario cambió el objetivo.

Nunca cambia silenciosamente la fase activa: registra en la nota de auditoría
por qué fue cancelada o sustituida.

## Bloqueos

Primero intentar una ruta alternativa segura.

Usar `BLOCKED` sólo si hace falta de verdad:

- una decisión de producto/semántica del usuario;
- una credencial o acceso no disponible;
- una acción destructiva o irreversible no autorizada;
- una dependencia externa que impide obtener evidencia.

El bloqueo debe decir exactamente qué falta. No convertir incertidumbre técnica
ordinaria en una pregunta al usuario.

## Límites permanentes

- nada de secretos en Git;
- nada de push directo a `main`;
- nada de merges automáticos a `main`;
- nada de borrados masivos fuera de una fase explícita y auditable;
- no modificar datos/productos humanos por “limpieza” documental;
- mantener separado hecho medido, inferencia y decisión;
- si CI no se pudo observar, declararlo; no inventar un verde.
