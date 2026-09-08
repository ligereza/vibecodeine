# -*- coding: utf-8 -*-
"""Motor semantico: un agente CIEGO escribe SIGNIFICADO, no coordenadas.

El agente emite una spec con vocabulario cerrado (22 figuras, 12 gestos, 9
tonos, 6 composiciones, 5 ritmos) y `compilar()` produce la geometria. La falla
silenciosa -- SVG valido que se ve mal, que es la que sobrevive un pipeline sin
supervision -- deja de ser improbable y pasa a ser INEXPRESABLE: no hay forma de
escribir "empieza en opacidad cero", el texto se mide antes de dibujarse, el
contraste se calcula WCAG y el agente no concatena strings.

Medido en la sesion que lo produjo (2026-07-28): 44% de defectos visuales
escribiendo SVG a mano contra ~11% con el motor, sobre XML 100% valido en los
dos casos. El detalle y sus limites honestos estan en
`docs/cultura/MOTOR_SEMANTICO.md`.

El techo creativo tambien es real: estos iconos son correctos y genericos. Por
eso el motor es el PISO para volumen, no el reemplazo de una pieza insignia
escrita a mano.

    from motor_semantico import compilar, validar_spec, ErrorSemantico
    svg, avisos = compilar(spec, slug="berlin")

Desde la linea de comandos, el camino es el script suelto -- que es el que usa
la caja, con cwd en /home/mak/codex:

    py motor_semantico/compilador.py spec.json salida.svg

`py -m motor_semantico.compilador` tambien funciona, pero emite un
RuntimeWarning de runpy porque este `__init__` ya importo el submodulo. Es
cosmetico y no se arregla quitando el re-export: la forma de arriba es la
recomendada y sale limpia.
"""
from .compilador import ErrorSemantico, compilar, contraste, validar_spec

__all__ = ["compilar", "validar_spec", "contraste", "ErrorSemantico"]
