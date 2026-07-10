import { Layers, Type, Eye, FlaskConical, TerminalSquare } from 'lucide-react';

// Cultura: ala de arte-investigacion del repo. Panel de consulta (sin API):
// presenta el metodo y el estado real de las cuatro lineas. Las herramientas
// ganan su propio panel cuando maduran (regla: instrumento -> material -> pieza).

interface Track {
  icon: typeof Layers;
  nombre: string;
  estado: 'instrumento vivo' | 'medidor listo' | 'por empezar';
  brief: string;
  detalle: string;
}

const TRACKS: Track[] = [
  {
    icon: Layers,
    nombre: 'tapiz',
    estado: 'instrumento vivo',
    brief: 'Patron visual tipo viaje: cultura del tejido, hogar calido, digestion.',
    detalle: 'Telar en projects/tapiz/vibecode (terminal vivo + spaces/void). Salidas: piezas SVG animadas, ambiente de terminal, patrones imprimibles/proyectables.',
  },
  {
    icon: Type,
    nombre: 'tilde',
    estado: 'medidor listo',
    brief: 'Que le pasa al espanol cuando una maquina lo comprime: n con tilde, acentos, apertura.',
    detalle: 'Medidor en desktop/tilde_meter.py (supervivencia de marcas, palabras degradadas). Falta juntar corpus real antes de cualquier pieza.',
  },
  {
    icon: Eye,
    nombre: 'psicosis',
    estado: 'por empezar',
    brief: 'Lectura empatica vs paranoide del mismo mensaje. Ejercicio introspectivo.',
    detalle: 'Tres ejes: conyugal, literario (indice de realidad de un autor muerto), plaga (mapa colectivo de proyecciones). Nunca perfila personas reales.',
  },
  {
    icon: FlaskConical,
    nombre: 'precursor',
    estado: 'por empezar',
    brief: 'Lo organico vs lo sintetico: geometria molecular real, mecanismo real, morfologia real.',
    detalle: 'Capa descriptiva/estetica solamente: el realismo como sustrato del surrealismo. Requiere el dossier de conocimiento (knowledge/) primero.',
  },
];

const ESTADO_STYLE: Record<Track['estado'], string> = {
  'instrumento vivo': 'bg-amber-500/15 text-amber-300',
  'medidor listo': 'bg-amber-500/10 text-amber-400/80',
  'por empezar': 'bg-zinc-800/80 text-zinc-500',
};

export default function CulturaPanel() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-sm font-bold text-zinc-200">Cultura</h2>
        <p className="text-[10px] text-zinc-600">
          Ala de arte-investigacion. Metodo: instrumento &rarr; material &rarr; pieza.
          Lo real como sustrato, la percepcion como material.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {TRACKS.map(t => {
          const Icon = t.icon;
          return (
            <div key={t.nombre} className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-5">
              <div className="mb-2 flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-amber-600/70 to-orange-800/70">
                  <Icon className="h-4 w-4 text-amber-100" />
                </div>
                <span className="text-sm font-bold text-zinc-100">{t.nombre}</span>
                <span className={`ml-auto rounded px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider ${ESTADO_STYLE[t.estado]}`}>
                  {t.estado}
                </span>
              </div>
              <p className="mb-1.5 text-[12px] leading-relaxed text-zinc-300">{t.brief}</p>
              <p className="text-[10px] leading-relaxed text-zinc-600">{t.detalle}</p>
            </div>
          );
        })}
      </div>

      <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-5">
        <div className="mb-2 flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-zinc-500">
          <TerminalSquare className="h-3.5 w-3.5 text-amber-500" />
          Instrumento tapiz (CLI local)
        </div>
        <pre className="overflow-x-auto rounded-lg bg-zinc-950/80 p-3 text-[11px] leading-relaxed text-zinc-400">{`# patron de espacios de un archivo (terminal)
py projects/tapiz/vibecode_spaces.py archivo.py -m void -p flujo

# stream negativo con typewriter
py projects/tapiz/vibecode_void.py archivo.py -g

# exportar pieza SVG (paleta flujo real)
py projects/tapiz/vibecode_spaces.py archivo.py -m void --svg pieza.svg`}</pre>
      </div>

      <div className="rounded-2xl border border-amber-900/30 bg-amber-950/10 p-4 text-[10px] leading-relaxed text-zinc-500">
        Limites del departamento: capa descriptiva y cultural si (estructura real,
        mecanismo, morfologia, historia, iconografia); nada generativo de sintesis;
        psicosis es lente introspectiva/literaria, jamas vigilancia o perfilado de
        personas reales.
      </div>
    </div>
  );
}
