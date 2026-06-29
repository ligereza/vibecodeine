import { useEffect, useMemo, useState } from 'react';
import {
  Shapes, Search, X, ChevronLeft, ChevronRight,
  ZoomIn, ZoomOut, Download, LayoutGrid, List, CheckCircle2, Clock, FileEdit,
} from 'lucide-react';
import { cn } from '../utils/cn';

// ── Types ─────────────────────────────────────────────────────────────
interface SvgPiece {
  id: string;
  name: string;
  type: string;
  area: 'suplementos' | 'eventos' | 'general';
  medio: 'impresion' | 'digital';
  herramienta: string;
  product?: string;
  realSizeCm: string;
  canvasPx: string;
  colors: string[];
  lastModified: string;
  status: 'aprobado' | 'en-revision' | 'borrador';
  svgContent?: string;
  notes?: string;
  svgUrl?: string;
}

// ── Mock data ─────────────────────────────────────────────────────────
const MOCK_SVG_INDEX: SvgPiece[] = [
  {
    id: 'omega3_etiqueta',
    name: 'Etiqueta Omega 3',
    type: 'etiqueta',
    area: 'suplementos',
    medio: 'impresion',
    herramienta: 'SVG vectorizado',
    product: 'Omega 3 EPA/DHA',
    realSizeCm: '16.5 × 6.5 cm',
    canvasPx: 'SVG',
    colors: ['#2d5a4a', '#f8f1e3', '#675f55'],
    lastModified: 'repo local',
    status: 'aprobado',
    svgContent: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 130"><rect width="330" height="130" rx="8" fill="#2d5a4a"/><rect x="10" y="10" width="310" height="110" rx="6" fill="none" stroke="#f8f1e3" stroke-width="1" stroke-dasharray="4 2" opacity="0.4"/><text x="165" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="#f8f1e3" font-family="serif">OMEGA 3</text><text x="165" y="62" text-anchor="middle" font-size="9" fill="#a8c5b8" font-family="sans-serif" letter-spacing="3">EPA · DHA · SUPLEMENTO</text><line x1="40" y1="72" x2="290" y2="72" stroke="#f8f1e3" stroke-width="0.5" opacity="0.3"/><text x="165" y="90" text-anchor="middle" font-size="8" fill="#a8c5b8" font-family="sans-serif">1000 mg · 60 cápsulas blandas</text><text x="165" y="108" text-anchor="middle" font-size="7" fill="#6a9a8a" font-family="sans-serif">Mantener en lugar fresco y seco</text></svg>`,
  },
  {
    id: 'vitamina_c_etiqueta',
    name: 'Etiqueta Vitamina C',
    type: 'etiqueta',
    area: 'suplementos',
    medio: 'impresion',
    herramienta: 'SVG editable',
    product: 'Vitamina C 1000mg',
    realSizeCm: '16.5 × 6.5 cm',
    canvasPx: 'SVG',
    colors: ['#f59e0b', '#fff7ed', '#92400e'],
    lastModified: 'repo local',
    status: 'en-revision',
    svgContent: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 130"><rect width="330" height="130" rx="8" fill="#f59e0b"/><rect x="10" y="10" width="310" height="110" rx="6" fill="#fef3c7" opacity="0.15"/><text x="165" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="#fff7ed" font-family="serif">VITAMINA C</text><text x="165" y="62" text-anchor="middle" font-size="9" fill="#fde68a" font-family="sans-serif" letter-spacing="3">1000 MG · ASCÓRBICO</text><line x1="40" y1="72" x2="290" y2="72" stroke="#fff7ed" stroke-width="0.5" opacity="0.4"/><text x="165" y="90" text-anchor="middle" font-size="8" fill="#fde68a" font-family="sans-serif">60 comprimidos efervescentes</text><text x="165" y="108" text-anchor="middle" font-size="7" fill="#d97706" font-family="sans-serif">Sabor naranja natural</text></svg>`,
  },
  {
    id: 'flyer_evento_rd',
    name: 'Flyer Evento NGO RD',
    type: 'flyer',
    area: 'eventos',
    medio: 'impresion',
    herramienta: 'SVG vectorizado',
    product: 'Evento Reduciendo Daño',
    realSizeCm: '10 × 14 cm',
    canvasPx: 'SVG',
    colors: ['#18181b', '#10b981', '#6366f1'],
    lastModified: 'repo local',
    status: 'aprobado',
    svgContent: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 280"><rect width="200" height="280" fill="#18181b"/><rect x="0" y="0" width="200" height="4" fill="#10b981"/><rect x="0" y="276" width="200" height="4" fill="#10b981"/><text x="100" y="60" text-anchor="middle" font-size="11" fill="#10b981" font-family="sans-serif" letter-spacing="4">NGO REDUCIENDO DAÑO</text><text x="100" y="110" text-anchor="middle" font-size="28" font-weight="bold" fill="white" font-family="serif">SAFER</text><text x="100" y="138" text-anchor="middle" font-size="28" font-weight="bold" fill="#10b981" font-family="serif">SPACES</text><text x="100" y="165" text-anchor="middle" font-size="8" fill="#71717a" font-family="sans-serif" letter-spacing="2">INTERVENCIÓN EN TERRENO</text><line x1="30" y1="180" x2="170" y2="180" stroke="#3f3f46" stroke-width="0.5"/><text x="100" y="210" text-anchor="middle" font-size="9" fill="#a1a1aa" font-family="sans-serif">Testeo · Contención · Información</text><text x="100" y="250" text-anchor="middle" font-size="8" fill="#52525b" font-family="sans-serif">ngo-rd.cl · @ngo_rd</text></svg>`,
  },
  {
    id: 'post_ig_omega3',
    name: 'Post IG Omega 3',
    type: 'post-ig',
    area: 'suplementos',
    medio: 'digital',
    herramienta: 'SVG editable',
    product: 'Omega 3 EPA/DHA',
    realSizeCm: '1080 × 1080 px',
    canvasPx: 'SVG',
    colors: ['#2d5a4a', '#f8f1e3', '#10b981'],
    lastModified: 'repo local',
    status: 'borrador',
    svgContent: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" fill="#2d5a4a"/><circle cx="100" cy="85" r="50" fill="#10b981" opacity="0.15"/><circle cx="100" cy="85" r="40" fill="none" stroke="#10b981" stroke-width="1" opacity="0.4"/><text x="100" y="78" text-anchor="middle" font-size="14" font-weight="bold" fill="#f8f1e3" font-family="serif">OMEGA 3</text><text x="100" y="96" text-anchor="middle" font-size="8" fill="#a8c5b8" font-family="sans-serif">EPA · DHA</text><text x="100" y="155" text-anchor="middle" font-size="9" fill="#f8f1e3" font-family="sans-serif">Tu salud, nuestra misión.</text><text x="100" y="175" text-anchor="middle" font-size="7" fill="#6a9a8a" font-family="sans-serif">@suplementos_rd</text></svg>`,
  },
  {
    id: 'pendon_suplementos',
    name: 'Pendón Suplementos',
    type: 'pendon',
    area: 'suplementos',
    medio: 'impresion',
    herramienta: 'SVG vectorizado',
    product: 'Línea Suplementos',
    realSizeCm: '80 × 180 cm',
    canvasPx: 'SVG',
    colors: ['#1e3a5f', '#f0f4f8', '#3b82f6'],
    lastModified: 'repo local',
    status: 'aprobado',
    svgContent: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 360"><rect width="160" height="360" rx="4" fill="#1e3a5f"/><rect x="0" y="0" width="160" height="60" fill="#3b82f6" opacity="0.3"/><text x="80" y="28" text-anchor="middle" font-size="10" font-weight="bold" fill="white" font-family="sans-serif">SUPLEMENTOS</text><text x="80" y="48" text-anchor="middle" font-size="7" fill="#93c5fd" font-family="sans-serif" letter-spacing="2">LÍNEA COMPLETA</text><text x="80" y="120" text-anchor="middle" font-size="13" font-weight="bold" fill="white" font-family="serif">Omega 3</text><text x="80" y="155" text-anchor="middle" font-size="13" font-weight="bold" fill="white" font-family="serif">Vitamina C</text><text x="80" y="190" text-anchor="middle" font-size="13" font-weight="bold" fill="white" font-family="serif">Magnesio</text><text x="80" y="225" text-anchor="middle" font-size="13" font-weight="bold" fill="white" font-family="serif">Zinc</text><line x1="20" y1="250" x2="140" y2="250" stroke="#3b82f6" stroke-width="0.5"/><text x="80" y="290" text-anchor="middle" font-size="8" fill="#93c5fd" font-family="sans-serif">Calidad certificada</text><text x="80" y="340" text-anchor="middle" font-size="7" fill="#475569" font-family="sans-serif">suplementos-rd.cl</text></svg>`,
  },
  {
    id: 'logo_rd',
    name: 'Logo NGO RD',
    type: 'logo',
    area: 'general',
    medio: 'digital',
    herramienta: 'SVG vectorizado',
    product: 'Identidad NGO RD',
    realSizeCm: 'variable',
    canvasPx: 'SVG',
    colors: ['#18181b', '#10b981', 'white'],
    lastModified: 'repo local',
    status: 'aprobado',
    svgContent: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" fill="#18181b"/><circle cx="100" cy="90" r="55" fill="none" stroke="#10b981" stroke-width="2"/><circle cx="100" cy="90" r="45" fill="none" stroke="#10b981" stroke-width="0.5" opacity="0.3"/><text x="100" y="83" text-anchor="middle" font-size="18" font-weight="bold" fill="white" font-family="sans-serif">NGO</text><text x="100" y="103" text-anchor="middle" font-size="11" fill="#10b981" font-family="sans-serif" letter-spacing="1">REDUCIENDO</text><text x="100" y="118" text-anchor="middle" font-size="11" fill="#10b981" font-family="sans-serif" letter-spacing="1">DAÑO</text><text x="100" y="170" text-anchor="middle" font-size="7" fill="#52525b" font-family="sans-serif" letter-spacing="2">HARM REDUCTION</text></svg>`,
  },
];

