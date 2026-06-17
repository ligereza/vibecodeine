#!/usr/bin/env bash
# finish_airdrop.sh — Cierra el flujo después de aplicar un airdrop

echo ""
echo "════════════════════════════════════════════════════════════"
echo "           FLUJO — Finalizar Airdrop"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "1. Estado actual:"
git status --short

echo ""
echo "2. Ejecutando pruebas..."
py -m pytest tests/ -q --tb=no 2>/dev/null || python3 -m pytest tests/ -q --tb=no 2>/dev/null || echo "Tests skipped"

echo ""
echo "3. Checkpoint recomendado:"
echo "   bash scripts/checkpoint.sh \"flujo v0.15 - [descripción]\""

echo ""
echo "4. Comandos para commit:"
echo "   git add ."
echo "   git commit -m \"feat: [descripción]\""
echo "   git push"

echo ""
echo "════════════════════════════════════════════════════════════"
