# SEMAFORO RD — el testeo en vivo en las pantallas de la fiesta

Idea original de Vibo (2026-07-03). No es automatizacion de lo existente:
es un SERVICIO NUEVO que solo RD puede ofrecer en Chile.

## El cruce

RD tiene dos activos que nadie mas tiene JUNTOS:

1. EL DATO: el stand de testeo sabe, en tiempo real, QUE circula ESTA noche
   en ESTA fiesta (sustancias, adulterantes, pureza aparente). Hoy ese dato
   muere en el meson: le sirve solo a quien se acerca (decenas de personas).
2. LA PANTALLA: el jefe domina Resolume/Chataigne/mapping LED (el repo ya
   tiene src/flujo/resolume/automator.py) y trabaja con las productoras que
   CONTROLAN las pantallas del evento (miles de personas).

La idea: conectar 1 con 2. Los resultados anonimos y agregados del testeo
de la noche se convierten en una CAPA VISUAL EN VIVO en las pantallas de la
fiesta, con la estetica de los reactivos (los colores de marca de RD SON
colores de reactivos — la identidad ya estaba disenada para esto sin saberlo).

## CORRECCION DE SEGURIDAD (feedback del jefe, 2026-07-03) — LEER PRIMERO

El dato del testeo es PRECIADO PARA VENDEDORES y puede ser PELIGROSO en
publico: anunciar adulterantes en pantalla revela inteligencia de mercado,
puede senalar presencia de bandas o grupos rivales, y expone al equipo del
stand a represalias ("la caseta de los soplones"). Por lo tanto:

REGLA DURA: el dato de la noche NUNCA va horizontal (a la pista/publico).
Va VERTICAL, por canales controlados:

1. En el stand, persona a persona (como hoy): quien testea recibe su alerta.
2. Canal cerrado a produccion + seguridad + equipo MEDICO del evento
   (radio/grupo interno): el equipo medico NECESITA saber que circula para
   responder a emergencias — sin que la pista lo sepa. Este "briefing medico
   en vivo" es el tier vendible real: invisible para vendedores, oro para
   la produccion.
3. Observatorio LENTO: reporte agregado, anonimo y DIFERIDO (semanas,
   multi-evento) — tendencias, jamas "que paso anoche en tal fiesta".
4. Alerta publica solo en caso extremo con riesgo vital inminente, decidida
   por RD + medico + produccion EN CONJUNTO (nunca automatizada), con
   redaccion que no identifique producto ni procedencia.

La PANTALLA conserva solo la capa de PRESENCIA: visual ambient con paleta
reactivo, lema y ubicacion del stand. Marca y mision a escala de recinto,
cero datos de la noche.

## Que ve la pista (version corregida)

- Estado normal: visual ambient con paleta reactivo + lema "Si vas a
  hacerlo, reduce danos" + donde esta el stand. Marca presente, bella, VJ-grade.
- (ELIMINADO por seguridad: el takeover publico de alertas. Ver correccion
  arriba — el dato va por canal vertical cerrado, no a pantalla.)

El multiplicador corregido: la pantalla multiplica PRESENCIA y llegada al
stand; el canal medico cerrado multiplica la capacidad de respuesta.

## Por que es negocio (no solo mision)

- Tier nuevo en la cotizacion: "Servicio Completo + Semaforo RD" (pantalla
  en vivo + reporte post-evento de sustancias para la productora). La
  productora paga por seguridad visible y contenido espectacular a la vez.
- El reporte post-evento (dato agregado y anonimo) vale para productoras,
  investigacion y fondos: RD se vuelve el observatorio de sustancias de la
  escena chilena, fiesta a fiesta.
- Diferenciador absoluto: ninguna otra ONG puede venderlo; ninguna
  productora AV tiene el dato.

## Como se construye con lo que YA existe en el repo

1. Captura: form/planilla minima en el stand (sustancia, resultado reactivo,
   flag adulterante) -> JSON de la noche. (El hub ya tiene Intake.)
2. Render: generador tipo gen_dark_fronts.py que produce los overlays
   (estados normal/alerta) en la paleta reactivo -> PNG/video loop.
3. Emision: el automator de Resolume/Chataigne EXISTENTE (XML pre-flight,
   CSV OSC ya generados por automator.py) dispara la capa via OSC. El
   bloqueador historico del .noisette por fin tiene un motivo de negocio
   para resolverse.
4. Etica primero: datos 100% anonimos y agregados; solo prevencion; sin
   marcas de sustancias "seguras" (una alerta informa riesgo, jamas avala
   consumo). Revisar redaccion con el equipo RD antes del piloto.

## Piloto minimo (1 evento)

- 1 laptop con Resolume + la capa RD en una pantalla secundaria.
- Planilla manual del testeo -> alguien del equipo actualiza el JSON.
- 2 overlays pregenerados (ambient + alerta) — sin software nuevo.
- Medir: visitas al stand antes/despues de cada aparicion en pantalla.

Si el piloto funciona, se integra a flujo como receta G de la skill y se
agrega el tier a la cotizacion general.
