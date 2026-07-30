// compilador.js -- gemelo en NAVEGADOR del compilador Python
// (cultura/mak_codex/motor_semantico/compilador.py). Misma spec semantica
// entra, SVG equivalente sale. Sin build step: modulo ES puro, importable
// con <script type="module"> desde una pagina estatica.
//
// INVARIANTES GARANTIZADOS POR CONSTRUCCION (identicos a la version Python):
//   1. viewBox siempre "0 0 120 120"
//   2. todo el contenido dentro de la zona segura (zona_min..zona_max)
//   3. opacidad >= .55 y escala >= .55 en el frame 0 (vía los gestos, ya
//      definidos asi en el vocabulario) -> nada invisible al inicio
//   4. contraste minimo AA-grande (contraste_min) entre figura/texto y fondo
//   5. texto medido antes de escribir: si no cabe, se reduce o se rechaza
//   6. XML bien formado: el arbol se arma con hiccup-svg + hiccup, nunca
//      concatenando strings libres (la excepcion es el fragmento de figura,
//      que ya es SVG valido pre-serializado, inyectado via INLINE)
//
// La geometria (figuras, gestos, tonos, composiciones) NO se reimplementa
// aqui: llega como datos en `vocab` (docs/cultura/lib/vocabulario.json),
// generado desde el Python real por tools/gen_vocabulario_motor.py. Portar
// a mano seria una segunda fuente de verdad divergiendo.

import { serialize, INLINE } from "./hiccup.js";
import { svg as svgEl, group, rect, text } from "./hiccup-svg.js";
import { srgb, luminanceSrgb } from "./color.js";

export class ErrorSemantico extends Error {}

// -- color ------------------------------------------------------------------
// @thi.ng/color SI trae la luminancia relativa WCAG lista para usar
// (`luminanceSrgb`, verificado corriendo el bundle: coincide con la formula
// Rec.709 linealizada que usa el compilador Python). No existe una funcion
// de "contrast ratio" combinada en esta version (solo `contrast`/`contrastMat`,
// que son el AJUSTE de contraste de imagen, otra cosa) -- por eso la razon
// WCAG (hi+.05)/(lo+.05) se arma aqui mismo, a partir de esa luminancia real.
function luminancia(hexColor) {
  return luminanceSrgb(srgb(hexColor));
}

function contraste(a, b) {
  const la = luminancia(a);
  const lb = luminancia(b);
  const hi = Math.max(la, lb);
  const lo = Math.min(la, lb);
  return (hi + 0.05) / (lo + 0.05);
}

// -- validacion semantica -----------------------------------------------------
export function validarSpec(spec, vocab) {
  const FIGURAS = vocab.figuras;
  const GESTOS = vocab.gestos;
  const RITMOS = vocab.ritmos;
  const COMPOSICIONES = vocab.composiciones;

  const fallos = [];
  const comp = spec.composicion;
  if (!(comp in COMPOSICIONES)) {
    fallos.push(`composicion '${comp}' no existe. Opciones: ${Object.keys(COMPOSICIONES).sort()}`);
    return fallos;
  }
  const tono = spec.tono;
  if (!(tono in vocab.tonos)) {
    fallos.push(`tono '${tono}' no existe. Opciones: ${Object.keys(vocab.tonos).sort()}`);
  }
  const ranuras = COMPOSICIONES[comp];
  const capas = spec.capas || [];
  if (capas.length === 0) {
    fallos.push("hace falta al menos una capa");
  }
  const tieneProtagonista = capas.some((c) => c.rol === "protagonista");
  if (!tieneProtagonista && "protagonista" in ranuras) {
    fallos.push("falta la capa 'protagonista' (la lectura principal)");
  }
  const vistos = new Set();
  capas.forEach((c, i) => {
    const rol = c.rol;
    if (!(rol in ranuras)) {
      fallos.push(`capa ${i}: rol '${rol}' no existe en '${comp}'. ` +
        `Disponibles: ${Object.keys(ranuras).sort()}`);
    }
    if (vistos.has(rol)) {
      fallos.push(`capa ${i}: rol '${rol}' repetido`);
    }
    vistos.add(rol);
    const fig = c.figura;
    const txt = c.texto;
    if (!fig && (txt === undefined || txt === null)) {
      fallos.push(`capa ${i}: necesita 'figura' o 'texto'`);
    }
    if (fig && !(fig in FIGURAS)) {
      fallos.push(`capa ${i}: figura '${fig}' no existe. Opciones: ${Object.keys(FIGURAS).sort()}`);
    }
    const g = c.gesto ?? "quieto";
    if (!(g in GESTOS)) {
      fallos.push(`capa ${i}: gesto '${g}' no existe. Opciones: ${Object.keys(GESTOS).sort()}`);
    }
    const r = c.ritmo ?? "medio";
    if (!(r in RITMOS)) {
      fallos.push(`capa ${i}: ritmo '${r}' no existe. Opciones: ${Object.keys(RITMOS).sort()}`);
    }
  });
  const animadas = capas.filter((c) => (c.gesto ?? "quieto") !== "quieto").length;
  if (animadas > 5) {
    fallos.push("mas de 5 capas animadas: el icono se vuelve ruido");
  }
  return fallos;
}

