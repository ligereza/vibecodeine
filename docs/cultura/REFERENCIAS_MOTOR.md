> Fuentes leídas durante la sesión que produjo el motor semántico (2026-07-28),
> con la cita textual y el lugar donde se usó cada una. Landeadas **verbatim**:
> reescribirlas a mano habría sido la ocasión perfecta para deformar una cita.
> Las referencias que este documento menciona como `REPORTE-FINAL.md` y
> `HALLAZGOS.md` están destiladas en `docs/cultura/MOTOR_SEMANTICO.md`.

# Referencias

Fuentes consultadas durante la sesión, con lo que aportó cada una y dónde se
usó. Solo se listan trabajos efectivamente recuperados y leídos; las citas
textuales están en el idioma original.

---

## A. Generación de SVG con modelos de lenguaje

### A1. SVGenius — *Benchmarking LLMs in SVG Understanding, Editing and Generation*
<https://arxiv.org/html/2506.03139v1>

Benchmark que mide LLMs generando y editando SVG. Los mejores resultados
reportados rondan **SSIM ~54%** (Claude-3.7-Sonnet 54.02; GPT-4o 52.41;
Gemini-2.0-Flash 50.07).

**Cómo se usó:** para afirmar que el estado del arte en generación de SVG por
LLM es mediocre, no un problema resuelto.
→ `REPORTE-FINAL.md` §5 · `HALLAZGOS.md` §1

### A2. Chat2SVG — *Vector Graphics Generation with LLMs and Image Diffusion Models*
<https://arxiv.org/html/2411.16602v2> · <https://arxiv.org/html/2411.16602>

Pipeline híbrido: el LLM produce una plantilla con primitivas geométricas, un
modelo de difusión la refina, y se optimiza en espacio latente.

> "We develop a specialized prompt system that directs LLMs to generate SVG
> templates using **basic geometric primitives**"

**Cómo se usó:** confirma que la solución del motor semántico (vocabulario
cerrado de primitivas en vez de coordenadas libres) es la misma a la que llegó
la literatura de forma independiente.
→ `REPORTE-FINAL.md` §5 · `HALLAZGOS.md` §1

### A3. SVGFusion — *A VAE-Diffusion Transformer for Vector Graphic Generation*
<https://arxiv.org/abs/2412.10437> · <https://arxiv.org/html/2412.10437>

Dos citas clave. La primera, el diagnóstico del problema:

> "Existing LLM-based models that generate SVG code as a **flat token sequence**
> struggle with poor structural understanding and **error accumulation**"

La segunda, sobre por qué el código SVG no es un buen espacio semántico:

> "syntactically different SVGs can be visually similar... A standard VAE,
> learning solely from SVG code, would incorrectly map these variations to
> **distant points** in the latent space"

Por eso su VP-VAE fusiona código SVG **con** la imagen rasterizada, usando
características visuales de DINOv2.

**Cómo se usó:** (1) el diagnóstico coincide con nuestro 44% de defectos
escribiendo SVG a mano; (2) es confirmación independiente de que **el píxel es
lo que ancla el significado** — el render no es opcional.
→ `REPORTE-FINAL.md` §5 · `HALLAZGOS.md` §1 y §2

### A4. StarVector — *Generating Scalable Vector Graphics Code from Images*
<https://arxiv.org/abs/2312.11556> · repo: <https://github.com/joanrod/star-vector>

Modelo multimodal (CLIP + StarCoder) para image-to-SVG. Introduce SVG-Bench.
Relevante su posición sobre evaluación:

> "We address challenges in SVG evaluation, showing that **pixel-based metrics
> like MSE fail to capture the unique qualities of vector graphics**"

**Cómo se usó:** fundamenta la propuesta de usar CLIP/DINO score como QA
automático en vez de métricas de píxel.
→ `HALLAZGOS.md` §1 y §3

### A5. LLM4SVG — *Empowering LLMs to Understand and Generate Complex Vector Graphics*
<https://arxiv.org/html/2412.11102v1>

Tabla comparativa amplia de métodos (optimización, redes neuronales, LLM) con
FID, CLIPScore, Aesthetic, HPS y tiempo de generación.

**Cómo se usó:** contexto general del campo y sus métricas.

### A6. SVGEditBench — *Quantitative Assessment of LLM's SVG Editing Capabilities*
<https://arxiv.org/html/2404.13710> · repo: <https://github.com/mti-lab/SVGEditBench>

