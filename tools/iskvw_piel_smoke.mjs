// Smoke-run of the campo skin's inline JS with DOM stubs. Exists because a
// scope refactor (PR #403) shipped `destino`/`dy` referenced outside the
// function that defined them: green CI, dead portfolio -- the draw loop threw
// on frame one and no test executed the JS. This runs the real script in node
// and fails on ANY uncaught error during boot + the first animation frames.
//
// Since the effects patch (datos/tablero.json) it also MEASURES the patch,
// because a master flag that is off by default is exactly the kind of code
// that rots unseen: the skin is booted three times -- without a board, with
// the board that ships (flag off) and with the flag on -- and the drawing
// trace of the first two has to be identical while the third has to differ.
// "Off changes nothing" stops being a claim and becomes a number.
//
// Invoked by tests/test_iskvw_piel_smoke.py. Node >= 18 (global fetch not
// needed: fetch is stubbed).
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const html = readFileSync(join(raiz, "iskvw", "piel", "campo", "index.html"), "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!scripts.length) { console.error("no inline <script> found"); process.exit(2); }

const noop = () => {};

// -- one boot of the skin, with its own sandbox and its own drawing trace --
// `tablero` is what datos/tablero.json answers (null = the file is not there,
// which is the path every visitor took before the patch existed).
// `antes` runs inside the sandbox right before the frames, so a test can poke
// state the real data does not carry.
async function correr({ tablero = null, cuadros = 30, caminar = true, antes = null } = {}) {
  let trabajoDeNodo = 0;       // per-node draw work actually executed
  const traza = [];            // every mark: what, where, in which colour
  let pincel = "";             // current fillStyle
  const marca = (x, y) => {
    // Rounded: the point is whether the patch MOVED something, not float noise.
    traza.push(`${x.toFixed(2)},${y.toFixed(2)},${pincel}`);
  };

  const ctx2d = new Proxy({}, {
    get: (t, k) => {
      if (k === "canvas") return canvas;
      if (k === "createRadialGradient" || k === "createLinearGradient")
        return (x, y) => { trabajoDeNodo++; marca(x, y); return { addColorStop: (o, c) => traza.push(`g:${c}`) }; };
      if (k === "fillText") return (g, x, y) => { trabajoDeNodo++; marca(x, y); };
      if (k === "arc") return (x, y) => marca(x, y);
      if (k === "moveTo" || k === "lineTo") return (x, y) => marca(x, y);
      if (k === "measureText") return () => ({ width: 10 });
      if (k === "getImageData") return () => ({ data: new Uint8ClampedArray(4) });
      return noop;
    },
    set: (t, k, v) => { if (k === "fillStyle" || k === "strokeStyle") pincel = String(v); return true; },
  });
  const canvas = {
    getContext: () => ctx2d, width: 800, height: 600,
    clientWidth: 800, clientHeight: 600,
    style: {}, addEventListener: noop, removeEventListener: noop,
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  };
  const el = () => ({
    classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
    style: {}, addEventListener: noop, removeEventListener: noop,
    textContent: "", innerHTML: "", appendChild: noop, setAttribute: noop,
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  });
  const elements = new Map();
  const getEl = id => {
    if (id === "c") return canvas;
    if (!elements.has(id)) elements.set(id, el());
    return elements.get(id);
  };

  let rafQueue = [];
  const sandbox = {
    console, Math, JSON, Date, Number, Array, String, Object,
    Float64Array, Int32Array, Uint8ClampedArray, Map, Set, URLSearchParams,
    performance: { now: () => rafQueue.length * 16.7 },
    requestAnimationFrame: cb => { rafQueue.push(cb); return rafQueue.length; },
    cancelAnimationFrame: noop,
    setTimeout: (cb) => 0, clearTimeout: noop, setInterval: () => 0, clearInterval: noop,
    // fetch: resolve datos/* against the repo so the REAL data shapes are what
    // the loop chews on; anything else 404s like the fallback path expects.
    fetch: async (url) => {
      const s = String(url);
      if (/datos\/tablero\.json$/.test(s)) {
        return tablero
          ? { ok: true, json: async () => tablero }
          : { ok: false, json: async () => ({}) };
      }
      const m = s.match(/datos\/(campo|archivo|obras)\.json$/);
      if (m) {
        try {
          const txt = readFileSync(join(raiz, "iskvw", "datos", `${m[1]}.json`), "utf8");
          return { ok: true, json: async () => JSON.parse(txt) };
        } catch { return { ok: false, json: async () => ({}) }; }
      }
      return { ok: false, json: async () => ({}) };
    },
    addEventListener: noop, removeEventListener: noop, history: { replaceState: noop },
    location: { hash: "", href: "http://smoke.local/" },
    navigator: { maxTouchPoints: 0 },
    devicePixelRatio: 1, innerWidth: 800, innerHeight: 600,
  };
  sandbox.window = sandbox;
  sandbox.document = {
    getElementById: getEl,
    querySelector: () => el(), querySelectorAll: () => [],
    addEventListener: noop, removeEventListener: noop,
    body: el(), documentElement: el(), hidden: false,
    createElement: () => el(),
  };

  const context = vm.createContext(sandbox);
  let failed = null;
  // arrancar() is async and fire-and-forget: its crash surfaces as an
  // unhandled rejection on the shared microtask queue, not as a sync throw.
  const onRejection = (e) => { failed = failed || e; };
  process.on("unhandledRejection", onRejection);
  try {
    for (const src of scripts) vm.runInContext(src, context, { timeout: 10000 });
  } catch (e) { failed = e; }

  // drain microtasks (the loader is async) then pump frames: the #403 bug threw
  // inside the FIRST frame, so frames are the point, not the parse.
  await new Promise(r => setTimeout(r, 50));
  if (!failed && antes) {
    try { vm.runInContext(antes, context); } catch (e) { failed = e; }
  }
  if (!failed) {
    try {
      // Without a gesture every node can sit outside d.alcance and the loop
      // body -- where the #403 bug lived -- silently never runs. Walk the
      // field: each frame, park the view on a different node so the per-node
      // code executes for real.
      for (let i = 0; i < cuadros && rafQueue.length; i++) {
        if (caminar)
          vm.runInContext(
            "if (typeof E!=='undefined' && typeof NODOS!=='undefined' && NODOS.length)" +
            `{ E.pos = NODOS[${i % 41} % NODOS.length].y; }`,
            context);
        const batch = rafQueue; rafQueue = [];
        for (const cb of batch) cb(i * 16.7);
      }
    } catch (e) { failed = e; }
  }
  process.off("unhandledRejection", onRejection);

  const leer = (expr, porDefecto) => {
    try { return vm.runInContext(expr, context); } catch { return porDefecto; }
  };
  return {
    failed, traza, trabajoDeNodo,
    nodos: leer("typeof NODOS !== 'undefined' && NODOS ? NODOS.length : -1", -1),
    pos: leer("typeof E !== 'undefined' ? E.pos : null", null),
    emisores: leer("typeof EMIS !== 'undefined' ? EMIS.n : -1", -1),
    patchOn: leer("typeof PATCH !== 'undefined' ? PATCH.on : null", null),
  };
}

function morir(msg) {
  console.error("SKIN SMOKE FAILED:", msg && msg.stack || msg);
  process.exit(1);
}

// ── 1. the skin as it ships: no board at all ──────────────────────────────
const base = await correr({});
if (base.failed) morir(base.failed);
if (base.nodos < 1) morir(new Error(`field is empty (NODOS=${base.nodos}): data did not load, loop untested`));
if (base.trabajoDeNodo < 1) morir(new Error("per-node draw code never executed: the smoke proved nothing"));
if (base.patchOn !== false) morir(new Error(`without a board the patch must stay off, got ${base.patchOn}`));
console.log(`OK: boot + frames ran without throwing (NODOS=${base.nodos}, marcas=${base.traza.length})`);

// ── 2. the board that actually ships, whatever it says ────────────────────
const tableroReal = JSON.parse(readFileSync(join(raiz, "iskvw", "datos", "tablero.json"), "utf8"));
const conArchivo = await correr({ tablero: tableroReal });
if (conArchivo.failed) morir(conArchivo.failed);
const igual = (a, b) => a.traza.length === b.traza.length && a.traza.every((v, i) => v === b.traza[i]);
if (tableroReal.mejoras && tableroReal.mejoras.patch_efectos) {
  console.log("OK: datos/tablero.json ships with the patch ON (by the artist's hand)");
} else if (!igual(base, conArchivo)) {
  morir(new Error("tablero.json has patch_efectos=false and the drawing CHANGED: "
    + "off must be byte-for-byte the old behaviour"));
} else {
  console.log(`OK: flag off draws exactly as before (${base.traza.length} marks identical)`);
}

// ── 3. the patch on, with gains loud enough to be unambiguous ─────────────
// The board's own routing, only louder, plus one node forced to carry the
// break tag: campo.json has no curatorial tags yet, so desgarro would sit
// untested on real data and rot.
const fuerte = {
  version: 1,
  mejoras: { patch_efectos: true },
  patch: [
    { dato: "tilde", efecto: "pulso", ganancia: 6 },
    { dato: "trazo", efecto: "curvatura", ganancia: 6 },
    { dato: "color", efecto: "sangrado", ganancia: 6 },
    { dato: "etiqueta", efecto: "desgarro", ganancia: 6 },
    { dato: "peso", efecto: "gravedad", ganancia: 6 },
  ],
};
const marcarQuiebre = "if (typeof NODOS!=='undefined') for (let i=0;i<NODOS.length;i+=7) NODOS[i].sen[3]=1;";
const encendido = await correr({ tablero: fuerte, antes: marcarQuiebre });
if (encendido.failed) morir(encendido.failed);
if (encendido.patchOn !== true) morir(new Error("the board turned the patch on and PATCH.on stayed false"));
if (encendido.emisores < 1) morir(new Error("patch on and nobody emitted: no work deformed anything"));

// Numeric comparison of two drawing traces. `movidas`/`maxSalto`/`maxDy` are
// geometry (a mark landed elsewhere), `tonos` is colour at the same index,
// `difs` is any difference at all including a different mark COUNT -- the
// only signature pulso leaves, since bending glyph time skips or adds glyphs.
function comparar(a, b) {
  let movidas = 0, maxSalto = 0, maxDy = 0, tonos = 0;
  let difs = Math.abs(a.traza.length - b.traza.length);
  const n = Math.min(a.traza.length, b.traza.length);
  for (let i = 0; i < n; i++) {
    if (a.traza[i] !== b.traza[i]) difs++;
    const pa = a.traza[i].split(","), pb = b.traza[i].split(",");
    if (pa.length < 3 || pb.length < 3) continue;
    const dx = Math.abs(+pb[0] - +pa[0]), dy = Math.abs(+pb[1] - +pa[1]);
    if (dx + dy > 0.5) { movidas++; maxSalto = Math.max(maxSalto, Math.hypot(dx, dy)); maxDy = Math.max(maxDy, dy); }
    if (pa.slice(2).join(",") !== pb.slice(2).join(",")) tonos++;
  }
  return { movidas, maxSalto, maxDy, tonos, difs, n };
}

const todo = comparar(base, encendido);
if (!todo.movidas) morir(new Error("patch on and not a single mark moved: the effects are inert"));
if (!todo.tonos) morir(new Error("patch on and no colour changed: sangrado is inert"));
console.log(`OK: patch on deforms -- ${todo.movidas}/${todo.n} marks displaced `
  + `(max ${todo.maxSalto.toFixed(1)} px), ${todo.tonos} colour changes, ${encendido.emisores} emitters`);

// ── 4. gravedad, which touches state and not the canvas ───────────────────
// Measured without walking the field, because the walk overwrites E.pos every
// frame and would hide exactly what this effect does.
// Park the reading in the WIDEST gap of the field. Anywhere else the measured
// archive is dense enough (219 works over some 5200 px) that the nearest work
// is already under the reading and there is nothing left to pull: a null
// measurement that says nothing about the effect.
const desviar = `
if (typeof E!=='undefined' && typeof NODOS!=='undefined' && NODOS.length > 1){
  const ys = NODOS.map(n => n.y).sort((a,b) => a-b);
  let corte = 1, hueco = 0;
  for (let i = 1; i < ys.length; i++){
    const h = ys[i] - ys[i-1];
    if (h > hueco){ hueco = h; corte = i; }
  }
  E.pos = (ys[corte] + ys[corte-1]) / 2;
}`;
const sinGravedad = await correr({ caminar: false, antes: desviar });
const conGravedad = await correr({ tablero: fuerte, caminar: false, antes: desviar });
if (conGravedad.failed) morir(conGravedad.failed);
const deriva = Math.abs(conGravedad.pos - sinGravedad.pos);
if (!(deriva > 1)) morir(new Error(`gravedad is inert: the reading drifted ${deriva} px with the patch on`));
console.log(`OK: gravedad pulls the reading ${deriva.toFixed(1)} px in 30 frames `
  + `(off: ${sinGravedad.pos.toFixed(1)}, on: ${conGravedad.pos.toFixed(1)})`);

// ── 5. the per-effect switches: each effect answers for what it encodes ────
// Under the master flag every effect has its own switch (`efectos` in the
// board). The doublecup rule: each switch is measured by the signature ONLY
// its effect can leave -- and a solo run doubles as proof that the other four
// switches really silence theirs, because their signatures must read zero.
const EFECTOS_NOMBRES = ["pulso", "curvatura", "sangrado", "desgarro", "gravedad"];
const solo = (efecto) => ({
  ...fuerte,
  efectos: Object.fromEntries(EFECTOS_NOMBRES.map(e => [e, e === efecto])),
});

// pulso bends glyph TIME, and glyph time is only drawn when the field folds
// into a work's form. Headless that state is unreachable through real data
// (the stroke fetch 404s in the sandbox), so the form is poked directly --
// same licence as marcarQuiebre above.
const armarForma = `
if (typeof E!=='undefined' && typeof NODOS!=='undefined' && NODOS.length){
  E.foco = {id:'__smoke__'};
  E.forma = 1;
  E.formaPts = NODOS.map((n, i) => [Math.cos(i*2.399), Math.sin(i*2.399)]);
}`;

// curvatura alone: geometry moves, colour does not.
const baseQ = await correr({ antes: marcarQuiebre });
const soloCurva = await correr({ tablero: solo("curvatura"), antes: marcarQuiebre });
if (soloCurva.failed) morir(soloCurva.failed);
const mCurva = comparar(baseQ, soloCurva);
if (!(mCurva.movidas > 0)) morir(new Error("curvatura alone displaced nothing: its switch is inert"));
if (mCurva.tonos !== 0) morir(new Error(`curvatura alone changed ${mCurva.tonos} colours: sangrado's switch leaks`));
console.log(`OK: curvatura alone displaces (${mCurva.movidas} marks, max ${mCurva.maxSalto.toFixed(1)} px) and zero colour changes`);

// sangrado alone: colour moves, geometry does not.
const soloSangre = await correr({ tablero: solo("sangrado"), antes: marcarQuiebre });
if (soloSangre.failed) morir(soloSangre.failed);
const mSangre = comparar(baseQ, soloSangre);
if (!(mSangre.tonos > 0)) morir(new Error("sangrado alone recoloured nothing: its switch is inert"));
if (mSangre.movidas !== 0) morir(new Error(`sangrado alone displaced ${mSangre.movidas} marks: a geometry effect leaks`));
console.log(`OK: sangrado alone recolours (${mSangre.tonos} marks) and zero displacement`);

// desgarro alone: tears are horizontal rows -- x moves, y never does.
const soloTira = await correr({ tablero: solo("desgarro"), antes: marcarQuiebre });
if (soloTira.failed) morir(soloTira.failed);
const mTira = comparar(baseQ, soloTira);
if (!(mTira.movidas > 0)) morir(new Error("desgarro alone displaced nothing: its switch is inert"));
if (mTira.maxDy > 0.01) morir(new Error(`desgarro alone moved a mark ${mTira.maxDy.toFixed(2)} px in y: tears are x-only, curvatura's switch leaks`));
if (mTira.tonos !== 0) morir(new Error(`desgarro alone changed ${mTira.tonos} colours: sangrado's switch leaks`));
console.log(`OK: desgarro alone tears x-only (${mTira.movidas} marks, max ${mTira.maxSalto.toFixed(1)} px, max dy ${mTira.maxDy.toFixed(2)})`);

// pulso alone: glyph time dilates, so glyphs change or vanish -- but nothing
// is pushed around and no state drifts.
const glifoBase = await correr({ antes: armarForma });
if (glifoBase.failed) morir(glifoBase.failed);
const soloPulso = await correr({ tablero: solo("pulso"), antes: armarForma });
if (soloPulso.failed) morir(soloPulso.failed);
const mPulso = comparar(glifoBase, soloPulso);
if (!(mPulso.difs > 0)) morir(new Error("pulso alone left the glyph trace identical: its switch is inert"));
console.log(`OK: pulso alone bends glyph time (${mPulso.difs} trace differences over ${glifoBase.traza.length} marks)`);

// gravedad alone: the reading drifts, exactly as in section 4.
const soloGrav = await correr({ tablero: solo("gravedad"), caminar: false, antes: desviar });
if (soloGrav.failed) morir(soloGrav.failed);
const derivaSolo = Math.abs(soloGrav.pos - sinGravedad.pos);
if (!(derivaSolo > 1)) morir(new Error(`gravedad alone is inert: the reading drifted ${derivaSolo} px`));
console.log(`OK: gravedad alone pulls the reading ${derivaSolo.toFixed(1)} px`);

// ── 6. master on, every switch off: the field must not feel a thing ────────
// This is what makes each switch a real gate and not a suggestion: with all
// five off the loud board has to draw mark for mark like no board at all, in
// both drawing modes, and the reading must not drift a pixel.
const mudo = solo("__ninguno__");           // every switch false
const apagadoQ = await correr({ tablero: mudo, antes: marcarQuiebre });
if (apagadoQ.failed) morir(apagadoQ.failed);
if (!igual(baseQ, apagadoQ)) morir(new Error("every switch off and the field trace still changed"));
const apagadoGlifo = await correr({ tablero: mudo, antes: armarForma });
if (apagadoGlifo.failed) morir(apagadoGlifo.failed);
if (!igual(glifoBase, apagadoGlifo)) morir(new Error("every switch off and the glyph trace still changed"));
const apagadoGrav = await correr({ tablero: mudo, caminar: false, antes: desviar });
if (apagadoGrav.failed) morir(apagadoGrav.failed);
const derivaMuda = Math.abs(apagadoGrav.pos - sinGravedad.pos);
if (derivaMuda > 1e-6) morir(new Error(`every switch off and the reading still drifted ${derivaMuda} px`));
console.log(`OK: every switch off under master on draws exactly the base `
  + `(${baseQ.traza.length} + ${glifoBase.traza.length} marks identical, drift ${derivaMuda.toFixed(1)} px)`);
