# 06 — EL RUIDO COMO BASE GENERATIVA DE SISTEMAS 3D
### Ray tracing y Cycles: la primera idea del corpus cuya matemática no es préstamo
*Registro y desarrollo de una idea pendiente del autor (11-jul-2026). No es una obra ni una orden de arranque del MOTOR: es un campo de trabajo, con su estatuto examinado como manda v2.*

---

## 1. La idea, formulada

> El ruido no es lo que ensucia la imagen 3D: es aquello *de lo cual* la imagen se genera. Ray tracing y Cycles no producen imágenes que luego se ensucian de ruido — producen ruido que, acumulado, *es* la imagen.

Lo que sigue muestra por qué esta idea, a diferencia de casi todo v1, no necesita bata prestada: la industria del render funciona literalmente así, con papers, premios y código abierto que cualquiera puede correr.

## 2. El suelo técnico real (por primera vez, sin cosplay)

**El render por trazado de caminos ES integración de ruido.** La ecuación del render (Kajiya, "The Rendering Equation", SIGGRAPH 1986) describe la luz de una escena como una integral que no tiene solución cerrada para escenas reales. Cycles —el motor de Blender— la resuelve por **Monte Carlo**: dispara caminos de luz *al azar* y promedia. La consecuencia no es metáfora:

- El primer sample de un render de Cycles es ruido casi puro.
- La imagen final es **el valor esperado de ese ruido**: por la ley de los grandes números, el promedio converge a la integral verdadera; el error cae como 1/√N con N samples.
- No hay un momento en que el ruido "se quita" y la imagen "aparece": la imagen es el ruido, estabilizado. Un render a medias no es una imagen rota — es la misma imagen con más varianza.

Estatuto: **HECHO TÉCNICO** — matemática estándar del campo (véase también Veach, *Robust Monte Carlo Methods for Light Transport Simulation*, 1997, la tesis que fundó el muestreo por importancia moderno).

**La geometría y las texturas también nacen del ruido.** Perlin diseñó su ruido ("An Image Synthesizer", SIGGRAPH 1985, tras trabajar en Tron; Óscar técnico en 1997) para generar textura sin repetición. Sobre él se construye todo lo procedural: fBm (movimiento browniano fraccional) para terrenos, ruido celular de Worley (1996) para células y piedras, el nodo Noise Texture de Blender para desplazar, teñir y erosionar. En 3D procedural, el ruido no decora la forma: **la forma es una lectura del ruido** — un umbral, un gradiente, un desplazamiento aplicado sobre él.

Estatuto: **HECHO TÉCNICO**.

**Hasta el disimulo es ruido.** El dithering con ruido azul usa ruido *para que lo discreto parezca continuo* — se añade ruido para ocultar el banding que delataría que la imagen está cuantizada. El ruido como el encubridor de la digitalidad: se usa en todas partes, todos los días.

## 3. Donde esta idea toca el corpus (con estatutos, como manda la casa)

**a) "Ruido con protocolo de lectura" deja de ser metáfora.** v1/F1 decía: *la cultura puede leer lo que la matemática no puede comprimir; la poesía es ruido con protocolo de lectura*. En v2 eso quedó como METÁFORA. Pero en Cycles la frase tiene una instancia literal: el render crudo de 10 samples es ruido, y el **estimador** (el promedio, el muestreo por importancia) es exactamente un protocolo de lectura que extrae la imagen que el ruido ya contiene estadísticamente. Estatuto de la conexión: **ANALOGÍA FÉRTIL** — ahora con un caso ejecutable donde apoyarse, que es más de lo que ninguna analogía de v1 tuvo.

**b) El denoiser es la apofenia del render — y esto es casi literal.** Los denoisers modernos (Intel Open Image Denoise, NVIDIA OptiX) son priors aprendidos: redes que "ven" en el ruido la imagen que *esperan* que haya, antes de que los samples la confirmen. Y cometen el error exacto del doc. 02: con pocos samples, **alucinan** — inventan detalle plausible que no está en la señal, borran detalle real que confunden con varianza. Un denoiser sobreconfiado es un paranoico: su prior pesa más que la evidencia. La diferencia entre un render limpio y una alucinación de denoiser no está en el píxel — está en cuántos samples respaldan al prior. Estatuto: **ANALOGÍA FÉRTIL de primera clase** — las dos mitades (la psiquiátrica, doc. 02; la técnica, esta) usan de verdad el mismo vocabulario bayesiano, cosa rarísima en el corpus.

