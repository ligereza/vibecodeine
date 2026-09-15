# ORDEN AUTOSUFICIENTE PARA EL AGENTE MAK — VIBECODEINE

Version revisada: 2026-09-13. Puedes empezar directamente en /home/mak sin conocer esta conversacion, el laboratorio anterior ni sus agentes.

Tu trabajo es implementar y ejecutar un motor experimental de aprendizaje de representaciones, aprovechar el codigo ya construido y dejarlo utilizable en MAK. Este documento contiene el contexto y el encargo. No tienes que pedir otro prompt al terminar cada subpaso.

## 1. Que proyecto es y donde trabajas

El repositorio es **VIBECODEINE**, https://github.com/ligereza/vibecodeine.git.

| Elemento | Identidad comprobada el 2026-09-13 |
| --- | --- |
| Raiz Git principal | /home/mak |
| Rama de ese checkout | main |
| HEAD observado y publicado entonces | fefb0c3333ec2e010c2500ce8f4d8c9df0a6c149 |
| Nombre real del remoto | vibecodeine-legacy |
| Otro checkout del mismo repositorio | /home/mak/flujo |
| Rama de ese otro checkout | integration/flujo-canonical-20260911 |
| Carpeta experimental previa | /home/mak/work/grammar-lab-20260912 |
| Distribucion Python declarada en pyproject.toml | mak-box |
| CLI declarado en pyproject.toml | flujo = flujo.cli:app |

**grammar-lab es una carpeta de trabajo dentro de VIBECODEINE, no otro repositorio.** El nombre del repositorio, el de la distribucion Python y el del comando no tienen por que coincidir.

Comprueba una vez raiz, rama, remoto y cambios actuales. No hagas git init ni inventes un remoto grammar-lab u origin. No mezcles silenciosamente los dos checkouts. El estado vivo de MAK prevalece sobre copias antiguas de Windows.

## 2. Intencion del usuario

El usuario trabaja en diseno, VJ, eventos, RD, cultura y 3D. Quiere que el trabajo de una especialidad deje capacidades aprovechables en otras y le abra oportunidades profesionales. MAK es su estacion principal; XIO es el frente en terreno. Windows es auxiliar y puede apagarse.

Su idea de **dimensiones del orden** consiste en descubrir formatos y lenguajes desde el material heterogeneo. El formato tambien se aprende: una regularidad puede convertirse en una operacion reutilizable; las excepciones pueden conservarse o motivar otra representacion. Pueden coexistir varios lenguajes.

No se busca imitar una estructura correcta de carpetas ni imponer un portafolio de salida predeterminado. Tampoco basta con dar nombres a agentes, aumentar instrucciones o acumular informes. El usuario ya dispone de herramientas, memoria y orquestacion.

**El resultado util es un motor que pueda ejecutarse sobre un lote, producir representaciones visibles y mostrar que reglas se descubrieron y reutilizaron, si las hubo.** La experimentacion puede dar un resultado negativo; el programa y sus salidas deben seguir siendo utilizables.

## 3. Que ocurrio antes y que no debes repetir

Un agente anterior estuvo unas diez horas encadenando comprobaciones. El estado inspeccionado contenia 157 preguntas y apuntaba a Q-1560, otra verificacion de que no se atribuyera aprendizaje. Hubo trabajo inicial aprovechable, pero la direccion se desvio hacia recibos, permisos, procedencia y confirmaciones de ausencia de aprendizaje.

Esta orden reemplaza esa continuacion automatica. Conserva la evidencia; no sigas generando preguntas por inercia. No necesitas leer los cientos de informes ni demostrar otra vez que la deriva existio.

Distingue tres cosas: un dato desconocido, una limitacion del lenguaje y un fallo de programa. No las conviertas en un UNKNOWN global. La ausencia de significado artistico certificado, identidad quimica o calibracion fisica no impide generar estructuras graficas experimentales. Tampoco autoriza a atribuirles esas propiedades.

## 4. Lectura inicial y activos que debes rescatar

Lee este documento y el manifiesto del corpus. Despues consulta solo las funciones y artefactos que vayas a utilizar:

