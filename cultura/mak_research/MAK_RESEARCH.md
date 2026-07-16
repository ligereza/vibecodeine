# MAK research -- departamento de investigacion cultural (4 APIs + local)

Sistema standalone en MAK (Debian 12, 192.168.50.2, GTX 1650 4GB, 16GB RAM).
Sin n8n (camino cerrado como FALLIDO 2026-07-15, no reintentar).
Estructura conceptual: **pagina (server) + acciones (modelos) + productos
(archivos) + correlacion semantica sobre los productos**. Recibe cualquier
tema X por 3 interfaces y devuelve informe Markdown.

## Los 6 modos (acciones)

| Modo UI | Script | Que hace | Salida |
|---|---|---|---|
| **Single** | research.py | Loop iterativo SEARCH->FETCH->ANALYZE->DECIDE->informe | informes/ |
| **Pipeline** | cadena.py | Encadenado: la salida de cada modelo alimenta al siguiente + correlacion | cadenas/ |
| **Discussion** | panel.py | Comite: todos los modelos convergen (paralelo + correlacion) | paneles/ |
| **Adversarial** | refutar.py | Proponente -> refutadores -> juez que veredicta | refutaciones/ |
| **Grafo** | grafo.py | Ejecutor real: las conexiones dibujadas DIRIGEN el orden (topologico) | grafos/ |
| **Corpus** | correlacionar_archivos.py | Correlaciona TODO el archivo acumulado (sin tema): clusteres, hilos, huecos | correlaciones/ |

Cadena LLM con fallback (research_lib.py): groq -> cerebras -> azure ->
ollama local. Cada modo respeta un orden; cadena/refutar usan el orden de
los nodos del canvas (prioridad).

**Single/Pipeline/Discussion/Adversarial** corren su script especializado y
regeneran su topologia como PRESET (el dibujo siempre matchea el modo).
**Grafo** es el ejecutor real (`grafo.py`): NO usa preset, ejecuta las
conexiones que dibujaste a mano en orden topologico -- cada nodo-modelo
recibe como contexto la salida concatenada de sus predecesores, los trigger
inyectan el tema, los output recopilan, y cierra con correlacion. Soporta
multiples triggers y outputs.

### Grafo real (conexiones dirigen la ejecucion)

- Conexiones editables por los puertos del canvas: click en el puerto de
  SALIDA (derecha) de un nodo, luego click en el puerto de ENTRADA
  (izquierda) de otro. Click sobre una arista la borra. Esc cancela.
- Multiples entradas/salidas: botones `+ In` / `+ Out` del tools menu. Los
  nodos base (trigger, output, los 4 modelos) se apagan con el toggle, no se
  borran; los extra (trigger2/output2/nota) si se borran.
- Validador anti-flujo-extremo (`grafo.py` `validar_grafo` + espejo JS
  `validarGrafo`, boton `Validar`): bloquea ciclos, modelos huerfanos, sin
  camino trigger->output, y fan-out/in > 6 o > 12 modelos. En modo grafo el
  run se bloquea si el grafo es invalido; en los otros modos solo avisa.

| Rol | Proveedor | Modelo |
|---|---|---|
| historico / rapido | Groq | llama-3.3-70b-versatile |
| tecnico | Cerebras | gpt-oss-120b |
| legal / **modelo capaz** | Azure Foundry | deployment gpt-5-mini |
| estetico / local | Ollama (GPU MAK) | gemma3:4b (aya-expanse:8b de repuesto) |

**Modelo capaz** (`MODELO_CAPAZ=azure` en research_lib): hace la correlacion
semantica y el auto-repair. Tiempos medidos (prompt corto): groq 1.2s,
cerebras 1.0s, azure 5.7s, ollama 6.6s.

Search: Tavily (1000 creditos/mes; basic=1, advanced=2).

## Correlacion semantica (el "departamento")

- **Por job:** panel.py y cadena.py cierran con `correlacionar()` --
  el modelo capaz lee lo que dijo cada modelo y produce hilo comun /
  convergencias / tensiones / vacios / mapa ordenado.
- **Sobre el archivo:** modo Corpus (correlacionar_archivos.py) lee los
  productos .json acumulados y arma un mapa del corpus completo.

## Densidad del trabajo

Perilla en la UI (corto/medio/largo) -> escala tokens por llamada con
techo duro (`research_lib.escala_tok`, tope 4000) para no pasar el
timeout del worker (1800s) ni los limites free-tier. CLI: `--densidad`.

## Interfaces (pagina)

1. **Web (LAN):** http://192.168.50.2:8890 -- canvas visual con nodos
   arrastrables, 5 modos, densidad, tools menu (zoom/pan/organizar),
   nodos nota agregables, progreso vivo, modal para ver resultados
   DENTRO de la app, boton de auto-repair en jobs fallidos, config de
   modelos por formulario. Auth opcional por `INTERFAZ_TOKEN`. Sin token
   = abierto (solo LAN, NO exponer a internet). **Firewall:** ufw de MAK
   bloquea 8890 desde la LAN; para ver desde otra maquina correr una vez
   `sudo ufw allow from 192.168.50.0/24 to any port 8890 proto tcp`.
