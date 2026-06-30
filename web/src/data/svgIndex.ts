// Mock data based on the real svg_index.json structure from vibecodeine.
// In production this comes from `py scripts/generate_svg_index.py`.

export type PieceType = 'etiqueta' | 'flyer' | 'pendon' | 'post-ig' | 'sticker' | 'logo' | 'rider' | 'cartelera' | 'stand';
export type PieceArea = 'suplementos' | 'eventos' | 'comun';
export type PieceMedio = 'impresion' | 'digital';

export interface SvgPiece {
  id: string;
  name: string;
  type: PieceType;
  area: PieceArea;
  medio: PieceMedio;
  herramienta: string;
  product?: string;
  realSizeCm: string;
  canvasPx: string;
  colors: string[];
  lastModified: string;
  status: 'aprobado' | 'en-revision' | 'borrador';
  svgContent?: string; // inline SVG for demo
  svgUrl?: string; // repo-served URL fallback
  notes?: string;
}

// ─── SVG snippets for demo pieces ───
const etiquetaSVG = `<svg viewBox="0 0 330 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="330" height="130" rx="6" fill="#f8f1e3" stroke="#2d5a4a" stroke-width="1.5"/>
  <rect x="8" y="8" width="100" height="114" rx="4" fill="#2d5a4a"/>
  <text x="58" y="55" text-anchor="middle" fill="white" font-size="11" font-weight="bold" font-family="sans-serif">OMEGA 3</text>
  <text x="58" y="72" text-anchor="middle" fill="#a3d9c8" font-size="7" font-family="sans-serif">1000mg</text>
  <text x="58" y="95" text-anchor="middle" fill="white" font-size="6" font-family="sans-serif">EPA + DHA</text>
  <rect x="120" y="14" width="200" height="35" rx="3" fill="#2d5a4a15"/>
  <text x="220" y="28" text-anchor="middle" fill="#1f2a24" font-size="7" font-weight="bold" font-family="sans-serif">INFORMACIÓN NUTRICIONAL</text>
  <line x1="130" y1="38" x2="310" y2="38" stroke="#2d5a4a30" stroke-width="0.5"/>
  <text x="130" y="48" fill="#675f55" font-size="5.5" font-family="sans-serif">Porción: 1 cápsula blanda</text>
  <rect x="120" y="56" width="200" height="60" rx="3" fill="#2d5a4a08"/>
  <text x="130" y="70" fill="#675f55" font-size="5" font-family="sans-serif">Ingredientes: Aceite de pescado concentrado,</text>
  <text x="130" y="79" fill="#675f55" font-size="5" font-family="sans-serif">gelatina, glicerina, vitamina E (tocoferol).</text>
  <text x="130" y="92" fill="#675f55" font-size="5" font-family="sans-serif">Modo de uso: Tomar 1 cápsula al día.</text>
  <text x="130" y="105" fill="#c2410f" font-size="4.5" font-family="sans-serif">⚠ Mantener fuera del alcance de los niños.</text>
  <text x="275" y="123" text-anchor="middle" fill="#675f55" font-size="4" font-family="sans-serif">Contenido neto: 60 cápsulas · Lote: 2024-A</text>
</svg>`;

const etiquetaMagnesioSVG = `<svg viewBox="0 0 330 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="330" height="130" rx="6" fill="#f8f1e3" stroke="#6366f1" stroke-width="1.5"/>
  <rect x="8" y="8" width="100" height="114" rx="4" fill="#4f46e5"/>
  <text x="58" y="48" text-anchor="middle" fill="white" font-size="8" font-weight="bold" font-family="sans-serif">GLICINATO</text>
  <text x="58" y="60" text-anchor="middle" fill="white" font-size="8" font-weight="bold" font-family="sans-serif">DE</text>
  <text x="58" y="72" text-anchor="middle" fill="white" font-size="8" font-weight="bold" font-family="sans-serif">MAGNESIO</text>
  <text x="58" y="90" text-anchor="middle" fill="#c7d2fe" font-size="7" font-family="sans-serif">500 mg</text>
  <rect x="120" y="14" width="200" height="35" rx="3" fill="#4f46e515"/>
  <text x="220" y="28" text-anchor="middle" fill="#1f2a24" font-size="7" font-weight="bold" font-family="sans-serif">INFORMACIÓN NUTRICIONAL</text>
  <line x1="130" y1="38" x2="310" y2="38" stroke="#4f46e530" stroke-width="0.5"/>
  <text x="130" y="48" fill="#675f55" font-size="5.5" font-family="sans-serif">Porción: 1 cápsula</text>
  <rect x="120" y="56" width="200" height="60" rx="3" fill="#4f46e508"/>
  <text x="130" y="70" fill="#675f55" font-size="5" font-family="sans-serif">Ingredientes: Glicinato de magnesio,</text>
  <text x="130" y="79" fill="#675f55" font-size="5" font-family="sans-serif">cápsula vegetal (HPMC), estearato de Mg.</text>
  <text x="130" y="92" fill="#675f55" font-size="5" font-family="sans-serif">Modo de uso: Tomar 1 cápsula diaria.</text>
  <text x="275" y="123" text-anchor="middle" fill="#675f55" font-size="4" font-family="sans-serif">Contenido neto: 90 cápsulas · Lote: 2024-B</text>
</svg>`;

