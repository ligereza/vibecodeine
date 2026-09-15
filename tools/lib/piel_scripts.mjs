// Load the executable scripts a static skin actually ships.
//
// A skin can share local runtime code. Keeping this parser in one place makes
// the smoke, cost meter, and venue exporters execute the same script graph as
// the browser instead of silently testing only inline code.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";

export function scriptsDePiel(html, rutaHtml) {
  const scripts = [];
  for (const m of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/gi)) {
    const attrs = m[1] || "";
    if (/type\s*=\s*["']application\/json["']/i.test(attrs)) continue;
    const src = attrs.match(/\bsrc\s*=\s*["']([^"']+)["']/i);
    if (src) scripts.push(readFileSync(join(dirname(rutaHtml), src[1]), "utf8"));
    else scripts.push(m[2]);
  }
  if (!scripts.length) throw new Error("no executable skin script found");
  return scripts;
}
