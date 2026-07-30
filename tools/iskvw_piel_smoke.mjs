// Smoke-run of the campo skin's inline JS with DOM stubs. Exists because a
// scope refactor (PR #403) shipped `destino`/`dy` referenced outside the
// function that defined them: green CI, dead portfolio -- the draw loop threw
// on frame one and no test executed the JS. This runs the real script in node
// and fails on ANY uncaught error during boot + the first animation frames.
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

// -- stubs: enough surface for the skin, everything else throws visibly --
const noop = () => {};
let trabajoDeNodo = 0; // per-node draw work actually executed (gradients/glyphs)
const ctx2d = new Proxy({}, {
  get: (t, k) => {
    if (k === "canvas") return canvas;
    if (k === "createRadialGradient" || k === "createLinearGradient")
      return () => { trabajoDeNodo++; return { addColorStop: noop }; };
    if (k === "fillText") return () => { trabajoDeNodo++; };
    if (k === "measureText") return () => ({ width: 10 });
    if (k === "getImageData") return () => ({ data: new Uint8ClampedArray(4) });
    return noop;
  },
  set: () => true,
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
  console, Math, JSON, Date, performance: { now: () => rafQueue.length * 16.7 },
  requestAnimationFrame: cb => { rafQueue.push(cb); return rafQueue.length; },
  cancelAnimationFrame: noop,
  setTimeout: (cb) => 0, clearTimeout: noop, setInterval: () => 0, clearInterval: noop,
  // fetch: resolve datos/* against the repo so the REAL data shapes are what
  // the loop chews on; anything else 404s like the fallback path expects.
  fetch: async (url) => {
    const m = String(url).match(/datos\/(campo|archivo|obras)\.json$/);
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
process.on("unhandledRejection", (e) => { failed = failed || e; });
try {
  for (const src of scripts) vm.runInContext(src, context, { timeout: 10000 });
} catch (e) { failed = e; }

// drain microtasks (the loader is async) then pump frames: the #403 bug threw
// inside the FIRST frame, so frames are the point, not the parse.
await new Promise(r => setTimeout(r, 50));
if (!failed) {
  try {
    // Without a gesture every node can sit outside d.alcance and the loop
    // body -- where the #403 bug lived -- silently never runs. Walk the
    // field: each frame, park the view on a different node so the per-node
    // code executes for real.
    for (let i = 0; i < 30 && rafQueue.length; i++) {
      vm.runInContext(
        "if (typeof E!=='undefined' && typeof NODOS!=='undefined' && NODOS.length)" +
        `{ E.pos = NODOS[${i % 41} % NODOS.length].y; }`,
        context);
      const batch = rafQueue; rafQueue = [];
      for (const cb of batch) cb(i * 16.7);
    }
  } catch (e) { failed = e; }
}

// the draw loop only exercises its per-node code with material in the field:
// an empty NODOS is a silently green smoke, which is the failure mode this
// tool exists to kill. Demand the data actually loaded.
const nodos = vm.runInContext("typeof NODOS !== 'undefined' && NODOS ? NODOS.length : -1", context);
if (!failed && nodos < 1) failed = new Error(`field is empty (NODOS=${nodos}): data did not load, loop untested`);
if (!failed && trabajoDeNodo < 1)
  failed = new Error("per-node draw code never executed: the smoke proved nothing");

if (failed) {
  console.error("SKIN SMOKE FAILED:", failed && failed.stack || failed);
  process.exit(1);
}
console.log(`OK: boot + frames ran without throwing (NODOS=${nodos})`);