- /home/mak/cultura/mak_codex/motor_semantico/compilador.py: validar_spec y compilar.
- /home/mak/cultura/mak_codex/motor_semantico/algebra.py: operaciones existentes.
- /home/mak/work/grammar-lab-20260912/experiment.py: serializacion, expansion, evaluacion y archivo.
- /home/mak/work/grammar-lab-20260912/corpus_manifest.json: entrada y particiones.
- Resultados Q-010 y Q-030, para conocer biblioteca y limites; Q-060/Q-100 solo si vas a reutilizar el dialecto SVG o el paquete de observaciones.
- El Conductor existente y el adaptador de continuidad, cuando conectes la ejecucion.

Extrae campos de estado y referencias concretas; no imprimas research.json o delivery.json completos si contienen miles de entradas. Amplia la lectura cuando aparezca una dependencia real, no para inventariar la caja.

Dos limitaciones comprobadas en el codigo anterior:

1. experiment.py:discover_library ya contiene los cuerpos y nombres text_mark_v1 y repeat_figure_gesture_v1. Activarlos por frecuencia sirve como heuristica o control; no demuestra descubrimiento abierto de cuerpos.
2. stitch_motif_learning.py cuenta fragmentos de tres tokens con Counter, sin invocar Stitch. Su tokenizador elimina informacion; comparar secuencias despues de tokenizar no demuestra conservar el programa original.

Si existe una correccion posterior, aprovechala y comprueba su llamada efectiva. No reconstruyas trabajo terminado por obedecer una observacion antigua.

## 5. Corpus inicial concreto

Fuente del contrato:

    /home/mak/work/grammar-lab-20260912/corpus_manifest.json

Fuente de datos:

    /home/mak/cultura/mak_codex/motor_semantico/lote.json

Interfaz: **semantic-icons-v1**, specs graficos JSON que el validador acepta y el compilador interpreta. Revisa su firma y salida reales antes de adaptar. Este lote contiene diez registros, nueve validos y una excepcion preservada. No son diez programas lambda listos para Stitch: la conversion es parte del trabajo.

| Uso | Slugs fijados en el manifiesto |
| --- | --- |
| Construccion: 6 | 01-warehouse-refugio; 02-detroit-maquina; 03-berlin-muro; 04-taz-efimera; 05-castlemorton; 06-criminal-justice |
| Desarrollo: 2 | 07-plur-afecto; 08-red-global |
| Reserva: 2 | 09-acid-trance; 10-inclusividad |

El manifiesto fija la revision de origen y SHA-256 del lote:
cd77e13c53127a78340f84c476f2ad570b0da20d2611dc2316ec589ba8457697.

Comprueba ese contrato una vez al iniciar el run. Si cambio, identifica el cambio y crea una version del experimento; no sobrescribas resultados anteriores ni abras una auditoria general.

Extrae las particiones programaticamente. No vuelques todo el lote en el contexto del agente durante el descubrimiento. La reserva contiene una entrada valida y una invalida por ausencia de protagonista: la segunda comprueba manejo de excepciones, no cuenta como positivo de generalizacion.

Slugs distintos no prueban independencia de procedencia. Este corpus sirve para una demostracion acotada; no sostiene por si solo transferencia entre todos los proyectos. Si alguna reserva ya influyo en decisiones anteriores, documentalo y limita la afirmacion: cambiar el nombre de version no devuelve independencia.

Un ejemplo oficial de Stitch puede comprobar instalacion y mecanismo, pero debe quedar separado del lote del usuario y rotulado como control. No presentes sus resultados como aprendizaje sobre este corpus.

## 6. Implementacion: descubrir, componer y mostrar

El codigo reutilizable queda versionable en VIBECODEINE, integrado con sus paquetes. La carpeta experimental conserva datos y resultados. Implementa o completa un unico ciclo:

material -> programas interpretables -> abstracciones -> biblioteca -> siguientes composiciones -> salidas visibles -> checkpoint.

### Definicion de descubrimiento

Una abstraccion cuenta como descubierta si **su cuerpo es producido por el algoritmo a partir de las entradas**, en lugar de estar escrito de antemano en el codigo o agregado manualmente.

