# SEGURIDAD del asistente de voz (CODE/VIBO/REDU) + secretario Claude

## Modelo de amenaza (lo que queremos evitar)

- Que tu cuenta de Gmail/Google quede abierta y **alguien use tu Claude de PAGO** a
  traves del puente de voz (gastando plata o tocando el repo).
- Que **dejes a VIBO escuchando sin querer** y empiece a hacer pedidos a Claude.
- Que el **microfono capte** cuando no lo sabes.
- Que Gemini (nube) lea **credenciales** (.env, llaves) o escriba fuera del repo.

## Defensas implementadas

1. **Agentes de pago APAGADOS por defecto.** `encargar_a_claude` no lanza nada de
   Claude salvo que TU pongas `VIBO_AGENTS_ENABLED=1` en el `.env`. Aunque dejen a
   VIBO escuchando, NO puede gastar tu Claude. (default = solo conversar / leer).
2. **Tope de gasto por corrida.** `VIBO_MAX_AGENTES` (15) + freno anti-bucle
   (5 ordenes / 60s) + un solo secretario a la vez.
3. **Microfono solo con la tecla.** El microfono se ABRE unicamente mientras
   mantienes F8; en reposo esta CERRADO y no captura nada.
4. **Auto-apagado por inactividad.** `VIBO_IDLE_MIN` (5 min): si dejas la app
   abierta sin usar, se cierra sola.
5. **Lectura/escritura acotada.** `leer_archivo`/`escribir_archivo` solo dentro del
   repo/proyectos y bloquean `.env`, llaves y secrets.
6. **Token GitHub de solo lectura.** Keys solo en `.env` (ignorado por git).
7. **Limpieza automatica** de agentes colgados al arrancar (sin LLM, gratis).

## PROTOCOLO OBLIGATORIO ANTES DE CERRAR UNA SESION

Correr SIEMPRE antes de dar por cerrada una sesion (cualquier agente o persona):

1. **Cerrar la voz.** Salir del asistente con ESC (no dejarlo escuchando).
2. **Matar agentes colgados.** `py tools/vibo_voz/limpiar.py` (o por voz
   "limpia procesos"). Verificar que no queden agentes de voz vivos.
3. **Confirmar agentes apagados.** Que `VIBO_AGENTS_ENABLED` quede vacio en el
   `.env` si no lo vas a seguir usando.
4. **Verificar que no se filtro nada.** `git status` limpio; ningun `.env`,
   `estado/`, `agentes/`, `proyectos.json` trackeado.
5. **Actualizar continuidad.** `context/LAST_HANDOFF.md` y
   `context/SESSION_STATE.json` con fecha/version reales.
6. **Cerrar sesiones de cuenta si es un equipo compartido.** Si la maquina no es
   solo tuya, cerrar Gmail/Google y la terminal (mata el arbol de procesos).

Sin estos 6 pasos, la sesion NO se considera cerrada.