const postFiestaSVG = `<svg viewBox="0 0 330 130" xmlns="http://www.w3.org/2000/svg">
  <rect width="330" height="130" rx="6" fill="#f8f1e3" stroke="#f59e0b" stroke-width="1.5"/>
  <rect x="8" y="8" width="100" height="114" rx="4" fill="#b45309"/>
  <text x="58" y="45" text-anchor="middle" fill="white" font-size="9" font-weight="bold" font-family="sans-serif">POST</text>
  <text x="58" y="60" text-anchor="middle" fill="white" font-size="9" font-weight="bold" font-family="sans-serif">FIESTA</text>
  <circle cx="58" cy="85" r="14" fill="#f59e0b40" stroke="#f59e0b" stroke-width="1"/>
  <text x="58" y="88" text-anchor="middle" fill="white" font-size="7" font-family="sans-serif">⚡</text>
  <rect x="120" y="14" width="200" height="100" rx="3" fill="#b4530908"/>
  <text x="220" y="35" text-anchor="middle" fill="#1f2a24" font-size="7" font-weight="bold" font-family="sans-serif">RECUPERACIÓN Y BIENESTAR</text>
  <text x="130" y="55" fill="#675f55" font-size="5" font-family="sans-serif">Complejo vitamínico con electrolitos,</text>
  <text x="130" y="64" fill="#675f55" font-size="5" font-family="sans-serif">aminoácidos y antioxidantes para una</text>
  <text x="130" y="73" fill="#675f55" font-size="5" font-family="sans-serif">recuperación más rápida y segura.</text>
  <text x="130" y="90" fill="#c2410f" font-size="4.5" font-family="sans-serif">⚠ Tabla nutricional en corrección</text>
  <text x="130" y="105" fill="#675f55" font-size="4" font-family="sans-serif">Contenido: 30 sobres · Gomitas disponibles</text>
</svg>`;

const flyerSVG = `<svg viewBox="0 0 175 248" xmlns="http://www.w3.org/2000/svg">
  <rect width="175" height="248" rx="6" fill="#1f2a24"/>
  <rect x="12" y="12" width="151" height="80" rx="4" fill="#2d5a4a"/>
  <text x="87" y="45" text-anchor="middle" fill="white" font-size="14" font-weight="bold" font-family="sans-serif">OMEGA 3</text>
  <text x="87" y="62" text-anchor="middle" fill="#a3d9c8" font-size="8" font-family="sans-serif">EPA + DHA de alta pureza</text>
  <text x="87" y="78" text-anchor="middle" fill="#f8f1e380" font-size="6" font-family="sans-serif">Salud cardiovascular · Cerebro · Articulaciones</text>
  <rect x="12" y="100" width="151" height="100" rx="4" fill="#2d5a4a20"/>
  <text x="87" y="120" text-anchor="middle" fill="#f8f1e3" font-size="7" font-weight="bold" font-family="sans-serif">¿Por qué suplementar?</text>
  <text x="24" y="138" fill="#a3d9c8" font-size="5.5" font-family="sans-serif">✓ Reduce inflamación</text>
  <text x="24" y="150" fill="#a3d9c8" font-size="5.5" font-family="sans-serif">✓ Mejora función cognitiva</text>
  <text x="24" y="162" fill="#a3d9c8" font-size="5.5" font-family="sans-serif">✓ Protege el corazón</text>
  <text x="24" y="174" fill="#a3d9c8" font-size="5.5" font-family="sans-serif">✓ Apoya salud articular</text>
  <text x="24" y="186" fill="#a3d9c8" font-size="5.5" font-family="sans-serif">✓ Fortalece sistema inmune</text>
  <rect x="12" y="208" width="151" height="28" rx="4" fill="#2d5a4a"/>
  <text x="87" y="225" text-anchor="middle" fill="white" font-size="7" font-weight="bold" font-family="sans-serif">Consulta · reducienodano.cl</text>
  <rect x="130" y="212" width="20" height="20" rx="2" fill="white"/>
  <text x="140" y="225" text-anchor="middle" fill="#1f2a24" font-size="6" font-family="sans-serif">QR</text>
</svg>`;

