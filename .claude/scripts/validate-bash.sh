#!/bin/bash
# PreToolUse Bash guard: los deny de Read() NO aplican a Bash, asi que
# grep -r / find . / cat escanean node_modules/.git/build y queman contexto.
# Este hook bloquea SCANS que devuelven contenido de dirs pesados, pero DEJA
# pasar cleanups (rm/-delete/-exec), metadata (du/wc/ls -d) y git, y cualquier
# comando ya scopeado (--exclude/-prune/-not -path).  Exit 2 = bloquear.
cmd=$(py -c "import sys,json; print((json.load(sys.stdin).get('tool_input') or {}).get('command',''))" 2>/dev/null)
[ -z "$cmd" ] && exit 0

# 1) ALLOW: verbos no-lectura o ya scopeados (aunque mencionen un dir pesado)
if printf '%s' "$cmd" | grep -qE '(\brm\b|-delete|-exec|\bdu\b|\bwc\b|\bgit\b|--exclude|--exclude-dir|-not[[:space:]]+-path|-prune|\bmv\b|\bcp\b)'; then
  exit 0
fi

# 2) BLOCK: lectura recursiva/volcado que ADEMAS toca un dir pesado
is_scan='(grep[[:space:]]+-[a-zA-Z]*[rR]|(^|[|&;[:space:]])rg[[:space:]]|find[[:space:]]+[./]|(^|[|&;[:space:]])cat[[:space:]]|(^|[|&;[:space:]])head[[:space:]]|(^|[|&;[:space:]])tail[[:space:]]|ls[[:space:]]+-[a-zA-Z]*R)'
heavy='(node_modules|__pycache__|\.git/|/dist/|/build/|\.pytest_cache|\.venv/)'
if printf '%s' "$cmd" | grep -qE "$is_scan" && printf '%s' "$cmd" | grep -qE "$heavy"; then
  echo "BLOCKED: scan que devuelve contenido de un dir pesado (quema contexto). Usa el Grep tool (respeta gitignore) o scopea/excluye la ruta." >&2
  exit 2
fi
exit 0
