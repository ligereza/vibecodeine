# iskvw, 2026-07-27 -- lo que fallo, medido

Archivado desde `context/LAST_HANDOFF.md` el 2026-07-27 porque el ratchet de
350 lineas se disparo. Es historico: la leccion vive en el checkpoint en tres
lineas, el detalle vive aca.

- **What the 2026-07-27 iskvw stretch got wrong, so it is not repeated.** It was
  written up as its own file and folded in here, because a second state document
  is how this repo lost whole sessions before. In order of cost: it treated the
  curation as a BLOCKER and closed by asking the user to decide which of the 697
  works were obra -- his correction was one line, "el objetivo n1 era que fuera
  adaptable a recibir mas obras y que fuera transmutable", and the filter is now
  configuration with everything in by default. It dismissed two references the
  user sent WITHOUT OPENING THEM, then asked the list about its own limits and
  got answers inside them. It invented a GPU limit that did not exist. It built
  for hours on the 8 pieces of `obras.json` while the archive was on the box. It
  shipped positions that came from a hash of the identifier -- a lie the repo had
  ALREADY warned about in `projects/cultura/doublecup/svg/README.md` -- and the
  correction is the only thing of that stretch worth keeping: PCA 3.8%, its own
  force layout 16.4%, t-SNE 48.9% of neighbourhood preserved. Two of the three
  looked good and lied, and one of those two was its own. It left 60 zero-byte
  SVGs that were indistinguishable from good traces, because the tracer opened
  the destination before tracing. And it tuned a parameter without measuring what
  it was for: the plan's tracer on photographs gave 13.5% legible and 42% noise;
  with the right parameters, 60% legible, 2% noise, 18 MB -> 4.9 MB.
  **If you are about to say "this does not apply" about something he sent you:
  open it first.**
