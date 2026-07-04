# AUDITORIA - Asistente de voz CODE/VIBO/REDU + secretario Claude (2026-07-04)

Nota de honestidad: los tokens son datos REALES medidos de los logs de sesion.
Latencia y % de fiabilidad son estimaciones cualitativas (no instrumentamos
benchmarks). No invento precision.

## PARTE 1 - INTEGRACIONES

### A) Funcionaron
1. **Gemini Live API (native-audio) <-> Python (websockets)** - voz en tiempo real
   (audio in + entiende + TTS). Artefacto: `vibo.py` (`client.aio.live.connect`,
   `send_realtime_input(activity_start/audio/activity_end)`). Funciono por: manual
   activity detection (push-to-talk) + transcripcion in/out. Patron: media-duplex
   controlado por tecla, no VAD.
2. **Python -> Claude Code CLI (headless)** - `claude -p` en la carpeta del proyecto.
   Artefacto: `claude_bridge.encargar_a_claude` (`_resolver_claude` + `cmd /c`).
   Patron: delegacion bajo demanda, en segundo plano, con log + ESTADO.
3. **Gemini function-calling -> GitHub REST (solo lectura) + FS local**. Artefacto:
   `github_tools.py`, `leer_archivo`/`escribir_archivo`. Patron: el modelo barato
   resuelve con herramientas baratas antes de escalar.
4. **GitHub Actions `claude.yml`** (blindado, inactivo). Patron: automatizacion en
   la nube con gate por autor.

### B) Fallaron (y como se arreglaron)
1. **Modelo Live inexistente** `gemini-live-2.5-flash-preview` -> error 1008 "not
   found for bidiGenerateContent". Fix: `list_models.py` -> la cuenta expone
   `gemini-2.5-flash-native-audio-latest`. Leccion: no asumir ids de modelo.
2. **Error 1007** "audio content type not supported" (native-audio, intermitente)
   -> traceback + rebote a publico. Fix: capturar `APIError/ConnectionClosed` y
   reconectar el MISMO modo. Punto de quiebre: el `receive()` de una sesion en
   teardown.
3. **CLI `claude` no encontrado** (no estaba en PATH del subprocess; ademas es un
   `.cmd`). Fix: `shutil.which` + fallback `%APPDATA%/npm/claude.cmd` + `cmd /c`.
4. **Agentes headless se quedaban preguntando** (son de un tiro, nadie lee). Fix:
   preambulo "no preguntes, elige lo seguro y reporta".

### C) Bucles / recursion
1. **`claude.yml`**: `issue_comment:[created]` disparaba con cada comentario,
   incluidos los del propio Claude -> A(comenta)->workflow->Claude(comenta)->A.
   Circuit breaker: gate `sender.type != 'Bot'` + `author_association` + `concurrency`.
2. **Anti-bucle local**: un secretario a la vez + `_MAX_ORDENES` 5/60s +
   `_MAX_TOTAL_SESION` 15. Artefacto: `claude_bridge.encargar_a_claude` (checks al inicio).

## PARTE 2 - TOKENS (datos reales)

### D) Desglose (medido de los logs de Claude Code)
| Tarea | IN | OUT | cache_creado | cache_leido | TOTAL | Necesario? |
|---|---|---|---|---|---|---|
| Agente "mover SVG" | 16,884 | 4,526 | 111,322 | 354,559 | 487,291 | NO (ambiguo, se nego) |
| Agente "copiar SVG" | 17,188 | 4,983 | 49,749 | 596,345 | 668,265 | Parcial (volvio a preguntar) |
| Suma 2 agentes | 34,072 | 9,509 | 161,071 | 950,904 | ~1,155,556 | ~50% desperdicio |
| Sesion interactiva (setup) | 106,784 | 510,193 | 814,024 | 60,534,112 | ~61,965,113 | necesaria (iterativa) |

Clave: ~950k de los 1.16M son **cache_leido** (~10x mas barato). Tokens "caros"
reales de los 2 agentes: ~205k.

### E) Oportunidades de ahorro (Top)
1. **Contexto que Claude recarga por orden (~500k tok).** Causa: cada `claude -p`
   hace onboarding del repo. Ahorro potencial: **>90% por orden** con el patron
   operador (Gemini pasa contexto reducido) + preambulo "no onboarding". Ya
   implementado (`encargar_a_claude(contexto=...)`).
2. **Ida-y-vuelta por ambiguedad** (2 corridas para 1 tarea = ~2x). Causa: ordenes
   vagas + agente preguntando. Ahorro: ~50% en esos casos. Fix: preambulo + operador
   que pre-verifica.
3. **Escalar a Claude para cosas baratas** (guardar un texto). Ahorro: ~500k tok por
   evento evitado. Fix: `escribir_archivo`/`leer_archivo` locales.
