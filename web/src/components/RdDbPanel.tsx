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
import { Database, Upload, CheckCircle2, CircleDashed, MapPin, AlertTriangle } from 'lucide-react';

interface Venue {
  nombre: string;
  estado: string;
  preferido: boolean;
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
}
interface VenueCat {
  id: string;
  nombre: string;
  tipo: string;
  escala: string;
  capacidad: string;
}
interface Data {
  productoras: Productora[];
  venues: VenueCat[];
  resumen?: {
    productoras: number;
    con_vector: number;
    confirmadas: number;
    venues: number;
    eventos?: number;
    eventos_triangulables?: number;
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
  // Cache-buster: tras reemplazar un logo hay que forzar que el <img> lo relea.
  const [rev, setRev] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const objetivo = useRef<string>('');

  const cargar = () =>
    fetch('/api/rd-db')
      .then(r => r.json())
      .then(d => {
        setData(d);
        setEstado(d?.error ? 'error' : 'ok');
      })
      .catch(() => setEstado('error'));

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
            Productoras y venues. Fuente: <code className="text-zinc-400">data/productoras/*.json</code>
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
                clic en el recuadro del logo para reemplazarlo
              </span>
            </div>
            <div className="divide-y divide-zinc-800/60">
              {data!.productoras.map(p => (
                <div key={p.slug} className="flex items-center gap-4 px-4 py-3">
                  <button
                    onClick={() => pedirArchivo(p.slug)}
                    disabled={subiendo === p.slug}
                    title="Reemplazar logo"
                    className="group relative flex h-14 w-20 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950 hover:border-emerald-700"
                  >
                    {/* Solo se pide el logo si el backend dice que hay uno. Antes
                        se pedia para las 20 y las 14 sin logo devolvian 404: la
                        consola quedaba con 18 errores rojos que se leen como una
                        falla de la app, y no lo son. */}
                    {p.logo.archivo !== false && (
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
                      <span className="font-medium text-zinc-100">{p.nombre}</span>
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
