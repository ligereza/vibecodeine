# 🧠 Autonomous Research Agent — Plantilla n8n + LLM local

> **Plantilla de workflow para n8n** que implementa un agente de investigación autónomo con bucle: busca en internet, descarga, analiza con IA local (vía Ollama) y sigue investigando hasta obtener resultados satisfactorios.

> **NOTA 2026-07-15 (estado real):** modelo actual = **aya-expanse:8b** (mejor español que
> mistral-nemo). El JSON usa `this.helpers.httpRequest` nativo (el sandbox del Code node NO
> tiene `fetch`/`AbortController`) y el webhook lleva `webhookId`. Único pendiente: el loop
> completo corre en UN nodo Code y el task-runner de n8n corta a los **300 s**
> (`N8N_RUNNERS_TASK_TIMEOUT`); subir ese env a 1200 o bajar `max_iterations`. Handoff
> completo en `cultura/PLAN.md`.

---

## 📋 Índice

1. [Requisitos Previos](#1-requisitos-previos)
2. [Arquitectura del Workflow](#2-arquitectura-del-workflow)
3. [Guía de Importación](#3-guía-de-importación)
4. [Configuración Paso a Paso](#4-configuración-paso-a-paso)
5. [Cómo Usarlo](#5-cómo-usarlo)
6. [Estructura del Bucle de Research](#6-estructura-del-bucle-de-research)
7. [Personalización](#7-personalización)
8. [Solución de Problemas](#8-solución-de-problemas)
9. [Ejemplos de Respuesta](#9-ejemplos-de-respuesta)

---

## 1. Requisitos Previos

**Runtime: MAK + ethernet.** n8n corre en la máquina **MAK**, accesible en
`http://localhost:5678` desde la propia MAK, o en `http://<IP-de-MAK>:5678` desde
cualquier otra máquina de la red por ethernet. Ollama corre local en MAK (nativo o en
Docker) con el modelo `mistral-nemo:latest` ya descargado.

| Componente | Descripción |
|---|---|
| **n8n** | Corriendo en MAK, UI en `http://localhost:5678` (o `http://<IP-MAK>:5678` desde la LAN) |
| **Ollama** | Local en MAK, con el modelo `mistral-nemo:latest` descargado |
| **Tavily API Key** | Gratuita (1000 calls/mes) en [tavily.com](https://tavily.com) |
| **Conectividad n8n -> Ollama** | Depende de donde vive n8n respecto a Ollama, ver tabla en 4.3 (default: `host.docker.internal:11434`) |

### Verificar que Ollama tiene Mistral Nemo:

```bash
# En MAK, directo (Ollama nativo):
ollama list

# Si no aparece, descargarlo:
ollama pull mistral-nemo:latest
```

### Verificar conectividad desde n8n a Ollama:

```bash
# Si n8n corre en Docker en MAK, Ollama corriendo en el host:
docker exec -it n8n curl http://host.docker.internal:11434/api/tags

# Si n8n corre nativo en MAK (sin Docker):
curl http://localhost:11434/api/tags
```

---

## 2. Arquitectura del Workflow

```
                      ┌─────────────────────────────┐
                      │     🚀 WEBOOK (POST)        │
                      │     /research               │
                      │     {topic, max_iterations}  │
                      └─────────────┬───────────────┘
                                    │
                      ┌─────────────▼───────────────┐
                      │  ⚙️ SET: Inicializar        │
                      │  topic, maxIters, API keys   │
                      └─────────────┬───────────────┘
                                    │
                      ┌─────────────▼───────────────┐
                      │  🔄 CODE: Research Loop      │
                      │                              │
                      │  ┌──────────────────────┐    │
                      │  │ 🔎 Tavily Search     │    │
                      │  └─────────┬────────────┘    │
                      │            ▼                 │
                      │  ┌──────────────────────┐    │
                      │  │ 📄 Fetch URL Content  │    │
                      │  └─────────┬────────────┘    │
                      │            ▼                 │
                      │  ┌──────────────────────┐    │
                      │  │ 🤖 Ollama Analyze     │    │
                      │  └─────────┬────────────┘    │
                      │            ▼                 │
                      │  ┌──────────────────────┐    │
                      │  │ 🧠 Decide Next Step   │◄───┤ LOOP
                      │  └─────────┬────────────┘    │
                      │       CONTINUAR              │
                      │       o FINALIZAR            │
                      └─────────────┬───────────────┘
                                    │ (hallazgos)
                      ┌─────────────▼───────────────┐
                      │  🤖 LLM: Informe Final      │
                      │  (Mistral Nemo)              │
                      └─────────────┬───────────────┘
                                    │
                      ┌─────────────▼───────────────┐
                      │  📤 Responder al Webhook     │
                      │  (Informe Markdown)          │
                      └─────────────────────────────┘
```

### 🔄 El Bucle en detalle:

Cada iteración del bucle ejecuta **4 fases**:

```
ITERACIÓN N
  │
  ├─ 1. SEARCH  → Tavily API busca con la query actual (5 resultados)
  │
  ├─ 2. FETCH   → Descarga el HTML de los top 3 resultados
  │                Limpia etiquetas, extrae texto (~4000 chars)
  │
  ├─ 3. ANALYZE → Mistral Nemo analiza cada página:
  │                • key_facts: hechos clave
  │                • relevance: alta/media/baja
  │                • summary: resumen 2-3 frases
  │                • new_angles: nuevos ángulos
  │
  └─ 4. DECIDE  → Mistral Nemo evalúa hallazgos acumulados:
                   • "FINALIZAR: <razón>" → Termina el bucle
                   • "CONTINUAR: <nueva query>" → Siguiente iteración
```

---

## 3. Guía de Importación

### Paso 1: Importar el workflow

1. Abre n8n en MAK: `http://localhost:5678` (o `http://<IP-de-MAK>:5678` desde otra máquina de la red)
2. Ve a **Workflows** → **Import from File**
3. Selecciona el archivo `research_agent_mistral_nemo.json`
4. Haz clic en **Import**

### Paso 2: Configurar credenciales

El workflow usa **HTTP Requests directos** desde el Code node (no necesita credenciales de n8n para Tavily/Ollama). Pero el par **Basic LLM Chain** (`@n8n/n8n-nodes-langchain.chainLlm`, nodo **🤖 LLM: Generar Informe Final**) + **Ollama Chat Model** (`@n8n/n8n-nodes-langchain.lmChatOllama`, sub-nodo **Ollama: Mistral Nemo**) sí necesita credenciales de Ollama. Los dos nodos están conectados entre sí por la conexión `ai_languageModel` (el sub-nodo alimenta al Basic LLM Chain).

1. Haz doble clic en el sub-nodo **Ollama: Mistral Nemo** (colgado debajo de **🤖 LLM: Generar Informe Final**)
2. En **Credential to connect with** → **Create New**
3. Selecciona **Ollama** como proveedor
4. Configura:
   - **Base URL**: `http://host.docker.internal:11434`
   - **Model**: `mistral-nemo:latest` (ya viene seteado en los parámetros del nodo)
5. Haz clic en **Save**

---

## 4. Configuración Paso a Paso

### 4.1 Webhook Trigger

El webhook ya está configurado para recibir POST en `/research`.

**Body esperado (JSON):**

```json
{
  "topic": "Impacto de la inteligencia artificial en la educación superior latinoamericana",
  "max_iterations": 5,
  "tavily_api_key": "tvly-tu-api-key-aqui"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `topic` | string | ✅ Sí | Tema de investigación |
| `max_iterations` | number | ❌ No (default: 5) | Máximo de iteraciones del bucle |
| `tavily_api_key` | string | ❌ No* | API key de Tavily |

> \* Si no envías `tavily_api_key`, debes configurar la variable de entorno `TAVILY_API_KEY` en n8n.

### 4.2 Configurar API Key como variable de entorno (recomendado)

En tu `docker-compose.yml` de n8n, añade:

```yaml
services:
  n8n:
    environment:
      - TAVILY_API_KEY=tvly-tu-api-key-real
```

O en el contenedor:

```bash
docker exec -it n8n sh -c 'echo "export TAVILY_API_KEY=tvly-tu-key" >> ~/.bashrc'
```

### 4.3 Ajustar la URL de Ollama (si es necesario)

En el nodo **⚙️ Init: Configurar Variables**, cambia el valor de `ollamaBaseUrl` (usado por el Code node del bucle). La credencial Ollama del par **Basic LLM Chain / Ollama Chat Model** (paso 3) se configura por separado y debe apuntar al mismo host.

| Escenario | Valor |
|---|---|
| n8n en Docker en MAK, Ollama nativo en el host de MAK | `http://host.docker.internal:11434` ✅ (default) |
| n8n nativo en MAK (sin Docker), Ollama también nativo | `http://localhost:11434` |
| Ollama corriendo en otra máquina de la red | `http://<IP-de-esa-máquina>:11434` |

---

## 5. Cómo Usarlo

### 5.1 Activar el workflow

En n8n, haz clic en el interruptor **Active** (esquina superior derecha). El webhook estará escuchando.

### 5.2 Lanzar una investigación

#### Opción A: Desde n8n (prueba manual, directo en MAK)

1. Haz clic en **Test workflow** (o **Listen for test event**)
2. Envía este JSON de prueba:

```json
{
  "topic": "wachuma / huachuma (San Pedro, Echinopsis pachanoi): historia, etnobotánica andina, contexto cultural y legal",
  "max_iterations": 4
}
```

#### Opción B: Desde curl / cualquier cliente HTTP, por ethernet desde otra máquina

```bash
curl -X POST http://<MAK-IP>:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "wachuma / huachuma (San Pedro, Echinopsis pachanoi): historia, etnobotánica andina, contexto cultural y legal", "max_iterations": 4}'
```

Reemplaza `<MAK-IP>` por la IP de MAK en la red local. Desde la propia MAK, usa `http://localhost:5678/webhook/research`.

#### Opción C: Desde otro workflow de n8n

Usa un nodo **HTTP Request** que apunte a `http://localhost:5678/webhook/research` (o `http://<MAK-IP>:5678/webhook/research` si el otro workflow corre en otra máquina).

### 5.3 Interpretar la respuesta

El workflow devuelve un JSON con:

```json
{
  "topic": "...",
  "totalIterations": 3,
  "totalFindings": 9,
  "queriesUsed": ["query inicial", "query 2", "query 3"],
  "findings": [...],
  "completedAt": "2026-07-15T..."
}
```

Y el **informe final** generado por Mistral Nemo con formato Markdown estructurado.

---

## 6. Estructura del Bucle de Research

### 🔍 Función `searchTavily(query, apiKey)`

```javascript
POST https://api.tavily.com/search
Headers:
  Authorization: Bearer {apiKey}
  Content-Type: application/json

Body:
  query:          currentQuery       // Consulta actual
  search_depth:   "advanced"         // Búsqueda profunda (2 credits)
  max_results:    5                  // Top 5 resultados
  include_answer: true               // Respuesta generada por Tavily
  include_raw_content: false         // No incluir HTML crudo
  topic:          "general"          // Categoría general
```

### 📄 Función `fetchUrlContent(url)`

- Descarga el HTML completo con timeout de 10s
- Limpia `<script>`, `<style>`, y todas las etiquetas HTML
- Trunca a **4000 caracteres** para no saturar a Ollama

### 🤖 Función `analyzeWithOllama(prompt, systemPrompt)`

```javascript
POST http://ollama:11434/api/generate
Body:
  model:    "mistral-nemo:latest"
  prompt:   systemPrompt + "\n\n" + prompt
  stream:   false
  options:
    temperature: 0.3    // Respuestas precisas, poca creatividad
    num_predict: 1024   // Máximo de tokens de respuesta
```

### 🧠 Función `decideNextStep(findings, topic, iteration)`

El modelo evalúa los hallazgos acumulados y decide:

- **FINALIZAR** → La información es suficiente → termina el bucle
- **CONTINUAR** → Falta información → genera nueva query específica
- Evita repetir consultas ya hechas (tracking con `queryHistory`)

### ⚠️ Mecanismos de seguridad

| Mecanismo | Descripción |
|---|---|
| `maxIterations` | Límite duro de iteraciones (default 5) |
| `queryHistory` | Evita repetir la misma consulta |
| `continue` en bucle | Si Tavily no devuelve resultados, genera nueva query |
| Timeout HTTP | 10s máximo por URL descargada |
| Truncado de contenido | Máximo 4000 chars por página |

---

## 7. Personalización

### 7.1 Cambiar el modelo de Ollama

En el nodo **⚙️ Init: Configurar Variables**, cambia `modelName`:

```
mistral-nemo:latest  →  llama3.1:8b
                     →  qwen2.5:7b
                     →  deepseek-r1:8b
                     →  phi4:latest
```

### 7.2 Ajustar la profundidad de investigación

| Parámetro | Ubicación | Efecto |
|---|---|---|
| `max_iterations` | Body del webhook | Más iteraciones = más exhaustivo pero más lento |
| `max_results: 5` | Code node (searchTavily) | Más resultados por búsqueda |
| `.slice(0, 3)` | Code node (línea ~130) | Cuántos URLs analizar por iteración |
| `temperature: 0.3` | Code node (analyzeWithOllama) | 0.1 = muy preciso, 0.7 = más creativo |

### 7.3 Cambiar el idioma del output

Edita el prompt del nodo **🤖 LLM: Generar Informe Final**:
- Busca `Genera el informe en español`
- Cambia a `Generate the report in English`

### 7.4 Añadir filtros de búsqueda

En la función `searchTavily`, añade al body:

```javascript
include_domains: ["nature.com", "sciencedirect.com"],  // Solo sitios científicos
exclude_domains: ["reddit.com", "quora.com"],           // Excluir foros
time_range: "month",                                     // Solo último mes
country: "cl"                                            // Resultados de Chile
```

### 7.5 Añadir notificaciones

Puedes añadir un nodo **Telegram** o **Email** al final para recibir el informe:

```
📤 Responder → [nuevo nodo Telegram/Email]
```

---

## 8. Solución de Problemas

### ❌ "ECONNREFUSED" al llamar a Ollama

**Causa**: n8n (Docker, en MAK) no puede alcanzar el Ollama nativo que corre en el host de MAK.

**Soluciones**:

```bash
# 1. Confirmar que Ollama está escuchando en el host de MAK
curl http://localhost:11434/api/tags

# 2. Probar conectividad desde el contenedor de n8n hacia el host
docker exec -it n8n curl http://host.docker.internal:11434/api/tags

# 3. Si host.docker.internal no resuelve (Linux sin el mapeo agregado),
#    agrega esto al docker-compose.yml de n8n:
#    extra_hosts:
#      - "host.docker.internal:host-gateway"
```

Revisa también que `ollamaBaseUrl` (nodo **⚙️ Init**) y la credencial Ollama del sub-nodo **Ollama: Mistral Nemo** (sección 3) apunten al mismo valor.

### ❌ "Model not found" en Ollama

```bash
# En MAK, directo (Ollama nativo):
ollama list

# Descargar Mistral Nemo
ollama pull mistral-nemo:latest
```

### ❌ Error 401 en Tavily

- Verifica que tu API key sea válida en [tavily.com/dashboard](https://tavily.com/dashboard)
- Asegúrate de que empieza con `tvly-`
- Si usas variable de entorno, verifica: `docker exec -it n8n printenv TAVILY_API_KEY`

### ❌ El bucle se ejecuta muy lento

Cada iteración hace 3-4 llamadas a Ollama. Con Mistral Nemo (~12B params), cada llamada puede tomar 10-60s dependiendo de tu hardware.

**Optimizaciones**:
- Reduce `max_results` (de 5 a 3)
- Reduce `.slice(0, 3)` a `.slice(0, 2)` (menos URLs por iteración)
- Reduce `max_iterations` en la llamada
- Usa un modelo más pequeño: `phi3:mini`, `llama3.2:3b`

### ❌ "Out of memory" en Ollama

Mistral Nemo necesita ~8-10 GB de RAM/VRAM. Si no tienes suficiente:

```bash
# Usar un modelo más ligero
docker exec -it ollama ollama pull phi3:mini
# Luego cambia modelName en el nodo Init a "phi3:mini"
```

---

## 9. Ejemplos de Respuesta

### Input:

```json
{
  "topic": "Avances en baterías de estado sólido 2026",
  "max_iterations": 2
}
```

### Output (resumido):

```markdown
## INFORME DE INVESTIGACIÓN

### 1. RESUMEN EJECUTIVO
Las baterías de estado sólido están experimentando un avance significativo 
en 2026, con Toyota y Samsung SDI liderando la carrera hacia la producción 
en masa. Los principales avances se centran en electrolitos de sulfuro y 
ánodos de litio metálico...

### 2. HALLAZGOS PRINCIPALES

#### 2.1 Fabricantes y estado de producción
- **Toyota** anunció producción limitada para Lexus en 2026-2027
  - Fuente: https://toyota.com/news/solid-state-battery-2026
- **Samsung SDI** completó su planta piloto en Corea del Sur
  - Fuente: https://samsungsdi.com/...

#### 2.2 Densidad energética
- Las baterías de estado sólido alcanzan 400-500 Wh/kg
- Comparación: las de iones de litio actuales ~250-300 Wh/kg

[...]
```

---

## 📁 Archivos incluidos

| Archivo | Descripción |
|---|---|
| `research_agent_mistral_nemo.json` | Workflow listo para importar en n8n |
| `research_agent_documentacion.md` | Este documento |

---

## 🔗 Referencias

- [Tavily API Docs](https://docs.tavily.com/)
- [Ollama Docs](https://ollama.com/docs)
- [n8n Code Node Docs](https://docs.n8n.io/code/code-node/)
- [Mistral Nemo en Ollama](https://ollama.com/library/mistral-nemo)

---

*Plantilla creada para Arena.ai — Julio 2026*
