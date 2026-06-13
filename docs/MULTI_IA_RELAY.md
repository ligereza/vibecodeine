# Flujo — Relay entre múltiples IAs

Fecha: 2026-06-12

## Objetivo

Permitir trabajar con dos o más chats de IA en paralelo sin que todo dependa de repetir manualmente el contexto completo.

La idea no es conectar chats web de forma invasiva ni saltarse límites. La idea es usar un repositorio/carpeta como memoria compartida y crear paquetes de handoff entre IAs.

---

## Respuesta corta

No existe una forma universal, estable y segura de conectar dos chats web gratuitos en pestañas distintas para que hablen solos entre sí.

Lo que sí se puede hacer:

1. Usar APIs oficiales cuando existan.
2. Usar un repo/carpeta como memoria compartida.
3. Crear paquetes de ida/vuelta entre IAs.
4. Automatizar apertura de pestañas y preparación de prompts.
5. Mantener humano-en-el-loop para enviar, revisar y aprobar.

---

## Modelo recomendado

```txt
Repo/checkpoints = memoria común
Chat A = Director / planificador
Chat B = Crítico / especialista / optimizador
Humano = productor final que aprueba
Scripts = preparan contexto, prompts, paquetes y checkpoints
```

---

# Flujo relay manual-asistido

## 1. Crear sesión relay

```bash
bash scripts/start_ai_relay.sh "nombre del caso"
```

Esto crea una carpeta:

```txt
_relay_sessions/FECHA_nombre-del-caso/
├── 00_SHARED_CONTEXT.md
├── 01_CHAT_A_DIRECTOR_PROMPT.md
├── 02_CHAT_B_SPECIALIST_PROMPT.md
├── 03_RESPONSE_CHAT_A.md
├── 04_RESPONSE_CHAT_B.md
├── 05_SYNTHESIS.md
└── README.md
```

## 2. Chat A: Director

Chat A lee el contexto y produce:

- diagnóstico
- preguntas
- plan
- qué debe revisar Chat B
- paquete para Chat B

## 3. Chat B: Especialista

Chat B recibe:

- contexto resumido
- respuesta de Chat A
- tarea específica

Y produce:

- crítica
- mejoras
- riesgos
- cambios accionables

## 4. Síntesis

El humano o una tercera IA sintetiza:

```txt
Respuesta A + Respuesta B > plan final > checkpoint
```

---

# ¿Cómo evitar que cada chat espere tanto al usuario?

No se puede eliminar completamente al usuario en chats web gratuitos sin automatizar interfaces de forma frágil. Pero sí se puede reducir el trabajo humano a:

```txt
copiar paquete preparado > pegar/enviar > copiar respuesta > guardar
```

El resto lo hacen scripts y plantillas.

---

# Modo más autónomo usando APIs oficiales

Si tienes acceso a APIs gratuitas o free-tier:

```txt
Local orchestrator
> Modelo A API
> Modelo B API
> Guarda respuestas
> Genera síntesis
> Commit/checkpoint
```

Ventajas:

- real conexión entre modelos
- sin depender del DOM del navegador
- reproducible
- menos manual

Desventajas:

- free tiers cambian
- requiere claves/API keys
- cuotas limitadas
- no todos los modelos potentes están gratis

---

# Modo no recomendado

Automatizar chats web con Playwright/Selenium para:

- logins automáticos
- enviar prompts solos
- cambiar cuentas
- saltar cuotas
- resolver captchas
- scraping intensivo

Riesgos:

- bloqueo de cuentas
- errores por cambios de interfaz
- exposición de sesión/cookies
- incumplimiento de términos
- resultados difíciles de auditar

---

# Roles sugeridos

## Chat A — Director técnico

Lee contexto completo y decide qué hacer.

Salida:

```txt
Plan
Prioridades
Preguntas
Paquete para especialista
```

## Chat B — Especialista visual/técnico

Recibe tarea acotada.

Salida:

```txt
Crítica
Optimización
Riesgos
Pasos concretos
```

## Chat C opcional — Sintetizador

Combina ambas respuestas y genera checkpoint.

---

# Regla principal

No intentes que todas las IAs sepan todo. Haz que cada IA reciba un paquete pequeño y un rol claro.

```txt
Menos contexto repetido
+ mejor handoff
+ respuestas más útiles
+ menos cuota gastada
```
