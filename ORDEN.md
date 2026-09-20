# ORDEN.md — buffer de ejecución autónoma

> **Propietario: ChatGPT supervisor. Codex NO edita este archivo.**

```yaml
schema: vibecodeine-supervisor-order-v1
state: READY
generation: 2
branch: SUPERVISOR
repo: ligereza/vibecodeine
base_context_pr: 569
last_audited_head: 19fb13e5ed312d105caf28233270d1ad25819ba2
last_audit: 2026-09-20
accepted_through: none
```

## Regla de consumo

Codex toma la **primera fase PENDING** cuya dependencia esté satisfecha. Antes
de empezarla hace pull/rebase y relee este archivo. Al terminar reporta sólo en
`CODEX_STATE.md`, commit y push. El supervisor aceptará o devolverá el trabajo
en la siguiente auditoría.

## Fases actuales

### S001 — Baseline reproducible de la rama de supervisión
**Estado:** PENDING  
**Objetivo:** demostrar exactamente qué contiene `SUPERVISOR` antes de seguir
cambiando arquitectura documental.  
**Alcance:** registrar HEAD/base, árbol limpio/sucio, diff respecto de `main`
y respecto de `docs/contexto-canonico-20260920`; comprobar existencia de
`AGENTS.md`, `REAL_INFO.md`, `HISTORICO.md`, `SUPERVISOR.md`,
`ORDEN.md`, `CODEX_STATE.md`. No modificar producto.  
**Aceptar con:** comandos + resultados en `CODEX_STATE.md`; cualquier
inconsistencia real se corrige sólo si es trivial y de esta infraestructura.  
**Parar si:** la rama local no puede sincronizarse con `origin/SUPERVISOR`.

### S002 — Veredicto real del PR #569 y fallos derivados
**Estado:** PENDING  
**Depende de:** S001.  
**Objetivo:** inspeccionar el PR #569, sus workflows/checks y cualquier fallo
provocado por la consolidación documental.  
**Alcance:** corregir únicamente regresiones causadas por el nuevo bootstrap
`AGENTS.md -> REAL_INFO.md`; no arreglar deuda histórica ajena.  
**Aceptar con:** URLs/IDs o salida de checks, test focal relevante y commit de
reparación si hizo falta.  
**Parar si:** el fallo necesita una decisión de producto no relacionada con
contexto/agentes.

### S003 — Censo de fuentes de autoridad todavía competidoras
**Estado:** PENDING  
**Depende de:** S001.  
**Objetivo:** localizar Markdown/config/prompts activos que todavía se
autoproclamen `CURRENT`, `CANONICAL`, `MASTER`, `LAST_HANDOFF`,
`NEXT` o “source of truth” global.  
**Alcance:** excluir historia explícita, vendored, productos humanos y
`docs/recovered`; clasificar cada hallazgo como activo, dominio o histórico.
No hacer una poda masiva en esta fase.  
**Aceptar con:** inventario corto y reproducible + lista concreta de hallazgos
que realmente compiten con el bootstrap.  
**Parar si:** el término pertenece sólo a un dominio local y no compite con la
autoridad global.

### S004 — Censo de routers automáticos de contexto
**Estado:** PENDING  
**Depende de:** S003.  
**Objetivo:** encontrar todo código, hook, skill o config que le diga a un
agente qué leer primero.  
**Alcance:** `.claude/`, `.github/skills/`, diagnostics, herramientas de
contexto, prompts y rutas equivalentes. Detectar referencias a
`DECISIONES.md`, handoffs, PHASE o archivos retirados como first-read.  
**Aceptar con:** tabla ruta → comportamiento → correcto/obsoleto, y correcciones
quirúrgicas de los obsoletos.  
**Parar si:** la referencia es evidencia histórica y nunca se ejecuta/rutea.

### S005 — Gate automático contra regresión de bootstrap
**Estado:** PENDING  
**Depende de:** S003, S004.  
**Objetivo:** hacer que CI detecte si reaparece otra entrada global o un router
vuelve a mandar a historia.  
**Alcance:** extender/reutilizar tests existentes; no crear un framework nuevo.
Debe fijar como mínimo: un solo `AGENTS.md`, `REAL_INFO.md` como segundo
paso, historia fuera de first-read y ausencia de case variants.  
**Aceptar con:** test focal rojo ante fixture/condición inválida y verde en el
árbol correcto; registrar comando exacto.  
**Parar si:** ya existe una prueba equivalente; en ese caso fortalecerla en vez
de duplicarla.

