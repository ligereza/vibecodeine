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

## Nomenclatura (2026-09-03)

Las palabras se enredaron y eso fue fuente de errores. Quedan asi:

| Palabra | Que es |
|---|---|
| **MAK** | el computador Linux. Solo, sin apellido, siempre es la maquina. |
| **la rama MAK** | `refs/heads/MAK`. Se dice completo, con la palabra rama. |
| **el checkout MAK** | `/home/mak`, donde esa rama esta montada. Se dice completo. |
| **la rama FLUJO** | `refs/heads/FLUJO`. |
| **el checkout FLUJO** | `/home/mak/flujo`. |
| **vibecodeine** | el repositorio: `ligereza/vibecodeine` en GitHub y su unico clon local. |
| **IRIS** | el sistema interno con que el operador ordena el archivo. No es un repo ni un archivo. |
| **iskvw.cl** | el sitio publico, dormido. |

Hay **un solo** repositorio local, `/home/mak/.git`. `/home/mak/flujo` no es
otro repositorio: es un worktree del mismo. Y no se dice "caja": esa palabra la
invente yo y no definia nada.

`ligereza/MAK`, `ligereza/flujo` y `ligereza/IRIS` existen en GitHub y estan
**vacios** (0 KB, cero commits). Son nombres reservados para separar el sistema
despues de ordenarlo. No son autoridad de nada y el codigo no esta ahi.

## La autoridad es el operador

No reconstruyas un contrato desde los archivos borrados, desde el historico ni
desde ningun documento viejo que encuentres: se borraron a proposito. No le
agregues reglas a este archivo.

Dos fuentes, y ninguna es un documento: **preguntarle a el, o medir la
maquina.**
