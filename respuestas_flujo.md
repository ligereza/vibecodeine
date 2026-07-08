# Respuestas sobre el proyecto flujo

## 1. Punto de entrada y comando de inicio diario

**Punto de entrada:** `src/flujo/__main__.py` → importa `cli.app` desde `src/flujo/cli.py`

**Comando diario:** 
```bash
py -m flujo app
py -m flujo app --desktop  # con interfaz gráfica
```

También existen comandos de verificación:
```bash
py -m flujo verify
py -m flujo health
py -m flujo version
```

---

## 2. Subpaquetes en src/flujo/ y sus funciones

| Subpaquete | Función |
|---|---|
| `analyze/` | Análisis de colores dominantes y OCR de proyectos flyer |
| `comercial/` | Configuración de suplementos RD, generación de contraportadas SVG, validación |
| `dashboard/` | Componentes de dashboard |
| `eventos/` | Gestión de eventos Studio (flyers, Instagram) |
| `export/` | Exportación a Illustrator, ZIP, puentes COM |
| `flyer/` | Importación de emails con links de IG, creación de proyectos flyer |
| `ig/` | Integración con Instagram (instaloader) |
| `index/` | Índice SQLite de flyers, búsqueda de duplicados |
| `intake/` | Procesamiento de intake.json, schemas de entrada |
| `jobs/` | Gestión de jobs, briefs, estados |
| `knowledge/` | Memoria operacional versionada |
| `plano/` | Planos de stands, validación de layouts |
| `privacy/` | Gestión de privacidad de datos |
| `render/` | Render de piezas vectoriales, formatos, autofit, rescale |
| `resolume/` | Automatización Resolume Arena vía Chataigne/OSC/SMPTE |
| `route/` | Resolver de rutas de entrega según área/pieza |
| `serve/` | Servidor web local, API |
| `templates/` | Plantillas base |
| `web/` | Hub web React/Vite |

**Archivos clave raíz:**
- `cli.py` - CLI principal (97KB, todo los comandos)
- `airdrop.py` - Motor de actualizaciones sin push directo
- `paths.py` - Rutas del repo
- `version.py` - Versión y changelog

---

## 3. Modificar lógica de generación SVG de un flyer

Archivos involucrados (en orden):

1. **`src/flujo/render/piezas.py`** - Render principal de piezas vectoriales
2. **`src/flujo/render/formats.py`** - Definición de formatos (medidas, área, pieza)
3. **`src/flujo/comercial/contraportada_svg.py`** - Generador específico para contraportadas de suplementos (reemplaza placeholders en SVG base)
4. **Plantilla SVG base** - Ej: `svg/suplementos_rd/04_contraportadas/01_contraportada_base_10x14cm.svg`
5. **`src/flujo/comercial/suplementos_config.py`** - Datos de los suplementos (nombre, beneficios, info nutricional, colores)
6. **`src/flujo/flyer/project.py`** - Creación de estructura de proyecto flyer
7. **`src/flujo/flyer/import_email.py`** - Importación desde email con links de IG

**Flujo:** Brief → `piezas.py` lee formato → carga plantilla SVG → reemplaza textos → exporta.

---

## 4. ¿Qué es airdrop? ¿Cuándo usar airdrop vs push directo?

**Airdrop** es el protocolo de entrega para agentes **sin acceso push directo al repo**.

**Estructura correcta:**
```
_airdrop/HANDOFF_2026-06-30_descripcion.md
_airdrop/context/LAST_HANDOFF.md
_airdrop/src/flujo/modulo.py
_airdrop/tests/test_modulo.py
```

**Cuándo usar airdrop:**
- Agente remoto sin credenciales de GitHub
- Sesión API-only (Claude Code, Qwen via API)
- Cuando el guardrail bloquea push directo a `main`

**Cuándo usar push directo:**
- Tienes acceso write al repo
- Estás en sesión local con credenciales configuradas
- Creas rama + PR (no push directo a main por guardrail)

**Validación:**
```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje corto"
```

---

## 5. Comando completo para verificar cambios Python

```bash
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```

Si tocaste web también:
```bash
cd web && npm run typecheck && npm run build:context && cd ..
```

Si es airdrop:
```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje corto"
```

---

## 6. Modificar airdrop.py: permisos especiales y razón

**Requiere autorización explícita del usuario** con flag:
```bash
py scripts/validate_airdrop.py --allow-airdrop-engine
py scripts/run_airdrop_checks.py "mensaje corto" --allow-airdrop-engine
```

**Razón:** `airdrop.py` es el **motor de actualizaciones** del repo. Un error aquí puede:
- Corromper el proceso de apply de futuros airdrops
- Borrar archivos críticos del repo
- Romper el sistema de backup/manifest
- Impedir la continuidad entre sesiones de agentes

Está protegido por validación estricta en `scripts/validate_airdrop.py` y `docs/AGENT_AIRDROP_PROTOCOL.md`.

---

## 7. ¿Por qué no se puede reescribir arbitrariamente resolume/automator.py?

**Razones:**

