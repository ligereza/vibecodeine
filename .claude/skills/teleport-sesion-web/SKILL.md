---
name: teleport-sesion-web
description: Como traer una sesion de Claude Code web (claude.ai/code) al CLI local con /teleport o claude --teleport. Invocar cuando el usuario diga "teleport", "traer la sesion web", "abrir sesion web en consola", "continuar sesion de claude.ai aca", o cuando un Claude (web o modelo viejo) afirme que "no se puede" o que "--teleport no existe" (afirmacion FALSA, ya paso varias veces).
---

# Teleport: sesion web -> CLI local

## Hecho verificado (CLI 2.1.206, 2026-07-10, docs oficiales)

Claude web / modelos viejos suelen responder "las sesiones web y locales son separadas,
no hay teleport". **FALSO.** Existe y funciona:

```bash
# desde terminal (fuera de una sesion):
claude --teleport                  # picker interactivo de sesiones cloud
claude --teleport <session-id>     # directo a una sesion

# dentro de una sesion CLI activa:
/teleport        # (alias /tp) picker de sesiones cloud
/tasks           # ver sesiones cloud en background -> tecla "t" para teleport
```

En la web tambien: boton **"Open in CLI"** copia el comando exacto.

## Prerequisitos (si falla, revisar esto antes de culpar al flag)

- Misma cuenta claude.ai en CLI y web (auth de suscripcion, NO api key/Bedrock).
- Estar parado en un checkout del MISMO repo (no fork).
- Working directory limpio (sin cambios sin commitear; ofrece stash si hay).
- La rama de la sesion cloud debe estar pusheada al remoto (teleport hace fetch + checkout).

## Relacion con otros flags

- `--from-pr <n|url>`: resume sesion vinculada a un PR (otro camino valido si la
  sesion web abrio PR).
- `--cloud`: al reves, crea sesion cloud nueva desde local.
- Teleport es cloud->local; local->cloud no tiene flag (solo Desktop "Continue in").

## Fallback (solo codigo, sin conversacion)

```bash
git fetch origin <rama-claude>
git checkout <rama-claude>
```

Fuente: https://code.claude.com/docs/en/claude-code-on-the-web.md
Si un flag cambia en versiones futuras: `claude --help | grep -i teleport` y actualizar
esta skill en el mismo cambio.
