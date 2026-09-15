# iskvw · la cara visible

El portafolio cambia seguido. Esta carpeta separa fuentes, contrato y pieles:
**cambiar el estilo no significa rehacer el sitio ni reescribir los datos**.

```
  datos/obras.json     catálogo pequeño de herramientas/obras declaradas a mano
  datos/micelio.json   snapshot de relaciones que MAK produjo
  datos/campo.json     posiciones medidas y capas del archivo
  datos/archivo.json   contenido regenerable que consume una piel (no versionada)
  datos/portafolio.json formato regenerable: selección completa y orden (no versionado)
  ESQUEMA_ARCHIVO.md   contrato de forma y reglas de la proyección
  cultura/mak_plataforma/contrato_archivo.py  conversión pura compartida
  PROMPT_ESTETICA.md   instrucciones para pedir una piel nueva
  piel/lib/skin_runtime.js runtime común: carga, orden y cambio de piel
  piel/                cada estilo de portafolio, en su propia carpeta
```

## Para pedir un estilo nuevo

Pasale a un agente —Arena, Google AI Studio, el que sea— estos recursos:

    PROMPT_ESTETICA.md
    cultura/mak_plataforma/contrato_archivo.py
    datos/ESQUEMA.md

Lo que devuelva va a `piel/<nombre>/`. No tiene que tocar `datos/` ni nada más.
Si para que funcione hay que editar el contenido o inventar campos, la
propuesta no cumple el contrato.

La raíz abre `campo`; `campo` y `terminal` consumen el mismo `portafolio.json` +
`archivo.json`. El selector común conserva la query y el hash de la lectura
actual. La vista 3D de venues vive en `tools/venue3d/`, fuera de las pieles.

## Por qué así

Tres razones, y las tres son del autor:

- **El estilo se reemplaza entero, no se parchea.** Cada piel vive aparte; la
  anterior no se borra.
- **El sitio no puede mentir.** Ningún elemento afirma un dato que no tiene: es
  la regla que gobierna todo este repo.
- **No es un sitio con título y menú.** La interfaz puede ser parte de la obra.
  Está explicado en el contrato.