const pendonSVG = `<svg viewBox="0 0 80 200" xmlns="http://www.w3.org/2000/svg">
  <rect width="80" height="200" rx="2" fill="#1f2a24"/>
  <rect x="4" y="4" width="72" height="50" rx="3" fill="#2d5a4a"/>
  <text x="40" y="25" text-anchor="middle" fill="white" font-size="6" font-weight="bold" font-family="sans-serif">REDUCIENDO</text>
  <text x="40" y="35" text-anchor="middle" fill="white" font-size="6" font-weight="bold" font-family="sans-serif">DAÑO</text>
  <text x="40" y="47" text-anchor="middle" fill="#a3d9c8" font-size="4" font-family="sans-serif">Suplementos</text>
  <circle cx="40" cy="85" r="18" fill="#2d5a4a30" stroke="#2d5a4a" stroke-width="0.5"/>
  <text x="40" y="88" text-anchor="middle" fill="#a3d9c8" font-size="8" font-family="sans-serif">💊</text>
  <text x="40" y="115" text-anchor="middle" fill="white" font-size="5" font-weight="bold" font-family="sans-serif">Cuidado</text>
  <text x="40" y="123" text-anchor="middle" fill="white" font-size="5" font-weight="bold" font-family="sans-serif">Informado</text>
  <text x="40" y="140" text-anchor="middle" fill="#675f55" font-size="3.5" font-family="sans-serif">Pre y Post Fiesta</text>
  <text x="40" y="148" text-anchor="middle" fill="#675f55" font-size="3.5" font-family="sans-serif">Omega 3 · Magnesio</text>
  <text x="40" y="156" text-anchor="middle" fill="#675f55" font-size="3.5" font-family="sans-serif">Proteína · Vitaminas</text>
  <rect x="4" y="170" width="72" height="24" rx="3" fill="#2d5a4a"/>
  <text x="40" y="185" text-anchor="middle" fill="white" font-size="4.5" font-weight="bold" font-family="sans-serif">reducienodano.cl</text>
</svg>`;

const postIgSVG = `<svg viewBox="0 0 108 135" xmlns="http://www.w3.org/2000/svg">
  <rect width="108" height="135" rx="4" fill="#1f2a24"/>
  <rect x="4" y="4" width="100" height="60" rx="3" fill="linear-gradient(#2d5a4a, #1f2a24)"/>
  <rect x="4" y="4" width="100" height="60" rx="3" fill="#2d5a4a"/>
  <text x="54" y="28" text-anchor="middle" fill="white" font-size="10" font-weight="bold" font-family="sans-serif">¿SABÍAS</text>
  <text x="54" y="42" text-anchor="middle" fill="white" font-size="10" font-weight="bold" font-family="sans-serif">QUE...?</text>
  <text x="54" y="56" text-anchor="middle" fill="#a3d9c8" font-size="5" font-family="sans-serif">Serie educativa RD</text>
  <rect x="4" y="68" width="100" height="50" rx="3" fill="#2d5a4a15"/>
  <text x="54" y="82" text-anchor="middle" fill="#f8f1e3" font-size="5" font-family="sans-serif">El Omega 3 reduce la</text>
  <text x="54" y="91" text-anchor="middle" fill="#f8f1e3" font-size="5" font-family="sans-serif">inflamación cerebral post</text>
  <text x="54" y="100" text-anchor="middle" fill="#f8f1e3" font-size="5" font-family="sans-serif">consumo de sustancias.</text>
  <text x="54" y="113" text-anchor="middle" fill="#675f55" font-size="4" font-family="sans-serif">Fuente: PubMed 2023</text>
  <rect x="4" y="122" width="100" height="9" rx="2" fill="#2d5a4a"/>
  <text x="54" y="129" text-anchor="middle" fill="white" font-size="4" font-weight="bold" font-family="sans-serif">@reducienodano · reducienodano.cl</text>
</svg>`;

