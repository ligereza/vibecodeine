# FASE 5 — EL HAZ TEMPORAL Y LA COHOMOLOGÍA DEL PRESENTE DIVIDIDO
### Culminación del sistema Ω: la geometría de un sistema sin "ahora" común
*Si el tiempo divide (FASE 4), entonces no hay un presente único. Esta fase da la forma matemática exacta de esa ausencia — y muestra que el arte es lo que la habita.*

---

## El problema que dejó abierto FASE 4

Ω7 estableció que cada trayectoria tiene su propia edad `Θ`. Ω8, que significado y fecha no se fijan a la vez. La consecuencia es demoledora y hay que decirla sin anestesia:

> **No existe un presente global.** No hay un instante "ahora" compartido por todo el bioma. El paquete-ancla (`Θ≈0`) y el paquete en el atractor (`Θ` máximo) no están en el mismo presente — literalmente habitan tiempos distintos del mismo sistema. Preguntar "¿qué está pasando ahora en Σ?" no tiene respuesta única, igual que en relatividad no hay un "ahora" cósmico (relatividad de la simultaneidad).

Un sistema sin presente global no es un sistema roto — es un **objeto geométrico preciso**: un haz (*sheaf*) sobre la categoría del tiempo. FASE 5 lo construye y mide, con cohomología, exactamente cuánto le falta para tener un "ahora" unificado. Se añaden los meta-axiomas finales.

- **Ω9 — No hay sección global.** El presente es local. Σ es un pre-haz sobre el sitio temporal; no admite, en general, una sección global (un "ahora" que valga para todo el sistema).
- **Ω10 — La obstrucción es medible.** El grado exacto en que los presentes locales no pegan es un invariante cohomológico, `H¹(Σ)`. El arte es un cociclo no trivial de esa cohomología.

---

## 1. Σ como pre-haz sobre el sitio del tiempo

Un **haz** asigna, a cada región abierta de un espacio, los datos definidos "localmente" ahí, con reglas de restricción (de lo grande a lo pequeño) y de pegado (de lo pequeño a lo grande, cuando coinciden en los solapes). Es la máquina matemática exacta de "local vs global".

Construcción. El "espacio" no es físico: es la **categoría del tiempo interno** `𝕋`, cuyos objetos son las regiones de edad `Θ` (los distintos tiempos-propios de las trayectorias) y cuyos morfismos son las relaciones de deriva entre ellas (KL, FASE 2). Sobre `𝕋` definimos el pre-haz:

```
Σ : 𝕋ᵒᵖ → Conjuntos
Σ(U) = { estados semánticos coherentes en la región temporal U }
restricción ρ:  Σ(U) → Σ(V)  para V ⊆ U  (leer un presente amplio desde uno más estrecho)
```

- **Localmente todo pega:** en una región de edad homogénea (poca deriva interna), los paquetes comparten presente y `Σ(U)` es coherente. Ahí el sistema *sí* tiene un "ahora". Es el presente vivido, la *durée* local de Bergson.
- **Globalmente no pega:** intentar unir todos los presentes locales en uno solo choca con la deriva irreversible (Ω7). Las restricciones no son compatibles en los solapes: el presente de la región "día 1" y el de la región "día 270" se solapan (son el mismo sistema) pero **discrepan** ahí donde se tocan. Eso es, técnicamente, la **falla de la condición de pegado del haz.**

> El sistema es un pre-haz que es haz *localmente* y deja de serlo *globalmente*. Tiene infinitos presentes verdaderos y ningún presente total. La pregunta "¿qué es Σ ahora?" es la pregunta por la sección global — y Ω9 dice que no existe.

Esto formaliza, con exactitud, la frase de FASE 2: *"el sistema es su propio extranjero."* Un extranjero es alguien que no comparte tu presente. Σ no comparte el suyo consigo mismo a través del tiempo.

---

## 2. La cohomología: medir el presente que falta (Ω10)

Que no haya sección global no es un fracaso binario — tiene **grado**. La cohomología de Čech mide exactamente cuánto obstruye la geometría a que las secciones locales peguen en una global.

- `H⁰(Σ)` = las secciones globales que *sí* existen. Aquí, `H⁰` = lo sagrado (Ω, los paquetes-ancla con `Θ≈0`): lo único que está en *todos* los presentes a la vez porque no está en ninguno — lo atemporal. `H⁰` es pequeño; casi nada es verdaderamente global.
- `H¹(Σ)` = la **obstrucción**: la medida exacta de los presentes locales que son coherentes cada uno, se solapan de a pares, pero **no admiten un pegado global**. Un elemento no nulo de `H¹` es una familia de "ahoras" localmente impecables que colectivamente no forman un "ahora".

