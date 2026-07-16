# cultura/ - plan operativo (handoff para agentes)

Subsistema de arte-investigacion. Primer sujeto: **wachuma** (huachuma / San Pedro).
Regla de reparto: la investigacion la hace un **LLM local en MAK** via n8n (gratis,
volumen); Claude/Sonnet solo construyen y auditan el rig.

Modelo elegido 2026-07-15: **aya-expanse:8b** (Cohere, multilingue, fuerte en
espanol -- probado: entiende matiz + modismo rioplatense y saca JSON limpio;
~8 tok/s en CPU). Reemplaza a mistral-nemo 12B (mas lento, peor espanol).
Modelos en MAK tras limpieza: `aya-expanse:8b` (research) + `nemo-exec:latest`
(agente de ejecucion del usuario). Borrados: mistral-nemo, deepseek-r1-abliterated,
qwen2.5-abliterate. Limpieza de disco MAK: -12 GB (imagen docker vieja + caches).

Limites cultura (CLAUDE.md): capa descriptiva/cultural si; nada generativo de
sintesis; nunca perfilar personas reales; enfoque reduccion de danos, no guia de
consumo.

## Inventario

| Archivo | Que es | Estado |
|---|---|---|
| research_agent_mistral_nemo.json | Workflow n8n: loop de research autonomo (Tavily + Ollama aya-expanse:8b) | desplegado; bloqueado solo por timeout 300s del Code node (ver seccion 1) |
| research_agent_documentacion.md | Manual del workflow (runtime MAK + ethernet) | actualizado |
| BLENDER.trilogy_450frames.py | Trilogia original: 3 actos x 150 frames (primitivas+modifiers) | referencia, no tocar |
| BLENDER.geonodes_450.py | Trilogia FUSIONADA: 15 modos x 30 frames en UN arbol de Geometry Nodes | verificado en Blender 4.5.4 |
| blend-math-lab.html | Lab interactivo: f(b,l), superficie, histogramas, algebra | terminado |
| trilogia.3d.blender.html | Ensayo-juguete: modos de mezcla como convivencia | terminado |
| xio-concept.html | Grafo de 41 nodos: guia cultural/conceptual de xio | terminado; su punto de crecimiento es el server |
| .dev | API key Tavily (SOLO checkout local, gitignored) | NUNCA commitear |

## 1. Loop de research (n8n en MAK) -- DESPLEGADO Y VERIFICADO 2026-07-15

Topologia real de MAK (dell-11m, Debian, 192.168.50.2 por ethernet): n8n 2.30.5 en
docker con network_mode host; Ollama systemd en 127.0.0.1:11434; ufw activo.
Hechos aplicados (no repetir):

1. ufw: `sudo ufw allow proto tcp from 192.168.50.1 to any port 5678` (solo el PC
   por ethernet; el hotspot xio queda afuera, coherente con el aislamiento MAK-xio).
2. El JSON usa `ollamaBaseUrl = http://127.0.0.1:11434` porque n8n es host-network
   en Linux (host.docker.internal NO existe ahi).
3. El Code node llama `this.helpers.httpRequest` capturado como metodo
   (`const __self = {helpers: this.helpers}`). Era el bug del "oso": las funciones
   sueltas perdian `this` y fallaba en silencio -> hallazgos vacios -> el modelo
   alucinaba. El sandbox del task-runner NO expone `fetch` ni `AbortController`,
   asi que hay que usar el helper nativo de n8n (no fetch global).
4. Webhook: el nodo necesita `webhookId` (sin el, "Activated" pero la ruta
   /webhook/research da 404). Ya esta puesto.
4. Import por CLI (la UI tambien sirve): el JSON necesita un campo `id`;
   despues de CADA import hay que `publish:workflow` y `docker restart n8n`:
   `docker exec n8n n8n import:workflow --input=/tmp/wf.json`
   `docker exec n8n n8n publish:workflow --id=wachumaMAK00000001`
   `docker restart n8n` (verificar "Activated workflow" en docker logs).
5. Credencial Ollama en el nodo "Ollama: Mistral Nemo": Base URL `http://127.0.0.1:11434`.
6. Tavily key: por env `TAVILY_API_KEY` de n8n o en el body del request
   (`tavily_api_key`); la key vive en cultura/.dev del checkout local, jamas en el JSON.
7. Disparar por ethernet:

```bash
curl -X POST http://<IP-MAK>:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "wachuma / huachuma (San Pedro, Echinopsis pachanoi): historia, etnobotanica andina, contexto cultural y legal", "max_iterations": 4}'
```

Devuelve informe Markdown generado por el LLM local. Detalle completo en
`research_agent_documentacion.md`.

