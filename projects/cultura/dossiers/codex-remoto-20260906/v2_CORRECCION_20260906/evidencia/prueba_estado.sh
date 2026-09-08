#!/usr/bin/env bash
# Prueba de estado de IRIS y de la curaduría persistida. Corte declarado en la salida.
# SOLO LECTURA: hace GET y un POST de control cuyo 404 esperado prueba que la
# superficie servida no acepta escritura. No modifica ningún archivo de MAK.
# Uso: bash evidencia/prueba_estado.sh
set -u
B="${IRIS_BASE:-http://127.0.0.1:8900}"
echo "# prueba_estado.sh  ---  corte $(date -Is)"
echo "# base HTTP: $B"
echo
echo "## 1. Superficie servida (universo A: iskvw)"
printf "%-38s %-5s %-10s %s\n" RUTA HTTP BYTES TIPO
for r in /portafolio/ /portafolio/editor.html /portafolio/mesa_montaje.js \
         /portafolio/datos/archivo.json /portafolio/datos/campo.json \
         /portafolio/datos/obras.json /portafolio/datos/curaduria.json; do
  printf "%-38s %-5s %-10s %s\n" "$r" \
    "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$B$r")" \
    "$(curl -s --max-time 10 "$B$r" | wc -c)" \
    "$(curl -s -o /dev/null -w '%{content_type}' --max-time 10 "$B$r")"
done
echo
echo "## 2. Control de escritura sobre la superficie servida (404 = solo lectura)"
printf "POST /portafolio/datos/curaduria.json -> %s\n" \
  "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -X POST -d '{}' "$B/portafolio/datos/curaduria.json")"
echo
python3 - <<'PY'
import json, collections, os, time
A = os.path.expanduser("~/iskvw/datos")
D = os.path.expanduser("~/plataforma/director_runs/portfolio-editor-20260808")
L = os.path.expanduser("~/plataforma/common_ledger.jsonl")

def jsonl(p):
    out = []
    if not os.path.exists(p):
        return out
    for ln in open(p, errors="replace"):
        ln = ln.strip()
        if ln:
            try: out.append(json.loads(ln))
            except Exception: pass
    return out

def mtime(p):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(p))) if os.path.exists(p) else "-"

print("## 3. Universo A -- iskvw (visión de máquina). NO mezclar con el universo B.")
a = json.load(open(f"{A}/archivo.json")); c = json.load(open(f"{A}/campo.json"))
u = json.load(open(f"{A}/curaduria.json"))
print(f"archivo.json   fuente={a['fuente']}  generado={a['generado']}")
print(f"               piezas={len(a['piezas'])}  vinculos={len(a['vinculos'])}  por_clase={a['meta']['por_clase']}")
print(f"campo.json     mtime={mtime(f'{A}/campo.json')}  piezas={len(c['piezas'])}"
      f"  con_percepcion={c['meta']['con_percepcion']}  filtradas={c['meta']['filtradas']}"
      f"  vecindad_conservada={c['meta']['vecindad_conservada']}")
tip = collections.Counter(x.get("tipo") for x in c["piezas"])
print("               tipificacion completa (suma debe ser %d):" % len(c["piezas"]))
tot = 0
for k, v in tip.most_common():
    print(f"                 {str(k):16} {v:>4}"); tot += v
print(f"                 {'TOTAL':16} {tot:>4}")
print(f"curaduria.json decisiones en ESTE archivo = {len(u['piezas'])}  (mtime {mtime(f'{A}/curaduria.json')})")

print()
print("## 4. Universo B -- portfolio-editor (decision humana persistida)")
inbox = f"{D}/PORTFOLIO_INBOX.json"
if os.path.exists(inbox):
    ib = json.load(open(inbox))
    print(f"PORTFOLIO_INBOX.json  schema={ib.get('schema')}  status={ib.get('status')}"
          f"  total={ib.get('total')}  assets={ib.get('available_assets')}  mtime={mtime(inbox)}")
    print("                      tipo_contenido=",
          dict(collections.Counter(x.get("tipo_contenido") for x in ib["items"])))
sel = jsonl(f"{D}/selections.jsonl"); cla = jsonl(f"{D}/classifications.jsonl")
dra = jsonl(f"{D}/decision_drafts.jsonl"); con = jsonl(f"{D}/connections.jsonl")
ts = sorted(r.get("ts", "") for r in sel if r.get("ts"))
print(f"selections.jsonl      filas={len(sel)}  items_distintos={len({r.get('item_id') for r in sel})}"
      f"  sesiones={len({r.get('session_id') for r in sel if r.get('session_id')})}")
print(f"                      rango={ts[0] if ts else '-'} -> {ts[-1] if ts else '-'}")
print("                      decision=", dict(collections.Counter(r.get("decision") for r in sel)))
print("                      reason_code=", dict(collections.Counter(r.get("reason_code") for r in sel)))
print("                      provider=", dict(collections.Counter((r.get("work") or {}).get("provider") for r in sel)))
print(f"classifications.jsonl filas={len(cla)}")
print("                      status=", dict(collections.Counter(r.get("status") for r in cla)))
print("                      promotion=", dict(collections.Counter(r.get("promotion") for r in cla)))
fk = collections.Counter()
for r in cla: fk.update((r.get("fields") or {}).keys())
print("                      campos=", dict(fk))
print(f"decision_drafts.jsonl filas={len(dra)}   connections.jsonl filas={len(con)}")
led = jsonl(L); isk = [r for r in led if r.get("domain") == "iskvw"]
print(f"common_ledger.jsonl   filas={len(led)}  dominio iskvw={len(isk)}")
print("                      type=", dict(collections.Counter(r.get("type") for r in isk)))
print("                      action=", dict(collections.Counter(r.get("action") for r in isk)))
print("                      owner=", dict(collections.Counter(r.get("owner") for r in isk)))

print()
print("## 5. Compilador de dossier (contrato, sin ejecutarlo sobre datos reales)")
cp = os.path.expanduser("~/tools/compile_portfolio_dossier.py")
if os.path.exists(cp):
    import sys
    sys.path.insert(0, os.path.expanduser("~"))
    sys.path.insert(0, os.path.expanduser("~/flujo/src"))
    try:
        from flujo.knowledge.portfolio_dossier import (
            compile_portfolio_dossier, PortfolioDossierError,
            SCHEMA, PLAN_SCHEMA, PRACTICE_SCHEMA)
        print(f"{cp}: existe y su motor carga")
        print(f"  salida={SCHEMA}")
        print(f"  entradas={PLAN_SCHEMA} + {PRACTICE_SCHEMA}")
        try:
            compile_portfolio_dossier({}, {})
            print("  AVISO: acepta entradas vacias, el contrato no valida")
        except PortfolioDossierError as e:
            print(f"  contrato activo: rechaza entradas vacias con {str(e).count(',')+1} errores de validacion")
        print("  LIMITE: consume un plan y un estado de evidencia; NO lee el archivo")
        print("  del artista, NO abre una base de datos y NO publica un asset.")
    except Exception as e:
        print(f"{cp}: no se pudo cargar el motor -> {type(e).__name__}: {e}")
else:
    print(f"{cp}: NO EXISTE")
PY
