# Task prompts - flujo

Prompts listos para el flujo multi-agente. Copiar/pegar y rellenar `<...>`.
Contexto barato primero: `py tools/vibo_voz/contexto_repo.py task "<keywords>"`.

## 1. Qwen/NIM: mascar contexto

```
Eres lector de contexto del repo 'flujo'. NO propongas cambios.
Lee SOLO estas rutas: <rutas>.
Devuelve, en <= 20 lineas:
- que hace cada archivo (1 linea)
- funciones/simbolos clave y donde se usan
- riesgos o zonas fragiles
- que falta para la tarea: <tarea>
Sin relleno. Si algo no esta en las rutas, di "no visible".
```

## 2. Claude: validar el plan

```
Eres arquitecto/revisor del repo 'flujo'. Lee CLAUDE.md + context/LAST_HANDOFF.md si hace falta.
Aqui va un plan propuesto por un modelo barato para: <tarea>.
Plan:
<plan>
Devuelve: (1) que esta bien, (2) errores o riesgos, (3) el plan corregido minimo
(archivos a tocar, orden, verificacion), (4) que dejar al editor barato vs que exige Claude.
Se breve. No implementes todavia.
```

## 3. Aider: implementar una tarea

```
Tarea: <tarea>. Sigue este plan aprobado:
<plan>
Toca SOLO estos archivos: <archivos>. Cambios minimos y completos, sin TODO ni stubs.
Anade/actualiza tests en tests/ si aplica.
No toques src/flujo/airdrop.py, workflows, ni credenciales sin que se pida.
Al final deja la verificacion lista: py -m compileall src/flujo && py -m pytest tests/ -q && py -m flujo verify.
```

## 4. Revision final de diff

```
Revisa este diff del repo 'flujo' antes de merge. Tarea: <tarea>.
Diff:
<diff>
Marca: bugs, regresiones, cambios de comportamiento publico (CLI/API/entrega), seguridad,
TODO/stubs, o falta de tests. Da veredicto: MERGE / CAMBIOS (con la lista minima). Se breve.
```

## 5. Cerrar handoff

```
Cierra la sesion del repo 'flujo'. Actualiza:
- context/LAST_HANDOFF.md (ASCII-only, compacto: estado actual / listo / pendiente /
  bloqueadores / proximo paso; unifica a Cauce).
- context/SESSION_STATE.json (version = pyproject.toml, date real, assistant_name,
  current_focus, done, doing, next, blockers, ai_stack).
Refleja lo que REALMENTE cambio esta sesion. No dejes version/fecha vieja.
```
