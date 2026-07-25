// productoras.ts — snapshot minimo de la base de productoras RD, para el
// bundle standalone de Plano/Rider (sin backend Python, sin data/rd.db).
//
// Fuente real: data/productoras/*.json (15 archivos, versionados en el repo,
// NO gitignored -- distinto de data/rd.db que es una proyeccion regenerable
// y si esta gitignored). `src/flujo/rd/database.py` (funcion build_rd_db,
// linea ~321) arma esa DB leyendo esos mismos JSON: el slug es el nombre de
// archivo sin extension (pf.stem) y el nombre es el campo "name".
//
// Este archivo SOLO trae {slug, name}: se reviso cada JSON fuente a mano
// (2026-07-25) y no tienen datos sensibles/privados (instagram vacio o
// handle publico, notas editoriales, sin contactos ni telefonos ni emails),
// pero igual se recorta a lo minimo que el pedido necesita (asociar un
// preset a una productora), no todo el registro completo.
//
// Regenerar a mano si data/productoras/ cambia: no hay script automatico
// todavia (15 entradas, bajo volumen). Ver reporte de la sesion 2026-07-25
// para el comando usado (py -c leyendo json.load por archivo).

export interface ProductoraRef {
  slug: string;
  name: string;
}

export const RD_PRODUCTORAS: ProductoraRef[] = [
  { slug: 'amelie', name: 'Amelie' },
  { slug: 'cachorros', name: 'Cachorros' },
  { slug: 'creamfields', name: 'Creamfields' },
  { slug: 'dame', name: 'Dame' },
  { slug: 'frvr', name: 'FRVR' },
  { slug: 'impulsefest', name: 'Impulse Fest' },
  { slug: 'livejam', name: 'LiveJam' },
  { slug: 'nebula', name: 'Nebula' },
  { slug: 'openklub', name: 'OpenKlub' },
  { slug: 'piknic', name: 'Piknic Electronik' },
  { slug: 'psiquiatrico', name: 'Psiquiatrico' },
  { slug: 'sundeck', name: 'Sundeck' },
  { slug: 'technoyouth', name: 'Techno Youth' },
  { slug: 'thegrid', name: 'The Grid' },
  { slug: 'tycircle', name: 'TY Circle' },
];