**PENDIENTE (knob de n8n, lo revisa el usuario):** todo el loop corre dentro de UN
solo nodo Code de forma sincrona; el task-runner de Code de n8n tiene timeout por
defecto de **300 s** (`N8N_RUNNERS_TASK_TIMEOUT`). Con aya en CPU, 2 iteraciones se
pasan de 300s -> el webhook devuelve HTTP 200 con cuerpo vacio y el log dice
"Task execution timed out after 300 seconds". VERIFICADO que aya busca en Tavily y
analiza (CPU 350%, 2 conexiones :443) -- solo falta que termine dentro del tope.
Arreglos: (a) subir el timeout en el env del contenedor n8n
`N8N_RUNNERS_TASK_TIMEOUT=1200` y reiniciar; (b) bajar `max_iterations` a 1 y
analizar 1 URL/iteracion; (c) refactor mayor: sacar el loop del Code node a nodos
n8n nativos (HTTP Request + IF + Loop). Recomendado: (a).

## 2. Blender: trilogia fusionada en Geometry Nodes

```
Abrir Blender 4.5 LTS -> Scripting -> abrir BLENDER.geonodes_450.py -> Alt+P
(o headless: blender -b -P cultura/BLENDER.geonodes_450.py)
```

- 450 frames = 15 modos x 30 = 15 s @ 30 fps. Un marker por modo.
- MEZCLA: Simulation Zone itera b <- modo(b, l) una vez por frame (30 iteraciones
  por segmento hacia el punto fijo del operador).
- MAPA: l = u (la direccion x del punto en [0,1]); atributos addr_u/addr_v -> material.
- RELIEVE: TWIN_structure desplaza geometria real; TWIN_gaze plano con bump; la luz
  orbital los delata.
- IMPORTANTE: las Simulation Zones evaluan frame a frame -- reproducir desde frame 1.
- Verificado headless en Blender 4.5.4: reset por segmento OK, NORMAL converge a b=u,
  MULTIPLY colapsa a 0.15*u^14, twin gaze permanece plano.

## 3. xio: cue engine + panel + WoL + fabric + sonda + automap (v1.4 de showcontrol)

Puntos de crecimiento implementados del grafo (`orq` + `fabric` + `sonda`/`p_inv`): cue
list con fades temporizados, panel de control en navegador, Wake-on-LAN con verificacion
de servicio, signal fabric (una senal 0..1 abanica a muchos canales DMX / faders OSC),
descubrimiento de nodos Art-Net (ArtPoll/ArtPollReply) y automapeo optico de DMX por
matriz de transporte (single / Hadamard multiplexado).
Codigo: `xio/new-plugins/showcontrol/cueengine.py` + `panel.py` + `fabric.py` +
`discovery.py` + `automap.py` (+ wiring `__init__.py`).
Tests off-device (45 en total): `test_cueengine.py` (12, incluye 3 regresiones de la
auditoria adversarial), `test_protocols.py` (11, incluye WoL), `test_fabric.py` (6),
`test_discovery.py` (5), `test_automap.py` (8) y `test_integration.py` (3: nodo Art-Net
virtual + servidor OSC dummy por UDP real, mas fabric end-to-end).

### Signal fabric (nodo `fabric` del grafo)

Ruteo hub-and-spoke O(N+M): N senales logicas, M rutas, sin malla N*M. Una senal en
[0,1] mapea por ruta a `min + (max-min) * v**curve` y abanica a canales DMX (cualquier
universo) o faders OSC (host/port por ruta). `set(master, 0.5)` actualiza todo lo atado
a `master` de una y emite el set minimo de paquetes. Hilo keep-alive 30 Hz mientras hay
rutas activas (re-emite el frame DMX estable cada 1s: guarda contra timeout de nodos
Art-Net). Se apaga solo cuando no hay rutas (disciplina de bateria).

```bash
# cargar el fabric: DMX necesita 'output' {protocol,host}; OSC lleva host/port por ruta
curl -X POST http://<phone>:5000/api/plugins/showcontrol/fabric -H "Content-Type: application/json" -d '{
  "output": {"protocol": "artnet", "host": "192.168.x.x"},
  "signals": ["master", "hue"],
  "routes": [
    {"signal": "master", "sink": "dmx", "universe": 0, "channel": 1},
    {"signal": "master", "sink": "dmx", "universe": 0, "channel": 5, "max": 200, "curve": 2.2},
    {"signal": "hue", "sink": "osc", "host": "192.168.x.y", "port": 9000, "address": "/hue", "kind": "float"}
  ]}'
curl -X POST http://<phone>:5000/api/plugins/showcontrol/fabric/set -d '{"signal": "master", "value": 0.5}'
curl http://<phone>:5000/api/plugins/showcontrol/fabric/state
```

### Descubrimiento Art-Net (nodo `sonda` del grafo)

Antes de disparar DMX a ciegas, ver que fixtures estan vivos en la LAN. Difunde un
ArtPoll (OpCode 0x2000) a UDP 6454 y colecta los ArtPollReply (0x2100): IP, nombres,
MAC, OEM y mapa de puertos. El builder y el parser son puros (unit-tested contra bytes
a mano); solo `discover()` toca la red (un envio SO_BROADCAST + recv acotado por
timeout, sin shell). En el panel: boton "SCAN LAN" -> lista de nodos; tap en un nodo
mete su IP en `output.host` del JSON del show.

