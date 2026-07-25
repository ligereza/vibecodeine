# LAST HANDOFF -- estado para el proximo agente

Version: 0.56.1 | Fecha: 2026-07-25 | Identidad: Cauce | sesion:
orquestacion para el sucesor (director Fable, background job).

## Sesion 2026-07-25 (orquestacion) -- HECHO

1. RESCATE: working tree de la sesion fallida commiteado y pusheado en
   show/dref-preshow-20260724 (commit 69118fb): src/flujo/rd/eventos.py +
   tests/test_rd_eventos.py (18 verdes) + hub.py (4 contadores en _get_rd_db)
   + context/failed-handoff.md. Nada quedo suelto en el checkout.
2. PLAN DE MISION: context/ORQUESTACION_SUCESOR.md (este PR) = entrada
   obligatoria del proximo director. Fases F0-F5 + triage vivo/muerto con
   evidencia + decisiones abiertas del usuario. Diagnostico central: el repo
   tiene ratchets para AGREGAR y ninguno para RETIRAR herramientas; F5 crea el
   mecanismo (registro VIVO/MUERTO en CAPACIDADES.md + regla de retiro).
3. Leccion de la sesion: un inventario Haiku entrego 2 de 3 claims falsas
   (spot-check con grep las refuto). Reporte barato = claim, no hecho.

## PROXIMO (en orden, detalle en ORQUESTACION_SUCESOR.md)

F0 cerrar rescate (4 contadores RdDbPanel + PR contra rd) -> F1 poda con
certificado de defuncion -> F2 docs/OPERACION_APP.md -> F3 division RD/ISKVW
(decision usuario) -> F4 suplementos en app (decision usuario) -> F5 registro
VIVO/MUERTO + regla de retiro.

BLOCKERS: 4 decisiones del usuario (seccion 3 del doc).

Historia anterior: docs/handoffs/archive/LAST_HANDOFF_20260620_20260724.md
(archivado 2026-07-25, regla de tope 350 lineas)