const stickerSVG = `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="48" fill="#2d5a4a" stroke="#a3d9c8" stroke-width="1.5"/>
  <text x="50" y="35" text-anchor="middle" fill="white" font-size="8" font-weight="bold" font-family="sans-serif">CUIDA</text>
  <text x="50" y="47" text-anchor="middle" fill="white" font-size="8" font-weight="bold" font-family="sans-serif">TU</text>
  <text x="50" y="59" text-anchor="middle" fill="white" font-size="8" font-weight="bold" font-family="sans-serif">VIAJE</text>
  <text x="50" y="75" text-anchor="middle" fill="#a3d9c8" font-size="5" font-family="sans-serif">reducienodano.cl</text>
</svg>`;

const logoSVG = `<svg viewBox="0 0 140 140" xmlns="http://www.w3.org/2000/svg">
  <rect width="140" height="140" rx="70" fill="#1f2a24"/>
  <circle cx="70" cy="60" r="30" fill="none" stroke="#2d5a4a" stroke-width="2"/>
  <circle cx="70" cy="60" r="20" fill="#2d5a4a40"/>
  <text x="70" y="65" text-anchor="middle" fill="white" font-size="12" font-weight="bold" font-family="sans-serif">RD</text>
  <text x="70" y="105" text-anchor="middle" fill="#a3d9c8" font-size="7" font-weight="bold" font-family="sans-serif">SUPLEMENTOS</text>
  <text x="70" y="117" text-anchor="middle" fill="#675f55" font-size="5" font-family="sans-serif">Línea de cuidado</text>
</svg>`;

const carteleraSVG = `<svg viewBox="0 0 108 192" xmlns="http://www.w3.org/2000/svg">
  <rect width="108" height="192" rx="4" fill="#111"/>
  <rect x="6" y="6" width="96" height="120" rx="3" fill="#333"/>
  <text x="54" y="55" text-anchor="middle" fill="#888" font-size="8" font-family="sans-serif">📸</text>
  <text x="54" y="70" text-anchor="middle" fill="#666" font-size="5" font-family="sans-serif">Foto IG del evento</text>
  <text x="54" y="82" text-anchor="middle" fill="#555" font-size="4" font-family="sans-serif">(descargada con instaloader)</text>
  <rect x="6" y="132" width="96" height="24" rx="3" fill="#2d5a4a"/>
  <text x="54" y="140" text-anchor="middle" fill="white" font-size="5" font-weight="bold" font-family="sans-serif">CLUB SOL</text>
  <text x="54" y="150" text-anchor="middle" fill="#a3d9c8" font-size="4" font-family="sans-serif">Viernes 21 Jun · 23:00</text>
  <rect x="6" y="162" width="96" height="24" rx="3" fill="#1f2a24"/>
  <text x="54" y="174" text-anchor="middle" fill="#675f55" font-size="4" font-family="sans-serif">Reduciendo Daño presente</text>
  <text x="54" y="183" text-anchor="middle" fill="#675f55" font-size="3.5" font-family="sans-serif">Stand informativo + testeo</text>
</svg>`;

