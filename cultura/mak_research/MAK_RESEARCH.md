# MAK research -- sistema de investigacion cultural (Hub + servicios internos)

Sistema standalone en MAK (Debian 12, 192.168.50.2, GTX 1650 4GB, 16GB RAM).
Sin n8n (camino cerrado como FALLIDO 2026-07-15, no reintentar).
Recibe cualquier tema X por un Hub humano o por canales de maquina y devuelve
un informe Markdown. Research no es una interfaz publica independiente: su
servidor escucha solo en loopback y el Hub lo expone bajo `/research/`.

## Arquitectura

```
tema X --> [Hub /research/]  [ntfy iPhone]  [CLI ssh]
                    |
              [servicio interno :8890]
                    \                 |            /
                     worker.py (lock: 1 job a la vez)
                    /                              \
        research.py (loop iterativo)      panel.py (debate multi-modelo)
             |                                     |
   SEARCH Firecrawl/SearXNG/Tavily ->      busquedas por angulo ->
   CAPTURE Firecrawl/Crawl4AI/urllib ->    panelistas -> replicas ->
   ANALYZE (LLM fallback) -> DECIDE        sintesis y correlacion
             v                                     v
   ~/research/informes/*.md               ~/research/paneles/*.md
```

El buscador se selecciona con `RESEARCH_SEARCH_PROVIDER=firecrawl` para una
corrida API-first. En `auto`, SearXNG es primero, Firecrawl es fallback y
Tavily es el ultimo respaldo si hay llave. El JSON conserva `motor`,
`capture_backend`, `capture_attempts` y el recorte enviado al modelo.
Cada finding conserva además `analysis_provider`, `search_backend` y
`search_query`; los reintentos no se resumen como si fueran una sola llamada.

Cadena LLM configurable (research_lib.py): los proveedores presentes en
`/home/mak/research/research.env` participan; `--providers groq` aisla Groq
para una comparacion reproducible. Azure requiere `RESEARCH_AZURE_ENABLED=1`.
Watsonx solo participa si sus variables existen. La compuerta del informe
marca `review_required` si faltan URLs de evidencia, consultas registradas o
la separacion DICEN/INFERIMOS/NO SE ENCONTRO.

Panel: cada angulo pide primero su proveedor configurado:

| Angulo | Proveedor | Modelo |
|---|---|---|
| historico | Groq | GROQ_MODEL activo |
| estetico | Ollama local | OLLAMA_MODEL activo |
| legal | Groq | GROQ_MODEL activo |
| tecnico | Cerebras | gpt-oss-120b |

Search: Firecrawl Search consume creditos por consulta; SearXNG es local y no
consume API; Tavily solo se intenta si hay llave y los anteriores no entregan.

## Interfaces

1. **Web humana (local):** http://127.0.0.1:8900/research/ -- formulario
   tema + modo + n; lista informes. El Hub es la unica superficie Web y
   mantiene el servicio Research interno en `127.0.0.1:8890`.
2. **ntfy (iPhone, sin PC):** publicar a `$NTFY_TOPIC_IN` (ver
   research.env). Formatos: `tema` (research), `panel: tema`,
   `research: tema`. Respuestas por `$NTFY_TOPIC_OUT`: ack, informe
   (900 chars + ruta), fallos.
3. **CLI:** para delegacion remota usar `tools/mak/delegar.py research`, que
   envia el trabajo al Hub; los scripts `~/research/{research,panel}.py` son
   herramientas locales del servicio y no superficies de red.

## Operacion

- Keys: `/home/mak/research/research.env` (600). NUNCA commitear ni imprimir
  valores. La configuracion activa se inspecciona solo por nombres.
- Servicios: Hub/Research internos bajo systemd; no usar cron ni workers
  permanentes para una corrida manual. Logs: `~/research/{cola,interfaz}.log`.
- Frugalidad (regla del usuario): defaults research 2 iteraciones,
  panel 1 replica; mas profundidad = flag explicito. Un job a la vez.
- Marco cultural (viaja con toda pieza): capa DESCRIPTIVA (historia,
  estetica, derecho, contexto social); nada operativo, nada de sintesis
  quimica ni cultivo; jamas perfilar personas reales. `--sin-marco`
  lo apaga para temas no sensibles.

## Trampas conocidas (no re-descubrir)

- Cloudflare 403 codigo 1010 si falta User-Agent custom (urllib
  default bloqueado): research_lib._http_json ya manda
  `flujo-mak-research/1.0`.
- Groq `openai/gpt-oss-20b` es el modelo activo validado; los modelos
  `openai/gpt-oss*` requieren `max_completion_tokens = pedido + 2048` porque
  consumen presupuesto en razonamiento.
- Catalogo free de Cerebras ROTA (hoy: gpt-oss-120b, gemma-4-31b,
  zai-glm-4.7): si model_not_found, `GET https://api.cerebras.ai/v1/models`.
- qwen3 mete tags `<think>` en la salida: por eso gemma3:4b (ademas
  cabe entero en los 4GB de VRAM).
- ntfy header Title debe ser ASCII (research_lib lo pliega).

## Backlog para los agentes que siguen (VS Code / Antigravity)

Mejoras en orden de valor; NO romper lo que ya corre:

1. Progreso vivo en interfaz.py (hoy: estados en cola/corriendo/listo);
   SSE o polling de un status.json por job.
2. Tests: research_lib y source_pipeline con mocks urllib (sin gastar APIs
   reales). En esta caja `pytest` no esta instalado, por lo que el gate actual
   se valida con `py_compile` y smoke Python hasta autorizar una instalacion.
3. Rotacion/indice de informes (hoy crecen sin limite).
4. LiteLLM proxy (gateway unico :4000) SOLO si el numero de consumidores
   crece; hoy seria complejidad gratis.
5. Auth minima (token en query o basic) para interfaz.py si algun dia
   sale de la LAN.

Regla de verificacion: cambio tocado = correr un research de 1 iteracion,
revisar `meta.errors`, `meta.captureBackends` y `quality`, y no declarar OK si
el resultado es `review_required`. Un panel de 0 replicas es opcional y no
sustituye la trazabilidad del informe.