1. **Schema `.noisette` no validado:** La función `build_chataigne_noisette_experimental()` ha sido reescrita **4 veces consecutivas** (v0.48.2 a v0.48.5) especulando sobre la estructura interna del formato `.noisette` de Chataigne 1.10.3, pero **nunca se validó contra un archivo real exportado desde Chataigne**.

2. **Marcado como `experimental`:** El propio nombre indica que es tentativo. Sin un fixture real, cualquier cambio es adivinanza.

3. **LAST_HANDOFF.md lo documenta como pendiente:** Dice explícitamente: *"No reescribas `build_chataigne_noisette_experimental` adivinando el schema otra vez... pide al usuario un `.noisette` real exportado desde su Chataigne 1.10.3 y guárdalo como fixture en `tests/`"*.

4. **El XML y CSV sí funcionan:** `build_chataigne_xml()` y `write_osc_csv()` son estables y validados. Solo el `.noisette` es problemático.

**Solución correcta:** Pedir al usuario un archivo `.noisette` real exportado desde su Chataigne, usarlo como referencia/fixture, y solo entonces modificar el generador.

---

## 8. Añadir campo "origen" a las 8 contraportadas de suplementos ONG

**Archivos a modificar (en orden):**

1. **`src/flujo/comercial/suplementos_config.py`**
   - Añadir parámetro `origen: str` al dataclass `Suplemento`
   - Actualizar las 8 definiciones (Impulso, Creatina, Pre Fiesta, Recovery, Colágeno Fit, Omega+ Immune, Sleep Relax, + el 8vo si existe en JSON spec)

2. **`src/flujo/comercial/contraportada_svg.py`**
   - Modificar `generar_contraportada()` para leer `suplemento.origen`
   - Añadir `_replace_text_in_svg()` para el placeholder de "origen" en la plantilla SVG

3. **Plantilla SVG base** (`svg/suplementos_rd/04_contraportadas/01_contraportada_base_10x14cm.svg`)
   - Añadir placeholder de texto para "ORIGEN" o similar

4. **Opcional: `svg/suplementos_rd/04_contraportadas/suplementos_rd_illustrator_spec.json`**
   - Si existe este JSON maestro, añadir campo "origen" a cada artboard

5. **Regenerar:**
   ```bash
   py -m flujo suplementos contraportada "Impulso" --output salida.svg
   # o correr el generador de las 8 contraportadas
   ```

6. **Verificar:**
   ```bash
   py -m flujo suplementos validate svg/suplementos_rd/04_contraportadas/generadas/*.svg
   py -m compileall src/flujo
   py -m pytest tests/ -q
   ```

---

## 9. Limitación de codificación en LAST_HANDOFF.md y CLAUDE.md

**Ambos deben ser ASCII-only** (solo caracteres ASCII, sin UTF-8 especial).

**Razón:**
- Compatibilidad máxima entre sesiones de agentes remotos
- Evitar problemas de encoding en sistemas Windows/Git Bash
- Facilitar lectura mecánica por scripts de validación
- Garantizar que cualquier agente (Claude, Qwen, NIM) pueda leer/escribir sin errores de codificación

**En CLAUDE.md dice explícitamente:**
> `context/LAST_HANDOFF.md` y este archivo: ASCII-only.

---

## 10. Reglas de routing AI: ¿qué tarea para Claude, qué tarea para Qwen?

**Matriz de routing (de `docs/AI_PROVIDER_ROUTING.md`):**

| Proveedor | Rol | Cuándo usar |
|---|---|---|
| **Claude Code / Opus** | Arquitecto, review final | Diseño de solución, decisiones de arquitectura, bugs difíciles, revisión de diff antes de merge, seguridad, tocar `airdrop.py` |
| **Qwen API** (DashScope) | Editor barato | Edición simple guiada por plan, generar tests/boilerplate, resumir contexto de rutas gordas |
| **NVIDIA NIM** | Alternativa barata | Igual que Qwen cuando DashScope no rinde |
| **OpenRouter** | Fallback | Cuando un proveedor está caído |

**Escalar a Claude cuando:**
- Decisión de arquitectura o enfoque
- Toca seguridad, credenciales, CI workflows, `airdrop.py`
- Cambia comportamiento público (CLI, API, formato de entrega)
- Ya se intentó antes y falló (ver changelog en `version.py`)
- Review final antes de merge

**Dejar en Qwen/NIM cuando:**
- Hay plan claro y cambio es mecánico/local
- Generar tests, docstrings, boilerplate
- Traducir plan de Claude a ediciones concretas
- Resumir/mascar contexto de archivos grandes

**Flujo tipo bajo consumo:**
1. Contexto barato: `py tools/vibo_voz/contexto_repo.py task "<keywords>"`
2. Plan: Qwen/NIM redacta borrador → **Claude valida el plan**
3. Implementa: Aider con architect=Claude + editor=Qwen/NIM
4. Review final: **Claude revisa el diff**
5. Cierre: actualizar `LAST_HANDOFF.md` + `SESSION_STATE.json`
