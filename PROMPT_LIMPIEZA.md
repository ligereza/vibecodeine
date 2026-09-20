# Limpieza de VIBECODEINE

Trabajar sólo en la rama SUPERVISOR.

Objetivo: limpiar primero el árbol activo y recién después crear un único contexto operacional.

Reglas:
- No usar "viejo = basura": medir consumidor, reemplazo y propósito.
- MAK = computador Linux físico; FLUJO = software; Windows = estación actual; XIO = repo separado.
- arte-ascii-readme.svg ES el README; no crear README.md.
- AGENTS.md fue retirado y no debe tratarse como autoridad.
- Git explica historia; código + consumidores + tests describen el presente.
- Una retirada explícita pesa más que una restauración mecánica posterior si no hubo reactivación explícita.

Prioridades:
1. Recuperar tools/contexto_repo.py con --json desde 9e247e0d y combinarlo con el retiro de AGENTS de cc3c0000.
2. Corregir scripts/flujo_health.py para aceptar arte-ascii-readme.svg y dejar de exigir wrappers legacy.
3. Retirar nuevamente Airdrop usando a6fe4662 como referencia.
4. Retirar la copia xio/ usando d0126f92 como referencia; conservar cultura/mak_plataforma/xio_evidence.py.
5. Revisar y retirar wrappers legacy ya reemplazados: flujo_pipeline.py, nuevo_pedido.sh, backlog_list.py, brief_to_project.py, flyer_set_input.py, sanitize_sensitive.py; luego evaluar flujo.py, flujo_daily.py y abrir_dashboard.sh.
6. Revisar one-shots/resucitados: consolidate_static_duplicates.py, tapiz_live_loop.py y watsonx_*; conservar inicialmente system_map.py, gen_iskvw_prototipo.py, enviar_a_mak.py, tapiz_telemetry.py, find_duplicates.py y github_setup_labels.py.
7. Limpiar referencias activas a AGENTS.md, STATUS.md, REPOS.md, LAST_HANDOFF.md y Airdrop.
8. Podar documentación narrativa histórica sólo después de extraer cualquier invariante útil. No borrar BASES/, borradores/, dossiers, postulaciones, investigación ni evidencia recuperada por ser .md.
9. Mantener ci-integration.yml y render_piezas_vectoriales.yml; corregir contratos viejos en vez de borrarlos.
10. Hacer commits pequeños y validar referencias/tests tras cada grupo.

No crear todavía SYSTEM.md. Al terminar dejar un resumen de archivos eliminados/modificados/conservados, tests, fallos restantes y elementos que luego deben condensarse en un único contexto operacional.