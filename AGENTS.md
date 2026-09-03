# AGENTS.md

El unico archivo de contrato de este repositorio. Escrito de cero el
2026-09-03, despues de borrar todos los anteriores.

Tiene tres punteros y nada mas. **No contiene hechos**: cada vez que un
documento de este repo afirmo un hecho, envejecio y termino mintiendo con cara
de medicion.

## Los tres

| Para | Ir a |
|---|---|
| lo que el operador decidio | `DECISIONES.md` |
| lo que existe y esta corriendo ahora | `.venv/bin/python tools/mak_status.py` |
| que paso antes con un archivo o un documento | `context/HANDOFF_HISTORICO.md` |

## Lo que cada uno es, y lo que no

**`DECISIONES.md`** es el documento activo. Se agrega al final, no se
reescribe. Solo decisiones: una decision no envejece porque ya paso.

**`tools/mak_status.py`** es de donde salen los hechos. Ninguno se escribe en
prosa. Si necesitas saber que servicio corre, en que rama estas o que esta
sucio, se pregunta a la maquina, no a un documento.

**`context/HANDOFF_HISTORICO.md`** es un registro. Antes se llamaba
`LAST_HANDOFF.md` y se leia como estado; ya no. Sirve para buscar informacion
que falte o para saber que paso con algun archivo o documento. Nada en el es
una instruccion ni un hecho vigente.

## La autoridad es el operador

No reconstruyas un contrato desde los archivos borrados, desde el historico ni
desde ningun documento viejo que encuentres: se borraron a proposito. No le
agregues reglas a este archivo.

Dos fuentes, y ninguna es un documento: **preguntarle a el, o medir la
maquina.**