const TYPE_OPTIONS = ['all', 'etiqueta', 'flyer', 'pendon', 'post-ig', 'logo', 'rider', 'cartelera', 'sticker'];

const STATUS_CONFIG = {
  aprobado: { icon: <CheckCircle2 className="h-3 w-3" />, color: 'border-emerald-500/30 bg-emerald-950/40 text-emerald-400' },
  'en-revision': { icon: <Clock className="h-3 w-3" />, color: 'border-blue-500/30 bg-blue-950/40 text-blue-400' },
  borrador: { icon: <FileEdit className="h-3 w-3" />, color: 'border-zinc-600 bg-zinc-800/40 text-zinc-400' },
};

// ── API loader ────────────────────────────────────────────────────────
async function loadFromApi(): Promise<SvgPiece[]> {
  const res = await fetch('/api/list-svg-works');
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (!data || !data.groups) {
    return MOCK_SVG_INDEX;
  }

  const list: SvgPiece[] = [];
  
  for (const [groupName, items] of Object.entries(data.groups)) {
    const arr = items as any[];
    for (const item of arr) {
      const isEditable = item.kind === 'editable' || item.name.toLowerCase().includes('editable');
      const isVector = item.kind === 'vectorizado' || item.name.toLowerCase().includes('vectorizado');
      const area = groupName.toLowerCase().includes('suplementos') ? 'suplementos' : 'eventos';
      const type = item.name.toLowerCase().includes('etiqueta') ? 'etiqueta' : 'flyer';
      const tool = isEditable ? 'SVG editable' : 'SVG vectorizado';
      
      let svgContent = '';
      try {
        const svgRes = await fetch('/' + item.path);
        if (svgRes.ok) {
          svgContent = await svgRes.text();
        }
      } catch (e) {
        console.error("Error fetching content for " + item.path, e);
      }

      // Format name nicely
      const cleanProduct = item.name
        .replace('_editable', '')
        .replace('_vectorizado', '')
        .replace('.svg', '')
        .replace(/^[0-9]+_/, '')
        .replace(/_/g, ' ')
        .toUpperCase();

      list.push({
        id: item.name.replace(/\.[^/.]+$/, ""),
        name: isEditable ? `${cleanProduct} (Editable)` : `${cleanProduct} (Vectorizado)`,
        type: type,
        area: area as any,
        medio: 'impresion',
        herramienta: tool,
        product: cleanProduct,
        realSizeCm: '10 × 14 cm',
        canvasPx: '2000 × 2800 px',
        colors: area === 'suplementos' ? ['#173F2F', '#F6EFE3', '#161513'] : ['#09090b', '#3f3f46'],
        lastModified: 'repositorio local',
        status: isVector ? 'aprobado' : 'en-revision',
        svgContent: svgContent || `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#161513"/><text x="50" y="55" text-anchor="middle" fill="#fff" font-size="5" font-family="sans-serif">${item.name}</text></svg>`,
        svgUrl: '/' + item.path,
      });
    }
  }

  return list.length > 0 ? list : MOCK_SVG_INDEX;
}

