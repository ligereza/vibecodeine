#!/bin/bash
# research.sh "tema" [iteraciones] -- wrapper del runner standalone (sin n8n)
exec python3 ~/research/research.py "$1" --iteraciones "${2:-3}" --ntfy
