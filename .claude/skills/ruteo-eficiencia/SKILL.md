---
name: ruteo-eficiencia
description: >
  Guia de decision para NO hacer el trabajo a mano cuando ya existe un comando/skill
  instalado mas barato para esa forma de tarea (busqueda amplia, lectura de carpeta
  gorda, limpieza de codigo cambiado, revision de diff, compresion de output o de un
  doc de memoria). Traduce un pedido verboso/repetitivo al comando concreto que lo
  resuelve con menos tokens, en vez de reinventar la logica en el hilo principal.
  Invocar cuando el usuario pida "ahorra tokens", "que comando uso para esto",
  "esto se puede hacer mas barato/rapido", o cuando el pedido es claramente
  repetitivo/verboso y hay un atajo ya instalado en el repo.
---

# Ruteo de eficiencia: comando ya instalado, no reinventar

Esta skill NO comprime nada por si misma (eso ya lo hacen `caveman` para output y
`caveman-compress` para docs). Su trabajo es mas chico: mirar la FORMA del pedido y
decir que herramienta YA INSTALADA lo resuelve mas barato, antes de gastar el hilo
principal haciendolo a mano.

No confundir con `toma-de-decisiones` (esa decide QUE MODELO/agente externo — Gemini
vs Claude vs Qwen — hace una tarea). Esta skill decide QUE COMANDO dentro de una
sesion Claude Code ya resuelve la forma del pedido.

## Tabla de ruteo

| Forma del pedido | Ruta | Por que |
|---|---|---|
| "que hay en el repo / mapa rapido" sin necesidad de detalle | `py tools/vibo_voz/contexto_repo.py` | 0 tokens, mecanico |
| Contexto para una tarea concreta (rutas relevantes) | `py tools/vibo_voz/contexto_repo.py task "<keywords>"` | 0 tokens, imprime rutas + como derivarlas |
| Leer/resumir carpeta gorda (`jobs/`, `projects/`, `svg/suplementos_rd/`, `docs/handoffs/archive/`) | `py tools/vibo_voz/pedir_a_gemini.py "consulta" ruta...` | Modelo barato lee volumen, Claude recibe resumen |
| Busqueda amplia sin editar ("donde esta X", "que llama a Y", "listar usos de Z") | agente `Explore`, o `cavecrew-investigator` si esta instalado | No carga el hilo principal con exploracion cruda |
| Edicion quirurgica, 1-2 archivos, alcance ya claro | editar directo, o `cavecrew-builder` si esta instalado | Delegar algo tan chico cuesta mas que hacerlo |
| Revisar un diff/branch por bugs | `/code-review` (o `cavecrew-reviewer` si esta instalado) | Ya existe, no re-implementar el review a mano |
| Limpieza de codigo ya cambiado (reuse, simplificacion, eficiencia) | `/simplify` | Exactamente su proposito, no reinventarlo en prosa |
| Comprimir un doc de memoria largo (`CLAUDE.md`, notas, todos) | `/caveman-compress <archivo>` | Ya hace esto; revisar el diff resultante antes de aceptar (ver riesgos abajo) |
| Usuario pide respuestas mas cortas en general, de ahora en mas | `/caveman` (modo persistente) | Comprime TODO el output futuro, no una tarea puntual |
| Mensaje del commit | `/caveman-commit` | Formato Conventional Commits, ya comprimido |
| Comentarios de PR | `/caveman-review` | Una linea por hallazgo, ya comprimido |
| Investigacion profunda multi-fuente | skill `deep-research` | Ya orquesta fan-out + verificacion |
| Tarea grande, el usuario pide explicito multi-agente/fan-out | `Workflow` tool | Solo si el usuario lo pide con esas palabras; no ofrecerlo solo |

## Regla de oro

Antes de escribir 500 tokens de prosa o explorar el repo a mano: **hay una fila de la
tabla que ya calza?** Si si, usa esa ruta. Si no, segui normal — esta skill no reemplaza
juicio, solo evita reinventar lo que ya esta resuelto.

## Que NO hacer

- No inventar "compresion automatica de tokens" que no exista (no hay forma real de medir
  `token_cost(input)` en vivo desde una skill; cualquier pedido que lo prometa como
  automatismo silencioso es sospechoso — confirmar con el usuario antes de adoptarlo).
- No rutear a `/caveman-compress` sobre `CLAUDE.md` o `context/LAST_HANDOFF.md` sin
  mostrar el diff antes: son reglas operativas, un compresor via LLM puede limar un
  matiz sin que se note.
- No usar `Workflow`/fan-out multi-agente porque "parece mas eficiente": consume mucho
  mas que resolverlo directo salvo que el usuario haya pedido orquestacion explicita.
- No delegar algo mas barato de hacer directo que de explicarle a un subagente (edicion
  de 1 linea, respuesta que ya se sabe).
