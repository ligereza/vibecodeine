# Certificado de archivado -- duplicados CRT phosphor

- **Fecha de archivado:** 2026-07-25
- **Causa:** `tools/crtdots.py` y `tools/crt_phosphor/crt_phosphor.py` eran el mismo
  concepto (convertidor CRT phosphor / Rutt-Etra de imagenes), duplicados entre si,
  con cero consumidores medidos -- sin test, sin comando CLI, sin import desde
  ningun otro modulo del repo -- y sin actividad desde 2026-07-03.
- **Condicion de resurreccion:** que una pieza real (candidato natural: un filtro
  visual para `tapiz` o `sala3d`) los necesite de verdad y los cablee (import +
  test + consumidor real), no que se especule sobre su utilidad.
- **Nota:** el codigo queda intacto en el historial de git (movido con `git mv`,
  no se borro nada). Recuperable en cualquier momento desde este directorio o
  desde el historial de `tools/crtdots.py` y `tools/crt_phosphor/`.
