# Formato de entrega: evidencia de ejecución

La entrega no es un debate. Debe contener estos artefactos utilizables:

1. `DRY_RUN_ENVIO_20260906.md`
2. `PAQUETE_DE_ACCION_TITULAR_20260906.md`
3. `postulaciones/BORRADORES_SIN_FIRMA/FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv`
4. `postulaciones/BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md`
5. `verificador/revision_ids_y_gastos.py` o equivalente ejecutable
6. `REPORTE_EJECUCION_CLAUDE_20260906.md`, máximo una página y escrito al final

## Tabla mínima del dry-run

| Expediente | Resultado | Campos completos | Bloqueos del titular | Adjuntos/archivos | Próxima acción |
|---|---|---|---|---|---|
| Ama Amoedo | PUEDE/NO PUEDE PASAR A CUENTA | conteo verificable | identidad, CV, portfolio, cuenta | rutas y estado real | archivo exacto |
| Difusión | PUEDE/NO PUEDE PASAR A CUENTA | conteo verificable | región, identidad, Perfil Cultura | rutas y estado real | archivo exacto |
| Formativas | PUEDE/NO PUEDE PASAR A CUENTA | conteo verificable | región, estudios, asistentes, espacio | rutas y estado real | archivo exacto |
| Creación alternativa | PUEDE/NO PUEDE PASAR A CUENTA | conteo verificable | región, identidad, Perfil Cultura | rutas y estado real | sólo alternativa |

No se aceptan palabras sin resolver como `PUEDE/NO PUEDE` ni “enviable” cuando falten datos.

## Pruebas de cierre

```bash
bash VERIFICAR_INTEGRIDAD.sh
python3 verificador/verificar_presupuestos.py
bash verificador/pruebas_negativas.sh
python3 verificador/comprobacion_cruzada.py
python3 postulaciones/generar_texto_por_campo.py
```

La salida debe indicar v1 30/30, v2 coincidente, presupuestos OK, control positivo 1 y 14 defectos inyectados detectados. Si la generación modifica archivos, se regenera el manifiesto y se repite la integración.
