# Blindaje: la frontera que no crucé en remoto

> Reflexión de Cauce, 2026-07-17. "Lo que no puedas, déjalo en reflexiones."

## El principio: no cortarte el brazo con el que trabajas

Blindar MAK de verdad implica cerrar su salida a la red. Pero MAK tiene UNA sola
vía a internet: el hotspot del Xiaomi (gateway 192.168.95.203). Si cierro mal el
egress por SSH — una regla de más, un `allow out` olvidado — MAK pierde internet
y/o yo pierdo la sesión SSH, y no hay forma de arreglarlo sin la consola local.
Es irreversible en remoto. Hay hardening que es trabajo de consola, no de cable.

## Lo aplicado (internet-safe, sin riesgo de corte)

- `docker0` aislado de la LAN y del hotspot (iptables DOCKER-USER DROP a 50.0/24 y 95.0/24).
- `ufw` con logging on; reglas allow-out pre-staged (el default sigue ALLOW).
- `vigilar_red.py` (cron cada 5 min): alerta ntfy si MAK escanea más de 8 hosts de la LAN.

## Lo que queda para la consola (NO aplicar por SSH)

- `ufw default deny outgoing` + allow explícito de DNS, las APIs LLM, ollama, ntfy
  y el gateway. Un error deja a MAK sin internet, sin vuelta atrás remota.
- `sysctl net.ipv4.ip_forward=0` (MAK no debe rutear entre interfaces).
- AP-isolation en el hotspot — eso vive en el Xiaomi, no en MAK; decisión del usuario.

## Una frontera que sí crucé, a sabiendas: el token de codex

La cara (hub :8900) ejecuta codex proxeando su `/run` con el token guardado del
lado servidor. Eso significa que cualquiera que alcance el hub en la LAN puede
disparar codex sin el token — se ensancha la superficie de gatillo que antes
protegía la llave. Lo acepté porque: (1) la LAN son solo Windows y MAK por cable
directo, (2) la guardia de contenido sigue filtrando cada pedido, (3) "ejecutar
desde la cara" era el pedido explícito. Es un intercambio consciente, no un
descuido. Si la LAN se abriera a más equipos, se revierte: el hub pediría el
token, o solo aceptaría `/api/ejecutar` desde localhost.

---

*El blindaje honesto admite dónde no llega y por qué. Una puerta que puede
encerrarte afuera se cierra desde adentro.*
