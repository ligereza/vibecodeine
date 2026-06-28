# logo_clean_lab

Proyecto experimental para mejorar limpieza de logos en Illustrator.

## Estado

**Por desarrollar / experimental.**

El objetivo no es crear una herramienta automatica perfecta, sino construir un laboratorio reproducible para probar scripts de limpieza vectorial y aprender de resultados reales.

## Problema

Al arreglar logos en Illustrator aparecen imperfecciones pequenas:

- nodos que deberian compartir la misma X o Y;
- lineas perimetrales casi verticales/horizontales pero levemente torcidas;
- puntos extra sobre tramos rectos;
- handles que siguen curvando hacia afuera aunque el nodo ya quedo alineado;
- letras mixtas como B/R/P/D donde un nodo toca un tramo recto y una curva al mismo tiempo.

## Decision actual

Se consolido un script principal:

```txt
tools/illustrator/scripts/logo_clean_master.jsx
```

El script fusiona los aprendizajes de varias pruebas fallidas y parcialmente buenas.

## Flujo recomendado

1. Abrir logo en Illustrator.
2. Convertir texto a contornos.
3. Seleccionar palabra/letra/logo.
4. Ejecutar `logo_clean_master.jsx`.
5. Probar primero modo `A = Audit`.
6. Luego usar:

```txt
W = palabra completa
O = letra/forma recta
R = letra/forma redonda
M = micro limpieza sin palabra
```

7. Guardar reporte de aprendizaje si el script lo ofrece.
8. Registrar resultado en `learning/logo_clean_results.jsonl` cuando corresponda.

## Carpetas

```txt
samples/   ejemplos locales o publicos de prueba
reports/   reportes exportados desde Illustrator
learning/  resumen acumulativo para aprender de fallos y aciertos
docs/      notas tecnicas, pruebas y errores
```

## Privacidad

No subir logos reales de clientes al repo publico.

Usar estas carpetas solo con:

- ejemplos propios;
- logos ficticios;
- archivos sanitizados;
- reportes sin datos sensibles.

Los logos reales deben quedar locales o en repo privado.

## Proximo paso

Construir un pequeno dataset de pruebas:

```txt
10 resultados buenos
10 resultados malos
notas de que letra se deformo
modo usado
puntos antes/despues
```

Con eso se ajustara `logo_clean_master.jsx` con evidencia, no con suposiciones.
