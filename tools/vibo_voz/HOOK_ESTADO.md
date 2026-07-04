# Hook de ESTADO para sesiones interactivas (gratis, 0 tokens)

Para que una sesion de Claude Code (esta, la de Unreal, cualquiera) deje una marca
en la bitacora ESTADO **cada vez que empieza o termina una labor**, se usan hooks.
Un hook es un comando que ejecuta la app (no el LLM), asi que **no gasta tokens**.

CODE lee esa bitacora con `leer_estado` solo cuando le preguntas ("novedades?").

## Instalacion (una vez por proyecto)

En el proyecto donde corras Claude Code, edita (o crea) `.claude/settings.json` y
agrega los hooks. Reemplaza `NOMBRE` por el nombre del proyecto (flujo, unreal, ...)
y deja la ruta al ESTADO compartido:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cmd /c echo - [%date% %time%] NOMBRE: empezo sesion >> \"C:\\IA\\flujo\\tools\\vibo_voz\\estado\\ESTADO.md\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cmd /c echo - [%date% %time%] NOMBRE: termino labor >> \"C:\\IA\\flujo\\tools\\vibo_voz\\estado\\ESTADO.md\""
          }
        ]
      }
    ]
  }
}
```

- **SessionStart** se dispara cuando abres/reanudas la sesion.
- **Stop** se dispara cuando Claude termina de responder (fin de una labor).

Con esto, ESTADO.md se llena solo. Los agentes headless que lanza CODE ya escriben
su "empezo/termino" automaticamente; este hook cubre las sesiones que abres tu.

Nota: la carpeta `estado/` esta en .gitignore (es bitacora local, no se sube).
