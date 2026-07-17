#!/bin/bash
# instalar_diccionarios.sh -- baja el diccionario hunspell de espanol (via el
# descargador seguro) y extrae la lista plana es.txt para lenguaje_lib.
# Si la URL rota, buscar la nueva en github.com/LibreOffice/dictionaries.
set -eu
DEST="$HOME/lenguaje/diccionarios"
mkdir -p "$DEST"
BASE_URL="https://raw.githubusercontent.com/LibreOffice/dictionaries/master/es"

python3 "$HOME/plataforma/descargar.py" "$BASE_URL/es_ES.dic" --dest "$DEST"
python3 "$HOME/plataforma/descargar.py" "$BASE_URL/es_ES.aff" --dest "$DEST"

python3 - <<'PY'
import os, unicodedata
dest = os.path.expanduser("~/lenguaje/diccionarios")
palabras = set()
with open(os.path.join(dest, "es_ES.dic"), encoding="utf-8",
          errors="replace") as f:
    next(f, None)  # primera linea = conteo
    for line in f:
        w = line.split("/")[0].strip()
        if w and w[0].isalpha():
            palabras.add(unicodedata.normalize("NFC", w.lower()))
with open(os.path.join(dest, "es.txt"), "w", encoding="utf-8") as f:
    for w in sorted(palabras):
        f.write(w + "\n")
print("diccionario listo: %d palabras -> es.txt" % len(palabras))
PY
