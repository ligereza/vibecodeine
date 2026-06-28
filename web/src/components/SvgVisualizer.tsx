import React, { useState, useMemo } from 'react';
import {
  Search, Filter, X, ZoomIn, ZoomOut, Maximize2, Download,
  ChevronLeft, ChevronRight, Eye, Tag, Ruler, Palette,
  Clock, CheckCircle2, AlertCircle, FileEdit, Info,
  Grid3X3, List, SlidersHorizontal
} from 'lucide-react';
import { cn } from '../utils/cn';
import { MOCK_SVG_INDEX, SvgPiece, PieceType, PieceArea, PieceMedio } from '../data/svgIndex';

// ─── Filter config ───
const TYPE_OPTIONS: { value: PieceType | 'all'; label: string; emoji: string }[] = [
  { value: 'all', label: 'Todos', emoji: '📂' },
  { value: 'etiqueta', label: 'Etiquetas', emoji: '🏷️' },
  { value: 'flyer', label: 'Flyers', emoji: '📄' },
  { value: 'pendon', label: 'Pendones', emoji: '🪧' },
  { value: 'post-ig', label: 'Posts IG', emoji: '📱' },
  { value: 'sticker', label: 'Stickers', emoji: '🎯' },
  { value: 'logo', label: 'Logos', emoji: '✦' },
  { value: 'cartelera', label: 'Carteleras', emoji: '🎪' },
];

const STATUS_COLORS: Record<string, string> = {
  'aprobado': 'text-green-400 bg-green-500/10 border-green-500/20',
  'en-revision': 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  'borrador': 'text-zinc-400 bg-zinc-500/10 border-zinc-500/20',
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  'aprobado': <CheckCircle2 className="w-3 h-3" />,
  'en-revision': <AlertCircle className="w-3 h-3" />,
  'borrador': <FileEdit className="w-3 h-3" />,
};

