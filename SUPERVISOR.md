# SUPERVISOR

Contexto vivo y compacto de la rama `SUPERVISOR`.

Este archivo no es una bitácora ni un archivo histórico. Se **reescribe** cuando
cambia la situación de la rama. Git conserva el pasado.

## Misión

Auditar `main` después de integraciones mecánicas que recuperaron trabajo
válido pero también resucitaron superficies retiradas, documentación de sesión,
wrappers y contratos obsoletos.

La meta no es reducir archivos por sí misma. La meta es dejar una superficie
operativa coherente, medible y explicable sin perder código vigente, evidencia,
investigación, obra ni conocimiento humano útil.

Regla central:

> No reconstruir `main` dentro de `SUPERVISOR`. Antes de restaurar algo
> eliminado, demostrar un consumer actual o una pérdida funcional.

## Modelo de trabajo

Hay dos agentes con responsabilidades deliberadamente distintas.

### Supervisor remoto

Es amnésico entre ejecuciones, por eso este archivo debe bastarle como memoria
de trabajo compacta.

En cada ciclo:

1. lee primero `ORDEN.md`;
2. si sigue `READY`, termina sin abrir más contexto;
3. si está `DONE` o `BLOCKED`, recién entonces lee `SYSTEM.md` y este
   archivo;
4. mide sólo el delta necesario desde el último trabajo consumido;
5. consume el resultado de Codex y reemplaza estado viejo de **esta cola viva**;
6. investiga la siguiente tarea y la **prevalida**: rutas existentes,
   owner/consumer, supuestos actuales, comandos y criterio de éxito;
7. reemplaza `ORDEN.md` con una única tarea `READY` suficientemente precisa
   para que Codex no repita esa investigación.

No crea documentos de errores, handoffs, cierres de sesión ni diarios de
decisiones.

### Codex local

Ejecuta; no redescubre el sistema.

1. lee `ORDEN.md`;
2. abre únicamente los archivos necesarios para cumplir esa orden;
3. corrige dentro del write-set los fallos causados por su propia tarea;
4. si una prueba devuelve muchos errores, agrupa por causa raíz/firma en vez de
   investigar o copiar cada error;
5. no amplía el alcance por fallos externos/preexistentes;
6. reemplaza `ORDEN.md` con `DONE` si cumplió el objetivo o `BLOCKED` si el
   objetivo no cabe en el alcance;
7. no crea `ERRORES.md`, `RESULTADOS.md` ni otro archivo de traspaso.

El reporte puede incluir como máximo cinco grupos de fallos representativos,
con conteo y clasificación `task_local`, `external` o `unknown`. Si necesita
contexto no suministrado por la orden para completar el objetivo, devuelve
`BLOCKED`; no inicia una arqueología completa.

## Decisiones de esta auditoría

No restaurar sólo porque algo exista en historia o en `main`:

- Airdrop y sus superficies retiradas;
- copia completa de XIO dentro de VIBECODEINE;
- `AGENTS.md` como contrato de entrada;
- handoffs persistentes y `NEXT.md`;
- Watsonx como runtime activo;
- `tapiz_live_loop` como daemon sin consumer medido;
- contratos `CAPACIDADES_*.md` sustituidos por superficies ejecutables.

Una retirada explícita prevalece sobre una reaparición mecánica mientras no
haya una reactivación posterior explícita.

"Un solo contexto" tampoco significa "un solo Markdown": se preservan datos,
evidencia, investigación, dossiers, obra, contratos técnicos consumidos y
conocimiento humano real.

## Cola viva

Esta sección describe sólo problemas **actuales**. Se edita/reduce en cada
ciclo; no se añaden entradas históricas resueltas.

1. **Pytest no recolecta** porque
   `tests/test_scan_roots_skip_cloud_mounts.py` importa
   `tools.consolidate_static_duplicates.PROTECTED_TOPS`, aunque esa herramienta
   fue retirada.
2. **Registry de tools desalineado**: conserva
   `consolidate_static_duplicates.py` y omite herramientas presentes. Debe
   representar el árbol real sin inventar vigencia.
3. **`repo_audit`** reporta clasificación stale para `mak_status`.
4. **Mapa/taxonomía de tests** conserva tests retirados y tiene tests actuales
   sin lane.
5. Dos herramientas declaradas `VIVO` fallan en `--help`:
   `compile_vigia_capture_plans.py` y
   `reportar_calibracion_deepseek.py`.
6. Quedan referencias ejecutables a autoridades retiradas en superficies como
   `system_status.py` y fallbacks de `diagnostics.py`.
7. Superficies opcionales `searxng` y `mak_research_queue` aparecen sin
   fuente local; su estado debe ser explícito, no un falso fallo global.

## Regla de restauración

Antes de restaurar un archivo eliminado, probar:

- owner actual;
- consumer actual;
- capacidad que se rompe sin él;
- ausencia de una superficie nueva equivalente;
- que no fue una retirada explícita resucitada mecánicamente.

Menciones históricas y wrappers legacy no bastan.

## Cierre

La rama queda lista cuando:

- la suite relevante puede recolectarse y los gates no dependen de excepciones
  ad hoc;
- registries y taxonomías describen el árbol real;
- no quedan consumers actuales apuntando a autoridades retiradas;
- las ausencias deliberadas se interpretan como tales;
- no se perdió contenido o evidencia real;
- `SYSTEM.md` conserva únicamente las reglas durables y esta cola viva queda
  vacía.

Cuando la auditoría termine, `SUPERVISOR.md` puede retirarse antes del merge;
Git conserva la operación.
