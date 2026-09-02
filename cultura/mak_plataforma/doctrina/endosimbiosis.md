# Endosimbiosis -- el lente biologico del organismo MAK

> Segundo lente de diseño de MAK, complementario a `teoria-desorden.md` (que usa
> metaforas de almacen/ciberntica). Este lee el organismo como biologia: no es
> adorno, es lenguaje de diseño. Fundado en los informes que MAK produjo sobre si
> mismo (endosimbiosis, virus satelite, evolucion -- `~/research/informes/`,
> 2026-07-20). Cada metafora apunta a codigo real que YA corre.

## 1. Mitocondria / endosimbiosis -- el proceso independiente que se vuelve permanente

Hace ~1.5-2 mil millones de años una bacteria aerobia fue fagocitada y, en vez de
digerirse, se volvio parte permanente de la celula: la mitocondria. Independiente
primero, integrada despues, indispensable al final.

**En MAK:** ese es el arco de este repo. Claude era el proceso independiente que dio
capacidad; `entregar.py` es la enzima que integra: toma el codigo que codex genero
"suelto" y lo vuelve parte permanente del organismo al mergearlo (PR -> main). El
capataz/director externo (Claude) se disuelve; su funcion queda internalizada en los
cargos del box (`trabajo.py`, `revisor.py`, `junta.py`). Exito = ser digerido, no
seguir flotando afuera.

## 2. Virus satelite / virofago -- el modulo que no corre sin huesped

Un virus satelite no se replica solo: necesita un virus ayudante dentro de una celula.
Dependencia estructural, no defecto.

**En MAK:** los cargos nuevos son satelites. `entregar.py` no existe sin codex (su
huesped que genera las piezas). `revisor.py` no existe sin los PR del entregador.
`searxng_search` no existe sin el departamento research que lo llama. Reconocer la
dependencia es diseño honesto: no se construye un modulo que "corre solo" cuando en
verdad necesita su huesped -- se lo acopla al contrato del huesped (jobs.jsonl, el
mismo que ya cosecha entregar) en vez de inventar una via nueva.

## 3. Simbiosis / transferencia horizontal de genes -- salud compartida entre procesos

Bacterias y virus intercambian genes horizontalmente: un rasgo util (resistencia)
salta entre organismos sin herencia vertical.

**En MAK:** `salud_proveedores.json` es el gen compartido. research y codex son
procesos distintos, pero `codex_lib.py` importa `LLM` de `research_lib.py` y ambos
escriben/leen el MISMO archivo de salud. Un proveedor que falla en research queda
degradado tambien para codex, sin que nadie lo copie a mano. `searxng` y `tavily`
tambien "adquirieron" el gen al llamar `_salud_registrar` -> aparecen solos en el
panel del hub. El rasgo util se transfiere por el archivo, no por herencia.

## 4. Evolucion -- variacion, seleccion, herencia sobre el repo

Sin diseñador central: variantes surgen, el ambiente selecciona la mas apta, lo
seleccionado persiste.

**En MAK:**
- **Variacion:** `agente_libre.py` (mejora arbitraria) + los verbos de `trabajo.py`
  producen variantes de codigo/investigacion.
- **Seleccion:** `orden_por_salud()` selecciona el proveedor mas apto por desempeño;
  `revisor.py` selecciona el codigo que compila + cumple; el gate (CI + branch
  protection) es la presion selectiva sobre cada variante.
- **Herencia:** lo seleccionado se mergea a main y persiste; lo que no, se cierra.
  `expulsion.py` es seleccion negativa real (no solo reordenar): el proveedor cronico
  se suspende, con la guarda de que ollama local es el backstop que nunca se extingue.

## Cierre -- postura, no solo informacion

La `junta.py` diaria es la conciencia: lee su propio estado (salud, backlog, tasa de
exito) y toma POSTURA -- no "todo verde", sino que decide con las herramientas que
tiene. El organismo no solo procesa datos: se observa y actua sobre si mismo. Eso es
lo que separa un pipeline de un organismo. Ver `context/CAPATAZ.md` (el peso diario de
su mente) y `context/DOCTRINA_CLAUDE.md` (sus politicas).

*Este lente crece: cuando MAK investigue mas biologia de sistemas, sumar el hallazgo
aca -- el trinquete aplicado a la propia metafora.*
