---
name: verificar-antes-de-negar
description: >
  Protocolo para actualizar/verificar un dato antes de afirmar que algo "no existe",
  "no se puede" o "no funciona" -- sobre todo flags de CLI, comandos, modelos, precios,
  features o cualquier cosa que cambia despues del knowledge cutoff. El conocimiento del
  modelo es viejo; el repo y las tools evolucionan. Invocar cuando el usuario diga
  "verifica", "actualiza esa info", "eso ya existe", "estas seguro?", "revisa la version
  real", o cuando estes a punto de negar la existencia de una feature/comando/opcion, o
  cuando un sub-agente reporte "no existe" sobre algo que el usuario afirma con version o
  fecha concreta. Destilada del incidente teleport (2026-07-10): Claude nego 3 veces que
  `claude --teleport` existiera; era real (docs oficiales + `claude 2.1.206 --help`), o
  antes de declarar "hecho", "confirmado", "funciona", "OK" sin medicion adjunta
  (verificar-antes-de-afirmar).
---

# Verificar antes de negar: no afirmar "no existe" desde memoria vieja

Regla base: **el knowledge cutoff es una fuente vencida.** CLIs, flags, modelos,
precios y features cambian cada semana. Afirmar "eso no existe / no se puede" desde
memoria de entrenamiento es la forma mas cara de equivocarse: quema tokens del usuario
en una discusion, y encima tiene razon el.

## 1. El anti-patron que dispara esta skill

Vas a decir alguna de estas frases sobre algo tecnico que puede haber cambiado:

```txt
"eso no existe"          "no hay tal flag"       "no se puede"
"no esta soportado"      "estas confundiendo"    "las X y las Y son separadas"
```

STOP. Antes de escribirla, corre el protocolo. NO la escribas sin verificar.

## 2. Prioridad de fuentes (de mas a menos confiable AHORA)

1. **La tool/binario real, en vivo.** `claude --help | grep -i <flag>`,
   `<cli> --version`, correr el comando y ver el error real. Fuente de verdad #1.
2. **Docs oficiales en vivo** via WebFetch de la URL canonica (no de memoria).
3. **La afirmacion fechada/versionada del usuario.** Si dice "en 2.1.206, hoy, segun
   los docs" -> pesa MAS que tu memoria. El vio la version nueva; tu no.
4. **Tu memoria de entrenamiento.** La MAS vieja. Ultimo lugar, no primero.
5. **Un sub-agente que "leyo los docs".** Puede haber leido un slice viejo o parcial
   (paso en el incidente teleport). Su "no existe" NO cierra el tema; verificalo tu
   contra (1) o (2).

## 3. Protocolo (en orden, para al primer SI)

```bash
# a) el binario mismo (lo mas barato y definitivo)
<cli> --version
<cli> --help 2>&1 | grep -iE "<termino>|<sinonimo>"

# b) si no hay binario o el help es ambiguo: docs oficiales EN VIVO
#    (WebFetch de la URL canonica; NO cites de memoria)

# c) si (a) y (b) confirman -> el usuario tenia razon, dilo y da el comando
# d) si ambos lo niegan de verdad -> reporta QUE consultaste y su version/fecha,
#    no solo "no existe" a secas
```

## 4. Regla de oro con el usuario

Si el usuario da un dato **especifico + fechado + con version** ("`--teleport`, CLI
2.1.206, 2026-07-10, docs oficiales") y tu instinto dice "no existe":

- El falso negativo casi siempre es TUYO, no del usuario.
- No repitas la negacion. Verifica en vivo (seccion 3) y, si confirma, **reconoce el
  error claro y da el comando/dato correcto.** Sin rodeos ni "pero tecnicamente".
- Si tras verificar en vivo de verdad no existe, muestra la evidencia concreta
  (output de `--help`, version, URL) -- no una afirmacion pelada.

## 5. Cierre: dejar el dato actualizado

Si descubriste que un dato tuyo estaba vencido y es probable que otro modelo lo repita:

- Ofrece capturarlo donde toque: una skill nueva/actualizada en `.claude/skills/`,
  una nota en `context/LAST_HANDOFF.md`, o el changelog de `src/flujo/version.py`.
- Asi el proximo agente (web o local, caro o gratis) no vuelve a quemar tokens del
  usuario en la misma discusion ya resuelta. Es la regla del runway aplicada a los
  hechos, no solo al codigo.

Fuente del incidente: sesion 2026-07-10 (alineacion plano PACKS + teleport). Ver la
skill hermana `teleport-sesion-web` para el caso concreto que origino esta.

## Simetrico: verificar antes de AFIRMAR

El mismo protocolo aplica al falso POSITIVO. Antes de escribir "hecho",
"funciona", "confirmado", "OK", "ya esta listo": adjunta la medicion
(output de comando, test verde, tamano/timestamp de archivo, ojo del
usuario). Sin medicion, la frase esta prohibida. Casos reales: render
entregado como OK que salio celeste plano; "corte de bateria confirmado"
que era falso. Un positivo no ganado es tan caro como un negativo no
ganado.