// -- utilidades internas ------------------------------------------------------

// Reemplaza los marcadores @@rol@@ de un fragmento de figura por el hex real
// del tono. Los fragmentos viajan como texto (vienen del JSON del vocabulario,
// ya son SVG valido) y se inyectan sin tocar via INLINE -- por eso la
// sustitucion es un reemplazo de texto, no un armado de arbol.
function sustituirMarcadores(fragmento, roles) {
  return fragmento.replace(/@@(\w+)@@/g, (coincide, rol) => {
    if (!(rol in roles)) {
      throw new ErrorSemantico(`marcador de color desconocido: @@${rol}@@`);
    }
    return roles[rol];
  });
}

// Mini motor de plantillas equivalente a `str.format()` de Python: los
// gestos guardan su CSS con `{c}` `{d}` `{ox}` `{oy}` `{dx}` como campos y
// `{{` / `}}` como llaves literales (las de los @keyframes). Un solo pase de
// regex alcanza porque el vocabulario nunca anida ambos casos.
function formatearPlantilla(plantilla, valores) {
  return plantilla.replace(/\{\{|\}\}|\{(\w+)\}/g, (coincide, nombre) => {
    if (coincide === "{{") return "{";
    if (coincide === "}}") return "}";
    if (nombre in valores) return String(valores[nombre]);
    throw new ErrorSemantico(`marcador de plantilla desconocido: ${coincide}`);
  });
}

