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
if command -v pytest &> /dev/null; then
    pytest -q || echo "Tests fallaron (revisa antes de continuar)"
else
    echo "pytest no encontrado, salteando tests"
fi

echo ""
echo "3. Checkpoint recomendado:"
echo "   bash scripts/checkpoint.sh \"flujo v0.15 - [descripción del airdrop]\""

echo ""
echo "4. Comandos para commit:"
echo "   git add ."
echo "   git commit -m \"feat: [descripción]\""
echo "   git push"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Cuando estés listo, ejecuta los comandos de arriba."
echo "════════════════════════════════════════════════════════════"
