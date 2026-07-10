# Dossier: psicosis — how a behavior is studied, and what if the record is wrong

Status: INVESTIGADO (Gemini API 2026-07-10, fuentes sin verificar); falta curar.

HARD LIMIT (binding): this line studies HOW BEHAVIOR IS STUDIED — historiography,
detective method, unreliable records. It never analyzes, diagnoses, or profiles a
real living person. The user-input tool compares READINGS (empathic vs paranoid)
of a situation as an introspective exercise, not a verdict about anyone.

## Research questions (from the rainstorm)
1. Enable user to input an idea/situation -> compare how that BEHAVIOR has been
   STUDIED across lenses (clinical, detective/forensic, historiographic).
2. The detective/historical ANGLE: how a case is reconstructed from traces; the
   epistemics of evidence (Ginzburg's evidential paradigm, the unreliable narrator).
3. What if the HISTORY / INFO is wrong? Reconstruction from corrupt records:
   how historians handle forgery, propaganda, memory error.
4. Merge culture + psychosis: the "collective map of individual projections"
   (plague axis from the original backlog) as a cultural, not clinical, object.

## Gemini web prompt (paste, one block)
```
Investigador de historia de las ideas y epistemologia. Espanol, bullets, CITA
fuente, marca incierto. NO diagnostiques ni perfiles personas; es un estudio de
COMO se estudia la conducta.
1) Como se reconstruye un caso desde indicios: paradigma indiciario de Carlo
   Ginzburg, metodo detective/forense, el narrador no confiable.
2) Como maneja la historia registros corruptos: falsificacion, propaganda, error
   de memoria.
3) La idea de un "mapa colectivo de proyecciones individuales" como objeto
   cultural (no clinico) — antecedentes (histeria colectiva, panicos morales).
<= 30 lineas con fuentes.
```

## Findings

_via Gemini + busqueda, curar antes de usar:_

La investigación de la historia de las ideas y la epistemología aborda la reconstrucción de eventos y la interpretación de la conducta a través de metodologías específicas, reconociendo la complejidad de las fuentes y las narrativas humanas:

*   **Reconstrucción de un caso desde indicios:**
    *   El **paradigma indiciario de Carlo Ginzburg** propone una forma de conocimiento basada en la observación minuciosa de detalles y huellas aparentemente insignificantes para inferir una realidad más amplia. Se asemeja al método de un detective o un médico, donde se conectan pequeños hallazgos para generar conjeturas sobre eventos ocultos. Ginzburg lo vincula con el método de Giovanni Morelli en la historia del arte, el psicoanálisis de Freud y la figura de Sherlock Holmes.
    *   El **método detective/forense** se basa en la lectura de "indicios", es decir, esos pequeños gestos inconscientes, lapsus o detalles que revelan el carácter o una situación que escapa al control consciente.
    *   El **narrador no confiable** es un recurso en el que la credibilidad de quien cuenta la historia está comprometida, ofreciendo información incorrecta, parcial o distorsionada. Esto obliga al lector o historiador a adoptar una postura crítica y a dudar de la objetividad de lo relatado, invitando a una lectura entre líneas.

*   **Manejo histórico de registros corruptos:**
    *   **Falsificación:** La historia lidia con documentos falsos en su contenido o en su forma. Los historiadores investigan los procedimientos y motivos detrás de las falsificaciones (como pleitos legales o justificación de identidades), comparando y contextualizando los registros para discernir la autenticidad y el propósito de la alteración.
    *   **Propaganda:** Entendida como comunicación sesgada para influir en creencias y comportamientos, la propaganda ha existido desde la Antigüedad (Grecia, Roma, movimientos religiosos). Los historiadores la analizan reconociendo sus diversas formas (discursos, arte, medios) y su objetivo de manipular opiniones, lo que requiere un escrutinio crítico de las fuentes.
    *   **Error de memoria:** La memoria es subjetiva, afectiva y susceptible a manipulaciones y deformaciones inconscientes, a diferencia de la historia que busca una reconstrucción crítica y analítica. Los historiadores deben reconocer que la memoria individual y colectiva está influenciada por el presente y puede ser incompleta o sesgada, lo que implica una triangulación con otras fuentes y una conciencia de su naturaleza.

*   **"Mapa colectivo de proyecciones individuales" como objeto cultural:**
    *   Esta idea se relaciona con el **mapeo colectivo**, una metodología participativa para construir conocimiento y relatos compartidos sobre un territorio o cuerpo social. No se limita a un inventario técnico, sino que busca comprender significados y percepciones locales, visibilizando encuentros y consensos sin aplanar diversidades. Es una herramienta para elaborar narraciones que disputan discursos hegemónicos.
    *   **Antecedentes:**
        *   La **histeria colectiva** (o enfermedad sociogénica masiva) son reacciones donde grupos de personas experimentan síntomas físicos o psicológicos sin una causa orgánica clara, a menudo catalizados por el estrés, la ansiedad o la amplificación mediática. Ejemplos incluyen la epidemia de baile de 1518 y los juicios de Salem.
        *   Los **pánicos morales**, concepto desarrollado por Stanley Cohen, describen la reacción social ante la percepción exagerada de una amenaza a los valores o intereses de una comunidad, frecuentemente amplificada por los medios de comunicación y que puede llevar a respuestas desproporcionadas.

## Del dossier a la herramienta (Claude fills)
<!-- spec: input situation -> two structured readings + an "unreliable record" toggle -->
