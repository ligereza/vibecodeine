---
name: orquestacion-gemini-claude
description: Patron probado para montar un asistente donde un modelo barato/gratis (Gemini) actua como operador/capataz por voz y delega solo lo caro a Claude Code (ejecutor), con seguridad opt-in, contexto reducido y anti-bucles. Invocar al construir un puente voz->agente, un sistema multi-modelo caro/barato, un bridge headless a Claude CLI, o al querer bajar el gasto de tokens de agentes delegando la preparacion de contexto a un modelo barato. Destilada del asistente de voz CODE/VIBO/REDU de este repo (tools/vibo_voz).
---

# Orquestacion Gemini (operador) + Claude (ejecutor)

Como montar un asistente donde el modelo barato manda y el caro solo ejecuta.
Referencia viva: `tools/vibo_voz/` (voz Gemini Live + bridge a Claude CLI).

## Description
Gemini (Live API, gratis) conversa por voz, rutea, lee/escribe texto, prepara y
REDUCE contexto, y supervisa/limpia procesos. Claude Code (de pago) se invoca
headless (`claude -p`) SOLO para editar codigo/archivos o correr comandos, y recibe
el contexto ya masticado para no re-explorar el repo. Todo lo caro esta apagado por
defecto.

## Strengths
- Voz natural en tiempo real (Gemini Live native-audio).
- Delegacion barata: el 90% del trabajo (leer, decidir, resumir, notas) es gratis.
- Ahorro por contexto: pasar contexto reducido baja una orden de ~500k a ~5-20k tok.
- Seguro por defecto: agentes de pago off, tope de gasto, anti-bucle, menor privilegio.
- Auditable: bitacora ESTADO + logs por agente, sin loops que quemen tokens.

## Weaknesses
- Gemini puede preparar mal el contexto -> Claude ejecuta lo equivocado con confianza.
- native-audio da error 1007 intermitente (mitigar con reconexion; o usar modelo Live no-audio).
- Agentes headless son de un tiro: no dialogan (deben elegir lo seguro y reportar).
- Requiere el CLI de Claude instalado/logueado localmente.

## Security Posture
- Vulnerabilidades criticas: 2 (key en git, @claude abierto en Actions) -> mitigadas.
- Altas: 2 (lectura de credenciales, agentes de pago) -> mitigadas; injection parcial.
- Residuales: 3 (acceso fisico al .env, acceptEdits autonomo, tier free de datos).
- Risk score: BAJO-MEDIO (con agentes off por defecto).

## Token Efficiency
- Promedio por orden sin operador: ~500k tok (recarga de contexto del repo).
- Con operador + preambulo "no onboarding" + tools locales: ~5-20k tok.
- Ahorro potencial: >90% en ordenes de agente.
- Nota: gran parte del gasto bruto es cache_leido (~10x mas barato); optimizar reduce
  sobre todo recarga y errores.

## Model Recommendations
- Conversar / rutear / decidir: **Gemini**.
- Leer / resumir / buscar / guardar texto: **Gemini** (tools locales).
- Preparar y reducir contexto para delegar: **Gemini (operador)**.
- Editar codigo / entregable validado / correr tests/comandos: **Claude**.
- Automatizacion desatendida en la nube: **Claude Actions** solo si repo privado +
  tope de gasto + gate por autor.

## Architecture Diagram
```
   Voz (F8) ─► Gemini Live ── VIBO (cara) / CODE (nucleo) / REDU (trabajo ONG)
                   │  tools baratos: leer/escribir_archivo, existe, ESTADO,
                   │                 listar/supervisar/limpiar_procesos
                   │  (resuelve gratis lo que puede)
                   ▼  solo si hay que editar/correr codigo:
             OPERADOR: junta y REDUCE contexto
                   ▼
        encargar_a_claude(instruccion, contexto)   [OFF por defecto]
                   ▼
             claude -p (headless, en la carpeta del proyecto)
                   ▼   deja "empezo/termino" en ESTADO
             Gemini lee el resultado ─► te lo dicta por voz
```

## Common Pitfalls
- Escalar a Claude para algo barato (guardar un texto) -> usa `escribir_archivo`.
- Ordenes vagas -> el agente headless pregunta al vacio y desperdicia una corrida.
- Asumir el id del modelo Live -> lista primero (`list_models.py`).
- Dejar el LLM en loop para "vigilar" -> usa artefactos/hooks que escriben ESTADO gratis.
- Dejar los agentes de pago habilitados o el mic abierto -> off por defecto, mic solo con tecla.

## Integration Checklist
- [ ] API keys en .env (gitignored), nunca en codigo/logs.
- [ ] Token de servicio de solo lectura; escritura/kill acotados.
- [ ] Capacidades caras/destructivas OFF por defecto (opt-in explicito).
- [ ] Rate limit + tope por sesion + un ejecutor a la vez (anti-bucle).
- [ ] Error handling: reconexion ante fallos del modelo, no traceback.
- [ ] Contexto reducido por el operador antes de delegar.
- [ ] Monitoreo/limpieza sin loop (ESTADO + limpieza al arrancar).
- [ ] Protocolo de cierre (apagar voz, matar colgados, no dejar escuchando).
- [ ] Docs + auditoria al dia.
