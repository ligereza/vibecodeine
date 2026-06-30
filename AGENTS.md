# AGENTS.md · contrato operativo para agentes de flujo

Este archivo es el contrato corto para cualquier agente que retome `flujo`. La fuente diaria de verdad sigue siendo `context/LAST_HANDOFF.md`.

## Índice operativo

1. [Lectura obligatoria y Mandamiento Cero](#1-lectura-obligatoria-y-mandamiento-cero)
2. [Entrada diaria](#2-entrada-diaria)
3. [Rol del agente y alcance](#3-rol-del-agente-y-alcance)
4. [Modo Dual: RD vs Studio](#4-modo-dual-rd-vs-studio)
5. [Ruteo Gmail / Apps Script](#5-ruteo-gmail--apps-script)
6. [Jobs e intake](#6-jobs-e-intake)
7. [EVENTOS y Studio](#7-eventos-y-studio)
8. [SUPLEMENTOS y RD](#8-suplementos-y-rd)
9. [Resolume + Chataigne](#9-resolume--chataigne)
10. [Web / React](#10-web--react)
11. [Airdrop y verificación](#11-airdrop-y-verificación)
12. [Entrega final](#12-entrega-final)

---

## 1. Lectura obligatoria y Mandamiento Cero

Lee antes de modificar:

1. `context/LAST_HANDOFF.md`
2. `README.md`
3. `docs/AGENT_OPERATING_MANUAL.md`
4. `docs/FLUJO_AREAS_EVENTOS_SUPLEMENTOS.md`
5. El archivo específico de tu tarea.

### Mandamiento Cero de Autorevisión

- No entregues parches incompletos.
- No ocultes errores con `try/except: pass`.
- No dejes placeholders de entrega final: `TODO`, `completar luego`, `...`, `NotImplementedError`.
- Si modificas Python, ejecuta y reporta:

```bash
py -m compileall src/flujo
```

- Si modificas `web/`, ejecuta y reporta:

```bash
cd web
npm run build:context
```

- Toda respuesta final debe incluir un bloque de verificación con pruebas ejecutadas.

Reglas de entorno:

```txt
Usuario: Windows + Git Bash.
Comandos para el usuario: usar py, no python.
LAST_HANDOFF.md: ASCII-only.
Credenciales: nunca guardar tokens o datos sensibles.
```

---

## 2. Entrada diaria

Comando principal:

```bash
py -m flujo app
```

Modo escritorio:

```bash
py -m flujo app --desktop
```

Chequeo general:

```bash
py -m flujo verify
```

---

## 3. Rol del agente y alcance

Trabaja local-first, con cambios trazables. Antes de tocar archivos:

1. Identifica el área: RD/SUPLEMENTOS, Studio/EVENTOS, web, CLI, docs o pipeline.
2. Lee los archivos relacionados.
3. Haz cambios mínimos pero completos.
4. Verifica compilación/build.
5. Si no hay acceso de push, empaqueta airdrop.

---

## 4. Modo Dual: RD vs Studio

La app mantiene un único backend local, pero dos contextos visuales:

### Modo RD (ONG Reduciendo Daño)

Incluye:

```txt
SUPLEMENTOS
cotizaciones base
plantillas 10x14 cm
contraportadas SVG automáticas
plano impreso de teatro/stands/testeo
rider/costos
```

### Modo Studio / Personal (VJ & Club)

Incluye:

```txt
EVENTOS
SvgVisualizer
flyers de Instagram
carteleras
Resolume Arena
Chataigne SMPTE/OSC
```

No mezcles presupuestos ONG con setlists o automatizaciones artísticas personales.

---

## 5. Ruteo Gmail / Apps Script

Rutas oficiales por asunto:

```txt
subject:eventos     -> [EVENTOS]     -> area/eventos
subject:evento      -> [EVENTOS]     -> area/eventos
subject:suplementos -> [SUPLEMENTOS] -> area/suplementos
subject:suplemento  -> [SUPLEMENTOS] -> area/suplementos
```

Bridge:

```txt
tools/gmail_to_github_issues.gs
docs/GMAIL_A_REPO_GRATIS.md
```

Configuración base:

```txt
GMAIL_ROUTES = subject:eventos|EVENTOS|pedido,area/eventos,estado/por-revisar,gmail,instagram,action/descargar-ig;subject:evento|EVENTOS|pedido,area/eventos,estado/por-revisar,gmail,instagram,action/descargar-ig;subject:suplementos|SUPLEMENTOS|pedido,area/suplementos,estado/por-revisar,gmail;subject:suplemento|SUPLEMENTOS|pedido,area/suplementos,estado/por-revisar,gmail
```

---

## 6. Jobs e intake

Crear y preparar job:

```bash
py -m flujo job new "nombre pedido" --email inbox/correo.txt
py -m flujo job prepare jobs/<job>
```

Procesar intake JSON:

```bash
py -m flujo intake json inbox/pedido.json
```

Cotización:

```bash
py -m flujo brief paquete-cotizacion jobs/<job>
```

---

## 7. EVENTOS y Studio

Descarga de flyers/carteleras desde Instagram:

```bash
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/"
```

Regla estricta:

```txt
Usar instaloader. No usar yt-dlp.
```

Apps externas como Photoshop, droplets o Blender requieren autorización explícita por flags.

---

## 8. SUPLEMENTOS y RD

Comandos principales:

```bash
py -m flujo suplementos list
py -m flujo suplementos contraportada "Impulso" --output salida.svg
py -m flujo suplementos validate svg/suplementos_rd/04_contraportadas/generadas/*.svg
```

La línea RD debe preservar separación visual, cotizaciones y entregables institucionales.

---

## 9. Resolume + Chataigne

Comando oficial para jobs de EVENTOS con setlist SMPTE:

```bash
py -m flujo resolume automatizar jobs/<job_id>
```

Opciones:

```bash
py -m flujo resolume automatizar jobs/<job_id> --fps 25
py -m flujo resolume automatizar jobs/<job_id> --host 127.0.0.1 --port 7000
```

Salida:

```txt
jobs/<job_id>/deliverables/show_automation.xml
```

Lee la especificación antes de desarrollar:

```txt
tools/resolume_chataigne_automator/SPEC.md
src/flujo/resolume/automator.py
```

---

## 10. Web / React

Frontend:

```txt
web/src/components/AppShell.tsx
web/src/components/SvgVisualizer.tsx
```

Build obligatorio si tocas web:

```bash
cd web
npm run build:context
```

Entregables esperados:

```txt
context/flujo_hub.html
context/svg_visualizer.html
```

---

## 11. Airdrop y verificación

Si no tienes acceso de push, entrega ZIP con `_airdrop/` en la raíz.

Validar airdrop:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje"
```

Verificaciones mínimas:

```bash
py -m compileall src/flujo
py -m flujo verify
```

Si modificaste web:

```bash
cd web
npm run build:context
```

---

## 12. Entrega final

Toda entrega debe incluir:

1. Resumen de archivos modificados.
2. Qué problema resuelve.
3. Cómo usarlo con comandos `py`.
4. Riesgos o pendientes reales, si existen.
5. **Reporte Formal de Verificación y Tolerancia Cero a Errores** con comandos ejecutados y resultado.

No declares éxito si no ejecutaste la verificación correspondiente.
