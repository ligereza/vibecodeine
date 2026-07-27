# Prompt para pedir una estética nueva

Copiá todo lo que está bajo la línea y pegalo en Arena, en Google AI Studio o en
el agente que uses, **junto con** `CONTRATO.md` y `datos/ESQUEMA.md`.

Lo que devuelva va a `piel/<nombre>/` y no toca nada más.

---

Necesito la **cara visible** de un archivo de obra digital. Se llama **ISKVW**.
No es un portafolio de agencia ni un currículum: es el archivo de un artista, y
lo que importa es dejar ver la obra, no venderla.

**Leé primero los dos archivos que te paso**: `CONTRATO.md` dice qué tiene que
cumplir cualquier propuesta, y `ESQUEMA.md` dice exactamente qué datos vas a
recibir. Todo lo que muestres tiene que salir de ahí.

## Lo que NO quiero, y es lo más importante

No quiero un sitio convencional. Concretamente:

- **Nada de título arriba + menú + secciones apiladas.** Ese formato ya está
  descartado.
- Nada de "hero" con una frase grande y un botón.
- Nada de grilla de tarjetas con sombra y hover que levanta.
- Nada de scroll narrativo con animaciones de aparición.

Si tu propuesta se puede describir como "un sitio de portafolio bien hecho",
está mal. Empezá de nuevo.

## Lo que sí busco

**La interfaz puede ser parte de la obra.** La referencia que me gusta es un
instrumento corriendo, no un documento: un lienzo generativo vivo de fondo
—reacción-difusión, redes de nodos, grillas que pulsan—, secciones que se
conmutan en vez de apilarse, una barra de estado que reporta lo que realmente
está pasando, y controles que el visitante puede mover para alterar lo que ve.

No copies esa referencia: **entendé el principio**. El principio es que el
visitante entra a algo que está funcionando, no a algo que está publicado.

Otras direcciones que servirían igual, para que veas el rango: un archivo que se
explora como un mapa y no como una lista; una interfaz que se comporta como una
herramienta de trabajo real; algo que responda al gesto del visitante y cambie
según lo que toca. Cualquier cosa donde **mirar la obra sea hacer algo**, no
desplazarse.

## Reglas que no se negocian

1. **Ningún elemento puede afirmar un dato que no tiene.** Si mostrás un
   contador, que cuente de verdad. Si una obra no tiene año, no le inventes uno.
   Un número decorativo que finge medir algo es el peor error posible acá.
2. **Todo el texto visible en español correcto, con acentos y eñes.**
3. **Tiene que abrir sin internet**: sin CDN, sin fuentes remotas, sin analytics.
   Todo lo que necesite va adentro.
4. **Tiene que poder verse en un teléfono.** No igual, pero sí visible.
5. **No modifiques los datos.** Si necesitás un campo que no existe, decilo en
   tu respuesta en vez de inventarlo.

## Qué entregar

Una carpeta autocontenida con un `index.html` que se abra con doble clic y lea
`datos/obras.json`. Si usás librerías, que viajen adentro.

Y aparte, en tu respuesta: **tres o cuatro líneas explicando cuál es la idea**.
Qué es esto, por qué esta forma y no otra, y qué hace el visitante. Si no podés
explicarlo en cuatro líneas, probablemente sea decoración.
