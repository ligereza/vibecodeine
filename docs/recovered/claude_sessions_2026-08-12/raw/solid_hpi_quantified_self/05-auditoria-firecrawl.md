# Auditoría de Firecrawl

## Primera tanda

- Inventario enviado: 470 URLs.
- Tanda: `019ff181-0e38-746f-9a2e-8f72fd247cb5`.
- Estado final: cancelada por decisión del usuario.
- Capturas completadas: 43.
- Créditos utilizados: 43.

De los 43 resultados, 43 devolvieron HTTP 200, 36 contenían señales de README y 22 pasaron un filtro conservador de legibilidad. Los resultados restantes tenían ruido de GitHub, README ausente o contenido corto.

## Segunda tanda popularidad

- 40 URLs seleccionadas con GitHub API usando `sort=stars&order=desc`.
- Se excluyeron los repositorios ya procesados.
- Tanda: `019ff18d-37e2-7726-b1ad-70ef4e1988d6`.
- Formato: JSON estructurado.
- Campos: propósito, funciones, fuentes de datos, almacenamiento, local-first, privacidad, relevancia institucional, mantenimiento, ruido y confianza.

Esta segunda tanda se dejó procesando; debe revisarse antes de aceptar sus conclusiones. “Popular” significa ordenado por estrellas en GitHub, no necesariamente mejor, más seguro o más mantenido.

## Regla de calidad

Firecrawl captura evidencia. No valida código, seguridad, licencia ni afirmaciones del README. Toda conclusión final debe conservar la URL, separar descripción de interpretación y marcar los campos desconocidos.
