#!/usr/bin/env python3
"""roles.py -- matriz de trabajo autonomo del organismo MAK. EDITABLE.

Postura: THROUGHPUT-FIRST. Los modelos rapidos (cerebras/groq/local) hacen el
grueso; el capaz (azure gpt-5-mini) y el coder fuerte (NIM deepseek-v4-pro) se
reservan para roles de decision -- y eso YA vive en los modos:
  - research 'cadena'  : etapas rapidas + sintesis con el capaz
  - research 'refutar' : tesis/antitesis rapidas + JUEZ capaz
  - codex 'generar'    : planner=azure (spec) + coder=NIM-pro (draft)
  - codex 'revisar'    : 3 lentes DeepSeek + veredicto capaz (limpiar/dogfood)
Por eso el orquestador aplica la politica ELIGIENDO EL MODO por verbo.

El fallback offline lo maneja red_ok() en research_lib/codex_lib: sin internet,
el mismo rol corre en local (gemma3 / deepseek-coder); al volver la red, vuelve
a la nube. Aca solo se define QUE trabajo y a QUE RITMO.
"""

# verbo -> como se despacha. depto+modo ya traen los modelos correctos por rol.
VERBOS = [
    {"verbo": "multiplicar", "depto": "research", "modo": "research", "fuente": "concepto"},
    {"verbo": "definir",     "depto": "research", "modo": "research", "fuente": "definir"},
    {"verbo": "limpiar",     "depto": "codex",    "modo": "revisar",  "fuente": "modulo"},
    {"verbo": "desarrollar", "depto": "codex",    "modo": "generar",  "fuente": "backlog"},
]

# ritmo (throughput-first pero gentil con cupo/CPU). el cron dispara cada CADA_MIN;
# GAP evita amontonar; offline el local es serial+lento -> mas espacio.
CADA_MIN = 30
MAX_DIA = 24            # tope de tareas autonomas por dia (evita quemar cupo)
GAP_MIN = 22            # minimo entre tareas (online)
GAP_MIN_OFFLINE = 50    # offline: mas espacio (el GPU hace una a la vez)
LOAD_MAX = 3.0          # si load1 supera esto, el cuerpo esta ocupado: saltar

# 'limpiar' rota estos modulos del organismo (dogfood). rutas bajo /home/mak.
MODULOS = [
    "/home/mak/research/research_lib.py",
    "/home/mak/codex/codex_lib.py",
    "/home/mak/plataforma/hub.py",
    "/home/mak/plataforma/filtro_entrada.py",
    "/home/mak/plataforma/latido.py",
    "/home/mak/lenguaje/hook_barrido.py",
]

# SEMILLAS ya no es el motor sino la semilla de ARRANQUE; el motor es
# ~/plataforma/backlog.jsonl (cosechado de las LAGUNAS DE INFORMACION de cada
# informe por backlog.py; ver diseno/eventos_y_backlog.md).
SEMILLAS = [
    "genealogia cultural de la tilde y los signos diacriticos del castellano",
    "el paradigma indiciario de Ginzburg como lente para leer registros culturales",
    "drogas de diseno en la cultura electronica: historia, estetica y reduccion de dano",
    "la gramatica del telar como sistema generativo de patrones (field, border, medallion)",
    "esteganografia cultural: senales de baja entropia en el lenguaje cotidiano",
    "entropia de archivos borrados: el git log como poetica del descarte",
    "branding de cepas y diagramas de Markush: el mito del linaje como retorica visual",
    "herramientas espejo (dual-use) en el arte digital: el filo esta en la aplicacion",
]