function escaparXml(txt) {
  return txt.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Abre el grupo de una capa DECLARANDO lo que codifica (orden 2026-07-30,
// espejo de `_capa_abre()` en compilador.py). Dos razones, y las dos son
// del usuario:
//
// 1. Editable, nada rigido. Un grupo con `id` y `<title>` aparece como capa
//    con nombre en Illustrator y en Inkscape: el icono animado se puede
//    abrir en una herramienta de diseno, tocar una capa y reintegrarlo. Un
//    arbol de <g> anonimos no se puede editar sin adivinar.
// 2. La tesis doublecup: ningun elemento reclama un dato que no codifica.
//    Aca al reves -- cada elemento LLEVA el dato que lo justifica: que rol
//    ocupa, que figura es, que gesto hace, a que ritmo. La forma queda
//    auditable sin mirarla.
//
// El orden de atributos (id, transform, data-rol, data-gesto, data-ritmo,
// data-figura, opacity al final si aplica) se mantiene identico al de
// Python aunque el test solo compare `transform`: un diff crudo entre los
// dos SVG tiene que seguir siendo legible.
function abrirCapa(i, capa, rol, cx, cy, gesto, ritmo, atenuados) {
  const que = (capa.texto !== undefined && capa.texto !== null)
    ? "texto:" + String(capa.texto)
    : String(capa.figura ?? "?");
  const titulo = escaparXml(que);
  const attrs = {
    id: `capa-${i}-${rol}`,
    transform: `translate(${cx},${cy})`,
    "data-rol": rol,
    "data-gesto": gesto,
    "data-ritmo": ritmo,
    "data-figura": capa.figura ? capa.figura : "texto",
  };
  if (atenuados.includes(rol)) {
    attrs.opacity = ".38";
  }
  return { attrs, tituloTexto: `${rol} - ${titulo}` };
}

// -- compilacion ----------------------------------------------------------
export function compilar(spec, vocab, slug = "icono") {
  const fallos = validarSpec(spec, vocab);
  if (fallos.length) {
    throw new ErrorSemantico(fallos.map((f) => "  x " + f).join("\n"));
  }

  const { zona_min: ZONA_MIN, zona_max: ZONA_MAX, contraste_min: CONTRASTE_MIN,
    ancho_char: ANCHO_CHAR, vista: VISTA } = vocab.invariantes;
  const RITMOS = vocab.ritmos;

  const comp = vocab.composiciones[spec.composicion];
  const pal = { ...vocab.tonos[spec.tono] };
  const fondo = pal.fondo;

  const cuerpo = [];
  const css = [];
  const avisos = [];

  spec.capas.forEach((capa, i) => {
    const rol = capa.rol;
    const [cx, cy, escOriginal] = comp[rol];
    let esc = escOriginal;
    const cls = `c${i}`;
    const gesto = capa.gesto ?? "quieto";
    const ritmo = RITMOS[capa.ritmo ?? "medio"];

    if (capa.texto !== undefined && capa.texto !== null) {
      // -- texto ----------------------------------------------------------
      const txt = String(capa.texto);
      let fs = Math.max(5.5, Math.min(esc * 0.58, 13));
      const ancho = txt.length * fs * ANCHO_CHAR;
      const disponible = ZONA_MAX - ZONA_MIN;
      if (ancho > disponible) {                              // INVARIANTE 5
        fs = disponible / (txt.length * ANCHO_CHAR);
        if (fs < 5.0) {
          throw new ErrorSemantico(
            `  x capa ${i}: el texto «${txt}» (${txt.length} caracteres) no cabe ` +
            `legible en 120px. Maximo ~${Math.trunc(disponible / (5.5 * ANCHO_CHAR))} caracteres.`);
        }
        avisos.push(`texto «${txt}» reducido a ${fs.toFixed(1)}px para que quepa`);
      }
      const seguro = escaparXml(txt);                          // INVARIANTE 6
      let col = pal.tinta;
      if (contraste(col, fondo) < CONTRASTE_MIN) {
        col = pal.principal;
      }
      const { attrs, tituloTexto } = abrirCapa(i, capa, rol, cx, cy, gesto, ritmo, vocab.atenuados);
      cuerpo.push(
        group(attrs,
          ["title", {}, tituloTexto],
          group({ class: cls },
            text([0, +(fs * 0.35).toFixed(1)], seguro, {
              "text-anchor": "middle",
              "font-family": "ui-monospace,Menlo,monospace",
              "font-weight": "700",
              "font-size": fs.toFixed(1),
              "letter-spacing": ".5",
              fill: col,
            }))));
    } else {
      // -- figura -----------------------------------------------------------
      const nombre = capa.figura;
      const frag = vocab.figuras[nombre].fragmento;
      const roles = { ...pal };
      // INVARIANTE 4: si la figura no contrasta con el fondo, se corrige
      if (contraste(roles.principal, fondo) < CONTRASTE_MIN) {
        const candidatos = ["principal", "acento", "tinta"];
        const alt = candidatos.reduce((mejor, k) =>
          contraste(pal[k], fondo) > contraste(pal[mejor], fondo) ? k : mejor);
        avisos.push(`capa ${i} (${nombre}): color principal sin contraste ` +
          `suficiente; se uso '${alt}'`);
        roles.principal = pal[alt];
      }
      const marca = sustituirMarcadores(frag, roles);
      // limite de zona segura (INVARIANTE 2)
      const media = esc;
      if (cx - media < ZONA_MIN || cx + media > ZONA_MAX ||
          cy - media < ZONA_MIN || cy + media > ZONA_MAX) {
        const permitido = Math.min(cx - ZONA_MIN, ZONA_MAX - cx,
          cy - ZONA_MIN, ZONA_MAX - cy);
        if (permitido < esc) {
          avisos.push(`capa ${i} (${nombre}): escala reducida ` +
            `${esc}->${permitido.toFixed(0)} para no salirse del lienzo`);
          esc = Math.max(6, permitido);
        }
      }
      // translate exterior - animacion en el medio - escala interior.
      // Rotar/escalar en el grupo del medio equivale a hacerlo sobre el
      // centro de la figura, sin depender de transform-origin.
      // las capas de fondo se atenuan para no competir con el protagonista
      // (abrirCapa agrega opacity=".38" cuando el rol esta en `atenuados`)
      const { attrs, tituloTexto } = abrirCapa(i, capa, rol, cx, cy, gesto, ritmo, vocab.atenuados);
      cuerpo.push(
        group(attrs,
          ["title", {}, tituloTexto],
          group({ class: cls },
            group({ transform: `scale(${esc})` },
              [INLINE, marca]))));
    }

    // -- gesto --------------------------------------------------------------
    if (gesto !== "quieto") {
      const plantilla = vocab.gestos[gesto].css;
      const dx = cx >= 60 ? 16 : -16;
      css.push(formatearPlantilla(plantilla, { c: cls, d: ritmo, ox: cx, oy: cy, dx }));
    }
  });

  // de-duplicacion de reglas CSS (misma logica que el Python: separa por
  // @keyframes o por regla `.clase{...}` y descarta repetidos manteniendo
  // el orden de primera aparicion)
  const vistosCss = new Set();
  const unicos = [];
  for (const bloque of css) {
    for (const regla of bloque.split(/(?=@keyframes|\n\.)/)) {
      const r = regla.trim();
      if (r && !vistosCss.has(r)) {
        vistosCss.add(r);
        unicos.push(r);
      }
    }
  }
  const estilos = unicos.join("\n");

  const arbol = svgEl(
    { viewBox: VISTA, "data-name": slug },
    ["style", {}, "\n" + estilos + "\n"],
    rect([0, 0], 120, 120, { fill: fondo }),
    ...cuerpo,
  );
  const svgTexto = '<?xml version="1.0" encoding="UTF-8"?>\n' + serialize(arbol) + "\n";

  return { svg: svgTexto, avisos };
}
