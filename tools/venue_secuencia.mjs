// A venue as a DETERMINISTIC orbit: N fixed camera angles, one line-only SVG
// each. The artist had already faked a 360 viewer by hand, frame by frame, over
// a real reference; this industrialises that technique instead of replacing it.
// The frames come out of the SAME projection the live viewer runs (see
// tools/venue3d_contexto.mjs), so the reel and the screen cannot disagree.
//
// Line-only is the point: a plotter and a laser cannot rasterise, but they can
// follow a polyline. Each <g> carries data-confianza, so a laser layer can drop
// everything nobody backs before it costs a single ILDA point.
//
//   node tools/venue_secuencia.mjs                       # 120 cuadros, 1080x1080
//   node tools/venue_secuencia.mjs --cuadros 24 --salida _logs/orbita
//   node tools/venue_secuencia.mjs --venue otra-sala --aristas 400 --alto 0.35
//
// Output goes wherever --salida says (default _logs/venue_secuencia/, which is
// gitignored: these are frames, not sources -- the source is the venue JSON).
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { correr, RAIZ } from "./venue3d_contexto.mjs";

const arg = (nombre, porDefecto) => {
  const i = process.argv.indexOf("--" + nombre);
  return i > 0 && process.argv[i + 1] ? process.argv[i + 1] : porDefecto;
};

const cuadros = Math.max(1, parseInt(arg("cuadros", "120"), 10));
const lado = Math.max(64, parseInt(arg("lado", "1080"), 10));
const inclinacion = parseFloat(arg("alto", "0.45"));
const venue = arg("venue", "");
const aristas = arg("aristas", "");
const salida = join(RAIZ, arg("salida", "_logs/venue_secuencia"));

const query = [
  venue ? `venue=../../../data/venues/${venue}.json` : "",
  aristas ? `aristas=${aristas}` : "",
].filter(Boolean).join("&");

const s = await correr(query ? "?" + query : "", { ancho: lado, alto: lado, cuadros: 2 });
if (s.falla) {
  console.error("el visor no arranco:", s.falla.stack || s.falla);
  process.exit(1);
}
const nombre = s.leer("ESTADO.venue.nombre");
const dibujadas = s.leer("ESTADO.dibujadas");
const omitidas = s.leer("ESTADO.omitidas");
if (!(s.leer("ESTADO.aristas") > 0)) {
  console.error("la sala no trae geometria: no hay secuencia que exportar");
  process.exit(1);
}

mkdirSync(salida, { recursive: true });
const svgs = s.leer(
  `secuencia(${cuadros}, {alto_: ${inclinacion}, w: ${lado}, h: ${lado}})`);
let bytes = 0;
svgs.forEach((svg, i) => {
  const f = join(salida, `cuadro_${String(i).padStart(4, "0")}.svg`);
  writeFileSync(f, svg, "utf8");
  bytes += Buffer.byteLength(svg);
});

// El primero y el ultimo NO pueden ser iguales: si lo fueran, la vuelta no
// estaria repartida y el loop se trabaria en un cuadro repetido.
if (cuadros > 2 && svgs[0] === svgs[1]) {
  console.error("dos cuadros consecutivos son identicos: la orbita no avanza");
  process.exit(1);
}

console.log(`${nombre} · ${cuadros} cuadros de ${lado}x${lado} · ${dibujadas} aristas por ` +
            `cuadro${omitidas ? ` (${omitidas} fuera del tope)` : ""} · ` +
            `${(bytes / 1024).toFixed(0)} KB en ${salida}`);
