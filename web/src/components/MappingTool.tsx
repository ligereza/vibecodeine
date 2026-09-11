import { ExternalLink } from 'lucide-react';

export default function MappingTool() {
  return (
    <div className="flex h-[calc(100vh-2rem)] min-h-[520px] flex-col gap-2">
      <div className="flex flex-col items-start gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-bold text-zinc-200">Mapping LED</h2>
          <p className="text-[10px] text-zinc-600">Event Rigging Master Console - pixel mapping / rigging 3D</p>
        </div>
        <a
          href="mapping.html"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 rounded-lg border border-zinc-800/60 px-3 py-1.5 text-[11px] font-medium text-zinc-400 hover:border-zinc-600 hover:text-zinc-200"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          Abrir en pestaña nueva
        </a>
      </div>
      {/* Ruta relativa: funciona igual servido por flujo app y abierto como
          context/flujo_hub.html via file:// (la absoluta /mapping.html rompia el fallback). */}
      <iframe
        src="mapping.html"
        title="Event Rigging Master Console"
        className="h-full w-full flex-1 rounded-xl border border-zinc-800/60"
      />
    </div>
  );
}
