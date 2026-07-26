// Simbolos propios del plano: los que la jefa de eventos agrega soltando un
// .svg en data/plano_simbolos/ y declarandolo en data/plano_simbolos.json.
//
// El hub los sirve en /api/plano-simbolos y esto los carga ANTES de montar
// React (web/src/main.tsx), asi PlanoTool ya los tiene en su primer render.
// Hasta el 2026-07-26 el editor visual tenia su propia lista fija de iconos: un
// simbolo agregado aparecia en el plano de `flujo plano` y NO en el editor,
// que es justamente donde ella trabaja.
//
// Sin hub (bundle estatico) no hay simbolos propios y el editor funciona con
// los de fabrica, igual que antes.

export interface SimboloPropio {
  id: string;
  etiqueta: string;
  color: string;
  zona: string;
  cuando: string;
  /** Contenido del .svg de la disenadora. Vacio = solo reetiqueta uno de fabrica. */
  svg: string;
}

/** Se muta en su lugar: PlanoTool la lee en vivo, no copia al importar. */
export const SIMBOLOS_PROPIOS: SimboloPropio[] = [];

const POR_ID = new Map<string, SimboloPropio>();

export function simboloPropio(id: string): SimboloPropio | undefined {
  return POR_ID.get(id);
}

const RE_COMENTARIO = /<!--[\s\S]*?-->/g;
const RE_SCRIPT = /<script\b[\s\S]*?<\/script\s*>/gi;
const RE_EVENTO = /\son[a-z]+\s*=\s*("[\s\S]*?"|'[\s\S]*?')/gi;
const RE_DECL = /<\?xml[\s\S]*?\?>|<!DOCTYPE[\s\S]*?>/gi;
const RE_SVG_ABRE = /<svg\b([^>]*)>/i;
const RE_VIEWBOX = /viewBox\s*=\s*["']([^"']+)["']/i;
const RE_MEDIDA = /\b(width|height)\s*=\s*["']([\d.]+)/gi;

function medidas(atributos: string): [number, number] {
  const vb = RE_VIEWBOX.exec(atributos);
  if (vb) {
    const p = vb[1].replace(/,/g, ' ').split(/\s+/).filter(Boolean);
    if (p.length === 4) {
      const w = Number(p[2]);
      const h = Number(p[3]);
      if (w > 0 && h > 0) return [w, h];
    }
  }
  const found: Record<string, number> = {};
  let m: RegExpExecArray | null;
  RE_MEDIDA.lastIndex = 0;
  while ((m = RE_MEDIDA.exec(atributos)) !== null) found[m[1].toLowerCase()] = Number(m[2]);
  const w = found.width || 0;
  const h = found.height || 0;
  return w > 0 && h > 0 ? [w, h] : [160, 160];
}

/**
 * Encaja el .svg de la disenadora en la casilla del icono, centrado en (cx, cy).
 *
 * MISMA convencion que los iconos de fabrica y que el lado Python
 * (src/flujo/plano/iconos.py): lienzo de 160x160 escalado por `scale`. Se
 * mantiene la proporcion, se reemplaza `currentColor` por el color declarado y
 * se recorta lo que no debe viajar en un plano que se entrega (script, on*).
 * Devuelve '' si el archivo no parece un SVG, y quien llama dibuja el marcador
 * neutro de siempre.
 */
export function markupSimboloPropio(
  svg: string, color: string, cx: number, cy: number, scale: number,
): string {
  const limpio = svg
    .replace(RE_DECL, '')
    .replace(RE_COMENTARIO, '')
    .replace(RE_SCRIPT, '')
    .replace(RE_EVENTO, '');
  const apertura = RE_SVG_ABRE.exec(limpio);
  if (!apertura) return '';
  const [w, h] = medidas(apertura[1]);
  let interior = limpio.slice(apertura.index + apertura[0].length);
  const cierre = interior.toLowerCase().lastIndexOf('</svg>');
  if (cierre !== -1) interior = interior.slice(0, cierre);
  interior = interior.split('currentColor').join(color).trim();

  const k = (160 * scale) / Math.max(w, h);
  const tx = cx - (k * w) / 2;
  const ty = cy - (k * h) / 2;
  return `<g transform="translate(${tx.toFixed(2)} ${ty.toFixed(2)}) scale(${k.toFixed(4)})">${interior}</g>`;
}

export interface NuevoSimbolo {
  etiqueta: string;
  color: string;
  zona: string;
  cuando: string;
  /** Contenido del archivo .svg que eligio la usuaria. */
  svg: string;
}

/**
 * Guarda un simbolo nuevo y recarga el catalogo.
 *
 * Devuelve el motivo cuando falla: quien lo usa no lee logs, y un fallo mudo
 * se siente como "la app no guarda". Sin hub no hay donde escribir y se dice.
 */
export async function guardarSimbolo(nuevo: NuevoSimbolo): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch('/api/plano-simbolos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nuevo),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data?.ok) {
      return { ok: false, error: data?.error || `No se pudo guardar (${res.status}).` };
    }
    await loadPlanoSimbolos();
    return { ok: true };
  } catch {
    return { ok: false, error: 'No hay conexión con flujo. Abrí la app con `py -m flujo app`.' };
  }
}

export async function loadPlanoSimbolos(signal?: AbortSignal): Promise<void> {
  try {
    const res = await fetch('/api/plano-simbolos', { signal });
    if (!res.ok) return;
    const data = await res.json();
    if (!Array.isArray(data?.simbolos)) return;

    const limpios: SimboloPropio[] = [];
    for (const raw of data.simbolos) {
      const id = typeof raw?.id === 'string' ? raw.id.trim() : '';
      if (!id) continue;
      limpios.push({
        id,
        etiqueta: typeof raw.etiqueta === 'string' && raw.etiqueta ? raw.etiqueta : id,
        color: typeof raw.color === 'string' && raw.color ? raw.color : '#9ca3af',
        zona: typeof raw.zona === 'string' ? raw.zona : '',
        cuando: typeof raw.cuando === 'string' ? raw.cuando : 'siempre',
        svg: typeof raw.svg === 'string' ? raw.svg : '',
      });
    }
    SIMBOLOS_PROPIOS.splice(0, SIMBOLOS_PROPIOS.length, ...limpios);
    POR_ID.clear();
    for (const s of limpios) POR_ID.set(s.id, s);
  } catch {
    // Sin hub, o el plazo nos aborto: solo los simbolos de fabrica.
  }
}
