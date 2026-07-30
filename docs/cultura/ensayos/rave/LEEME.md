# El informe rave: ensayo + anexo iconográfico

Qué hay acá, y qué regenera qué.

| Archivo | Qué es | Se edita a mano |
|---|---|---|
| `ensayo.md` | El ensayo. Formato ENSAYO (siete exigencias, ver [`../../FORMATO_ENSAYO.md`](../../FORMATO_ENSAYO.md)) | **sí** |
| `iconos/*.svg` | Los 16 íconos animados. La FUENTE | **sí** |
| `iconos.json` | El manifiesto: un concepto nombrable por entrada, con el `ancla` al pasaje que lo justifica | **sí** |
| `GUIA-DE-EDICION.md` | Los 4 niveles de riesgo al editar un ícono | **sí** |
| `galeria.html` | La galería, con el taller del motor semántico | **no: GENERADA** |

## Los comandos

```bash
# ¿está sano? (7 clases de error; la útil es la var(--x) usada y no declarada)
py tools/iconos_conjunto.py validar --raiz docs/cultura/ensayos/rave

# regenerar la galería después de editar un .svg o el manifiesto
py tools/iconos_conjunto.py construir --raiz docs/cultura/ensayos/rave --titulo "EL INFORME RAVE"

# ¿de verdad se mueven? cuenta cuadros distintos por ícono (los GIF no entran al repo)
py tools/iconos_conjunto.py animar --raiz docs/cultura/ensayos/rave --salida <scratchpad>
```

## Lo que hay que saber antes de tocar

- **El artefacto es una animación, no un ícono.** Cada `.svg` abre con su paleta y
  sus velocidades declaradas como variables: cambiarlas no puede romper la
  animación, porque la apariencia está separada del motor. Los cuatro niveles de
  riesgo están en la guía.
- **Cada `.svg` funciona solo.** Arrastrá `iconos/05-shoom-smiley-acid-house.svg`
  al navegador y se ve animado, sin pasar por la galería. Así se itera rápido.
- **El estilo no se unifica.** Son 16 lenguajes visuales distintos a propósito.
  El validador cuida que no se rompan, no que se parezcan.
- **`ancla` no es decoración.** Es el pasaje del ensayo que justifica el ícono, y
  `tests/test_ensayo_rave.py` exige que sea un título real del documento.
- **Las fuentes del ensayo están declaradas como deuda** en su cabecera: el texto
  cita fuentes que no viajaron con el material original. Se completan leyendo, no
  inventando una URL.
- Medido el 2026-07-30: **los dieciséis dan 10 de 10 cuadros distintos**. La
  primera medición acusó a `11-inclusividad-raices-queer-negras` de estar casi
  estático y era falso: el defecto era del instrumento —el avance de la
  animación se inyectaba después de la palabra `infinite` y en una regla
  `... infinite alternate` dejaba `alternate` colgando, así que el navegador
  descartaba la declaración entera. Ahora el avance va como regla global y
  `tests/test_iconos_conjunto.py` exige que todo ícono que declara `@keyframes`
  se mueva dentro de **su propio** ciclo.

## De dónde salió

De una sesión en la nube (2026-07-28) que empezó como un encargo de ilustración y
terminó en una investigación sobre cómo hacer que un agente ciego produzca
artefactos visuales confiables. El porqué, con mediciones y límites honestos, en
[`../../MOTOR_SEMANTICO.md`](../../MOTOR_SEMANTICO.md); las fuentes de esa
investigación, verbatim, en
[`../../REFERENCIAS_MOTOR.md`](../../REFERENCIAS_MOTOR.md).
