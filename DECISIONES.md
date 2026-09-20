# DECISIONES

Lo que el operador decidio, con la fecha en que lo dijo.

---

## 2026-09-03

- **No hay nodo Windows.** Era un equipo antiguo y ya no esta. Esta caja Linux
  es todo el sistema.

- **El sistema crea formatos de portafolio primero y despues decide como
  ordenar las obras.** No busca el orden perfecto de una obra. En sus palabras:
  "yo planteo un sistema que primero cree formatos de portafolio y luego decide
  como ordenar las obras, no buscar el orden perfecto de una obra".

- **Exigir descripcion escrita por pieza para poder decidir sobre ella queda
  eliminado.** Lo llamo estupido y tenia razon: dejaba la mitad del archivo
  declarada indecidible.

- **Todos los archivos de contrato se borran y se empieza de cero con un solo
  `AGENTS.md`.** `CLAUDE.md`, el `AGENTS.md` anterior, el `agents.md` en
  minusculas y los tres de `contracts/departments/`, en los dos checkouts.

- **`LAST_HANDOFF.md` pasa a llamarse `HANDOFF_HISTORICO.md` y queda como
  historico.** En sus palabras, no sirve "para nada mas que revisar info que
  falte o saber que paso con algun archivo o documento". No es el estado, no es
  una instruccion, y no se rutea como lectura inicial.

- **El documento activo contiene solo decisiones.** Los hechos no se escriben:
  los imprime un comando que lee la maquina en el momento.

- **Un test que defiende un modelo de documentos que ya no existe se borra**, no
  se le cambia el string para que deje de gritar.

- **Nomenclatura fijada.** `MAK` solo, sin apellido, es el computador Linux.
  La rama y el directorio se dicen completos: "la rama MAK", "el checkout MAK".
  El repositorio se llama `vibecodeine`. Queda escrita en `AGENTS.md`.

- **Separar el sistema en repos propios es lo proximo, despues de ordenar.**
  `ligereza/MAK`, `ligereza/flujo` y `ligereza/IRIS` se dejan reservados y
  vacios a proposito; no se borran.

---

## 2026-07-26

- **Idioma: espanol al operador, ingles en el codigo.** La excepcion, no
  negociable: todo lo que un humano lee como producto -- piezas y datos de RD,
  curatoria de iskvw, lo que ve un directorio o un cliente -- va en espanol
  correcto CON tildes.

---

## 2026-09-06

- **El guardian de topologia main-only se retira.** `git-topology.yml`, el
  parrafo de `MAPA.md` que lo declaraba y el test que lo defendia. Se escribio
  el 2026-08-15 y la decision del 2026-09-03 sobre la nomenclatura de las ramas
  MAK y FLUJO, y sobre separar el sistema en repos propios, ya lo dejaba
  obsoleto. El tag `archive/house-history` se conserva: es el punto de
  preservacion y no depende del guardian.

---

## 2026-09-10

- **La union literal de MAK y FLUJO en `main` (decidida el 2026-09-08) no
  reabre la retirada del 2026-09-06.** Un agente, al integrar el `main` unido
  con el trabajo nuevo de las ramas, reintrodujo `git-topology.yml` (re-
  enmarcado como "testigo historico" en `MAPA.md`) y `context/LAST_HANDOFF.md`
  con contenido nuevo, sin dejar esta entrada -- una auditoria posterior lo
  encontro sin registro. Confirmado: no fue autorizado. Se revierten ambos:
  `git-topology.yml`, su parrafo en `MAPA.md` y `context/LAST_HANDOFF.md`
  salen de `main` de nuevo; `HANDOFF_HISTORICO.md` sigue siendo el unico
  historico, tal como quedo fijado el 2026-09-03.