Benchmark de **edición** de SVG por LLM (cambiar color, contorno, comprimir,
invertir, transparencia, recortar).

**Cómo se usó:** contexto para la Parte 2 (edición de íconos existentes).

### A7. OmniSVG — *A Unified Scalable Vector Graphics Generation Model*
<https://www.researchgate.net/publication/390601951_OmniSVG_A_Unified_Scalable_Vector_Graphics_Generation_Model>

Comparativa de tiempos y conteo de tokens entre métodos. Nota que
StarVector(8B) falla al generar SVG complejos en MMSVG-Character.

**Cómo se usó:** contexto sobre límites de complejidad.

### A8. SVG-T2I (panorama del campo)
<https://www.emergentmind.com/topics/svg-t2i>

Resumen comparativo de modelos text-to-SVG con FID, CLIPScore, HPS y tiempo.

---

## B. Espacios latentes de gráficos vectoriales

### B1. DeepSVG — *A Hierarchical Generative Network for Vector Graphics Animation*
<https://ar5iv.labs.arxiv.org/html/2007.11301> · repo: <https://github.com/alexandre01/deepsvg>

Arquitectura transformer jerárquica que separa formas de alto nivel de los
comandos que las dibujan. Permite interpolación en el espacio latente como
herramienta de animación.

**Cómo se usó:** primera de las dos formas en que la literatura sí conecta
"vector SVG" con "vector semántico".
→ `HALLAZGOS.md` §2

### B2. SVG-VAE — *Generating Scalable Vector Graphics Typography* (Magenta)
<https://magenta.tensorflow.org/svg-vae>

Modelo de espacio latente para tipografía vectorial. Permite manipular
atributos de alto nivel como "bold-ness" o "italic-ness" y transferir estilo
entre caracteres.

**Cómo se usó:** ejemplo concreto de álgebra sobre un espacio latente de SVG.
→ `HALLAZGOS.md` §2

### B3. DesigNet — *Learning to Draw Vector Graphics as Designers Do*
<https://arxiv.org/html/2604.06494v1>

VAE jerárquico con latentes globales y por trazo, coordenadas continuas y
supervisión geométrica explícita.

**Cómo se usó:** contexto sobre la evolución de los espacios latentes de SVG.

### B4. SVG (latent diffusion sin VAE) — ICLR 2026
<https://github.com/shiml20/SVG>

Difusión latente que usa representaciones auto-supervisadas (DINOv3) en vez de
un VAE. Nota: el nombre del repo coincide con el formato pero refiere a
*Self-supervised representations for Visual Generation*.

---

## C. Decodificación restringida por gramática

### C1. *Flexible and Efficient Grammar-Constrained Decoding* — ICML 2025
<https://openreview.net/forum?id=L6CYAzpO1k>

Algoritmo de GCD con preprocesamiento 17.71× más rápido, manteniendo eficiencia
en el cálculo de máscaras.

**Cómo se usó:** viabilidad práctica de aplicar GCD en producción.

### C2. *Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning* — EPFL
<https://openreview.net/forum?id=KkHY1WGDII> · repo: <https://github.com/epfl-dlab/GCD>

Hallazgo central:

> "grammar-constrained LMs **substantially outperform unconstrained LMs or even
> beat task-specific finetuned models**"

**Cómo se usó:** valida que el vocabulario cerrado del motor no solo previene
errores sino que puede mejorar la calidad de la salida.
→ `REPORTE-FINAL.md` §5 · `HALLAZGOS.md` §1 · `motor/esquema.py` (docstring)

### C3. *Structured Outputs and Constrained Decoding* — TMLS
<https://www.tmls.nyc/research/structured-outputs-constrained-decoding>

La advertencia más importante de toda la búsqueda:

> "a **guaranteed-valid response is not a guaranteed-correct one**, and the most
> expensive mistake in production structured-output systems is to confuse the two"

También distingue conformidad estructural de corrección semántica, y recomienda
"constrain the wire format and never the thinking".

**Cómo se usó:** es exactamente lo que medimos (0 errores de validación + 2
rondas de corrección visual). Sostiene la tesis central de la sesión:
**válido ≠ bueno**.
→ `REPORTE-FINAL.md` §5 · `HALLAZGOS.md` §1

### C4. *Structured Output Generation in LLMs: JSON Schema and Grammar-Based Decoding*
<https://medium.com/@emrekaratas-ai/structured-output-generation-in-llms-json-schema-and-grammar-based-decoding-6a5c58b698a6>