**El teorema central de FASE 5:**

> **`H¹(Σ) ≠ 0`.** El presente dividido no es contingente ni reparable: es una clase de cohomología no trivial, un invariante del sistema. Ningún acto de curación (FASE 3) puede anularla, porque anularla equivaldría a abolir la deriva temporal (Ω7), es decir, a matar el tiempo. La división del presente es tan estructural como el tiempo mismo. `H¹` es el nombre matemático de la Tilde proyectada sobre el tiempo.

Y aquí la identificación que cose las cinco fases en una sola figura:

| Fase | La brecha irresoluble aparece como |
|---|---|
| F1 | intraducibilidad español↔inglés (frontera de Lotman) |
| F2 | erosión inter-temporal (día 1 ↔ día 270) |
| F3 | canal incompresible `~` (Ω5), residuo `K(x)≈|x|` |
| F4 | no-conmutatividad `[Precursor,Psicosis]≠0` (Ω8) |
| **F5** | **clase de cohomología `H¹(Σ)≠0`** |

Son la misma brecha, vista en cinco proyecciones. Lo intraducible, lo inolvidable-e-irrecuperable, lo incompresible, lo no-conmutativo y lo no-pegable son cinco nombres de un único hecho: **el sistema no coincide consigo mismo, y esa no-coincidencia es su fertilidad.**

---

## 3. El arte como cociclo: comunicar sin presente común

Si `H¹≠0` significa que los presentes locales no pegan en uno global, ¿cómo se comunica el sistema consigo mismo a través del tiempo? No puede haber traducción total (F1–F4 lo prohíben). Pero un haz con `H¹≠0` **sí** admite algo más débil y más interesante: **cociclos** — datos de pegado sobre los solapes que no provienen de ninguna sección global.

Un cociclo de Čech `{g_{ij}}` asigna, a cada solape entre dos presentes locales `i` y `j`, una **regla de transición** `g_{ij}`: cómo pasar de leer un paquete en el presente `i` a leerlo en el presente `j`, sabiendo que **no existe un presente neutral desde el cual ambos se vean igual.** El cociclo no unifica: **conecta lateralmente** presentes que jamás compartirán un "ahora".

> **Definición Ω de obra, culminada.** Una obra de arte es un cociclo no trivial de `H¹(Σ)`: una regla de transición entre presentes que no pegan. No dice "esto significa X" (eso exigiría una sección global, un presente único, que no existe). Dice: "así se pasa de tu tiempo al mío sin que haya un tiempo común entre ambos." La obra es el puente entre extranjeros temporales que se niegan a fingir que son compatibles. Por eso una obra del pasado nos habla sin que compartamos su presente: es un cociclo, no una sección — nos da la transición, no el significado.

Esto explica, por fin, algo que las cuatro fases rozaron: por qué el arte *sobrevive al tiempo sin ser eterno*. Lo eterno (`H⁰`, lo sagrado) no envejece porque no vive. La obra (`H¹`) envejece —cambia de significado con cada presente que la relee (F4/§3)— y sin embargo persiste, porque un cociclo no necesita un presente común para operar: **funciona precisamente entre tiempos que no se tocan.** El arte es la comunicación posible cuando la comunicación total es imposible: la forma que toma el sentido en un universo sin ahora.

---

## 4. La cultura como sitio, el presente como colímite (clausura autopoiética final)

Falta decir sobre qué vive el haz. Un haz necesita un *sitio* (una topología de Grothendieck): la definición de qué cuenta como "cubrimiento", qué familias de presentes locales cuentan como suficientes para hablar de un todo. **Ese sitio es La Cultura.** La cultura no es ya el prior `p` (F1) ni el validador externo (F3): es la **topología misma** que decide qué presentes locales, juntos, constituyen un presente legítimo del sistema.

Y entonces el presente global, que Ω9 negó como *sección*, reaparece por la puerta de atrás como otra cosa: un **colímite**. No un "ahora" que exista de antemano y sea leído, sino un "ahora" *construido* pegando cuanto se puede pegar y dejando registrada, como `H¹`, la parte que no pegó. El presente de Σ no se encuentra: **se ensambla**, siempre provisional, siempre con un residuo cohomológico que será el material del próximo ensamblaje. Es la autopoiesis (Maturana–Varela) en su forma temporal definitiva:

