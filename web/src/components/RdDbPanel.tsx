// RdDbPanel — la base de datos RD (productoras y venues) dentro del hub.
//
// Hasta ahora la DB solo se consultaba por CLI (`flujo rd-db ...`). Este panel
// la muestra y permite lo unico que hoy se hace a mano y a destiempo:
// reemplazar el logo de una productora.
//
// Politica de datos (2026-07-25, pedido del area de eventos RD): el endpoint
// que alimenta este panel arma cada registro con allowlist explicita y NO
// entrega contactos ni handles. Si algo de eso aparece aca, es un bug.
//
// Politica de logos (2026-07-23): el logo oficial se busca en la web de la
// productora y se guarda junto a su URL de origen. NUNCA se recorta de un
// flyer: un recorte es un derivado de baja calidad y sin fuente.

import { useEffect, useRef, useState } from 'react';
import { Database, Upload, CheckCircle2, CircleDashed, MapPin, AlertTriangle, BarChart3, ChevronRight, History, Layout, Radio } from 'lucide-react';

interface Venue {
  nombre: string;
  estado: string;
  preferido: boolean;
}
interface Evento {
  nombre: string;
  fecha?: string;
  fecha_iso?: string | null;
  venue?: string;
  estado?: string;
  fuente?: string;
  lineup?: string[];
  fuentes_primarias?: string[];
  sin_fuente_primaria?: boolean;
}
interface Distribucion {
  valor: string;
  conteo: number;
  porcentaje: number;
}
interface Evidencia2025 {
  event_id: string;
  hoja: string;
  indice_hoja: number;
  nombre: string;
  periodo: string;
  fecha_iso?: string | null;
  estado_fecha?: string;
  estado_duplicado?: string;
  tamano_grupo_duplicado?: number;
  venue_fuente?: string | null;
  productora_fuente?: string | null;
  estado_enlace?: string;
  filas: number;
  muestra_declarada: { campo: string; total: number; distribucion: Distribucion[] };
  resultados_colorimetricos: { campos: string[]; total: number; distribucion: Distribucion[] };
}
interface Productora {
  slug: string;
  nombre: string;
  aliases: string[];
  tipos: string[];
  venues: Venue[];
  logo: { estado: string; vector: boolean; archivo?: boolean };
  confirmada: boolean;
  confirmacion: string;
  fuente: string;
  eventos?: Evento[];
  /** SVG del logo horneado en el bundle sin servidor. Ausente con hub. */
  logo_svg?: string;
}
interface VenueCat {
  id: string;
  nombre: string;
  tipo: string;
  escala: string;
  capacidad: string;
}
// `__SIN_SERVIDOR__` lo define vite en los builds standalone; en el hub no
// existe, y ahi vale false.
const SIN_SERVIDOR = typeof __SIN_SERVIDOR__ !== 'undefined' && __SIN_SERVIDOR__;

interface Data {
  /** true = los datos vienen dentro del archivo, no de un servidor. */
  horneado?: boolean;
  productoras: Productora[];
  venues: VenueCat[];
  evidencia_2025?: Evidencia2025[];
  resumen?: {
    productoras: number;
    con_vector: number;
    confirmadas: number;
    venues: number;
    eventos?: number;
    eventos_triangulables?: number;
    eventos_sin_fuente_primaria?: number;
    eventos_sin_fecha_iso?: number;
    eventos_sin_lineup?: number;
  };
  excluido_a_proposito?: string[];
  error?: string;
}

// Los estados del logo llegan como llaves del dato ("sin_ficha",
// "no_encontrado"). Mostrados tal cual parecen un error del sistema; acá se
// dicen como se los diría una persona.
const ESTADO_LOGO: Record<string, string> = {
  sin_ficha: 'sin ficha',
  no_encontrado: 'sin logo',
  raster: 'logo sin vectorizar',
  vector: 'logo vectorial',
};

