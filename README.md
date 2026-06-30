# flujo · workspace operativo para pedidos, jobs y entregas

**flujo** convierte pedidos de diseño, eventos y suplementos en trabajo trazable: pedido -> job -> brief -> diseño/automatización -> revisión -> entrega.

El repositorio funciona como hub local para recibir pedidos, organizar jobs, revisar entregables, mantener coherencia visual y automatizar tareas de EVENTOS y SUPLEMENTOS sin depender de plataformas pesadas.

## Índice operativo

1. [Lectura obligatoria y Mandamiento Cero](#1-lectura-obligatoria-y-mandamiento-cero)
2. [Entrada diaria](#2-entrada-diaria)
3. [Modo Dual: RD vs Studio](#3-modo-dual-rd-vs-studio)
4. [Ruteo entrante Gmail / Apps Script](#4-ruteo-entrante-gmail--apps-script)
5. [GitHub Issues y Projects](#5-github-issues-y-projects)
6. [Jobs, intake y cotizaciones](#6-jobs-intake-y-cotizaciones)
7. [Modo RD: suplementos, cotizaciones y plano](#7-modo-rd-suplementos-cotizaciones-y-plano)
8. [Modo Studio: eventos, Instagram y Resolume](#8-modo-studio-eventos-instagram-y-resolume)
9. [Portal para jefatura](#9-portal-para-jefatura)
10. [Verificación, airdrops y sync](#10-verificación-airdrops-y-sync)
11. [Estructura principal](#11-estructura-principal)
12. [Próximas mejoras recomendadas](#12-próximas-mejoras-recomendadas)

---

## 1. Lectura obligatoria y Mandamiento Cero

Si eres una IA o vas a retomar el repo, lee en este orden:

1. `context/LAST_HANDOFF.md` — fuente principal de continuidad.
2. `docs/handoffs/README.md` — índice del historial operativo.
3. `AGENTS.md` — contrato de trabajo para agentes.
4. `docs/AGENT_OPERATING_MANUAL.md` — manual de operación y delegación.
5. `docs/FLUJO_AREAS_EVENTOS_SUPLEMENTOS.md` — rutas EVENTOS y SUPLEMENTOS.
6. `docs/GMAIL_A_REPO_GRATIS.md` — puente Gmail -> GitHub Issues.

### Mandamiento Cero de Autorevisión

- Tolerancia cero a código mediocre, parches incompletos, placeholders o silencios peligrosos.
- Prohibido ocultar errores con bloques mudos tipo `try/except: pass`.
- Prohibido dejar marcadores de trabajo incompleto como `TODO`, `completar luego`, `...` o `NotImplementedError` en entregas finales.
- Todo cambio Python debe verificarse al menos con:

```bash
py -m compileall src/flujo
```

- Todo cambio web debe verificarse en `web/` con:

```bash
npm run build:context
```

- Toda entrega de agente debe cerrar con un apartado llamado **Reporte Formal de Verificación y Tolerancia Cero a Errores** o el título específico pedido en su prompt.

Reglas permanentes:

```txt
- El usuario trabaja en Windows + Git Bash.
- En instrucciones para el usuario usar py, no python.
- Mantener context/LAST_HANDOFF.md en ASCII-only.
- No guardar tokens, credenciales ni datos sensibles.
- Entregar como airdrop si no hay acceso directo al repo.
```

---

## 2. Entrada diaria

En Windows / Git Bash:

```bash
py -m flujo app
```

Modo escritorio:

```bash
py -m flujo app --desktop
```

Verificar estado:

```bash
py -m flujo verify
```

Generar un prompt listo para IA web a partir de un pedido o correo:

```bash
py -m flujo ai-prompt "Necesito cotizar suplementos" --area suplementos
```

---

## 3. Modo Dual: RD vs Studio

`flujo` mantiene un único backend local y una única app servida por `py -m flujo app`, pero la interfaz visual debe separar dos espacios de trabajo.

### Modo RD (ONG Reduciendo Daño)

Aísla trabajo institucional de RD:

```txt
SUPLEMENTOS
cotizaciones base
plantillas 10x14 cm
contraportadas SVG automáticas
plano impreso de teatro/stands/testeo
rider y costos de stands
```

### Modo Studio / Personal (VJ & Club)

Aísla trabajo personal/artístico:

```txt
EVENTOS
visor SvgVisualizer
flyers/carteleras desde Instagram
shows Resolume Arena
automatización Chataigne por SMPTE/OSC
```

Justificación: un solo backend local ahorra recursos, pero la interfaz evita mezclar presupuestos ONG con setlists, VJ loops y automatizaciones personales.

---

## 4. Ruteo entrante Gmail / Apps Script

Gmail no se conecta directo al repo. El puente recomendado es Google Apps Script creando GitHub Issues.

Rutas oficiales por asunto:

```txt
subject:eventos     -> Issue [EVENTOS]     -> labels: area/eventos, estado/por-revisar, gmail
subject:evento      -> Issue [EVENTOS]     -> labels: area/eventos, estado/por-revisar, gmail
subject:suplementos -> Issue [SUPLEMENTOS] -> labels: area/suplementos, estado/por-revisar, gmail
subject:suplemento  -> Issue [SUPLEMENTOS] -> labels: area/suplementos, estado/por-revisar, gmail
```

Configuración base recomendada:

```txt
GITHUB_TOKEN = github_pat_...
GITHUB_REPO = ligereza/vibecodeine
GMAIL_LABEL_DONE = flujo-procesado
MAX_THREADS = 10
GMAIL_LOOKBACK = 7d
GMAIL_ROUTES = subject:eventos|EVENTOS|pedido,area/eventos,estado/por-revisar,gmail,instagram,action/descargar-ig;subject:evento|EVENTOS|pedido,area/eventos,estado/por-revisar,gmail,instagram,action/descargar-ig;subject:suplementos|SUPLEMENTOS|pedido,area/suplementos,estado/por-revisar,gmail;subject:suplemento|SUPLEMENTOS|pedido,area/suplementos,estado/por-revisar,gmail
```

Script:

```txt
tools/gmail_to_github_issues.gs
```

Guía:

```txt
docs/GMAIL_A_REPO_GRATIS.md
```

---

## 5. GitHub Issues y Projects

Templates activos:

```txt
.github/ISSUE_TEMPLATE/pedido_eventos.yml       -> [EVENTOS]
.github/ISSUE_TEMPLATE/pedido_suplementos.yml   -> [SUPLEMENTOS]
.github/ISSUE_TEMPLATE/cambio_diseno.yml        -> [Cambio]
.github/ISSUE_TEMPLATE/revision_privacidad.yml  -> [Privacidad]
```

Labels recomendados:

```txt
area/eventos
area/suplementos
instagram
action/descargar-ig
action/crear-job
action/cotizar
action/resolume
action/chataigne
estado/por-revisar
estado/pendiente-datos
estado/en-diseno
estado/revision
estado/entregado
```

---

## 6. Jobs, intake y cotizaciones

Crear job desde correo/texto:

```bash
py -m flujo job new "nombre pedido" --email inbox/correo.txt
py -m flujo job prepare jobs/<job>
```

Procesar intake JSON:

```bash
py -m flujo intake json inbox/pedido.json
```

Genera:

```txt
jobs/<folio>/brief.yaml
jobs/<folio>/estado.md
jobs/<folio>/resultado.md
```

Cotización multiformato:

```bash
py -m flujo brief paquete-cotizacion jobs/<job>
```

---

## 7. Modo RD: suplementos, cotizaciones y plano

### Suplementos RD

Listar suplementos:

```bash
py -m flujo suplementos list
```

Generar contraportada SVG 10x14 cm:

```bash
py -m flujo suplementos contraportada "Impulso" --output salida.svg
```

Validar SVGs antes de revisar/exportar:

```bash
py -m flujo suplementos validate svg/suplementos_rd/04_contraportadas/generadas/*.svg
```

### Plano / rider / stands

Generar plano SVG:

```bash
py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --output plano.svg
```

Validar plano antes de imprimir/exportar:

```bash
py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --validate
```

Rider y costos:

```bash
py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --rider
py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --costs
```

---

## 8. Modo Studio: eventos, Instagram y Resolume

### Descarga Instagram + Photoshop/Blender local

Para EVENTOS con link Instagram:

```bash
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/"
```

Por defecto descarga con `instaloader`, genera paleta y no abre apps externas. Para autorizar pasos locales:

```bash
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/" --run-droplet
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/" --render-blender
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/" --render-blender --open-blender
```

Regla:

```txt
Usar instaloader. No usar yt-dlp.
```

### Resolume + Chataigne por SMPTE/OSC

Los shows sincronizados por SMPTE entran por la ruta de EVENTOS y se transforman en jobs locales. El comando oficial nuevo es:

```bash
py -m flujo resolume automatizar jobs/<job_id>
```

Opciones:

```bash
py -m flujo resolume automatizar jobs/<job_id> --fps 25
py -m flujo resolume automatizar jobs/<job_id> --host 127.0.0.1 --port 7000
```

Salida esperada:

```txt
jobs/<job_id>/deliverables/show_automation.xml
```

El XML pre-flight configura:

```txt
entrada SMPTE HH:MM:SS:FF
salida OSC a 127.0.0.1:7000
acciones /composition/layers/{layer}/clips/{clip}/connect
```

Especificación:

```txt
tools/resolume_chataigne_automator/SPEC.md
```

---

## 9. Portal para jefatura

Generar portal visual:

```bash
py -m flujo portal --repo-url https://github.com/ligereza/vibecodeine
```

Salida:

```txt
context/portal_jefe.html
```

Muestra estados, pendientes y próximas acciones sin monday.com.

---

## 10. Verificación, airdrops y sync

Verificación integral:

```bash
py -m flujo verify
```

Validación mínima Python antes de entregar:

```bash
py -m compileall src/flujo
```

Build web antes de entregar cambios React/TypeScript:

```bash
cd web
npm run build:context
```

Flujo normal de airdrop:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje"
```

Si un apply ya se hizo y falló después en checks/checkpoint:

```bash
py scripts/run_airdrop_checks.py --resume "mensaje"
```

Sincronizar el repositorio local con GitHub desde la máquina del usuario:

```bash
py -m flujo github-sync --status
py -m flujo github-sync --push -m "actualizar flujo"
```

Reglas:

```txt
- No guardar tokens.
- No commitear datos sensibles.
- No borrar sin listar antes.
- Mantener LAST_HANDOFF actualizado y ASCII-only.
- No incluir caches, builds ni carpetas pesadas en airdrops.
```

---

## 11. Estructura principal

```txt
src/flujo/        código principal
web/              React/Vite para hub y visualizadores
context/          handoff, portal, reportes y HTML compilados
jobs/             trabajos locales
projects/         proyectos visuales y prompts delegados
tools/            scripts auxiliares y especificaciones
docs/             manuales operativos
schemas/          intake JSON
.github/          issue templates y workflows
knowledge/        memoria operacional versionable
```

---

## 12. Próximas mejoras recomendadas

1. Completar la separación visual en `web/src/components/AppShell.tsx` entre Modo RD y Modo Studio.
2. Expandir `src/flujo/resolume/automator.py` hacia `.noisette` nativo cuando se valide el formato local de Chataigne.
3. Implementar tests completos para parsing SMPTE y XML Resolume/Chataigne.
4. Profundizar `py -m flujo suplementos validate` con preflight visual de márgenes, contraste y sangrado.
5. Dividir `src/flujo/cli.py` en submódulos para mantenimiento más limpio.

---

## Licencia

MIT