export const MOCK_SVG_INDEX: SvgPiece[] = [
  {"id": "01_linea_suplementos_rd_editable", "name": "01_linea_suplementos_rd_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Linea completa", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/01_linea_suplementos_rd_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "02_impulso_editable", "name": "02_impulso_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Impulso", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/02_impulso_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "03_hongos_adaptogenos_editable", "name": "03_hongos_adaptogenos_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Hongos Adaptogenos", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/03_hongos_adaptogenos_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "04_pre_fiesta_editable", "name": "04_pre_fiesta_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Pre Fiesta", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/04_pre_fiesta_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "05_magnesio_editable", "name": "05_magnesio_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Magnesio", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/05_magnesio_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "06_creatina_monohidratada_editable", "name": "06_creatina_monohidratada_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Creatina", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/06_creatina_monohidratada_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "07_proteina_editable", "name": "07_proteina_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Proteina", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/07_proteina_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "08_post_fiesta_editable", "name": "08_post_fiesta_editable.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg+illustrator", "product": "Post Fiesta", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/08_post_fiesta_editable.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "01_linea_suplementos_rd_vectorizado", "name": "01_linea_suplementos_rd_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Linea completa", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/01_linea_suplementos_rd_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "02_impulso_vectorizado", "name": "02_impulso_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Impulso", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/02_impulso_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "03_hongos_adaptogenos_vectorizado", "name": "03_hongos_adaptogenos_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Hongos Adaptogenos", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/03_hongos_adaptogenos_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "04_pre_fiesta_vectorizado", "name": "04_pre_fiesta_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Pre Fiesta", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/04_pre_fiesta_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "05_magnesio_vectorizado", "name": "05_magnesio_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Magnesio", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/05_magnesio_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "06_creatina_monohidratada_vectorizado", "name": "06_creatina_monohidratada_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Creatina", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/06_creatina_monohidratada_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "07_proteina_vectorizado", "name": "07_proteina_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Proteina", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/07_proteina_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
  {"id": "08_post_fiesta_vectorizado", "name": "08_post_fiesta_vectorizado.svg", "type": "flyer", "area": "suplementos", "medio": "impresion", "herramienta": "svg", "product": "Post Fiesta", "realSizeCm": "10.0x14.0 cm", "canvasPx": "2000x2800", "colors": [], "lastModified": "2026-06-30", "status": "aprobado", "svgUrl": "/svg/suplementos_rd/08_post_fiesta_vectorizado.svg", "notes": "Real SVG - suplementos_rd"},
] as const;


export async function loadFromApi(): Promise<SvgPiece[]> {
  const resp = await fetch('/api/list-svg-works');
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const data = await resp.json();

  const readSvg = async (path?: string, inline?: string): Promise<{ svgContent?: string; svgUrl?: string }> => {
    if (inline) return { svgContent: inline };
    if (!path) return {};
    const normalized = path.replace(/^\/+/, '');
    const svgUrl = `/${normalized}`;
    try {
      const svgResp = await fetch(svgUrl);
      if (!svgResp.ok) return { svgUrl };
      const text = await svgResp.text();
      return text.trim().startsWith('<svg') || text.includes('<svg') ? { svgContent: text, svgUrl } : { svgUrl };
    } catch {
      return { svgUrl };
    }
  };

  const normalizePiece = async (item: any, groupName = 'comun'): Promise<SvgPiece> => {
    const name = String(item.name || item.id || 'pieza');
    const lower = `${name} ${item.path || ''} ${item.kind || ''}`.toLowerCase();
    const path = item.path ? String(item.path) : undefined;
    const svg = await readSvg(path, item.svgContent || item.svg);
    return {
      id: String(item.id || item.slug || path || name.replace(/\s+/g, '_').toLowerCase()),
      name,
      type: lower.includes('pendon') ? 'pendon' : lower.includes('sticker') ? 'sticker' : lower.includes('logo') ? 'logo' : lower.includes('rider') ? 'rider' : lower.includes('cartelera') ? 'cartelera' : lower.includes('post') ? 'post-ig' : lower.includes('flyer') ? 'flyer' : 'etiqueta',
      area: String(groupName).toLowerCase().includes('evento') ? 'eventos' : String(groupName).toLowerCase().includes('supl') ? 'suplementos' : 'comun',
      medio: lower.includes('ig') || lower.includes('digital') ? 'digital' : 'impresion',
      herramienta: String(item.kind || item.herramienta || 'repo'),
      product: item.product,
      realSizeCm: String(item.realSizeCm || item.real_size_cm || '—'),
      canvasPx: String(item.canvasPx || item.canvas_px || 'SVG'),
      colors: Array.isArray(item.colors) ? item.colors : [],
      lastModified: String(item.lastModified || item.modified || 'repo'),
      status: item.status || 'borrador',
      notes: item.notes || path,
      ...svg,
    } as SvgPiece;
  };

  if (Array.isArray(data?.pieces)) return Promise.all(data.pieces.map((item: any) => normalizePiece(item, item.group || item.area || 'comun')));
  if (Array.isArray(data?.works)) return Promise.all(data.works.map((item: any) => normalizePiece(item, item.group || item.area || 'comun')));
  if (data?.groups && typeof data.groups === 'object') {
    const batches = await Promise.all(
      Object.entries(data.groups).map(async ([groupName, items]) => Promise.all((items as any[]).map(item => normalizePiece(item, groupName))))
    );
    return batches.flat();
  }
  return [];
}

export const TYPE_OPTIONS: PieceType[] = ['etiqueta', 'flyer', 'pendon', 'post-ig', 'sticker', 'logo', 'rider', 'cartelera', 'stand'];
