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
        research.py (loop iterativo)      panel.py (debate 4 modelos)
             |                                     |
   SEARCH Tavily -> FETCH -> ANALYZE       4 busquedas paralelas ->
   (LLM fallback) -> DECIDE -> informe     4 panelistas -> replicas ->
             |                             sintesis Cerebras gpt-oss-120b
             v                                     v
   ~/research/informes/*.md               ~/research/paneles/*.md
```

Cadena LLM con fallback (research_lib.py): cerebras -> groq -> ollama local.
GPT mini/Azure fue retirado de MAK el 2026-07-28 para reservar ese cupo a la
sesion principal. Panel: cada angulo pide primero SU proveedor:

| Angulo | Proveedor | Modelo |
|---|---|---|
| historico | Groq | llama-3.3-70b-versatile |
| estetico | Ollama local | gemma3:4b (OLLAMA_MODEL; aya-expanse:8b instalado de repuesto) |
| legal | Groq | llama-3.3-70b-versatile |
| tecnico | Cerebras | gpt-oss-120b |

Search: Tavily (1000 creditos/mes; basic=1, advanced=2).

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

- Keys: `~/n8n-local/research.env` (600). Copia PC: `cultura/.dev`
  (gitignored). NUNCA commitear.
- Servicios: `cola.py` + `interfaz.py` via watchdog/cron; el unit
  `interfaz.service` del repo es solo compatibilidad y no está instalado en el
  runtime verificado. Logs: `~/research/{cola,interfaz}.log`.
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
- gpt-oss-120b es razonador: margen
  `max_completion_tokens = pedido + 2048` o devuelven vacio.
- Catalogo free de Cerebras ROTA (hoy: gpt-oss-120b, gemma-4-31b,
  zai-glm-4.7): si model_not_found, `GET https://api.cerebras.ai/v1/models`.
- qwen3 mete tags `<think>` en la salida: por eso gemma3:4b (ademas
  cabe entero en los 4GB de VRAM).
- ntfy header Title debe ser ASCII (research_lib lo pliega).

## Backlog para los agentes que siguen (VS Code / Antigravity)

Mejoras en orden de valor; NO romper lo que ya corre:

1. Open WebUI (:8080, ya corre): agregar connections Groq/Cerebras/Azure
   (OpenAI-compatible) para chat multi-modelo manual -- necesita login
   admin del usuario, es solo config UI.
2. Progreso vivo en interfaz.py (hoy: estados en cola/corriendo/listo);
   SSE o polling de un status.json por job.
3. systemd user units en vez de cron @reboot (loginctl enable-linger mak).
4. Tests: research_lib con mocks urllib (sin gastar APIs reales).
5. Rotacion/indice de informes (hoy crecen sin limite).
6. LiteLLM proxy (gateway unico :4000) SOLO si el numero de consumidores
   crece; hoy seria complejidad gratis.
7. Auth minima (token en query o basic) para interfaz.py si algun dia
   sale de la LAN.

Regla de verificacion: cambio tocado = correr un research de 1
iteracion y un panel de 0 replicas contra APIs reales y mirar
meta.errors antes de declarar OK.
