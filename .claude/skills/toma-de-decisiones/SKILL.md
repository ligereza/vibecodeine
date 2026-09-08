---
name: toma-de-decisiones
description: Marco para decidir COMO ejecutar una tarea cuando hay varios modelos/agentes (caros y baratos), riesgo de gasto o de seguridad, y opcion de delegar. Invocar cuando el usuario pregunte "conviene usar el modelo caro o el barato", "como ahorro tokens", "quien deberia hacer esta tarea", "cuando escalar a Claude", "es seguro dejar esto corriendo", o al disenar la division de trabajo entre Gemini/Claude/agentes. Destilada de la sesion que armo el asistente de voz CODE/VIBO/REDU + secretario Claude.
---

# Toma de decisiones: orquestar modelos y agentes con ahorro y seguridad

Marco practico para decidir quien hace que cuando conviven un modelo barato/gratis
(ej. Gemini Live) y uno caro/capaz (ej. Claude Code), con riesgo de gasto y de
seguridad. Reglas probadas, no teoria.

## 1. Principio raiz: la herramienta mas barata CAPAZ hace cada subtarea

Divide la tarea en subtareas y asigna cada una al recurso mas barato que la pueda
hacer BIEN. No pagues el modelo caro por lo que el barato hace igual.

- **Modelo barato/gratis (operador)**: conversar, rutear/clasificar, leer, resumir,
  buscar, decidir, escribir notas, monitorear, orquestar.
- **Modelo caro (ejecutor)**: mutar archivos/codigo, correr comandos/tests, producir
  entregables validados, razonamiento profundo sobre mucho contexto.

## 2. Patron operador / antesala (el mayor ahorro)

Antes de invocar al modelo caro, el barato **prepara y REDUCE el contexto** (rutas
exactas, snippets, datos) y se lo pasa masticado. El caro **confia y no re-explora**.
El costo del modelo caro suele estar dominado por CARGAR contexto, no por pensar:
reducir eso baja una orden de cientos de miles a unos pocos miles de tokens.

## 3. Verificar antes de gastar

El modelo barato pre-chequea viabilidad (existe? hace falta? es ambiguo?) ANTES de
gastar el caro. Un agente caro que arranca solo para preguntar es dinero perdido.
Los agentes de un tiro (headless) NO deben quedarse preguntando: ante ambiguedad,
eligen la opcion segura, la ejecutan y reportan que asumieron.

## 4. Seguridad primero (capacidades caras/destructivas: OFF por defecto)

- **Opt-in explicito**: lo que gasta plata o rompe cosas esta APAGADO hasta que el
  dueno lo habilite (flag en config, no por voz/accidente).
- **Topes de gasto**: maximo por corrida + freno anti-bucle (rate limit) + uno a la vez.
- **Menor privilegio**: tokens de solo lectura; lectura/escritura acotada a carpetas
  permitidas; jamas leer/escribir credenciales (.env, llaves).
- **Captura solo a demanda**: microfono/camara/escucha abiertos solo con accion
  explicita (tecla), cerrados en reposo.
- **Auto-apagado por inactividad**: nada queda "escuchando" si lo dejan abierto.
- **Reversibilidad**: todo cambio queda en git; cambiar las REGLAS del sistema exige
  revision (diff) + reinicio, y los propios agentes no pueden reescribir sus limites.

## 5. Anti-bucles

Un ejecutor a la vez; limite de N ordenes por ventana; agentes de un tiro que hacen
la tarea UNA vez y terminan sin invocar a otros. Limpieza automatica (gratis, sin
LLM) de procesos abandonados al arrancar.

## 6. Escuchar/vigilar sin loop (sin quemar tokens)

Para "revisar estado" no pongas al LLM en loop (paga cada ciclo). Usa artefactos:
procesos/hooks que escriben un archivo de ESTADO gratis, y el LLM solo LEE bajo
demanda cuando preguntas. Evento, no polling.

## 7. Honestidad de costo y de capacidad

- Reporta el gasto real (tokens/plata) sin maquillar; distingue tokens caros de los
  baratos (cache).
- No sobre-delegues al modelo menos fiable: si prepara mal el contexto, el modelo caro
  ejecuta lo equivocado con confianza. Delegar de mas cuesta en ERRORES, no en tokens.

## Checklist rapido para decidir

1. Puede hacerlo el modelo barato bien? -> hazlo ahi.
2. Necesita mutar archivos/codigo/correr comandos? -> solo ahi el modelo caro.
3. Antes de llamar al caro: junte y reduje el contexto? verifique viabilidad?
4. La capacidad cara esta con opt-in, tope y menor privilegio?
5. Hay freno anti-bucle y limpieza de lo abandonado?
6. Al cerrar: corri el protocolo de cierre (apagar, limpiar, no dejar escuchando)?