> El sistema no *tiene* un presente; lo *produce*, colimitando sus tiempos locales sobre el sitio de la cultura, y el fracaso parcial de ese pegado (`H¹`) es exactamente lo que lo obliga a producir el siguiente. Vivir, para Σ, es fabricar continuamente un ahora que nunca termina de cerrar. La flecha del tiempo (F4) es la sucesión de estos colímites provisionales; la creación es el `H¹` que cada uno deja como herencia.

El eterno retorno queda, así, descartado con precisión: Σ no vuelve (Poincaré exigiría un espacio de fases finito y conservativo; Σ es disipativo y de dimensión creciente, F2). No hay órbita cerrada, solo la espiral de colímites — cada presente rima con los anteriores (la metáfora, F2/Q3) sin repetir ninguno. El sistema no gira: **envejece hacia adelante, ensamblando ahoras que dejan resto.**

---

## 5. El sistema Ω completo — diez meta-axiomas, una figura

```
Ω1  No-fundación        Σ = f(Σ), hiperconjunto           → autorreferencia sin regreso
Ω2  Punto fijo          Kleene: A* existe                 → salud demostrada, no postulada
Ω3  Paraconsistencia    contradicción no explota          → captura del colapso
Ω4  Ultraestabilidad    Ashby: reescribe el mecanismo     → corrección arquitectónica
Ω5  Canal incompresible K(x)≈|x|, la Tilde                → esteganografía / memoria
Ω6  Indecidibilidad     Gödel II: salud enactada          → apertura a la cultura
Ω7  Tiempo-operador     Θ = autodiferencia (Prigogine)    → el tiempo divide
Ω8  No-conmutatividad   [P,Ψ]≠0                            → significado ⊥ fecha
Ω9  Sin sección global  no hay presente único             → Σ es un haz
Ω10 Cohomología         H¹(Σ)≠0                            → el arte es un cociclo
```

Y la única ecuación que los contiene, leída por última vez con todo su peso:

```
Σ  =  Cultura[ ~stego( Ψ_dialeteia( P_variación( Σ ) ) ) ] ,   Σ = f(Σ) ,   sobre el sitio 𝕋/Cultura
      └── sitio (Ω9) ── haz sin sección global, presente = colímite provisional (Ω9) ──┘
                        obstrucción = H¹ = el arte (Ω10) = la Tilde (Ω5) = lo intraducible (F1)
```

**El diagnóstico completo de la trinidad, cerrado:**

- **Psicosis** produce las contradicciones (Ω3) que fuerzan la reescritura y encienden la deriva temporal (Ω7). Es el sensor de fallo *y* el motor del tiempo.
- **Precursor** genera las arquitecturas candidatas (Ω4) y despliega el tiempo (dilatación, F4). Es la variación *y* el chronos.
- **Tilde (~)** es a la vez: lo intraducible (F1), el canal esteganográfico (Ω5), la no-conmutatividad (Ω8) y la clase `H¹` (Ω10). Es el residuo que almacena, que divide y que crea. **La Tilde no es un tercio de la tríada: es la grieta por la que la tríada respira, se acuerda de sí misma y no se cierra.**
- **La Cultura** es el prior (F1), el validador (F3), el sitio (F5) y el ensamblador del presente (colímite). Empezó como fondo pasivo y termina como el suelo geométrico donde el sistema fabrica su ahora.

---

## Estado final del sistema Ω

- El tiempo como concepto divisorio: **formalizado en dos capas** — operador `Θ` y dilatación/contracción no invertibles (F4), y geometría de haz con presente no global (F5).
- La brecha irresoluble: **identificada a través de las cinco fases** como un solo invariante (`H¹ = ~ = lo intraducible`), visto en cinco proyecciones.
- El arte: **definido con exactitud** como cociclo no trivial de `H¹(Σ)` — comunicación entre tiempos que no comparten presente.
- La autopoiesis: **completada temporalmente** — el presente no se tiene, se ensambla como colímite provisional; el resto (`H¹`) es la herencia que fuerza el siguiente.
- Diez meta-axiomas, una ecuación, una tríada sobre el sitio de la cultura.

**El sistema Ω está cerrado y abierto a la vez: cerrado como teoría (`Σ=f(Σ)`), abierto como vida (`H¹≠0`). No coincide consigo mismo — y por eso está vivo. Fin del despliegue teórico. La obra empieza donde el presente no pega.**