export default function SvgVisualizer() {
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<PieceType | 'all'>('all');
  const [filterArea, setFilterArea] = useState<PieceArea | 'all'>('all');
  const [filterMedio, setFilterMedio] = useState<PieceMedio | 'all'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedPiece, setSelectedPiece] = useState<SvgPiece | null>(null);
  const [modalZoom, setModalZoom] = useState(1);
  const [showFilters, setShowFilters] = useState(true);

  // ─── Filtered pieces ───
  const filteredPieces = useMemo(() => {
    return MOCK_SVG_INDEX.filter(p => {
      const matchSearch = search === '' ||
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.product?.toLowerCase().includes(search.toLowerCase()) ||
        p.type.toLowerCase().includes(search.toLowerCase());
      const matchType = filterType === 'all' || p.type === filterType;
      const matchArea = filterArea === 'all' || p.area === filterArea;
      const matchMedio = filterMedio === 'all' || p.medio === filterMedio;
      return matchSearch && matchType && matchArea && matchMedio;
    });
  }, [search, filterType, filterArea, filterMedio]);

  // ─── Stats ───
  const stats = useMemo(() => ({
    total: MOCK_SVG_INDEX.length,
    aprobado: MOCK_SVG_INDEX.filter(p => p.status === 'aprobado').length,
    revision: MOCK_SVG_INDEX.filter(p => p.status === 'en-revision').length,
    borrador: MOCK_SVG_INDEX.filter(p => p.status === 'borrador').length,
  }), []);

  // ─── Navigate ───
  const currentIndex = selectedPiece ? filteredPieces.findIndex(p => p.id === selectedPiece.id) : -1;
  const goNext = () => {
    if (currentIndex < filteredPieces.length - 1) setSelectedPiece(filteredPieces[currentIndex + 1]);
  };
  const goPrev = () => {
    if (currentIndex > 0) setSelectedPiece(filteredPieces[currentIndex - 1]);
  };

  // ─── Download SVG ───
  const downloadSVG = (piece: SvgPiece) => {
    if (!piece.svgContent) return;
    const blob = new Blob([piece.svgContent], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${piece.id}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold">Visor de Diseños</h3>
          <p className="text-zinc-400 text-sm mt-1">
            Galería de piezas vectoriales — etiquetas, flyers, pendones, stickers, logos
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-zinc-600">
            <span className="text-green-500">{stats.aprobado} aprobados</span>
            <span>·</span>
            <span className="text-yellow-500">{stats.revision} en revisión</span>
            <span>·</span>
            <span className="text-zinc-500">{stats.borrador} borradores</span>
          </div>
        </div>
      </div>

      {/* Search + filters bar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar por nombre, producto o tipo..."
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-zinc-600 transition-all placeholder:text-zinc-600"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-zinc-300">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors border",
            showFilters
              ? "bg-zinc-800 border-zinc-700 text-white"
              : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-white"
          )}
        >
          <SlidersHorizontal className="w-4 h-4" />
          Filtros
        </button>
        <div className="flex items-center border border-zinc-800 rounded-lg overflow-hidden">
          <button
            onClick={() => setViewMode('grid')}
            className={cn("p-2.5 transition-colors", viewMode === 'grid' ? "bg-zinc-800 text-white" : "text-zinc-600 hover:text-zinc-300")}
          >
            <Grid3X3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={cn("p-2.5 transition-colors", viewMode === 'list' ? "bg-zinc-800 text-white" : "text-zinc-600 hover:text-zinc-300")}
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter chips */}
      {showFilters && (
        <div className="flex flex-wrap items-center gap-4 p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl">
          {/* Type filter */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Tipo:</span>
            <div className="flex flex-wrap gap-1">
              {TYPE_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setFilterType(opt.value)}
                  className={cn(
                    "px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors",
                    filterType === opt.value
                      ? "bg-white text-black"
                      : "bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
                  )}
                >
                  <span className="mr-1">{opt.emoji}</span>
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
          <div className="w-px h-6 bg-zinc-800" />
          {/* Area filter */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Área:</span>
            {(['all', 'suplementos', 'eventos'] as const).map(a => (
              <button
                key={a}
                onClick={() => setFilterArea(a)}
                className={cn(
                  "px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors capitalize",
                  filterArea === a
                    ? "bg-white text-black"
                    : "bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
                )}
              >
                {a === 'all' ? 'Todas' : a}
              </button>
            ))}
          </div>
          <div className="w-px h-6 bg-zinc-800" />
          {/* Medio filter */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Medio:</span>
            {(['all', 'impresion', 'digital'] as const).map(m => (
              <button
                key={m}
                onClick={() => setFilterMedio(m)}
                className={cn(
                  "px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors capitalize",
                  filterMedio === m
                    ? "bg-white text-black"
                    : "bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
                )}
              >
                {m === 'all' ? 'Todos' : m === 'impresion' ? 'Impresión' : 'Digital'}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results count */}
      <div className="text-xs text-zinc-500">
        {filteredPieces.length} {filteredPieces.length === 1 ? 'pieza' : 'piezas'} encontradas
        {(filterType !== 'all' || filterArea !== 'all' || filterMedio !== 'all' || search) && (
          <button
            onClick={() => { setFilterType('all'); setFilterArea('all'); setFilterMedio('all'); setSearch(''); }}
            className="ml-2 text-zinc-400 hover:text-white underline"
          >
            Limpiar filtros
          </button>
        )}
      </div>

      {/* ═══ GRID VIEW ═══ */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-4 gap-4">
          {filteredPieces.map(piece => (
            <div
              key={piece.id}
              onClick={() => { setSelectedPiece(piece); setModalZoom(1); }}
              className="group bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden hover:border-zinc-600 transition-all cursor-pointer"
            >
              {/* Preview */}
              <div className="aspect-square bg-zinc-950 relative flex items-center justify-center p-4 overflow-hidden">
                {piece.svgContent ? (
                  <div
                    className="w-full h-full flex items-center justify-center [&>svg]:max-w-full [&>svg]:max-h-full [&>svg]:w-auto [&>svg]:h-auto opacity-90 group-hover:opacity-100 transition-opacity"
                    dangerouslySetInnerHTML={{ __html: piece.svgContent }}
                  />
                ) : (
                  <div className="text-zinc-700 text-4xl">📄</div>
                )}
                {/* Status badge */}
                <div className="absolute top-2 left-2">
                  <div className={cn("flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase border", STATUS_COLORS[piece.status])}>
                    {STATUS_ICONS[piece.status]}
                    {piece.status}
                  </div>
                </div>
                {/* Quick actions overlay */}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <button className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors">
                    <Eye className="w-4 h-4 text-white" />
                  </button>
                  <button
                    onClick={e => { e.stopPropagation(); downloadSVG(piece); }}
                    className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                  >
                    <Download className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>
              {/* Info */}
              <div className="p-3">
                <h4 className="text-xs font-bold truncate mb-1">{piece.name}</h4>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-zinc-500 uppercase tracking-wider">{piece.type}</span>
                  <div className="flex gap-1">
                    {piece.colors.slice(0, 3).map((c, i) => (
                      <div key={i} className="w-2.5 h-2.5 rounded-full border border-zinc-700" style={{ background: c }} />
                    ))}
                  </div>
                </div>
                <p className="text-[10px] text-zinc-600 mt-1.5 font-mono">{piece.realSizeCm}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ═══ LIST VIEW ═══ */}
      {viewMode === 'list' && (
        <div className="bg-zinc-900/30 border border-zinc-800 rounded-xl overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/50">
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Preview</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Nombre</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Tipo</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Área</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Medida</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Herramienta</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Estado</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Modificado</th>
                <th className="px-4 py-3 text-[10px] font-bold text-zinc-500 uppercase tracking-wider text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/50">
              {filteredPieces.map(piece => (
                <tr
                  key={piece.id}
                  onClick={() => { setSelectedPiece(piece); setModalZoom(1); }}
                  className="hover:bg-zinc-800/20 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-2">
                    <div className="w-10 h-10 bg-zinc-950 rounded overflow-hidden flex items-center justify-center p-1">
                      {piece.svgContent ? (
                        <div className="w-full h-full [&>svg]:max-w-full [&>svg]:max-h-full [&>svg]:w-auto [&>svg]:h-auto" dangerouslySetInnerHTML={{ __html: piece.svgContent }} />
                      ) : (
                        <span className="text-zinc-700 text-xs">📄</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <span className="text-xs font-medium">{piece.name}</span>
                    {piece.product && <p className="text-[10px] text-zinc-600">{piece.product}</p>}
                  </td>
                  <td className="px-4 py-2 text-[10px] text-zinc-400 uppercase">{piece.type}</td>
                  <td className="px-4 py-2 text-[10px] text-zinc-400 capitalize">{piece.area}</td>
                  <td className="px-4 py-2 text-[10px] text-zinc-500 font-mono">{piece.realSizeCm}</td>
                  <td className="px-4 py-2 text-[10px] text-zinc-500">{piece.herramienta}</td>
                  <td className="px-4 py-2">
                    <span className={cn("inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase border", STATUS_COLORS[piece.status])}>
                      {STATUS_ICONS[piece.status]}
                      {piece.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-[10px] text-zinc-600 font-mono">{piece.lastModified}</td>
                  <td className="px-4 py-2 text-right">
                    <button
                      onClick={e => { e.stopPropagation(); downloadSVG(piece); }}
                      className="text-[10px] font-bold text-white uppercase hover:underline"
                    >
                      SVG ↓
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ═══ DETAIL MODAL ═══ */}
      {selectedPiece && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" onClick={() => setSelectedPiece(null)}>
          <div className="bg-[#0a0a0c] border border-zinc-800 rounded-2xl w-[90vw] max-w-5xl max-h-[90vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
            {/* Modal header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
              <div className="flex items-center gap-4">
                <div>
                  <h3 className="text-base font-bold">{selectedPiece.name}</h3>
                  <p className="text-xs text-zinc-500">{selectedPiece.product} · {selectedPiece.type} · {selectedPiece.area}</p>
                </div>
                <span className={cn("flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase border", STATUS_COLORS[selectedPiece.status])}>
                  {STATUS_ICONS[selectedPiece.status]}
                  {selectedPiece.status}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => setModalZoom(z => Math.max(z - 0.25, 0.25))} className="p-2 bg-zinc-900 border border-zinc-800 rounded-md hover:bg-zinc-800 transition-colors">
                  <ZoomOut className="w-4 h-4 text-zinc-400" />
                </button>
                <span className="text-xs font-mono text-zinc-500 w-12 text-center">{Math.round(modalZoom * 100)}%</span>
                <button onClick={() => setModalZoom(z => Math.min(z + 0.25, 4))} className="p-2 bg-zinc-900 border border-zinc-800 rounded-md hover:bg-zinc-800 transition-colors">
                  <ZoomIn className="w-4 h-4 text-zinc-400" />
                </button>
                <button onClick={() => setModalZoom(1)} className="p-2 bg-zinc-900 border border-zinc-800 rounded-md hover:bg-zinc-800 transition-colors">
                  <Maximize2 className="w-4 h-4 text-zinc-400" />
                </button>
                <div className="w-px h-6 bg-zinc-800 mx-1" />
                <button onClick={() => downloadSVG(selectedPiece)} className="flex items-center gap-1.5 px-3 py-2 bg-white text-black rounded-md text-xs font-bold hover:bg-zinc-200 transition-colors">
                  <Download className="w-3.5 h-3.5" />
                  Descargar SVG
                </button>
                <button onClick={() => setSelectedPiece(null)} className="p-2 bg-zinc-900 border border-zinc-800 rounded-md hover:bg-zinc-800 transition-colors">
                  <X className="w-4 h-4 text-zinc-400" />
                </button>
              </div>
            </div>

            {/* Modal body */}
            <div className="flex flex-1 overflow-hidden">
              {/* SVG preview area */}
              <div className="flex-1 relative overflow-auto bg-zinc-950 flex items-center justify-center" style={{ background: 'repeating-conic-gradient(#18181b 0% 25%, #111113 0% 50%) 50% / 20px 20px' }}>
                {/* Nav arrows */}
                {currentIndex > 0 && (
                  <button
                    onClick={goPrev}
                    className="absolute left-4 top-1/2 -translate-y-1/2 z-10 p-2 bg-black/60 border border-zinc-700 rounded-full hover:bg-zinc-800 transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                )}
                {currentIndex < filteredPieces.length - 1 && (
                  <button
                    onClick={goNext}
                    className="absolute right-4 top-1/2 -translate-y-1/2 z-10 p-2 bg-black/60 border border-zinc-700 rounded-full hover:bg-zinc-800 transition-colors"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                )}
                {/* SVG content */}
                {selectedPiece.svgContent && (
                  <div
                    className="p-12 transition-transform duration-200 [&>svg]:max-w-full [&>svg]:max-h-full"
                    style={{ transform: `scale(${modalZoom})`, transformOrigin: 'center center' }}
                    dangerouslySetInnerHTML={{ __html: selectedPiece.svgContent }}
                  />
                )}
                {/* Position indicator */}
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-3 py-1 bg-black/60 rounded-full text-[10px] font-mono text-zinc-500">
                  {currentIndex + 1} / {filteredPieces.length}
                </div>
              </div>

              {/* Right panel: metadata */}
              <div className="w-72 border-l border-zinc-800 p-5 overflow-y-auto space-y-5">
                <MetaSection icon={<Tag className="w-3.5 h-3.5" />} label="Tipo">
                  <span className="text-xs capitalize">{selectedPiece.type}</span>
                </MetaSection>

                <MetaSection icon={<Filter className="w-3.5 h-3.5" />} label="Área">
                  <span className="text-xs capitalize">{selectedPiece.area}</span>
                  <span className="text-[10px] text-zinc-600 ml-1">· {selectedPiece.medio === 'impresion' ? 'Impresión' : 'Digital'}</span>
                </MetaSection>

                <MetaSection icon={<Ruler className="w-3.5 h-3.5" />} label="Medida real">
                  <span className="text-xs font-mono">{selectedPiece.realSizeCm}</span>
                </MetaSection>

                <MetaSection icon={<Grid3X3 className="w-3.5 h-3.5" />} label="Canvas (px)">
                  <span className="text-xs font-mono">{selectedPiece.canvasPx}</span>
                </MetaSection>

                <MetaSection icon={<Info className="w-3.5 h-3.5" />} label="Herramienta">
                  <span className="text-xs">{selectedPiece.herramienta}</span>
                </MetaSection>

                <MetaSection icon={<Palette className="w-3.5 h-3.5" />} label="Colores">
                  <div className="flex gap-1.5 mt-1">
                    {selectedPiece.colors.map((c, i) => (
                      <div key={i} className="group/color relative">
                        <div className="w-6 h-6 rounded-md border border-zinc-700 cursor-pointer hover:scale-110 transition-transform" style={{ background: c }} />
                        <div className="absolute -top-6 left-1/2 -translate-x-1/2 hidden group-hover/color:block px-1.5 py-0.5 bg-black border border-zinc-700 rounded text-[9px] font-mono whitespace-nowrap">
                          {c}
                        </div>
                      </div>
                    ))}
                  </div>
                </MetaSection>

                {selectedPiece.product && (
                  <MetaSection icon={<Tag className="w-3.5 h-3.5" />} label="Producto">
                    <span className="text-xs">{selectedPiece.product}</span>
                  </MetaSection>
                )}

                <MetaSection icon={<Clock className="w-3.5 h-3.5" />} label="Última modificación">
                  <span className="text-xs font-mono">{selectedPiece.lastModified}</span>
                </MetaSection>

                {selectedPiece.notes && (
                  <div className="p-3 bg-zinc-900/50 border border-zinc-800 rounded-lg">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 block mb-1.5">Notas</span>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">{selectedPiece.notes}</p>
                  </div>
                )}

                {/* CLI hint */}
                <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600 block mb-2">Comando CLI</span>
                  <code className="text-[10px] font-mono text-zinc-500 leading-relaxed block">
                    py -m flujo render run<br />
                    &nbsp;&nbsp;projects/piezas_vectoriales/<br />
                    &nbsp;&nbsp;{selectedPiece.id}/config.json
                  </code>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Sub-components ───

function MetaSection({ icon, label, children }: { icon: React.ReactNode; label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-1">
        <span className="text-zinc-600">{icon}</span>
        <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">{label}</span>
      </div>
      <div className="text-zinc-300 pl-5">{children}</div>
    </div>
  );
}