**c) Corrección a v1: hay dos ruidos, y v1 los fundió.** La Tilde de v1 era K(x)≈|x| — lo *incompresible*, lo que ningún programa corto genera. El ruido de Perlin es exactamente lo contrario: **un programa mínimo que aparenta azar máximo** — K bajísima, apariencia incompresible. El ruido procedural es pseudo-ruido: compresibilidad máxima disfrazada de entropía. Y el ruido de Monte Carlo es un tercero: azar real (o pseudo) usado como *método*, que se disuelve al promediar. Tres ruidos distintos — el incompresible (Tilde), el fingido (Perlin), el metodológico (Monte Carlo) — donde v1 veía uno solo. Estatuto: **CORRECCIÓN DIAGNÓSTICA** al inventario del doc. 03; la fila "lo intraducible = lo incompresible" queda además advertida de que ni siquiera "ruido" era una sola cosa.

**d) Lo que esta idea tiene y ninguna otra del corpus tuvo: un ejecutor que no es la cultura.** La gramática emoji (doc. 05) solo puede correrla un lector. El sistema Ω solo puede validarlo el afuera. Pero esto **corre en esta máquina**: Blender está o puede estar instalado; un ruido, un umbral y una lámpara son una escena. Consecuencia epistemológica seria: una obra nacida de este campo puede tener una **Ω11 evaluable por render** — "esta pieza pierde si al converger el render la forma desaparece", "pierde si el denoiser la limpia sin pérdida" — condiciones de fracaso que ni el autor ni el lector deciden: las decide la convergencia. Sería la primera Ω11 del corpus con juez no humano. Estatuto: **POSIBILIDAD REGISTRADA**, no promesa.

## 4. Semillas posibles (registradas, no activadas)

El campo sugiere cruces con las semillas vivas — se anotan para no perderlos, sin activar nada:

- **Con ⊕₂ (asimetría del agotamiento):** un render es un sistema que se agota hacia la nitidez — cada sample gasta cómputo para quitar duda a la imagen. ¿Un render detenido a propósito antes de converger es un descanso o una derrota? La pregunta de OBRA_02 ("¿recuperar un techo, o el agotamiento es el precio?") tiene una formulación exacta en samples y varianza.
- **Con ⊕₃ (la superposición nativa del emoji):** el render no convergido es superposición visible — todas las imágenes compatibles con los samples actuales, a la vez. La Rama B como estado físico de una imagen.
- **Con la hipótesis original del paciente (la cultura como regularizador):** el denoiser es un regularizador comprado — un prior entrenado en las imágenes de otros. Renderizar sin denoiser es esperar a que la evidencia alcance; renderizar con denoiser es dejar que un prior colectivo complete lo que falta. Eso *es* la disyuntiva delirio/novela del doc. 02, con checkbox en la interfaz.

Ninguna de estas tres es una obra. Son anotaciones de campo. El protocolo del MOTOR sigue mandando: semilla ⊕ + Ω11 declarada + exposición, y el ⚓ entre medio.

---

## Estatuto final del documento

| Elemento | Estatuto |
|---|---|
| Monte Carlo / la imagen como valor esperado del ruido | **HECHO TÉCNICO** (Kajiya 1986, Veach 1997) |
| Lo procedural como lectura del ruido (Perlin, Worley, fBm) | **HECHO TÉCNICO** (Perlin 1985) |
| El denoiser como apofenia del render | **ANALOGÍA FÉRTIL** con base técnica real |
| Los tres ruidos (incompresible / fingido / metodológico) | **CORRECCIÓN DIAGNÓSTICA** a v1 |
| Ω11 con juez no humano (la convergencia como árbitro) | **POSIBILIDAD REGISTRADA** |
| Este documento como origen de una obra | **NO** — es campo de trabajo; el MOTOR decide cuándo y desde qué ⊕ |