Conserva para cada una: identificador, cuerpo expandible, entradas de origen, frecuencia o soporte, coste declarado antes/despues y usos posteriores. Estas son trazas del programa, no una nueva serie de reportes o jobs.

Prueba Stitch real sobre un ejemplo oficial pequeno y registra paquete/version y llamada. Parte de https://github.com/mlb2251/stitch y sus bindings enlazados. https://github.com/gabegrand/lilo sirve como referencia de mecanismo; instalar todo su entorno no es obligatorio.

Puedes instalar dependencias minimas en un entorno aislado. Si hace falta una alternativa, justifica el motivo, opera sobre estructuras bien formadas y declara el metodo utilizado. No rebautices un sustituto como Stitch ni vuelvas a una lista de respuestas programadas manualmente.

### Representacion y generacion

Define primitivas con semantica conocida y programas completos. Conserva numeros, operadores, orden y campos relevantes. Una llamada que oculta todo el material dificulta descubrir estructura; un fragmento que cruza parentesis no es automaticamente una funcion.

Cuando aparezca una abstraccion, incorporala al vocabulario y utilizala en una generacion posterior. Genera candidatos por composicion y variaciones compatibles. Interpreta y renderiza mediante las capacidades existentes.

Guarda SVG u otra salida grafica del interprete y una vista comparativa simple de entradas/candidatos. Un HTML estatico basta; no construyas otra app. Cada candidato debe permitir inspeccionar su programa y las operaciones que usa. Un nombre diferente no equivale a una estructura nueva.

Los SVG estructurales existentes pueden estudiarse despues como otro dialecto. La falta de etiquetas de roles no prohibe representar los grupos, formas o transformaciones que contienen. No inventes semantica del mundo para hacerlos pasar por semantic-icons-v1.

## 7. Un entrypoint y salidas localizables

El CLI de FLUJO queda reservado para capacidades portables. Este experimento
es de MAK y tiene un único entrypoint local: `tools/grammar_runner.py`. No
inventes otro paquete ni vuelvas a exponerlo desde FLUJO.

Forma propuesta para la primera ejecucion:

~~~bash
PYTHONPATH=/home/mak /home/mak/.venv/bin/python /home/mak/tools/grammar_runner.py run --corpus /home/mak/work/grammar-lab-20260912/corpus_manifest.json --generations 3 --seed 42 --max-candidates 24 --output /home/mak/work/grammar-runs/first-run
~~~

Forma propuesta para continuarla:

~~~bash
PYTHONPATH=/home/mak /home/mak/.venv/bin/python /home/mak/tools/grammar_runner.py resume --checkpoint /home/mak/work/grammar-runs/first-run/checkpoint.json
~~~

Comprueba estas invocaciones en el entorno elegido y documenta su ruta absoluta real si el CLI pertenece a un entorno virtual. La identidad declarada en pyproject.toml no demuestra que el comando este instalado. Si first-run ya existe, reanudalo o usa otro directorio identificado; no sobrescribas la evidencia.

Cada run deja, en el mismo directorio:

| Salida | Uso |
| --- | --- |
| index.html | Ver entradas y candidatos generados |
| svg/ | Salidas graficas inspeccionables |
| programs/ | Programas de candidatos y referencias a operaciones |
| library.json | Biblioteca inicial y operaciones descubiertas |
| checkpoint.json | Version, entradas, semilla, generacion y estado de busqueda |
| metrics.json | Conservacion, reutilizacion, coste y limites medidos |

Adapta nombres si el runner existente tiene un contrato equivalente y publica las rutas reales. Todos los enlaces de la vista deben resolverse en MAK. Los JSON son soporte interno; no sustituyen el motor ni sus salidas visibles.

## 8. Comprobacion y dos resultados distintos

Prepara una comparacion acotada del vocabulario inicial y el ampliado sobre los mismos recursos. Cuenta la biblioteca y los residuos de forma consistente. Comprueba el metodo efectivo, la expansion, la reutilizacion cuando exista y el render.

**Una comprobacion satisfecha no se repite salvo un cambio material que pueda afectar su resultado o un fallo observado.** No hay una obligacion de pasarla dos veces. Tampoco se crea otra pregunta por demostrar nuevamente la misma propiedad.

