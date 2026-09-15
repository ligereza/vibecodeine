# MAK grammar runner

`tools/grammar_runner.py` ejecuta el ciclo experimental local de MAK sobre un
manifiesto `semantic-icons-v1`. El runner usa el validador/compilador de
`cultura/mak_codex/motor_semantico`, infiere cuerpos desde fragmentos repetidos
de la partición `construction`, congela esa biblioteca antes de leer
`development` y `final_reserved`, y despacha cada generación por el Conductor
durable de MAK.

El runner pertenece a MAK porque el corpus y el Conductor pertenecen a MAK.
No forma parte del CLI ni del checkout autónomo de FLUJO. La entrada verificada
es:

~~~
PYTHONPATH=/home/mak /home/mak/.venv/bin/python /home/mak/tools/grammar_runner.py run \
  --corpus /home/mak/work/grammar-lab-20260912/corpus_manifest.json \
  --generations 3 --seed 42 --max-candidates 24 \
  --output /home/mak/work/grammar-runs/first-run
~~~

El directorio de salida no se sobrescribe. Contiene index.html, svg/,
programs/, library.json, checkpoint.json y metrics.json.

~~~
PYTHONPATH=/home/mak /home/mak/.venv/bin/python /home/mak/tools/grammar_runner.py status \
  --checkpoint /home/mak/work/grammar-runs/first-run/checkpoint.json

PYTHONPATH=/home/mak /home/mak/.venv/bin/python /home/mak/tools/grammar_runner.py stop \
  --checkpoint /home/mak/work/grammar-runs/first-run/checkpoint.json

PYTHONPATH=/home/mak /home/mak/.venv/bin/python /home/mak/tools/grammar_runner.py resume \
  --checkpoint /home/mak/work/grammar-runs/first-run/checkpoint.json
~~~

stop deja un marcador y el proceso se detiene entre generaciones; resume lo
retira. Ctrl-C también interrumpe el proceso, y el último checkpoint durable
conserva las generaciones ya terminadas.

## Control Stitch separado

Se probó fuera del corpus de MAK el ejemplo oficial mínimo de dos programas:

~~~
PYTHONPATH=/tmp/stitch-check.bVBg7r /home/mak/.venv/bin/python -c 'import stitch_core; stitch_core.compress(["(foo (a a a))", "(bar (b b b))"], iterations=1, max_arity=3, threads=1, silent=True)'
~~~

Resultado observado: paquete stitch_core 0.1.29, una abstracción fn_0,
programas reescritos y compresión 806 -> 604. El runner de MAK no presenta
este control como aprendizaje sobre semantic-icons-v1: sus specs no son
programas Lisp de Stitch y se procesan con el intérprete local declarado en el
manifiesto.