export default function RdDbPanel() {
  const [data, setData] = useState<Data | null>(null);
  const [estado, setEstado] = useState<'cargando' | 'ok' | 'error'>('cargando');
  const [subiendo, setSubiendo] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string>('');
  const [productoraActiva, setProductoraActiva] = useState<string | null>(null);
  const [evidenciaActiva, setEvidenciaActiva] = useState<string | null>(null);
  // Cache-buster: tras reemplazar un logo hay que forzar que el <img> lo relea.
  const [rev, setRev] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const objetivo = useRef<string>('');

  // Sin hub se usa la copia horneada en el bundle. Antes esto mostraba "error"
  // en el archivo que se entrega sin servidor, que es justo donde no hay a
  // quien pedirle. La copia sale de la MISMA funcion que sirve el hub
  // (flujo.rd.panel), horneada por tools/gen_rd_standalone.py.
  // En el bundle suelto se va derecho al respaldo: probar el servidor primero
  // dejaba un 404 en la consola de quien abre el archivo.
  const cargarHorneada = async () => {
    try {
      const d = (await import('../data/rdDbEmbebida.json')).default as unknown as Data;
      setData(d);
      setEstado('ok');
    } catch {
      setEstado('error');
    }
  };

  const cargar = () =>
    SIN_SERVIDOR ? cargarHorneada() : fetch('/api/rd-db')
      .then(r => r.json())
      .then(d => {
        setData(d);
        setEstado(d?.error ? 'error' : 'ok');
      })
      .catch(cargarHorneada);

  useEffect(() => {
    cargar();
  }, []);

  const pedirArchivo = (slug: string) => {
    objetivo.current = slug;
    inputRef.current?.click();
  };

  const alElegir = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = ''; // permite volver a elegir el mismo archivo
    if (!file) return;
    const slug = objetivo.current;
    setSubiendo(slug);
    setAviso('');
    try {
      const b64: string = await new Promise((ok, err) => {
        const fr = new FileReader();
        fr.onload = () => ok(String(fr.result));
        fr.onerror = () => err(fr.error);
        fr.readAsDataURL(file);
      });
      const fuente = window.prompt(
        `URL de origen del logo de "${slug}" (opcional, pero conviene: queda guardada junto al archivo)`,
        '',
      );
      const r = await fetch('/api/rd-db/logo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug, filename: file.name, data: b64, fuente: fuente || '' }),
      }).then(x => x.json());
      if (r.ok) {
        setAviso(`${slug}: logo reemplazado (${r.archivo}, ${r.kb} KB)${r.fuente_guardada ? ' + fuente' : ''}`);
        setRev(v => v + 1);
        cargar();
      } else {
        setAviso(`${slug}: ${r.error}`);
      }
    } catch (err) {
      setAviso(`${slug}: fallo al subir (${err})`);
    } finally {
      setSubiendo(null);
    }
  };

  const r = data?.resumen;
  const activa = data?.productoras.find(p => p.slug === productoraActiva) ?? null;
  const evidencia = data?.evidencia_2025?.find(e => e.event_id === evidenciaActiva) ?? null;

  return (
    <div className="space-y-6">
      <input ref={inputRef} type="file" accept=".png,.jpg,.jpeg,.webp,.svg" onChange={alElegir} className="hidden" />

      <header className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-900/40 text-emerald-300">
          <Database className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight">Base de datos RD</h1>
          <p className="text-sm text-zinc-500">
            {data?.horneado
              ? 'Productoras y venues, con los datos dentro de este archivo. Para editarlos hace falta la aplicación completa.'
              : <>Productoras y venues. Fuente: <code className="text-zinc-400">data/productoras/*.json</code></>}
          </p>
        </div>
      </header>

      {estado === 'error' && (
        <div className="flex items-start gap-2 rounded-xl border border-amber-800/50 bg-amber-950/30 p-4 text-sm text-amber-300">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            Sin backend. Este panel lee la DB del repo, así que necesita <code>py -m flujo app</code> corriendo.
          </div>
        </div>
      )}

      {aviso && (
        <div className="rounded-xl border border-zinc-700 bg-zinc-900/60 px-4 py-2 text-[13px] text-zinc-300">{aviso}</div>
      )}

      {estado === 'ok' && r && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              // Los rotulos van en castellano llano: este panel se le muestra a
              // la directiva y a gente de fuera del equipo. "Triangulables" y
              // "fecha ISO" son jerga interna -- nadie afuera sabe que un evento
              // triangulable es uno que ya tiene fecha Y lineup. El dato es el
              // mismo; lo que cambia es que ahora se entiende sin traduccion.
              { k: 'Productoras', v: r.productoras, ayuda: 'Productoras en la base' },
              { k: 'Con logo vectorial', v: `${r.con_vector}/${r.productoras}`, ayuda: 'Tienen el logo en vector, listo para imprimir' },
              { k: 'Confirmadas', v: `${r.confirmadas}/${r.productoras}`, ayuda: 'Confirmaron que trabajan con RD' },
              { k: 'Venues', v: r.venues, ayuda: 'Recintos registrados' },
              { k: 'Eventos', v: r.eventos ?? 0, ayuda: 'Eventos registrados' },
              { k: 'Con fecha y lineup', v: r.eventos_triangulables ?? 0, ayuda: 'Tienen los datos completos para cruzarlos' },
              { k: 'Sin fuente primaria', v: r.eventos_sin_fuente_primaria ?? 0, ayuda: 'Falta URL oficial, ticketera o venue' },
              { k: 'Sin lineup', v: r.eventos_sin_lineup ?? 0, ayuda: 'Falta cargarles el lineup' },
              { k: 'Sin fecha', v: r.eventos_sin_fecha_iso ?? 0, ayuda: 'Falta cargarles la fecha' },
            ].map(c => (
              <div key={c.k} title={c.ayuda} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
                <div className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">{c.k}</div>
                <div className="mt-1 text-2xl font-black text-zinc-100">{c.v}</div>
                <div className="mt-1 text-[10px] leading-snug text-zinc-600">{c.ayuda}</div>
              </div>
            ))}
          </div>

          <section className="rounded-xl border border-zinc-800 bg-zinc-900/40">
            <div className="flex flex-wrap items-center gap-2 border-b border-zinc-800 px-4 py-3">
              <h2 className="text-sm font-bold">Productoras</h2>
              <span className="text-[11px] text-zinc-600">
                {data?.horneado ? '' : 'clic en el recuadro del logo para reemplazarlo'}
              </span>
            </div>
            <div className="divide-y divide-zinc-800/60">
              {data!.productoras.map(p => (
                <div key={p.slug} className={`flex flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:gap-4 ${productoraActiva === p.slug ? 'bg-emerald-950/15' : ''}`}>
                  <button
                    onClick={() => pedirArchivo(p.slug)}
                    disabled={subiendo === p.slug || !!data?.horneado}
                    title={data?.horneado
                      ? "Para cambiar el logo hace falta la aplicación completa"
                      : "Reemplazar logo"}
                    className="group relative flex h-14 w-20 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950 hover:border-emerald-700"
                  >
                    {/* Solo se pide el logo si el backend dice que hay uno. Antes
                        se pedia para las 20 y las 14 sin logo devolvian 404: la
                        consola quedaba con 18 errores rojos que se leen como una
                        falla de la app, y no lo son. */}
                    {/* Con el logo horneado se dibuja directo: pedirlo al
                        backend daba 404 en el archivo suelto y dejaba el
                        recuadro roto justo en las productoras que SI lo
                        tienen, al reves de lo que se quiere mostrar. */}
                    {p.logo_svg ? (
                      <span
                        className="max-h-full max-w-full p-1 [&>svg]:h-full [&>svg]:w-full [&>svg]:object-contain"
                        dangerouslySetInnerHTML={{ __html: p.logo_svg }}
                      />
                    ) : (!SIN_SERVIDOR && p.logo.archivo !== false) && (
                      <img
                        src={`/api/rd-db/logo?slug=${p.slug}&v=${rev}`}
                        alt=""
                        className="max-h-full max-w-full object-contain p-1"
                        onError={e => ((e.target as HTMLImageElement).style.visibility = 'hidden')}
                      />
                    )}
                    {p.logo.archivo === false && (
                      <span className="text-[9px] uppercase tracking-widest text-zinc-700">sin logo</span>
                    )}
                    <span className="absolute inset-0 flex items-center justify-center bg-black/70 opacity-0 transition-opacity group-hover:opacity-100">
                      <Upload className="h-4 w-4 text-emerald-300" />
                    </span>
                    {subiendo === p.slug && (
                      <span className="absolute inset-0 flex items-center justify-center bg-black/80 text-[10px] text-emerald-300">
                        subiendo…
                      </span>
                    )}
                  </button>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => { setProductoraActiva(p.slug); setEvidenciaActiva(null); }}
                        className="flex min-h-8 items-center gap-1 text-left font-medium text-zinc-100 hover:text-emerald-300"
                        aria-pressed={productoraActiva === p.slug}
                      >
                        {p.nombre}<ChevronRight className="h-3.5 w-3.5 text-zinc-600" />
                      </button>
                      <code className="text-[10px] text-zinc-600">{p.slug}</code>
                      {p.confirmada ? (
                        <span title={p.confirmacion} className="flex items-center gap-1 text-[10px] text-emerald-400">
                          <CheckCircle2 className="h-3 w-3" /> confirmada
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-[10px] text-zinc-600">
                          <CircleDashed className="h-3 w-3" /> sin confirmar
                        </span>
                      )}
                      {(p.eventos?.length ?? 0) > 0 && (
                        <span className={`rounded px-1.5 py-px text-[10px] ${
                          p.eventos!.some(e => e.sin_fuente_primaria)
                            ? 'bg-amber-950/50 text-amber-300'
                            : 'bg-emerald-950/50 text-emerald-300'
                        }`}>
                          {p.eventos!.filter(e => e.sin_fuente_primaria).length
                            ? `${p.eventos!.filter(e => e.sin_fuente_primaria).length} sin fuente primaria`
                            : 'fuentes primarias OK'}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-1.5">
                      {p.tipos.map(t => (
                        <span key={t} className="rounded border border-zinc-800 px-1.5 py-px text-[10px] text-zinc-500">
                          {t}
                        </span>
                      ))}
                      {p.venues.map(v => (
                        <span
                          key={v.nombre}
                          className="flex items-center gap-1 rounded border border-sky-900/50 bg-sky-950/30 px-1.5 py-px text-[10px] text-sky-300"
                        >
                          <MapPin className="h-2.5 w-2.5" />
                          {v.nombre}
                        </span>
                      ))}
                    </div>
                  </div>

                  <span
                    className={`shrink-0 rounded px-2 py-0.5 text-[10px] font-bold ${
                      p.logo.vector
                        ? 'bg-emerald-900/50 text-emerald-300'
                        : 'bg-zinc-800 text-zinc-500'
                    }`}
                  >
                    {/* El estado venia crudo del dato: "sin_ficha",
                        "no_encontrado". Son llaves, no palabras, y se leian
                        como si algo estuviera roto. */}
                    {p.logo.vector ? 'logo vectorial' : ESTADO_LOGO[p.logo.estado] || 'sin logo'}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {activa && (
            <section className="rounded-xl border border-emerald-900/60 bg-emerald-950/10 p-4 sm:p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-emerald-400">
                    <Layout className="h-3.5 w-3.5" /> Ficha de productora
                  </div>
                  <h2 className="mt-1 text-lg font-bold text-zinc-100">{activa.nombre}</h2>
                  <p className="mt-1 max-w-2xl text-xs leading-relaxed text-zinc-500">
                    Aquí se unen los eventos declarados por la productora con el venue conocido. El rider/plano queda como referencia pendiente hasta que exista un enlace explícito; no se adivina.
                  </p>
                </div>
                <button type="button" onClick={() => setProductoraActiva(null)} className="min-h-8 rounded-lg border border-zinc-800 px-3 text-xs text-zinc-500 hover:text-zinc-200">
                  cerrar
                </button>
              </div>
              {activa.eventos?.length ? (
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {activa.eventos.map((ev, index) => (
                    <article key={`${ev.nombre}-${index}`} className="rounded-xl border border-zinc-800 bg-zinc-950/50 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="font-semibold text-zinc-100">{ev.nombre}</h3>
                          <p className="mt-1 text-xs text-zinc-500">{ev.fecha || 'Fecha pendiente'}</p>
                        </div>
                        <span className="rounded bg-zinc-800 px-2 py-1 text-[10px] text-zinc-400">{ev.estado || 'sin estado'}</span>
                      </div>
                      <div className="mt-3 grid gap-2 text-xs sm:grid-cols-3">
                        <div><span className="block text-[10px] uppercase tracking-wider text-zinc-600">Venue</span><span className="text-zinc-300">{ev.venue || 'pendiente'}</span></div>
                        <div><span className="block text-[10px] uppercase tracking-wider text-zinc-600">Rider / plano</span><span className="text-zinc-500">pendiente de enlace</span></div>
                        <div><span className="block text-[10px] uppercase tracking-wider text-zinc-600">Fuente</span><span className="text-zinc-500">{ev.fuentes_primarias?.length ? 'primaria' : 'pendiente'}</span></div>
                      </div>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="mt-4 rounded-lg border border-dashed border-zinc-800 px-4 py-3 text-xs text-zinc-500">No hay eventos declarados para esta productora.</div>
              )}
            </section>
          )}

          {(data!.evidencia_2025?.length ?? 0) > 0 && (
            <section className="rounded-xl border border-violet-900/50 bg-violet-950/10">
              <div className="flex flex-wrap items-start justify-between gap-3 border-b border-violet-900/40 px-4 py-4">
                <div>
                  <h2 className="flex items-center gap-2 text-sm font-bold text-zinc-100"><History className="h-4 w-4 text-violet-300" /> Historial de evidencia 2025</h2>
                  <p className="mt-1 max-w-3xl text-xs leading-relaxed text-zinc-500">Fuente histórica importada. Las hojas aún no tienen enlace humano confirmado a productora o venue; se muestran por su <code>event_id</code> exacto y no se asignan automáticamente.</p>
                </div>
                <span className="rounded bg-violet-950/60 px-2 py-1 text-[10px] text-violet-300">{data!.evidencia_2025!.length} hojas/eventos fuente</span>
              </div>
              <div className="grid gap-2 p-3 sm:grid-cols-2 lg:grid-cols-3">
                {data!.evidencia_2025!.map(ev => (
                  <button key={ev.event_id} type="button" onClick={() => { setEvidenciaActiva(ev.event_id); setProductoraActiva(null); }} className={`min-h-20 rounded-xl border p-3 text-left transition-colors ${evidenciaActiva === ev.event_id ? 'border-violet-500 bg-violet-950/40' : 'border-zinc-800 bg-zinc-950/40 hover:border-violet-800'}`}>
                    <span className="block font-medium text-zinc-200">{ev.nombre}</span>
                    <span className="mt-1 block text-[10px] text-zinc-600"><code>{ev.event_id}</code> · {ev.fecha_iso || 'fecha no resuelta'} · {ev.filas} filas</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          {evidencia && (
            <section className="rounded-xl border border-violet-700/60 bg-zinc-950/60 p-4 sm:p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-violet-300"><BarChart3 className="h-3.5 w-3.5" /> Resumen del evento fuente</div>
                  <h2 className="mt-1 text-lg font-bold text-zinc-100">{evidencia.nombre}</h2>
                  <p className="mt-1 text-xs text-zinc-500">{evidencia.hoja} · <code>{evidencia.event_id}</code> · {evidencia.filas} filas de datos</p>
                </div>
                <button type="button" onClick={() => setEvidenciaActiva(null)} className="min-h-8 rounded-lg border border-zinc-800 px-3 text-xs text-zinc-500 hover:text-zinc-200">cerrar</button>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <DistributionCard title="Muestra declarada (campo format_raw)" total={evidencia.muestra_declarada.total} values={evidencia.muestra_declarada.distribucion} color="violet" />
                <DistributionCard title="Resultados colorimétricos observados" total={evidencia.resultados_colorimetricos.total} values={evidencia.resultados_colorimetricos.distribucion} color="amber" />
              </div>
              <div className="mt-4 grid gap-2 text-xs sm:grid-cols-3">
                <div className="rounded-lg border border-zinc-800 p-3"><span className="block text-[10px] uppercase tracking-wider text-zinc-600">Productora / venue</span><span className="text-zinc-400">{evidencia.productora_fuente || 'sin enlace'} · {evidencia.venue_fuente || 'sin enlace'}</span></div>
                <div className="rounded-lg border border-zinc-800 p-3"><span className="block text-[10px] uppercase tracking-wider text-zinc-600">Enlace</span><span className="text-zinc-400">{evidencia.estado_enlace || 'pendiente de revisión humana'}</span></div>
                <div className="rounded-lg border border-zinc-800 p-3"><span className="block text-[10px] uppercase tracking-wider text-zinc-600">Duplicados</span><span className="text-zinc-400">{evidencia.estado_duplicado || 'sin estado'}{evidencia.tamano_grupo_duplicado && evidencia.tamano_grupo_duplicado > 1 ? ` · grupo ${evidencia.tamano_grupo_duplicado}` : ''}</span></div>
              </div>
              <p className="mt-4 flex items-start gap-2 text-[11px] leading-relaxed text-zinc-600"><Radio className="mt-0.5 h-3.5 w-3.5 shrink-0" /> Los porcentajes describen la distribución literal de los campos fuente y no interpretan identidad, pureza, dosis ni seguridad.</p>
            </section>
          )}

          {data!.venues.length > 0 && (
            <section className="rounded-xl border border-zinc-800 bg-zinc-900/40">
              <div className="border-b border-zinc-800 px-4 py-3 text-sm font-bold">Venues</div>
              <div className="divide-y divide-zinc-800/60">
                {data!.venues.map(v => (
                  <div key={v.id} className="flex items-center gap-3 px-4 py-2 text-[13px]">
                    <span className="flex-1 text-zinc-200">{v.nombre}</span>
                    <span className="text-[11px] text-zinc-600">{v.tipo}</span>
                    <span className="text-[11px] text-zinc-600">{v.escala}</span>
                    <span className="text-[11px] text-zinc-600">cap. {v.capacidad}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {data!.excluido_a_proposito && (
            <p className="text-[11px] text-zinc-600">
              Excluido a propósito de este panel: {data!.excluido_a_proposito.join(', ')}. El endpoint usa allowlist de
              campos: un campo nuevo en el origen no se publica solo.
            </p>
          )}
        </>
      )}
    </div>
  );
}

function DistributionCard({
  title,
  total,
  values,
  color,
}: {
  title: string;
  total: number;
  values: Distribucion[];
  color: 'violet' | 'amber';
}) {
  const bar = color === 'violet' ? 'bg-violet-400' : 'bg-amber-400';
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-xs font-bold text-zinc-300">{title}</h3>
        <span className="shrink-0 text-[10px] text-zinc-600">n={total}</span>
      </div>
      <div className="mt-3 space-y-2">
        {values.slice(0, 8).map(item => (
          <div key={item.valor}>
            <div className="flex items-center justify-between gap-3 text-[11px]">
              <span className="min-w-0 truncate text-zinc-400" title={item.valor}>{item.valor}</span>
              <span className="shrink-0 text-zinc-500">{item.conteo} · {item.porcentaje.toFixed(1).replace('.0', '')}%</span>
            </div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div className={`h-full rounded-full ${bar}`} style={{ width: `${Math.min(item.porcentaje, 100)}%` }} />
            </div>
          </div>
        ))}
        {values.length > 8 && <p className="text-[10px] text-zinc-600">Se muestran los 8 valores más frecuentes; el total incluye todos.</p>}
        {!values.length && <p className="text-[11px] text-zinc-600">Sin valores registrados.</p>}
      </div>
    </div>
  );
}