4. **Modelo caro para tareas mecanicas.** Ahorro: usar `CLAUDE_MODEL=haiku`.

PROYECCION (estimada): con operador + preambulo + tools locales, una orden tipica
baja de ~500k a ~5-20k tok. Si haces ~20 ordenes/mes: de ~10M a ~0.3M tok/mes en
agentes (>95%). El grueso del gasto real ya es cache barato, asi que el impacto en
plata es menor que en tokens brutos, pero la reduccion de recarga es sustancial.

## PARTE 3 - SEGURIDAD

### F/H) Brechas encontradas y mitigadas
- **`leer_archivo` leia rutas arbitrarias** (podia leer `.env`/llaves a la nube).
  Severidad ALTA. Mitigada: restringido a repo/proyectos + bloqueo de credenciales.
- **Agentes de pago disparables por voz/accidente.** Severidad ALTA. Mitigada:
  `VIBO_AGENTS_ENABLED` off por defecto + tope + anti-bucle.
- **Microfono siempre abierto** (capturaba en reposo). Severidad MEDIA. Mitigada:
  se abre solo con F8.
- **`claude.yml`: cualquiera con @claude disparaba Claude con write.** Severidad
  CRITICA (si se activaba). Mitigada: gate por autor + anti-bot + permisos minimos.

### G) Residuales (no 100% cerrables)
- **Acceso fisico a la maquina** = acceso al `.env` local. No cerrable por software;
  mitigado por protocolo de cierre (cerrar terminal/Gmail en equipo compartido).
- **Agentes con `acceptEdits`** editan sin preguntar (por diseno). Mitigado:
  reversible por git + `CLAUDE_PERMISSION_MODE=plan` disponible.
- **Tier gratuito de Gemini** puede usar datos para entrenar. Mitigado: REDU no
  lee datos privados en voz; no meter secretos en el chat de voz.

### I) Matriz de riesgos
| Riesgo | Severidad | Mitigado | Gap | Accion |
|---|---|---|---|---|
| Key en logs/commits | CRITICA | SI | No | - |
| @claude abierto a cualquiera | CRITICA | SI | No | (verificar sin secret) |
| leer_archivo -> credenciales | ALTA | SI | No | - |
| Agentes de pago por accidente | ALTA | SI | No | - |
| Context/prompt injection (issue) | ALTA | Parcial | Si | issue=pedido + no-secretos (mitiga, no elimina) |
| Microfono en reposo | MEDIA | SI | No | - |
| acceptEdits autonomo | MEDIA | Parcial | Si | usar 'plan' si dudas |
| Acceso fisico a .env | MEDIA | Parcial | Si | protocolo de cierre |

## PARTE 4 - LINGUISTICA

### J) Cuando fuiste abstracto
- "es para github" (tras describir voz) -> entendi workflow de repo; era un asistente
  de voz que consulta GitHub. Lo descubri preguntando.
- "VIBO sera CODE... pero VIBO es su cara" -> primero iba a renombrar todo VIBO->CODE
  (error). Tu aclaraste: son capas distintas. Freno del rename a tiempo.
- "dejar uno de geminis a cargo" -> lo lei como overseer; correcto (supervisar_procesos).

### K) Analisis
TOP 5 palabras que repetias: **gemini/geminis**, **claude**, **tokens/gasto**,
**seguridad**, **procesos**. Comunican: foco en costo y control.
TOP 5 que casi no usabas (y ayudarian): **presupuesto/tope**, **rollback/revertir**,
**permisos/privilegio**, **auditoria/logs**, **latencia**. Las evitabas porque
pensabas en objetivos ("que no gaste", "que no escuche") mas que en mecanismos; darles
nombre acelera pedir la mitigacion exacta.

## PARTE 5 - COMPARATIVA (honesta)

Aclaracion: en este proyecto "Cloud" (Google Cloud services) NO se uso; el eje real
fue **Gemini (gratis) vs Claude Code (de pago)**. Comparo eso.

| Aspecto | Gemini Live (free) | Claude Code (paid) |
|---|---|---|
| Voz en tiempo real | SI (nativo) | NO |
| Editar repo / correr comandos | NO | SI (con criterio) |
| Costo por tarea | ~0 (tier free) | alto (recarga de contexto) |
| Fiabilidad instruccion compleja | media | alta |
| Fiabilidad conversacion | alta | n/a |
| Preparar/reducir contexto | SI (barato) | posible pero caro |

### O) Recomendacion por tarea
- Conversar / rutear / decidir -> **Gemini**.
- Leer/resumir/guardar texto/buscar -> **Gemini** (tools locales).
- Preparar contexto para delegar -> **Gemini (operador)**.
- Editar codigo / crear entregable validado / correr tests -> **Claude**.
- Automatizacion desatendida en la nube -> **Claude Actions** (blindado) solo si repo
  privado + tope de gasto.

