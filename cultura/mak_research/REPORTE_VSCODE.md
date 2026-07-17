# REPORTE VSCODE

## Fase 1 — índice y digest

### Comando ejecutado

```bash
cd /home/mak/research && python3 indice.py && python3 digest.py
```

### Salida real

```text
wrote informes/INDEX.md
wrote paneles/INDEX.md
wrote DIGEST.md
wrote informes/INDEX.md
wrote paneles/INDEX.md
wrote DIGEST.md
20260715-205039-genealogia-cultural-de-la-tilde-y-los-di.md
20260715-205308-genealogia-cultural-de-la-tilde-y-los-di.md
20260715-205544-genealogia-cultural-de-la-tilde-y-los-di.md
20260715-205800-genealogia-cultural-de-la-tilde-y-los-di.md
20260715-214703-paradigma-indiciario-de-carlo-ginzburg-y.md
20260715-214959-genealogia-visual-de-los-diagramas-de-ma.md
20260715-215759-iconografia-del-double-cup-en-la-cultura.md
20260715-223556-test-progress-update.md
20260715-223617-test.md
```

### Head de INDEX.md (informes)

```md
# Índice de informes

| fecha | tema | fuentes | link |
|---|---|---|---|
| 2026-07-15 20:50 | sin tema | — | [20260715-205039-genealogia-cultural-de-la-tilde-y-los-di.md](20260715-205039-genealogia-cultural-de-la-tilde-y-los-di.md) |
| 2026-07-15 20:53 | sin tema | — | [20260715-205308-genealogia-cultural-de-la-tilde-y-los-di.md](20260715-205308-genealogia-cultural-de-la-tilde-y-los-di.md) |
| 2026-07-15 20:55 | sin tema | — | [20260715-205544-genealogia-cultural-de-la-tilde-y-los-di.md](20260715-205544-genealogia-cultural-de-la-tilde-y-los-di.md) |
```

### Head de DIGEST.md

```md
# Digest de informes (últimos 7 días)

- [20260715-205039-genealogia-cultural-de-la-tilde-y-los-di.md](informes/20260715-205039-genealogia-cultural-de-la-tilde-y-los-di.md): (sin report)
- [20260715-205308-genealogia-cultural-de-la-tilde-y-los-di.md](informes/20260715-205308-genealogia-cultural-de-la-tilde-y-los-di.md): (sin report)
- [20260715-205544-genealogia-cultural-de-la-tilde-y-los-di.md](informes/20260715-205544-genealogia-cultural-de-la-tilde-y-los-di.md): (sin report)
```

## Fase 2 — exportar.py

### Comando ejecutado

```bash
cd /home/mak/research && python3 exportar.py informes/20260715-205039-genealogia-cultural-de-la-tilde-y-los-di.md && python3 exportar.py paneles/20260715-215251-el-sample-y-la-cita-como-gesto-estetico-.md
```

### Salida real

```text
wrote informes/20260715-205039-genealogia-cultural-de-la-tilde-y-los-di.html
wrote paneles/20260715-215251-el-sample-y-la-cita-como-gesto-estetico-.html
```

## Fase 3 — estadísticas

### Comando ejecutado

```bash
cd /home/mak/research && python3 estadisticas.py
```

### Salida real

```text
wrote USO.md
```

### Resumen generado

- Proveedores: azure 8, cerebras 3, groq 13, ollama 2.
- Errores más frecuentes: groq/cerebras 403 1010, tavily key ausente, ollama IP access not allowed.
- Búsquedas Tavily: básicas 10, avanzadas 0, créditos estimados 10.
- Duración promedio: 61.41 s por meta de json.

## Revisión cruzada

### Pruebas del otro agente

```bash
cd /home/mak/research && python3 -m unittest -v test_research_lib.py test_ua.py
```

Salida real:

```text
Ran 4 tests in 0.014s

OK
```

### Watchdog

```bash
cd /home/mak/research && ./watchdog.sh && ./watchdog.sh
```

Salida real:

```text
FIRST_EXIT:0
SECOND_EXIT:0
```

Servicios detectados:

```text
python3 /home/mak/research/cola.py
python3 /home/mak/research/interfaz.py
```