2. **ntfy (iPhone, sin PC):** publicar a `$NTFY_TOPIC_IN`. Formatos:
   `tema` (research), `panel: tema`, `research: tema`. Respuestas por
   `$NTFY_TOPIC_OUT`.
3. **CLI:** `python3 ~/research/{research,panel,cadena,refutar,grafo}.py "tema"`
   o `correlacionar_archivos.py`. `grafo.py` lee `~/research/workflow.json`
   (nodos + connections); valida y refusa si el grafo es invalido.

## Tools menu del canvas (UI)

- **Zoom:** botones -/+, 1:1, y rueda del mouse sobre el cursor.
- **Vista:** Encajar (fit-to-view por transform, no mueve nodos),
  Centrar; paneo arrastrando el fondo vacio.
- **Nodos:** `+ In` (trigger extra), `+ Out` (output extra), `+ Nota`,
  Organizar (auto-layout por prioridad), Reset. Los nodos nota son
  anotaciones del flujo, persisten en workflow.json, no se ejecutan.
- **Grafo:** `Validar` corre el chequeo de flujo extremo y muestra los
  problemas en el modal.
- **Conexiones:** dos clicks entre puertos para crear una arista, click
  sobre la arista para borrarla (ver seccion "Grafo real").

## Operacion

- Keys: `~/n8n-local/research.env` (600). Copia PC: `cultura/.dev`
  (gitignored). NUNCA commitear. Los MODELOS se cambian desde el
  formulario Config de la web o editando research.env (reinicia
  interfaz.py para que el proceso tome el cambio).
- Servicios: `cola.py` + `interfaz.py` via nohup; cron `*/5` watchdog.sh
  los revive. Logs: `~/research/{cola,interfaz,watchdog}.log`.
- Un job a la vez (worker.py flock). Frugalidad: defaults research 2
  iteraciones, panel 1 replica, densidad medio; mas = opt-in.
- Marco cultural: capa DESCRIPTIVA (historia, estetica, derecho,
  contexto social); nada operativo, nada de sintesis quimica ni cultivo;
  jamas perfilar personas reales. `--sin-marco` lo apaga.
- systemd: `interfaz.service` (unidad de usuario, rutas absolutas) queda
  como opcion; requiere `sudo loginctl enable-linger mak` una vez. Hoy
  se usa el watchdog por cron (sin sudo).

## Trampas conocidas (no re-descubrir)

- **Firefox cachea el HTML por origen:** interfaz.py ya manda
  `Cache-Control: no-cache`; localhost y 127.0.0.1 son cache separada.
- **pkill del server:** el cmdline real es `python3 /home/mak/research/
  interfaz.py` -- usar `pkill -f "research/interfaz.py"`, NO
  `"python3 interfaz.py"` (no matchea).
- **research.env se corrompe si un test escribe el archivo real:** los
  tests deben parchear `interfaz.ENV_FILE`, no `os.environ["RESEARCH_ENV"]`
  (ese se captura al importar). Si se pierden los modelos, restaurar:
  GROQ_MODEL=llama-3.3-70b-versatile, CEREBRAS_MODEL=gpt-oss-120b,
  AZURE_DEPLOYMENT=gpt-5-mini, OLLAMA_MODEL=gemma3:4b.
- Cloudflare 403 codigo 1010 si falta User-Agent custom (urllib default
  bloqueado): research_lib._http_json manda `flujo-mak-research/1.0`.
- gpt-5-mini y gpt-oss-120b razonan: margen `max_completion_tokens =
  pedido + 2048` o devuelven vacio. Azure NO acepta temperature custom.
- Catalogo free de Cerebras ROTA: si model_not_found,
  `GET https://api.cerebras.ai/v1/models`.
- ntfy header Title debe ser ASCII (research_lib lo pliega).
- **Corpus/sitecustomize.py:** hubo un `sitecustomize.py` huerfano en
  ~/research (nombre magico de Python, se auto-importa). Si reaparece,
  borrarlo -- no es parte del sistema.

## Backlog (NO romper lo que corre)

1. Open WebUI (:8080): agregar connections Groq/Cerebras/Azure -- necesita
   login admin del usuario, solo config UI.
2. Config por-nodo en los modos preset: grafo.py ya usa system_prompt del
   nodo; falta que cadena/panel/refutar lean temperature/system_prompt del
   canvas (hoy solo respetan orden/activo).
3. Nodos nota -> inyectar su texto como instruccion extra al flujo grafo.
4. Rotacion/paginado de informes (crecen sin limite).
5. LiteLLM proxy (gateway :4000) SOLO si crecen los consumidores.

Regla de verificacion: cambio tocado = correr un research de 1 iteracion
(densidad corto) y mirar meta.errors antes de declarar OK. Para la UI:
reload duro + pantallazo, no solo leer el codigo.