## PARTE 6 - ERRORES Y MEJORAS

### P) Top errores mas costosos
1. Ambiguedad -> 2 corridas de agente (~1.15M tok). Prevenible con operador + ordenes
   especificas + preambulo.
2. Id de modelo asumido -> varias reconexiones fallidas. Prevenible con `list_models`.

### Q) Mejoras propuestas
1. **Batching** de ordenes chicas (1 carga de contexto). Esfuerzo: chico. Ahorro: alto.
2. **Brief persistente** que Gemini mantiene y pasa a Claude. Esfuerzo: medio. Ahorro: alto.
3. **Modo plan por defecto** para ordenes destructivas, confirmar por voz. Esfuerzo: chico.
   Ganancia: seguridad.

## PARTE 7 - SKILL Y ROADMAP

### R) SKILL (resumen; la operativa vive en .claude/skills/toma-de-decisiones/)
- Description: orquestar modelo barato (Gemini) como operador/capataz y modelo caro
  (Claude) como ejecutor, con seguridad opt-in y ahorro por reduccion de contexto.
- Strengths: voz natural; delegacion barata; seguridad por defecto; anti-bucle; auditable.
- Weaknesses: Gemini puede preparar mal contexto; native-audio da 1007 intermitente;
  agentes de un tiro (sin dialogo).
- Security posture: criticas 2 (mitigadas), altas 2 (1 parcial: injection), residuales 3.
  Risk score: BAJO-MEDIO (con agentes off por defecto).
- Token efficiency: ~5-20k/orden con operador (vs ~500k sin el). Ahorro potencial >90%.
- Model recs: ver Parte 5-O.
- Pitfalls: (1) escalar a Claude para lo barato -> usa tools locales. (2) ordenes vagas
  -> el agente pregunta al vacio. (3) asumir ids de modelo -> lista primero.
- Checklist: [x] keys fuera de logs/commits [x] rate limits [x] error handling
  [x] limpieza/monitoreo [x] docs.

### S) Roadmap (3 pasos)
1. **Probar en vivo el ahorro (operador + haiku + continue).** Por que: validar la
   reduccion real de tokens. Esfuerzo: bajo. Quien: usuario (voz) + medir con ccusage.
   Exito: una orden tipica < 30k tok.
2. **Brief persistente por proyecto.** Que: archivo compacto que Gemini mantiene y
   pasa como contexto. Por que: elimina recarga. Esfuerzo: medio. Quien: Claude.
   Exito: agentes sin onboarding, contexto < 5k.
3. **Endurecer activacion cloud (si se usa).** Que: repo privado + tope de gasto API +
   verificar sin secret. Por que: cerrar el ultimo residual. Esfuerzo: bajo. Quien:
   usuario. Exito: claude.yml solo disparable por owner, con budget.

---

## P.S. RESUMEN EJECUTIVO

1. **SKILL METADATA** - Nombre: orquestacion-gemini-claude-segura. v1.0.
   Creado 2026-07-04. Estado: Production-Ready (agentes off por defecto).
   Mantenedor: usuario (LIGEREZA) + Vibo/CODE.

2. **TOKEN ECONOMICS** - Historico medido: ~1.16M (2 agentes) + ~62M sesion (mayoria
   cache barato). Ahorro potencial en agentes: >90% via operador/contexto reducido.
   Costo: dominado por cache_leido (barato); optimizar reduce sobre todo recarga y
   errores, no tanto plata bruta. ROI: alto en fiabilidad y velocidad, medio en $.

3. **SECURITY DASHBOARD** - Criticas: 2 (key/commits, @claude abierto) -> mitigadas.
   Altas: 2 (leer_archivo, agentes de pago) -> mitigadas; injection parcial.
   Medias: 2 (mic, acceptEdits) -> mic cerrada, plan disponible. Overall: BAJO-MEDIO.
   Cumple: menor privilegio, secretos fuera de git, opt-in de capacidades caras.

4. **MODEL SELECTION** - Gemini: conversar/rutear/leer/escribir texto/preparar contexto/
   supervisar. Claude: editar codigo/entregables validados/comandos. Cloud services: no
   usado (no aplica). Delta: Gemini ~gratis vs Claude alto por recarga -> mover todo lo
   posible a Gemini.

5. **NEXT SPRINT** - P1: probar ahorro en vivo (bajo). P2: brief persistente (medio).
   P3: endurecer cloud si se activa (bajo). Inicio sugerido: proxima sesion, tras un
   push. Esfuerzo total: bajo-medio.
