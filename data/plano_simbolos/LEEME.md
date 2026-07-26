# Símbolos propios del plano

Acá van los archivos `.svg` de los íconos que agregues al plano.

1. Exportá el ícono como SVG y guardalo en esta carpeta.
2. Declaralo en `data/plano_simbolos.json` (ese archivo lleva las instrucciones
   y un ejemplo listo para copiar).
3. Generá el plano de nuevo.

Si el archivo no aparece, si el nombre no coincide o si algún dato del bloque
está mal, el programa **avisa por pantalla** y sigue con el resto del plano. Un
ícono nunca desaparece en silencio.

**Truco de diseño:** si en el SVG usás `currentColor` en lugar de un color fijo,
el ícono toma el color que le declares en el JSON, y así el mismo archivo se ve
bien en el plano oscuro y en el blanco.

El ícono se reescala solo para calzar en su casilla, respetando su proporción.
No hace falta que lo exportes a un tamaño determinado.

## El archivo de ejemplo

`_ejemplo_hidratacion.svg` está acá sólo como referencia de cómo se ve un SVG
que funciona (fijate en `currentColor`). **No está declarado en el catálogo**, o
sea que no aparece en ningún plano: no es un símbolo real de la operación, es
una muestra para copiar. Los símbolos de verdad los definís vos.