Distingue:

- **Motor operativo:** el comando ejecuta el metodo, genera candidatos visibles, persiste y reanuda el trabajo con entradas y resultados inspeccionables.
- **Resultado experimental:** que abstracciones aparecieron, donde se reutilizaron, si hubo ahorro o beneficio estructural y que limites tiene la evidencia.

El resultado experimental puede ser negativo. No exijas ahorro positivo o transferencia universal para terminar la implementacion; tampoco declares aprendizaje si no lo hubo. Si no aparece una abstraccion, conserva el motor, la biblioteca resultante aunque este vacia, los candidatos y la conclusion limitada. No falsifiques una regla para cumplir el checklist.

## 9. Trabajo autonomo sin otro bucle de informes

Tu autorizacion de este encargo cubre implementar, probar y ejecutar localmente este ciclo, conservando los datos originales y los presupuestos autorizados. No esperes otro prompt tecnico para pasar de un subpaso al siguiente.

Usa el Conductor existente para trabajos efectivos del experimento. La recuperacion de la sonda Q-001 y su job de593ad5-992e-4b96-ad13-ae62928262a7 ya concluyeron; un handler que solo devuelve validated=true no ejecuta el aprendizaje. Registra un entrypoint y checkpoint de la etapa real.

El agente competente implementa y resuelve decisiones; el programa ejecuta las generaciones. No impongas un LLM local al razonamiento ni abras gasto externo ilimitado. Fija limites de lote, tiempo, memoria y reintentos. Guarda version del codigo, datos, semillas y biblioteca.

Comprueba una interrupcion/reanudacion del trabajo real y ofrece una forma de ver estado y detenerlo. Una vez agotado el lote, conserva los candidatos y termina o espera una entrada nueva. Una activacion sin trabajo, evidencia o presupuesto nuevo no debe llamar al LLM para volver a certificar que falta aprendizaje.

Mantiene un unico hito funcional. Un fallo concreto puede justificar corregir una pieza; repetir sin informacion obliga a cambiar de enfoque o cerrar con un impedimento identificado. No abras una cadena de recibos, permisos, hashes, auditorias o afirmaciones negativas.

Si administras un timer de este experimento que provoca repeticiones, identifica su ID y pausalo al cerrar, preservando su configuracion. No toques servicios generales. MAK conserva codigo, estado y salidas aunque Windows se apague; los informes de WIN ya publicados en peer_reports son aportes opcionales, no una dependencia.

## 10. Commit, push y cierre

La lectura de esta consultoria encontro 94 entradas cambiadas y un borrado previo de README en /home/mak. Preserva el trabajo ajeno. Selecciona solo archivos del motor y sus pruebas/instrucciones pertinentes; no hagas git add . sobre la raiz del home.

Revisa diff, rama, remoto y staged antes de un commit. Aisla tu cambio si hace falta sin borrar modificaciones ajenas. No publiques datos privados, entornos, caches o cientos de reportes para aparentar una entrega completa.

Si el usuario ya pidio commit/push en el encargo vigente, ejecútalos sin volver a preguntarle que repositorio es. El remoto observado es vibecodeine-legacy. La forma del push normal es:

    git -C /home/mak push vibecodeine-legacy HEAD:<rama-de-destino-verificada>

Sustituye el marcador: cuando el destino autorizado sea main, usa HEAD:main. No uses force-push para superar divergencias. Verifica el SHA remoto y declara cualquier rechazo concreto. Si el push no esta encargado, deja claro ese limite sin detener la implementacion ni fingir publicacion.

Al finalizar distingue: motor operativo o impedimento concreto, resultado experimental positivo/negativo, proceso activo/detenido y commit/push hechos o pendientes. Cambia la siguiente accion heredada Q-1560 por el estado real de este hito, conservando el historial.

La respuesta al usuario debe indicar el comando que probaste, donde abrir la salida visible, que operacion se aprendio y reutilizo si existio, y como continuar o detener la ejecucion. **No cierres con otro reporte como sustituto del motor; no mantengas agentes activos inventando preguntas cuando el hito ya termino.**
