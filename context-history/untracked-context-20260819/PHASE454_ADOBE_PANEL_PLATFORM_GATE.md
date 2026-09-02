# Phase 454 — Adobe CEP panel platform gate

## Alcance

Se auditó `tools/adobe_panel/` desde `/home/mak/*` para decidir si es una
herramienta activa de MAK o una pieza histórica de Windows. El panel es un
CEP para Illustrator, Photoshop y After Effects; no es un consumidor Linux ni
una página web de MAK runtime.

## Dueño y contrato

```text
tools/adobe_panel/index.html
  -> js/CSInterface.js + js/main.js
  -> Adobe CEP host (ILST/PHXS/PHSP/AEFT)
  -> tools/{illustrator,photoshop,after_effects}/scripts/*.jsx
  -> Windows PowerShell/registry install flow
```

`main.js` resuelve `repo_tools_path` por variable CEP, configuración de usuario
o ruta relativa, y despacha 7 scripts JSX existentes. `manifest.xml` declara
los cuatro hosts Adobe. `check_install.ps1` y `build_zxp.ps1` son explícitamente
Windows; no se deben adaptar artificialmente al servicio Linux `flujo`.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
node --check js/main.js                       -> exit 0
node --check js/CSInterface.js                -> exit 0
HTMLParser + local reference assertions       -> exit 0
JSON parse config.json                        -> exit 0
XML parse CSXS/manifest.xml                   -> exit 0
JSX consumer existence check                  -> exit 0 (7/7)
surface hash parity vs flujo-deploy           -> exit 0 (10/10)
```

La superficie contiene 10 archivos; `index.html` tiene 601 bytes y todas sus
referencias locales existen. Los 7 scripts JSX listados en `main.js` están
presentes bajo `tools/`. Cada archivo de `tools/adobe_panel` coincide con su
copia de `flujo-deploy`.

## Dictamen

```text
ADOBE_PANEL_SOURCE_INTACT
ADOBE_PANEL_JS_XML_CONTRACT_GREEN
ADOBE_PANEL_JSX_CONSUMERS_PRESENT
ADOBE_PANEL_DEPLOY_COPY_EXACT
ADOBE_PANEL_WINDOWS_EXTERNAL_CONSUMER
ADOBE_PANEL_NOT_LINUX_RUNTIME
```

No se fusiona con las herramientas Canvas/HTML de Tapiz ni con el hub. Se
mantiene como paquete de integración Windows/Adobe, listo para reactivarse
solo si el usuario trabaja nuevamente con Adobe en Windows. En MAK Linux se
clasifica como plataforma externa/histórica, no como basura ni como slice a
instalar.

## Riesgos y rollback

- No se ejecutaron PowerShell, registro Windows, Adobe, ZXPSignCmd ni JSX; la
  validación es estática y de presencia de consumidores.
- `build_zxp.ps1` puede crear certificados y paquetes en Windows; permanece
  fuera del flujo de integración automática.
- No hubo cambios en panel, scripts, despliegue o evidencia; rollback: no-op.

## Siguiente acción

Continuar con el siguiente HTML no cubierto de `/home/mak/*`, priorizando una
superficie con consumidor local Linux o una pieza visual no sensible. Mantener
Adobe CEP fuera del runtime MAK y conservarlo como integración de plataforma
externa.
