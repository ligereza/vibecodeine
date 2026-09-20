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

Carga el contexto caro.

En cada ciclo:

1. lee `SYSTEM.md`, este archivo y `ORDEN.md`;
2. inspecciona el estado actual de la rama/PR y sólo el código necesario para
   decidir;
3. consume el resultado `DONE` o `BLOCKED` dejado por Codex;
4. actualiza **esta cola viva**, sustituyendo estado viejo en vez de agregar
   historia;
5. elige una sola tarea de alto impacto y write-set acotado;
6. reemplaza `ORDEN.md` con la nueva orden `READY`.

No crea documentos de errores, handoffs, cierres de sesión ni diarios de
decisiones.

### Codex local

Ejecuta; no redescubre el sistema.

1. lee `ORDEN.md`;
2. abre únicamente los archivos necesarios para cumplir esa orden;
3. ejecuta cambios y pruebas;
4. reemplaza `ORDEN.md` con un reporte compacto `DONE` o `BLOCKED`;
5. no crea `ERRORES.md`, `RESULTADOS.md` ni otro archivo de traspaso.

Si necesita contexto que no está en la orden, debe pedirlo mediante el estado
`BLOCKED` en el mismo `ORDEN.md`, no iniciar una arqueología completa.

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
