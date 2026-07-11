// Compila la galeria 3D (sala flujo) desde template.html + las piezas reales
// del repo. Salida: tools/dist/sala3d.html (gitignored, autocontenida, apta
// para publicarse como artifact web con CSP estricta: todo inline).
//
// Uso:   node tools/sala3d/build.js
// Deps:  solo node + internet la primera vez (three.js r149 se cachea en
//        tools/sala3d/.cache/, gitignored via tools/dist no aplica: se crea aca).
'use strict';
const fs = require('fs');
const path = require('path');
const https = require('https');

const HERE = __dirname;
const ROOT = path.resolve(HERE, '..', '..');
const CACHE = path.join(HERE, '.cache');
const OUT_DIR = path.join(ROOT, 'tools', 'dist');
const OUT = path.join(OUT_DIR, 'sala3d.html');

const THREE_URL = 'https://unpkg.com/three@0.149.0/build/three.min.js';
const CSS3D_URL = 'https://unpkg.com/three@0.149.0/examples/jsm/renderers/CSS3DRenderer.js';

// pieza del repo -> token del template
const ARTS = {
  __ART_FIELD__: 'projects/tapiz/piezas_curadas/field_compete_engine.svg',
  __ART_BORDER__: 'projects/tapiz/piezas_curadas/border_validate_airdrop.svg',
  __ART_MEDALLION__: 'projects/tapiz/piezas_curadas/medallion_loom.svg',
  __ART_MIHRAB__: 'projects/tapiz/piezas_curadas/mihrab_spaces.svg',
  __ART_CAUCE__: 'projects/tapiz/piezas_curadas/cauce_cauce.svg',
};

function fetchCached(url, name) {
  const file = path.join(CACHE, name);
  if (fs.existsSync(file)) return Promise.resolve(fs.readFileSync(file, 'utf8'));
  fs.mkdirSync(CACHE, { recursive: true });
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return https.get(res.headers.location, r2 => pipe(r2)).on('error', reject);
      }
      pipe(res);
      function pipe(r) {
        if (r.statusCode !== 200) return reject(new Error(url + ' -> HTTP ' + r.statusCode));
        let body = '';
        r.setEncoding('utf8');
        r.on('data', d => { body += d; });
        r.on('end', () => { fs.writeFileSync(file, body); resolve(body); });
      }
    }).on('error', reject);
  });
}

function wrapCss3d(mjs) {
  let s = mjs.replace(/import\s*\{[^}]*\}\s*from\s*'three';/, '');
  s = s.replace(/export\s*\{[^}]*\};?/, '');
  return '(function(){\nconst {Matrix4, Object3D, Quaternion, Vector3} = THREE;\n' + s +
    '\nwindow.CSS3DObject = CSS3DObject;\nwindow.CSS3DRenderer = CSS3DRenderer;\n})();';
}

async function main() {
  let html = fs.readFileSync(path.join(HERE, 'template.html'), 'utf8');

  // dataset calm del ecosistema: usa tools/dist si existe, si no exige generarlo
  const calmPath = path.join(ROOT, 'tools', 'dist', 'system_status.json');
  if (!fs.existsSync(calmPath)) {
    throw new Error('falta tools/dist/system_status.json -- correr antes: py tools/compete_engine.py --demo');
  }
  const calm = fs.readFileSync(calmPath, 'utf8');
  JSON.parse(calm);

  const three = await fetchCached(THREE_URL, 'three.min.js');
  const css3d = wrapCss3d(await fetchCached(CSS3D_URL, 'CSS3DRenderer.mjs'));
  if (/^\s*(import|export)\b/m.test(css3d)) throw new Error('wrap CSS3D dejo import/export');

  const repl = { __THREE__: three, __CSS3D__: css3d, __CALM_JSON__: calm };
  for (const [tok, rel] of Object.entries(ARTS)) {
    const p = path.join(ROOT, rel);
    const svg = fs.readFileSync(p, 'utf8');
    if (!svg.startsWith('<svg')) throw new Error(rel + ' no parece SVG');
    repl[tok] = svg;
  }
  for (const [tok, val] of Object.entries(repl)) {
    if (!html.includes(tok)) throw new Error('token ausente en template: ' + tok);
    html = html.split(tok).join(val);
  }
  // __THREE__ vive legitimamente dentro de three.min.js (window.__THREE__)
  if (/__ART_|__CSS3D__|__CALM_JSON__/.test(html)) throw new Error('quedaron tokens sin reemplazar');

  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(OUT, html);
  console.log('OK', OUT, fs.statSync(OUT).size, 'bytes,',
    (html.match(/<svg /g) || []).length, 'svgs inline');
}

main().catch(e => { console.error('FALLO:', e.message); process.exit(1); });
