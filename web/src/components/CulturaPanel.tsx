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
    brief: 'Origen del diseno de alfombras, vinculo con la psicodelia, y que es hoy esa cultura oriental.',
    detalle: 'Telar en projects/tapiz/vibecode (terminal + export SVG). Dossier: dossiers/tapiz.md. Salidas: piezas SVG animadas, ambiente de terminal, patrones imprimibles.',
  },
  {
    icon: Type,
    nombre: 'tilde',
    estado: 'medidor listo',
    brief: 'El espanol como material: ambiguedad, la literatura como representacion, la perdida en la traduccion.',
    detalle: 'Medidor en desktop/tilde_meter.py (supervivencia de marcas). Dossier: dossiers/tilde.md. Falta juntar corpus real antes de la pieza.',
  },
  {
    icon: Eye,
    nombre: 'psicosis',
    estado: 'por empezar',
    brief: 'Como se estudia una conducta (angulo detective/historico) y que pasa si el registro esta mal.',
    detalle: 'Dossier: dossiers/psicosis.md. La herramienta (input situacion -> dos lecturas + duda del registro) viene despues del dossier. Nunca perfila personas reales.',
  },
  {
    icon: FlaskConical,
    nombre: 'precursor',
    estado: 'por empezar',
    brief: 'La cultura del diseno de drogas: concepto "designer drugs", cultura de semillas/fenotipos, patentes como artefacto visual.',
    detalle: 'Dossier: dossiers/precursor.md. Solo capa cultural/historica/legal/estetica; nada de sintesis, precursores ni metodo de cultivo.',
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
          Base cultural de las apps y representaciones. Metodo: dossier &rarr;
          instrumento &rarr; material &rarr; pieza. Investigacion en
          <span className="text-amber-400/80"> projects/cultura/dossiers/</span>.
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
