# La Fabrica Autonoma — vision grande de flujo

Pedido del jefe (2026-07-03): "piensa en grande, no labores enanas".

## La tesis

flujo ya no es una carpeta con scripts: es una FABRICA con 5 estaciones.
Cuatro existen. Falta una. Cuando se cierre el circuito, RD produce piezas,
cotizaciones y catalogo COMPLETO sin nadie frente a un PC — el humano solo
firma (aprueba PRs) y cobra.

```txt
1. CAPTACION    correo "Suplementos - X" -> issue automatico   [EXISTE]
2. PRODUCCION   @claude en el issue -> Vibo genera con la      [EXISTE - activar
                skill entregas-rd en un runner de GitHub        app + API key]
3. CALIDAD      molde CI (validar-piezas.yml): nada invalido   [EXISTE]
                entra a main. Revision sin revision.
4. MEMORIA      handoffs + skill: cada sesion hereda todo      [EXISTE]
5. VITRINA      el repo SE PUBLICA SOLO como catalogo web      [SE CONSTRUYE HOY]
                publico: galerias crema/dark + cotizacion
                con URL enviable a cualquier productora
```

## La estacion 5: publicar-catalogo.yml

GitHub Pages gratis: cada merge a main despliega automaticamente
https://<usuario>.github.io/vibecodeine/ con:
- Galeria crema (preview_flyers.html) y dark (preview_flyers_dark.html)
- Cotizacion general (crema y dark) lista para reenviar como LINK
- Los SVG servidos directo (la imprenta descarga el vectorizado con 1 click)

Consecuencia: el manager de la agencia no recibe un PDF adjunto — recibe
UNA URL siempre actualizada. Cada mejora al repo actualiza la vitrina sola.

OJO: Pages hace publico lo publicado (solo material de marketing; datadrops
sensibles NO se copian). Activar en Settings > Pages > Source: GitHub Actions.

## El ciclo completo cerrado (dia tipo, PC apagado)

```txt
09:00 llega correo de productora        -> issue [EVENTOS] solo
09:01 Apps Script menciona @claude      -> Vibo despierta en GitHub
09:07 PR con la pieza/cotizacion        -> molde CI verde
09:10 GitHub te avisa por email         -> apruebas desde el telefono
09:11 merge a main                      -> la vitrina se republica sola
09:12 respondes el correo con la URL    -> fin. 12 minutos, cero PC.
```

## La jugada mayor (siguiente horizonte)

Esta fabrica no es solo de RD. Correo -> issue -> agente -> pieza validada
-> catalogo publicado es un SISTEMA OPERATIVO CREATIVO que cualquier
productora, sello o marca chica pagaria por tener. RD puede ser el caso de
exito y flujo el producto licenciable: "tu estudio de diseno que trabaja
mientras duermes". El repo ya es el demo.

## TODO (orden de encendido)

1. [ ] Aplicar airdrop v9 + push (tu unica accion manual pendiente)
2. [ ] Activar escritura en claude.ai/code + app Claude GitHub + API key
3. [ ] Activar GitHub Pages (Settings > Pages > GitHub Actions)
4. [ ] Issue de prueba con @claude -> validar el ciclo entero
5. [ ] Fase 3: Apps Script agrega @claude al crear el issue (cero clicks)
6. [ ] Horizonte: cotizador self-service en la vitrina (form -> PDF) y
       flujo como producto para terceros