// ── Main component ────────────────────────────────────────────────────
export default function SvgVisualizer() {
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterArea, setFilterArea] = useState<'all' | 'suplementos' | 'eventos' | 'general'>('all');
  const [filterStatus, setFilterStatus] = useState<'all' | 'aprobado' | 'en-revision' | 'borrador'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedPiece, setSelectedPiece] = useState<SvgPiece | null>(null);
  const [modalZoom, setModalZoom] = useState(1);
  const [pieces, setPieces] = useState<SvgPiece[]>(MOCK_SVG_INDEX);
  const [sourceStatus, setSourceStatus] = useState('Demo local');

  useEffect(() => {
    let alive = true;
    if (window.location.protocol === 'file:') {
      setSourceStatus('Demo local (abre con py -m flujo app para datos reales)');
      return;
    }
    setSourceStatus('Cargando SVG reales...');
    loadFromApi()
      .then(data => alive && (setPieces(data), setSourceStatus(`${data.length} piezas`)))
      .catch(() => alive && setSourceStatus('Fallback demo activo'));
    return () => { alive = false; };
  }, []);

  const filtered = useMemo(() => pieces.filter(p => {
    const q = search.toLowerCase();
    return (
      (!q || p.name.toLowerCase().includes(q) || p.product?.toLowerCase().includes(q) || p.type.includes(q)) &&
      (filterType === 'all' || p.type === filterType) &&
      (filterArea === 'all' || p.area === filterArea) &&
      (filterStatus === 'all' || p.status === filterStatus)
    );
  }), [pieces, search, filterType, filterArea, filterStatus]);

  const stats = useMemo(() => ({
    total: pieces.length,
    aprobado: pieces.filter(p => p.status === 'aprobado').length,
    revision: pieces.filter(p => p.status === 'en-revision').length,
    borrador: pieces.filter(p => p.status === 'borrador').length,
  }), [pieces]);

  const currentIndex = selectedPiece ? filtered.findIndex(p => p.id === selectedPiece.id) : -1;

  const downloadSVG = (piece: SvgPiece) => {
    if (!piece.svgContent) return;
    const blob = new Blob([piece.svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${piece.id}.svg`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-black">
            <Shapes className="h-6 w-6" /> Visor de Diseños
          </h1>
          <p className="mt-1 text-sm text-zinc-500">
            Galería de piezas vectoriales — etiquetas, flyers, pendones, stickers, logos
          </p>
          <p className="text-[10px] text-zinc-600 mt-0.5">{sourceStatus}</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <span className="text-emerald-400 font-bold">{stats.aprobado}</span> aprobados ·
          <span className="text-blue-400 font-bold">{stats.revision}</span> revisión ·
          <span className="text-zinc-400 font-bold">{stats.borrador}</span> borradores
        </div>
      </div>

      {/* Search + view toggle */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar por nombre, producto o tipo..."
            className="w-full rounded-xl border border-zinc-800 bg-zinc-950 pl-10 pr-4 py-2.5 text-sm outline-none focus:border-zinc-600 transition-colors"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300">
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
        <button
          onClick={() => setViewMode(v => v === 'grid' ? 'list' : 'grid')}
          className="flex items-center gap-1.5 rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          {viewMode === 'grid' ? <List className="h-4 w-4" /> : <LayoutGrid className="h-4 w-4" />}
        </button>
      </div>

      {/* Filter chips */}
      <div className="flex flex-wrap gap-4">
        {/* Type */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Tipo:</span>
          {TYPE_OPTIONS.map(t => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={cn(
                'rounded-full px-2.5 py-0.5 text-[10px] font-bold transition-colors border',
                filterType === t
                  ? 'border-zinc-500 bg-zinc-800 text-zinc-200'
                  : 'border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300'
              )}
            >
              {t === 'all' ? 'Todos' : t}
            </button>
          ))}
        </div>

        {/* Area */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Área:</span>
          {(['all', 'suplementos', 'eventos', 'general'] as const).map(a => (
            <button
              key={a}
              onClick={() => setFilterArea(a)}
              className={cn(
                'rounded-full px-2.5 py-0.5 text-[10px] font-bold transition-colors border',
                filterArea === a
                  ? 'border-emerald-600 bg-emerald-950/50 text-emerald-300'
                  : 'border-zinc-800 text-zinc-500 hover:border-zinc-600'
              )}
            >
              {a === 'all' ? 'Todas' : a}
            </button>
          ))}
        </div>

        {/* Status */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[9px] font-bold uppercase tracking-widest text-zinc-600">Estado:</span>
          {(['all', 'aprobado', 'en-revision', 'borrador'] as const).map(s => (
            <button
              key={s}
              onClick={() => setFilterStatus(s)}
              className={cn(
                'rounded-full px-2.5 py-0.5 text-[10px] font-bold transition-colors border',
                filterStatus === s
                  ? 'border-zinc-500 bg-zinc-800 text-zinc-200'
                  : 'border-zinc-800 text-zinc-500 hover:border-zinc-600'
              )}
            >
              {s === 'all' ? 'Todos' : s}
            </button>
          ))}
        </div>
      </div>

      {/* Results count */}
      <div className="flex items-center justify-between text-xs text-zinc-500">
        <span>{filtered.length} {filtered.length === 1 ? 'pieza' : 'piezas'} encontradas</span>
        {(filterType !== 'all' || filterArea !== 'all' || filterStatus !== 'all' || search) && (
          <button
            onClick={() => { setSearch(''); setFilterType('all'); setFilterArea('all'); setFilterStatus('all'); }}
            className="text-zinc-500 hover:text-zinc-200 transition-colors"
          >
            Limpiar filtros
          </button>
        )}
      </div>

      {/* Grid view */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map(piece => {
            const status = STATUS_CONFIG[piece.status];
            return (
              <div
                key={piece.id}
                onClick={() => { setSelectedPiece(piece); setModalZoom(1); }}
                className="group bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden hover:border-zinc-600 transition-all cursor-pointer"
              >
                {/* Preview */}
                <div className="relative bg-zinc-950 flex items-center justify-center p-4" style={{ minHeight: 140 }}>
                  {piece.svgContent ? (
                    <div
                      className="w-full h-full flex items-center justify-center"
                      dangerouslySetInnerHTML={{ __html: piece.svgContent }}
                    />
                  ) : (
                    <span className="text-4xl">📄</span>
                  )}
                  {/* Status badge */}
                  <span className={cn('absolute top-2 right-2 flex items-center gap-1 rounded-full border px-1.5 py-0.5 text-[9px] font-bold', status.color)}>
                    {status.icon}
                    {piece.status}
                  </span>
                </div>
                {/* Info */}
                <div className="px-3 py-2 space-y-1">
                  <p className="text-xs font-bold truncate">{piece.name}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-zinc-500">{piece.type}</span>
                    <div className="flex gap-1">
                      {piece.colors.slice(0, 3).map((c, i) => (
                        <span key={i} className="h-3 w-3 rounded-full border border-zinc-700" style={{ backgroundColor: c }} />
                      ))}
                    </div>
                  </div>
                  <p className="text-[10px] text-zinc-600">{piece.realSizeCm}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* List view */}
      {viewMode === 'list' && (
        <div className="rounded-2xl border border-zinc-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-zinc-950/80">
              <tr>
                {['Preview', 'Nombre', 'Tipo', 'Área', 'Medida', 'Estado', ''].map(h => (
                  <th key={h} className="px-3 py-2.5 text-left text-[9px] font-bold uppercase tracking-widest text-zinc-600">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {filtered.map(piece => {
                const status = STATUS_CONFIG[piece.status];
                return (
                  <tr
                    key={piece.id}
                    onClick={() => { setSelectedPiece(piece); setModalZoom(1); }}
                    className="hover:bg-zinc-800/20 transition-colors cursor-pointer"
                  >
                    <td className="px-3 py-2">
                      <div className="h-10 w-14 rounded border border-zinc-800 bg-zinc-950 overflow-hidden flex items-center justify-center">
                        {piece.svgContent ? (
                          <div className="scale-50 origin-center" dangerouslySetInnerHTML={{ __html: piece.svgContent }} />
                        ) : <span className="text-lg">📄</span>}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <p className="font-medium">{piece.name}</p>
                      {piece.product && <p className="text-[10px] text-zinc-500">{piece.product}</p>}
                    </td>
                    <td className="px-3 py-2 text-xs text-zinc-400">{piece.type}</td>
                    <td className="px-3 py-2 text-xs text-zinc-400">{piece.area}</td>
                    <td className="px-3 py-2 text-xs text-zinc-400">{piece.realSizeCm}</td>
                    <td className="px-3 py-2">
                      <span className={cn('flex w-fit items-center gap-1 rounded-full border px-2 py-0.5 text-[9px] font-bold', status.color)}>
                        {status.icon}
                        {piece.status}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      <button
                        onClick={e => { e.stopPropagation(); downloadSVG(piece); }}
                        className="text-zinc-600 hover:text-zinc-200 transition-colors"
                        title="Descargar SVG"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {!filtered.length && (
        <div className="rounded-2xl border border-dashed border-zinc-800 p-10 text-center text-zinc-500">
          No hay piezas que coincidan.
        </div>
      )}

      {/* Detail Modal */}
      {selectedPiece && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
          onClick={() => setSelectedPiece(null)}
        >
          <div
            className="relative w-full max-w-4xl rounded-2xl border border-zinc-700 bg-zinc-900 shadow-2xl overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
              <div>
                <p className="font-bold">{selectedPiece.name}</p>
                <p className="text-xs text-zinc-500">
                  {selectedPiece.product} · {selectedPiece.type} · {selectedPiece.area}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className={cn('flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold', STATUS_CONFIG[selectedPiece.status].color)}>
                  {STATUS_CONFIG[selectedPiece.status].icon}
                  {selectedPiece.status}
                </span>
                <button
                  onClick={() => setModalZoom(z => Math.max(0.25, z - 0.25))}
                  className="rounded-lg border border-zinc-700 p-1.5 text-zinc-400 hover:text-zinc-200 transition-colors"
                >
                  <ZoomOut className="h-4 w-4" />
                </button>
                <span className="text-xs text-zinc-500 w-10 text-center">{Math.round(modalZoom * 100)}%</span>
                <button
                  onClick={() => setModalZoom(z => Math.min(4, z + 0.25))}
                  className="rounded-lg border border-zinc-700 p-1.5 text-zinc-400 hover:text-zinc-200 transition-colors"
                >
                  <ZoomIn className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setSelectedPiece(null)}
                  className="rounded-lg border border-zinc-700 p-1.5 text-zinc-400 hover:text-red-400 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Modal body */}
            <div className="grid md:grid-cols-[1fr_260px]">
              {/* SVG preview */}
              <div className="relative bg-zinc-950 flex items-center justify-center overflow-hidden" style={{ minHeight: 320 }}>
                {/* Nav arrows */}
                {currentIndex > 0 && (
                  <button
                    onClick={() => setSelectedPiece(filtered[currentIndex - 1])}
                    className="absolute left-3 rounded-full border border-zinc-700 bg-zinc-900/80 p-2 text-zinc-300 hover:text-white transition-colors"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </button>
                )}
                {currentIndex < filtered.length - 1 && (
                  <button
                    onClick={() => setSelectedPiece(filtered[currentIndex + 1])}
                    className="absolute right-3 rounded-full border border-zinc-700 bg-zinc-900/80 p-2 text-zinc-300 hover:text-white transition-colors"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </button>
                )}

                {selectedPiece.svgContent && (
                  <div
                    style={{ transform: `scale(${modalZoom})`, transformOrigin: 'center', transition: 'transform 0.2s' }}
                    className="p-6 max-w-xs w-full"
                    dangerouslySetInnerHTML={{ __html: selectedPiece.svgContent }}
                  />
                )}

                <span className="absolute bottom-2 right-3 text-[10px] text-zinc-700">
                  {currentIndex + 1} / {filtered.length}
                </span>
              </div>

              {/* Metadata panel */}
              <div className="border-l border-zinc-800 p-4 space-y-3 overflow-y-auto" style={{ maxHeight: 480 }}>
                {[
                  { label: 'Tipo', value: selectedPiece.type },
                  { label: 'Área', value: `${selectedPiece.area} · ${selectedPiece.medio}` },
                  { label: 'Medida real', value: selectedPiece.realSizeCm },
                  { label: 'Herramienta', value: selectedPiece.herramienta },
                  { label: 'Producto', value: selectedPiece.product },
                  { label: 'Modificado', value: selectedPiece.lastModified },
                ].map(({ label, value }) => value ? (
                  <div key={label}>
                    <p className="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-0.5">{label}</p>
                    <p className="text-xs text-zinc-300">{value}</p>
                  </div>
                ) : null)}

                {/* Colors */}
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-1">Colores</p>
                  <div className="flex gap-2 flex-wrap">
                    {selectedPiece.colors.map((c, i) => (
                      <div key={i} className="flex items-center gap-1.5">
                        <span className="h-5 w-5 rounded border border-zinc-700 shrink-0" style={{ backgroundColor: c }} />
                        <span className="text-[10px] text-zinc-400 font-mono">{c}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedPiece.notes && (
                  <div>
                    <p className="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-0.5">Notas</p>
                    <p className="text-[10px] text-zinc-500 break-all">{selectedPiece.notes}</p>
                  </div>
                )}

                {/* CLI hint */}
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-widest text-zinc-600 mb-1">Comando CLI</p>
                  <code className="block rounded-lg bg-black/40 p-2 text-[9px] text-zinc-500 leading-4">
                    py -m flujo render run<br />
                    projects/piezas_vectoriales/<br />
                    {selectedPiece.id}/config.json
                  </code>
                </div>

                {/* Download */}
                {selectedPiece.svgContent && (
                  <button
                    onClick={() => downloadSVG(selectedPiece)}
                    className="w-full flex items-center justify-center gap-2 rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2 text-xs font-bold text-zinc-300 hover:bg-zinc-700 transition-colors"
                  >
                    <Download className="h-3.5 w-3.5" /> Descargar SVG
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
