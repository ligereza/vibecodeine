# Checkpoint — Flujo relay entre múltiples IAs

Fecha: 2026-06-12

## Resumen

Se agregó un flujo para navegar entre varias IAs sin repetir contexto completo y sin depender de que los chats web se conecten directamente entre sí.

## Decisión

No intentar conectar dos pestañas de chat web de forma invasiva. Usar un modelo relay:

```txt
Repo/checkpoints = memoria común
Chat A = director/planificador
Chat B = especialista/crítico
Humano = productor final
Scripts = preparan handoffs
```

## Archivos creados

- `docs/MULTI_IA_RELAY.md`
- `scripts/start_ai_relay.sh`

## Comando nuevo

```bash
bash scripts/start_ai_relay.sh "nombre del caso"
```

Crea una sesión en:

```txt
_relay_sessions/FECHA_nombre/
```

con prompts y archivos para respuestas.

## Próximo paso

Probar con un caso real:

```bash
bash scripts/start_ai_relay.sh "revision portfolio-auto"
```

Usar Chat A como productor técnico y Chat B como especialista visual/técnico.
