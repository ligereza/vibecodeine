# Plan de cierre post-compact

Este es el plan director vigente. No crear otra herramienta ni otra ronda externa sin cerrar el gate anterior.

1. Cerrar PR #498: CI Ubuntu/Windows, merge a `main`, sincronizar MAK y verificar hashes/compilacion.
2. Probar contrato iskvw: lectura de obra, seleccion, relaciones y estado publico; separar archivo, curatoria y research.
3. Ejecutar respiracion completa: Vigia -> oportunidad -> contexto artistico -> juez Ollama -> ledger -> panel -> revision humana.
4. Probar supervivencia sin premium: Watsonx/AWS ausentes con Ollama activo; luego Ollama caido con fallback determinista.
5. Derivar estado operativo unico para ramas, CI, servicios, ledger, snapshots y publicacion; reescribir `LAST_HANDOFF`, no seguir acumulando contradicciones.
6. Confirmar MAK autonomo por cron: cola humana y reparaciones primero; `repasar` no fabrica ensayos cuando existen pendientes.
7. Medir SVG y obra: actualizar `README.svg`; probar icono representativo, animado y laser; distinguir RD, iskvw, Adobe y animacion.
8. Separar radar artistico: Fondart, residencias, clientes, colaboraciones, enfermeria y familia con privacidad y sin contacto automatico.
9. Limpiar ramas: conservar solo `main`, `mak`, `rd`, `iskvw`; rescatar trabajo solo si esta probado.
10. Cerrar con tests focalizados, `flujo verify`, ledger no vacio, evidencia real de MAK y memoria final.

Criterio de cierre: MAK detecta, clasifica, rechaza, conserva evidencia y deja una siguiente accion humana clara; no se considera autonomo por generar mas texto.

## Integraciones de segundo nivel

Estas capas se agregan al cierre, sin crear otro framework ni duplicar
`tandas.py`, `ledger.py`, `discernment.py` o `benchmark.py`.

11. **Degradacion comprobable**: ejecutar Watsonx/AWS caidos con Ollama y luego Ollama caido con el juez determinista; ningun camino puede promover hechos sin evidencia.
12. **Presupuesto por area**: imponer limites de tokens, tamano de evidencia, timeout, reintentos y cantidad de items; registrar el motivo de cada corte.
13. **Contratos negativos**: cada perfil debe demostrar casos `accept`, `revise` y `reject`; especialmente RD primario, iskvw publico/curatoria y oportunidades.
14. **Trazabilidad de decision**: guardar proveedor, lote, evidencia, juez, version de politica y siguiente accion humana en la misma cadena de ledger.
15. **Memoria activa**: detectar duplicados, contradicciones, evidencia vencida y entradas sin consumidor antes de permitir otra produccion.
16. **Respiracion por dominio**: demostrar ciclos independientes para RD, iskvw, SVG, Adobe y radar artistico; prohibir una salida generica para todos.
17. **Autonomia con freno**: el cron solo atiende cola real, cuarentena, reparacion o medicion; si no existe proposito, ejecuta revision ejecutiva y no inventa ensayos.
18. **Criterio de nivel superior**: medir decisiones correctas, artefactos reutilizables, evidencia conservada y reduccion del caos; no contar informes como exito.

Orden director: cerrar primero los gates 1–10; luego implementar 11–18 en bloques
medibles, empezando por degradacion, presupuesto y contratos negativos.
