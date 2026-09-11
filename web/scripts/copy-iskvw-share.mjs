import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..', '..');
const src = resolve(root, 'web', 'dist-iskvw', 'iskvw.html');
const dest = resolve(root, 'dist_compartir', 'herramientas_iskvw.html');
if (!existsSync(src)) {
  console.error(`Missing build output: ${src}`);
  process.exit(1);
}
mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log(`copied ${src} -> ${dest}`);
