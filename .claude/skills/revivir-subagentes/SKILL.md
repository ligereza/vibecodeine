---
name: revivir-subagentes
description: >
  Invocar cuando un subagente murio o quedo detenido y hay que recuperar su trabajo:
  el usuario paro una tarea ('x' en /tasks) y no dio feedback a tiempo, SendMessage
  devuelve "won't be resumed", TaskOutput dice "No task found", un agente cayo por
  API error / "session limit" / cuota, o el usuario dice "revive el subagente",
  "recupera esa tarea", "el agente murio". Tambien cuando el modelo principal fue
  bloqueado y delegado a otro (Fable -> Opus, sin retorno) y el sucesor debe
  reconstruir el contexto de la sesion anterior en vez de partir de cero.
---

# Revivir subagentes (y sucesores de un modelo bloqueado)

Mecanica verificada en vivo 2026-07-16 (Claude Code 2.1.191+). Dos escenarios con el
mismo nucleo: el contexto NO se pierde, persiste en transcripciones jsonl; lo que
cambia es si el agente original puede seguir usandolo o si hay que extraerlo y
darselo a un reemplazo.

## 1. Diagnostico: que le paso al agente

| Sintoma | Escenario | Salida |
|---|---|---|
| Caido por API error / "session limit" / cuota | A: recuperable | `SendMessage` al mismo agentId |
| `"stoppedByUser": true` en su `.meta.json`; SendMessage responde "won't be resumed"; TaskOutput "No task found" | B: irrecuperable | Extraer contexto + relanzar reemplazo |
| Modelo principal bloqueado, delego a otro modelo sin retorno | C: sucesor | Extraer contexto de la SESION + continuar |

Verificar el flag directo:
```bash
py -c "import json;print(json.load(open(r'<ruta agent-XXX.meta.json')))"
```

## 2. Escenario A: agente caido (API error) -- RESUME, no relances

`SendMessage` al agentId lo resume con TODO su contexto intacto. Probado: un agente
Fable retomo tras "session limit" y termino la tarea completa. Relanzar de cero aqui
es tirar el contexto gratis. Anti-patron: crear agente nuevo "por las dudas".

## 3. Escenario B: stoppedByUser -- extraer y relanzar

Un agente detenido por el usuario sale de la lista /tasks y en la practica es
irrecuperable (solo se destrabaria escribiendo en su transcripcion desde el panel,
pero ya no aparece ahi). El SDK con resume NO sirve: no limpia el flag y arriesga
corrupcion. Protocolo:

```bash
# 1. Localizar la transcripcion (si no tienes la ruta)
py .claude/skills/revivir-subagentes/extraer_contexto.py --buscar "keyword de la tarea"

# 2. Briefing comprimido (meta, tarea original, pedidos humanos, archivos, corte)
py .claude/skills/revivir-subagentes/extraer_contexto.py <ruta agent-XXX.jsonl>
```

Rutas: `~/.claude/projects/{proj}/{sessionId}/subagents/agent-{id}.jsonl` + `.meta.json`.

3. Relanzar agente NUEVO con el briefing pegado inline en el prompt, siguiendo el
patron de orquestacion (memoria `subagent-orchestration-pattern`): plan primero,
contexto inline completo, prohibido re-explorar docs ("si falta algo, PARA y
pregunta"), check-ins via SendMessage, verificacion independiente del auto-reporte.

Atencion especial del briefing: los "PEDIDOS HUMANOS POSTERIORES" son mensajes que
el usuario escribio directo en la transcripcion del muerto -- fuente #1 de trabajo
perdido. El reemplazo debe cubrirlos explicitamente.

## 4. Escenario C: modelo principal bloqueado (Fable -> Opus)

Si un refusal/bloqueo delega la sesion a otro modelo sin retorno, el sucesor hereda
el hilo pero puede haber perdido matices. Mismo nucleo que B, con la transcripcion
de SESION en vez de la de subagente:

```bash
py .claude/skills/revivir-subagentes/extraer_contexto.py ~/.claude/projects/<proj>/<sessionId>.jsonl
```

El sucesor ademas: lee MEMORY.md + memorias relevantes, y aplica el protocolo
anti-block acordado con el usuario (warn-first: avisar `[!] tema sensible: <cual>`
ANTES de entrar a zona riesgosa, ofrecer reformulacion, nunca rechazo seco que
vuelva a quemar un modelo). Prevenir el bloqueo del sucesor es parte del rescate.

## 5. La inversion de tokens del muerto (que se rescata y que no)

Preocupacion real del usuario: los tokens que el agente ya penso "se van a la basura".
Verificado 2026-07-17 contra un Fable muerto con 98,486 output_tokens invertidos:

| Producto | Rescatable? | Como |
|---|---|---|
| Analisis, hallazgos, planes, borradores (texto visible) | SI, completo | `--volcar rescate.md` (bloques en orden cronologico) |
| Archivos que escribio (Write/Edit) | SI, siguen en disco | briefing lista rutas; `git diff` para ver el estado |
| Tool calls (que miro, que corrio) | SI | briefing (nombres + rutas) |
| Thinking interno crudo | NO (persiste solo como firma) | -- |

```bash
py .claude/skills/revivir-subagentes/extraer_contexto.py <agent-XXX.jsonl> --volcar rescate.md
```

El rescate.md se pega/adjunta inline al reemplazo: hereda las conclusiones ya pagadas
en vez de re-pensarlas. Consecuencia preventiva: como el thinking crudo NO se rescata,
lo que protege la inversion es que el pensamiento se MATERIALICE seguido -- check-ins
frecuentes y archivos escritos temprano (patron orquestacion). Y el escenario A
(SendMessage resume) rescata el 100%, thinking incluido: agotar esa via antes de
declarar muerte.

## 6. Anti-patrones (todos costaron caro ya)

- **Read del jsonl entero en el hilo:** blobs base64 de screenshots revientan el
  contexto. Siempre `py` linea por linea (el script ya lo hace).
- **SDK `resume` para destrabar stoppedByUser:** no limpia el flag, arriesga
  corrupcion de la sesion activa.
- **Fire-and-forget del reemplazo:** repetir la muerte. Check-ins obligatorios.
- **Partir de cero "porque es mas facil":** re-quema los tokens que la transcripcion
  ya pago.

## 7. Auditoria de perdida (cuando sospechas que algo se perdio)

Patron workflow probado (~11 min): 3 extractores paralelos (transcripcion del
muerto / transcripcion del sucesor / estado git real con `git grep` de firmas en
HEAD) + 1 reconciliador. Veredicto por item: PRESENTE / PERDIDO / REEMPLAZADO /
PENDIENTE-LEGITIMO. Detecto 1 perdida real de proceso que ningun resumen mostraba.

Relacionado: memorias `revive-subagents`, `subagent-orchestration-pattern`; skill
`verificar-antes-de-negar` (antes de declarar "irrecuperable", verifica el flag real).