Explicación divulgativa: "It ensures 100% format compliance by construction — if
a sequence wasn't in the allowed grammar, it simply can't be produced".

### C5. *LLMs for Domain-Specific Language Generation — How to Constrain Your Dragon*
<https://medium.com/itemis/large-language-models-for-domain-specific-language-generation-part-2-how-to-constrain-your-dragon-e0e2439b6a53>

Patrón práctico: transformar el DSL en JSON Schema, generar con structured
output y serializar de vuelta al DSL.

**Cómo se usó:** es literalmente la arquitectura de `motor/esquema.py` →
`compilador.py`.

---

## D. Vector Symbolic Architectures / Computación hiperdimensional

### D1. Hyperdimensional Computing / Vector Symbolic Architectures (portal)
<https://www.hd-computing.com/>

Introducción canónica. Define las dos operaciones fundamentales:

> "HD/VSA addresses these challenges by providing a **binding** operation
> associating individual (John, Mary) with roles (AGENT, PATIENT) and a
> **superposition** operation that allows multiple associations to be composed
> into a coherent whole"

**Cómo se usó:** es la base teórica del hallazgo de que el spec del motor
—`(rol ⊗ figura ⊗ gesto) ⊕ ...`— ya era una VSA simbólica sin haberlo buscado.
→ `REPORTE-FINAL.md` §6 · `HALLAZGOS.md` §2 · `motor/algebra.py`

### D2. *Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning*
<https://arxiv.org/html/2512.14709v1>

Describe las tres operaciones núcleo (binding, superposition, permutation) y su
uso para representar estructuras role-filler.

**Cómo se usó:** formalización de la notación ⊗ / ⊕ usada en `algebra.py`.

### D3. *A comparison of vector symbolic architectures* — Artificial Intelligence Review
<https://link.springer.com/article/10.1007/s10462-021-10110-3>

Comparación experimental de once implementaciones de VSA; taxonomía de
operaciones de binding y su comportamiento en razonamiento analógico.

**Cómo se usó:** respaldo para la operación de analogía
(`BERLÍN − muro + grilla`).

### D4. *LARS-VSA: A Vector Symbolic Architecture for Learning with Abstract Rules*
<https://arxiv.org/html/2405.14436v1>

Introduce un "cuello de botella relacional" que separa rasgos de objeto de
reglas abstractas.

**Cómo se usó:** paralelo conceptual con la separación
figura (objeto) / rol (estructura) del motor.

### D5. *Vector Symbolic Architectures in Clojure*
<http://gigasquidsoftware.com/blog/2022/12/31/vector-symbolic-architectures-in-clojure/>

Implementación didáctica de bind/bundle/unbind con código.

**Cómo se usó:** aclaró la mecánica de unbind, que inspiró
`transferir_estilo()` en `algebra.py`.

---

## Verificación de enlaces

- **SVGFusion** (A3): enlace comprobado en vivo. El abstract oficial confirma
  la cita **palabra por palabra** ("Existing LLM-based models that generate SVG
  code as a flat token sequence struggle with poor structural understanding and
  error accumulation"). Versión v3, revisada 9-abr-2026.
- **OpenReview** (C1, C2): las URLs son válidas pero el sitio aplica una
  verificación anti-bot al acceder sin sesión. Si el enlace pide validación,
  buscar el título del trabajo directamente en openreview.net.
- El resto de enlaces proviene de los resultados de búsqueda de la sesión y no
  se recomprobó uno por uno.

---

## Nota sobre alcance y limitaciones

- Todas las fuentes se consultaron vía búsqueda web durante la sesión
  (28-07-2026). Se leyeron resúmenes, tablas y extractos; **no se reprodujeron
  ni ejecutaron los modelos citados.**
- Las cifras comparativas de esta sesión (44% vs. 11% de defectos; 95 vs. 72 de
  puntaje del crítico) son **mediciones propias sobre muestras pequeñas**
  (16 y 9 íconos). Son indicativas, no concluyentes.
- El crítico perceptual (`motor/critico.py`) es una heurística propia, no una
  métrica validada por la literatura. Su sesgo hacia lo convencional está
  documentado en `REPORTE-FINAL.md` §7.
- Ninguna de las herramientas citadas resuelve el problema abierto: medir si
  una **metáfora visual funciona**.