```bash
curl -X POST http://<phone>:5000/api/plugins/showcontrol/discover -d '{"timeout": 3}'
# -> {"ok": true, "count": N, "nodes": [{"ip": "...", "short_name": "...", "mac": "...", "ports": 1, ...}]}
```

### Automapeo optico de DMX (nodo `sonda`/`p_inv` del grafo)

El transporte de luz es lineal en el nivel DMX: `luz_medida = T . dmx`. Actuando una
BASE de canales y midiendo la respuesta, se recupera T columna a columna -- y T ES el
patch: que canal enciende que fixture, aprendido opticamente, sin direccionar a mano
(Sen et al. 2005, dual photography). Dos modos: `single` (un canal por vez, n frames) y
`hadamard` (grupos codificados, Schechner et al. 2007 multiplexed illumination): cada
fila de codigo +-1 se emite como dos frames (canales +1, luego -1) y se resta -- el
diferencial cancela la luz ambiente y da ventaja de SNR (~2/n de la varianza de single).
Matematica pura stdlib (sin numpy, sin camara: la camara es hardware del operador; la
secuencia y el estimador son nuestros). 8 tests: test_automap.py.

```bash
# 1) pedir el barrido; emitir cada step.emit a /artnet como 'channels', medir en orden
curl -X POST http://<phone>:5000/api/plugins/showcontrol/automap/plan \
  -d '{"channels": [1,2,3,4,5], "level": 255, "mode": "hadamard"}'
# 2) resolver: measurements alineadas a plan.steps -> respuesta por canal + residual
curl -X POST http://<phone>:5000/api/plugins/showcontrol/automap/solve \
  -d '{"channels": [1,2,3,4,5], "mode": "hadamard", "level": 255, "measurements": [...]}'
# -> {"ok": true, "response": {"1": 0.5, ...}, "residual": ~0}
```
Panel: abrir `http://<phone>:5000/api/plugins/showcontrol/panel` desde tablet/navegador
(GO grande, STOP, RELEASE, lista de cues con tap-to-jump, carga de JSON, WoL).
WoL: `POST /api/plugins/showcontrol/wol {"mac": "AA:BB:..", "verify_host": ip,
"verify_port": 22, "timeout": 30}` -- 3 magic packets + espera TCP del servicio.

API (server xio, prefijo /api/plugins/showcontrol):

```bash
# cargar show (output artnet o sacn; osc_host opcional)
curl -X POST http://<phone>:5000/api/plugins/showcontrol/cues -H "Content-Type: application/json" -d '{
  "output": {"protocol": "artnet", "host": "192.168.x.x"},
  "cues": [
    {"label": "open", "fade": 3.0, "levels": {"0": {"1": 255, "2": 128}},
     "osc": [{"address": "/scene/open", "args": [1]}]},
    {"label": "mid",  "fade": 5.0, "levels": {"0": {"1": 100}}, "follow": 10.0},
    {"label": "end",  "fade": 2.0, "levels": {"0": {"3": 255}}}
  ]}'
curl -X POST http://<phone>:5000/api/plugins/showcontrol/cue/go        # siguiente cue
curl -X POST http://<phone>:5000/api/plugins/showcontrol/cue/go -d '{"index": 2}'
curl -X POST http://<phone>:5000/api/plugins/showcontrol/cue/stop      # congela
curl -X POST http://<phone>:5000/api/plugins/showcontrol/cue/release -d '{"fade": 3}'
curl http://<phone>:5000/api/plugins/showcontrol/cue/state
```

Semantica: cue = look completo (canales ausentes bajan a 0); follow = auto-avance;
release funde a negro y apaga el hilo de tick (disciplina de bateria, 30 Hz solo
durante show; keep-alive 1 Hz para nodos Art-Net/sACN). Deploy al telefono: manual
por USB segun runbook xio (el codigo queda en repo; deploy decision del usuario).

Gap-audit del grafo -> codigo: lazo=charge_control OK; muros=arquitectura no-root OK;
orq/osc+dmx=protocols.py OK; orq/cue-engine=IMPLEMENTADO; fabric (formato canonico de
senales)=IMPLEMENTADO; sonda/descubrimiento Art-Net=IMPLEMENTADO;
sonda/p_inv=automapeo optico de DMX (matriz de transporte)=IMPLEMENTADO (este cambio);
splat/rllm = investigacion (necesitan GPU/camara: fuera del alcance software puro).

## Pendiente / siguiente

- Probar el loop n8n end-to-end en MAK con topic wachuma real.
- Deploy de showcontrol v1.4 (cue + fabric + sonda + automap) al Xiaomi (USB) + humo LAN.
- Cerrar el lazo `sonda`: glue de camara (el operador dispara la captura por step del
  plan y alimenta /automap/solve). La camara es hardware del usuario; la mate ya esta.
- `obs` (observabilidad): endpoint/panel de telemetria unificada (rates, hilos, ultimo
  error) -- siguiente nodo software puro candidato.
- Render real de los 450 frames (EEVEE Next) cuando el usuario quiera la pieza.