### S006 — Contexto barato por tarea
**Estado:** PENDING  
**Depende de:** S004.  
**Objetivo:** asegurar que el comando/herramienta barata de contexto entregue
el bootstrap mínimo y rutas específicas de la tarea, sin escanear todo el repo.  
**Alcance:** preferir `tools/contexto_repo.py` u otra implementación ya
existente. El resultado debe comenzar por `AGENTS.md` + `REAL_INFO.md` y no
inyectar handoffs globales.  
**Aceptar con:** ejecución real sobre al menos 3 consultas de dominios distintos
y salida acotada/relevante.  
**Parar si:** requiere indexar contenido masivo para funcionar.

### S007 — Superficie documental activa mínima
**Estado:** PENDING  
**Depende de:** S003.  
**Objetivo:** distinguir qué Markdown raíz/context/docs siguen siendo
navegación activa y cuáles son sólo compatibilidad/evidencia.  
**Alcance:** no borrar `docs/recovered`, productos humanos ni documentos con
consumidores de código. Reducir sólo duplicidad global demostrada.  
**Aceptar con:** mapa corto de documentos activos y consumidores; cualquier
retirada debe tener prueba de ausencia de consumidor o redirect explícito.  
**Parar si:** la autoridad del documento depende de una decisión humana de
producto.

### S008 — Simulación de “Codex amnésico”
**Estado:** PENDING  
**Depende de:** S005, S006, S007.  
**Objetivo:** probar el flujo como si un agente no supiera nada del proyecto.  
**Alcance:** a partir únicamente de `AGENTS.md`, `REAL_INFO.md` y una tarea
ficticia acotada, verificar que puede identificar dominio, archivos iniciales,
fuente de hechos y checks sin abrir historia. Puede implementarse como test o
script determinista si aporta valor; evitar LLM-in-test.  
**Aceptar con:** procedimiento reproducible y evidencia de que no necesita
`NEXT`, handoff, PHASE ni sesión recuperada.  
**Parar si:** la simulación empieza a codificar conocimiento específico de una
sola tarea.

### S009 — Auditoría del protocolo Supervisor ↔ Codex
**Estado:** PENDING  
**Depende de:** S001–S008 según avance.  
**Objetivo:** comprobar que `SUPERVISOR.md`, `ORDEN.md` y
`CODEX_STATE.md` no crean otra fuente de verdad global.  
**Alcance:** estos archivos gobiernan sólo la rama/bucle autónomo; no deben
contradecir `AGENTS.md` o `REAL_INFO.md`. Verificar que la propiedad de
archivos evita conflictos y que una fase puede auditarse por SHA/tests.  
**Aceptar con:** una pasada real del ciclo y ajustes mínimos al protocolo si
hicieron falta.  
**Parar si:** corregirlo exige meter estado efímero dentro de
`REAL_INFO.md`.

### S010 — Cierre de generación 1 y siguiente frontera real
**Estado:** PENDING  
**Depende de:** evidencia acumulada.  
**Objetivo:** medir qué problema de “agentes perdidos” sigue existiendo después
de S001–S009 y convertirlo en la siguiente cola, no asumir que la documentación
era la única causa.  
**Alcance:** revisar commits, tests, routers y fricción observada por Codex.
Proponer las próximas fases por evidencia.  
**Aceptar con:** `CODEX_STATE.md` deja un diagnóstico corto con problemas
restantes ordenados por causa, no por cantidad de archivos.  
**Parar si:** no queda ningún problema reproducible; reportar candidato a
`COMPLETE`.

## Auditoría del supervisor

**Generación 2 — HEAD auditado: `19fb13e5ed312d105caf28233270d1ad25819ba2`.** Desde la auditoría anterior sólo existe el commit `supervisor: seal initial order generation`, que modifica exclusivamente `ORDEN.md`. `CODEX_STATE.md` continúa `IDLE`, sin fase ejecutada, commit reclamado, archivos ni verificaciones; por tanto no se acepta ni rechaza ninguna fase. El HEAD no tiene statuses ni workflow runs observables. Se conserva la cola S001–S010 y `READY`; S001 sigue siendo la primera acción justificada.
