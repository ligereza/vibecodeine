import React, { useRef, useState, useCallback, useEffect } from 'react';
import { 
  Map, Download, Plus, Trash2, Eye, EyeOff, Printer, RotateCcw,
  Scan, Users, Moon, Home, Table, Armchair, Box, Zap,
  Lightbulb, Droplet, Thermometer, User, ShieldAlert, HeartPulse, Utensils,
  ChevronRight, ChevronLeft, Settings, Copy, Layers, Grid3X3, FileText,
  Heart, AlertTriangle, Coffee, RefreshCw, Flame
} from 'lucide-react';
import { cn } from '../utils/cn';
import { RD_PALETTE, RD_LOGO, calcCostos, formatCLP, ALL_PACKS, PACKS, type ExportTheme, type PackId } from '../rdBrand';

// ── Types ────────────────────────────────────────────────────────────
type TechnicalSymbolKey = string;

interface Element {
  id: string;
  type: 'rect' | 'symbol';
  symbolType?: TechnicalSymbolKey;
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
  color: string;
  visible: boolean;
  symbolKey?: string;
  locked?: boolean;
  category?: string;
}

const ZONE_COLORS: Record<string, string> = {
  testeo: '#2d5a4a',
  contencion: '#7c3aed',
  informativo: '#0369a1',
  descanso: '#059669',
  coordinacion: '#ca8a04',
  circulacion: '#9ca3af',
  power: '#f59e0b',
  heating: '#ef4444',
  rack: '#4b5563',
  extinguisher: '#dc2626',
  water: '#2563eb',
  scan: '#06b6d4',
  terrain: '#84cc16',
  circulation: '#9ca3af',
  sensory: '#8b5cf6',
  tent: '#2d5a4a',
  table: '#10b981',
  chairs: '#ca8a04',
  trash: '#71717a',
  light: '#fde047',
  contact: '#0ea5e9',
  security: '#f97316',
  medical: '#dc2626',
  food: '#a16207'
};

const ZONE_LABELS: Record<string, string> = {
  testeo: 'Zona Testeo',
  contencion: 'Contención',
  informativo: 'Stand Informativo',
  descanso: 'Zona Descanso',
  coordinacion: 'Coordinación',
  circulacion: 'Circulación Público',
  power: 'Electricidad',
  heating: 'Calefacción',
  rack: 'Rack Almacén',
  extinguisher: 'Extintor',
  water: 'Punto de Agua',
  scan: 'Medidas Recinto',
  terrain: 'Terreno Estable',
  circulation: 'Circulación Pública',
  sensory: 'Baja Estimulación',
  tent: 'Toldo / Carpa',
  table: 'Mesas',
  chairs: 'Sillas',
  trash: 'Basureros / Señalética',
  light: 'Iluminación',
  contact: 'Contacto Producción',
  security: 'Seguridad',
  medical: 'Equipo Médico',
  food: 'Alimentación Equipo'
};


type SymbolSpec = { key: TechnicalSymbolKey; label: string; color: string; icon: string; x: number; y: number; w: number; h: number };

const SYMBOL_CATALOG: SymbolSpec[] = [
  { key: 'scan', label: 'Medidas', color: ZONE_COLORS.scan, icon: 'Scan', x: 180, y: 260, w: 150, h: 150 },
  { key: 'terrain', label: 'Terreno', color: ZONE_COLORS.terrain, icon: 'Map', x: 380, y: 260, w: 150, h: 150 },
  { key: 'circulation', label: 'Circulación', color: ZONE_COLORS.circulation, icon: 'Users', x: 580, y: 260, w: 170, h: 150 },
  { key: 'sensory', label: 'Baja Estim.', color: ZONE_COLORS.sensory, icon: 'Moon', x: 780, y: 260, w: 170, h: 150 },
  { key: 'tent', label: 'Toldo 3x3', color: ZONE_COLORS.tent, icon: 'Home', x: 250, y: 350, w: 190, h: 170 },
  { key: 'table', label: 'Mesas', color: ZONE_COLORS.table, icon: 'Table', x: 500, y: 700, w: 180, h: 140 },
  { key: 'chairs', label: 'Sillas', color: ZONE_COLORS.chairs, icon: 'Armchair', x: 760, y: 700, w: 180, h: 140 },
  { key: 'rack', label: 'Rack', color: ZONE_COLORS.rack, icon: 'Box', x: 150, y: 1350, w: 160, h: 160 },
  { key: 'trash', label: 'Basureros', color: ZONE_COLORS.trash, icon: 'Trash2', x: 360, y: 1350, w: 160, h: 160 },
  { key: 'power', label: 'Electricidad', color: ZONE_COLORS.power, icon: 'Zap', x: 1800, y: 700, w: 160, h: 160 },
  { key: 'light', label: 'Iluminación', color: ZONE_COLORS.light, icon: 'Lightbulb', x: 2000, y: 700, w: 160, h: 160 },
  { key: 'water', label: 'Agua', color: ZONE_COLORS.water, icon: 'Droplet', x: 1800, y: 1300, w: 160, h: 160 },
  { key: 'heating', label: 'Calefacción', color: ZONE_COLORS.heating, icon: 'Thermometer', x: 1800, y: 1000, w: 160, h: 160 },
  { key: 'contact', label: 'Producción', color: ZONE_COLORS.contact, icon: 'User', x: 2200, y: 700, w: 160, h: 160 },
  { key: 'security', label: 'Seguridad', color: ZONE_COLORS.security, icon: 'ShieldAlert', x: 2200, y: 900, w: 160, h: 160 },
  { key: 'medical', label: 'Equipo Médico', color: ZONE_COLORS.medical, icon: 'HeartPulse', x: 2200, y: 1100, w: 160, h: 160 },
  { key: 'food', label: 'Alimentación', color: ZONE_COLORS.food, icon: 'Utensils', x: 2200, y: 1300, w: 160, h: 160 },
  { key: 'testeo', label: 'Testeo', color: ZONE_COLORS.testeo, icon: 'AlertTriangle', x: 1000, y: 550, w: 200, h: 200 },
  { key: 'contencion', label: 'Contención', color: ZONE_COLORS.contencion, icon: 'Heart', x: 1900, y: 550, w: 200, h: 200 },
  { key: 'extinguisher', label: 'Extintor', color: ZONE_COLORS.extinguisher, icon: 'Flame', x: 2400, y: 900, w: 160, h: 160 },
];

const SYMBOL_BY_KEY = Object.fromEntries(SYMBOL_CATALOG.map(s => [s.key, s])) as Record<string, SymbolSpec>;

const PLANO_FRAME = { x: 50, y: 50, w: 2870, h: 1950 };
const GRID = 20;

const REQUIREMENT_SYMBOL_MAP: Record<string, TechnicalSymbolKey> = {
  'Medidas disponibles del recinto (int/ext)': 'scan',
  'Tipo de terreno (nivelado, estable)': 'terrain',
  'Circulación pública segura': 'circulation',
  'Zona con menor estimulación sensorial para descanso': 'sensory',
  'Toldo/carpa (mínimo 3×3m)': 'tent',
  'Mesas (2-3 según modalidad)': 'table',
  'Sillas (4-6 por stand)': 'chairs',
  'Rack o caja de almacenamiento': 'rack',
  'Basureros, señalética': 'trash',
  'Punto eléctrico disponible': 'power',
  'Iluminación adecuada': 'light',
  'Agua/hidratación si aplica': 'water',
  'Calefacción si exterior nocturno': 'heating',
  'Contacto directo con producción': 'contact',
  'Coordinación con seguridad privada': 'security',
  'Acceso a equipo médico del evento': 'medical',
  'Extintor operativo en el stand': 'extinguisher',
  'Alimentación si jornada > 5 horas': 'food',
};

const makeSymbolElement = (key: TechnicalSymbolKey, idPrefix = 'symbol'): Element => {
  const spec = SYMBOL_BY_KEY[key] || SYMBOL_BY_KEY.power;
  return {
    id: `${idPrefix}-${spec.key}`,
    type: 'symbol',
    symbolKey: spec.key,
    x: spec.x,
    y: spec.y,
    w: spec.w,
    h: spec.h,
    label: spec.label,
    color: spec.color,
    visible: true,
  };
};

// ── Checklist Data (18 requirements in 4 categories) ───
const CHECKLIST_SECTIONS = [
  {
    title: 'Espacio',
    iconName: 'Grid3X3',
    items: [
      { text: 'Medidas disponibles del recinto (int/ext)', icon: 'Scan' },
      { text: 'Tipo de terreno (nivelado, estable)', icon: 'Map' },
      { text: 'Circulación pública segura', icon: 'Users' },
      { text: 'Zona con menor estimulación sensorial para descanso', icon: 'Moon' }
    ]
  },
  {
    title: 'Infraestructura',
    iconName: 'Square',
    items: [
      { text: 'Toldo/carpa (mínimo 3×3m)', icon: 'Home' },
      { text: 'Mesas (2-3 según modalidad)', icon: 'Table' },
      { text: 'Sillas (4-6 por stand)', icon: 'Armchair' },
      { text: 'Rack o caja de almacenamiento', icon: 'Box' },
      { text: 'Basureros, señalética', icon: 'Trash2' }
    ]
  },
  {
    title: 'Servicios',
    iconName: 'Zap',
    items: [
      { text: 'Punto eléctrico disponible', icon: 'Zap' },
      { text: 'Iluminación adecuada', icon: 'Lightbulb' },
      { text: 'Agua/hidratación si aplica', icon: 'Droplet' },
      { text: 'Calefacción si exterior nocturno', icon: 'Thermometer' }
    ]
  },
  {
    title: 'Coordinación',
    iconName: 'Users',
    items: [
      { text: 'Contacto directo con producción', icon: 'User' },
      { text: 'Coordinación con seguridad privada', icon: 'ShieldAlert' },
      { text: 'Acceso a equipo médico del evento', icon: 'HeartPulse' },
      { text: 'Alimentación si jornada > 5 horas', icon: 'Utensils' },
      { text: 'Extintor operativo en el stand', icon: 'Flame' }
    ]
  }
];

// Categoria de cada simbolo tecnico, derivada de las mismas 4 categorias del
// checklist (Espacio/Infraestructura/Servicios/Coordinacion) via REQUIREMENT_SYMBOL_MAP.
// Los simbolos sin item de checklist asociado (zonas de servicio: testeo, contencion)
// caen en 'Zonas de Atención'.
const ITEM_TEXT_TO_CATEGORY: Record<string, string> = {};
CHECKLIST_SECTIONS.forEach(section => {
  section.items.forEach(item => { ITEM_TEXT_TO_CATEGORY[item.text] = section.title; });
});
const SYMBOL_CATEGORY: Record<TechnicalSymbolKey, string> = {};
Object.entries(REQUIREMENT_SYMBOL_MAP).forEach(([itemText, symbolKey]) => {
  SYMBOL_CATEGORY[symbolKey] = ITEM_TEXT_TO_CATEGORY[itemText] || 'Zonas de Atención';
});
const CATEGORY_ORDER = ['Servicios', 'Infraestructura', 'Coordinación', 'Espacio', 'Zonas de Atención'];

// Helper to render Lucide icons dynamically for requirements
const renderRequirementIcon = (iconName: string, className = "w-4 h-4 text-zinc-400") => {
  switch (iconName) {
    case 'Scan': return <Scan className={className} />;
    case 'Map': return <Map className={className} />;
    case 'Users': return <Users className={className} />;
    case 'Moon': return <Moon className={className} />;
    case 'Home': return <Home className={className} />;
    case 'Table': return <Table className={className} />;
    case 'Armchair': return <Armchair className={className} />;
    case 'Box': return <Box className={className} />;
    case 'Trash2': return <Trash2 className={className} />;
    case 'Zap': return <Zap className={className} />;
    case 'Lightbulb': return <Lightbulb className={className} />;
    case 'Droplet': return <Droplet className={className} />;
    case 'Thermometer': return <Thermometer className={className} />;
    case 'User': return <User className={className} />;
    case 'ShieldAlert': return <ShieldAlert className={className} />;
    case 'HeartPulse': return <HeartPulse className={className} />;
    case 'Utensils': return <Utensils className={className} />;
    case 'Flame': return <Flame className={className} />;
    default: return <Grid3X3 className={className} />;
  }
};

const withMedida = (label: string, m: string) => `${label} (${m})`;

const placedSymbol = (key: TechnicalSymbolKey, id: string, x: number, y: number): Element => {
  const spec = SYMBOL_BY_KEY[key] || SYMBOL_BY_KEY.power;
  const category = SYMBOL_CATEGORY[key] || 'Zonas de Atención';
  return { id, type: 'symbol', symbolKey: spec.key, x, y, w: spec.w, h: spec.h, label: spec.label, color: spec.color, visible: true, category };
};

// Iconos agrupados por categoria (misma taxonomia del checklist), empaquetados
// en filas por ancho disponible (flow-wrap) en vez de 1 fila fija por categoria:
// evita colisionar con "Coordinacion Operativa" y usa el alto del frame mejor.
const ICON_ORIGIN = { x: 90, y: 930 };
const ICON_GAP_X = 200;
const ICON_ROW_HEIGHT = 330;
const ICON_CATEGORY_GAP_X = 260;
const ICON_AVAILABLE_WIDTH = 2700;

function layoutIconGroups(specs: { id: string; key: TechnicalSymbolKey }[]): Element[] {
  const groups: Record<string, { id: string; key: TechnicalSymbolKey }[]> = {};
  specs.forEach(spec => {
    const cat = SYMBOL_CATEGORY[spec.key] || 'Zonas de Atención';
    (groups[cat] = groups[cat] || []).push(spec);
  });
  const activeCats = CATEGORY_ORDER.filter(cat => groups[cat] && groups[cat].length);
  const out: Element[] = [];
  let curX = ICON_ORIGIN.x;
  let curRow = 0;
  activeCats.forEach(cat => {
    const items = groups[cat];
    const width = items.length * ICON_GAP_X;
    if (curX !== ICON_ORIGIN.x && curX + width > ICON_ORIGIN.x + ICON_AVAILABLE_WIDTH) {
      curRow += 1;
      curX = ICON_ORIGIN.x;
    }
    const y = ICON_ORIGIN.y + curRow * ICON_ROW_HEIGHT;
    items.forEach((spec, i) => out.push(placedSymbol(spec.key, spec.id, curX + i * ICON_GAP_X, y)));
    curX += width + ICON_CATEGORY_GAP_X;
  });
  return out;
}

// ── Default elements builder in 2970x2100 px format, por pack ───────
function buildElements(packId: PackId): Element[] {
  const base: Element[] = [
    { id: 'entrada', type: 'rect', x: 1235, y: 70, w: 500, h: 110, label: 'ENTRADA', color: '#6366f1', visible: true },
    { id: 'stand1', type: 'rect', x: 90, y: 230, w: 560, h: 400, label: withMedida('Stand Informativo', '3x3 m'), color: '#0369a1', visible: true },
    { id: 'mesa1', type: 'rect', x: 90, y: 660, w: 560, h: 220, label: 'Mesa 1', color: '#10b981', visible: true },
  ];

  const iconSpecs: { id: string; key: TechnicalSymbolKey }[] = [
    { id: 'power', key: 'power' }, { id: 'light', key: 'light' }, { id: 'water', key: 'water' },
    { id: 'extinguisher', key: 'extinguisher' }, { id: 'medical', key: 'medical' },
    { id: 'security', key: 'security' }, { id: 'trash', key: 'trash' }, { id: 'contact', key: 'contact' },
  ];

  if (packId === 'TESTEO' || packId === 'COMPLETO') {
    base.push(
      { id: 'stand2', type: 'rect', x: 730, y: 230, w: 560, h: 400, label: withMedida('Stand Testeo', '3x3 m'), color: '#2d5a4a', visible: true },
      { id: 'mesa2', type: 'rect', x: 730, y: 660, w: 560, h: 220, label: 'Mesa 2', color: '#10b981', visible: true },
    );
    iconSpecs.push({ id: 'testeo', key: 'testeo' });
  }

  if (packId === 'COMPLETO') {
    // Coordinacion va apilada bajo la Mesa 3 (misma columna), no como 4a columna:
    // una 4a columna a x=2010 invadiria la zona de la leyenda (default x=2060).
    base.push(
      { id: 'descanso', type: 'rect', x: 1370, y: 230, w: 560, h: 400, label: withMedida('Zona Descanso', '~9 m²'), color: '#059669', visible: true },
      { id: 'mesa3', type: 'rect', x: 1370, y: 660, w: 560, h: 220, label: 'Mesa 3', color: '#10b981', visible: true },
      { id: 'coordinacion', type: 'rect', x: 1205, y: 1620, w: 560, h: 300, label: 'Coordinación Operativa', color: '#ca8a04', visible: true },
    );
    iconSpecs.push(
      { id: 'testeo2', key: 'testeo' },
      { id: 'contencion', key: 'contencion' },
      { id: 'contencion2', key: 'contencion' },
      { id: 'food', key: 'food' },
      { id: 'sensory', key: 'sensory' },
    );
  }

  base.push(...layoutIconGroups(iconSpecs));

  return base;
}

// ── Main component ───────────────────────────────────────────────────
type Page = 'req' | 'map' | 'config';

const PLANO_CHECKED_ITEMS_KEY = 'plano_checked_items';

export default function PlanoTool() {
  const [preset, setPreset] = useState<PackId>('TESTEO');
  const [exportTheme, setExportTheme] = useState<ExportTheme>('dark');
  const [page, setPage] = useState<Page>('map');
  const [elements, setElements] = useState<Element[]>(() => buildElements('TESTEO'));
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [checkedItems, setCheckedItems] = useState<string[]>(() => {
    try {
      const raw = localStorage.getItem(PLANO_CHECKED_ITEMS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });
  const [legendPos, setLegendPos] = useState({ x: 1990, y: 120 });
  const [zoom, setZoom] = useState(1);
  const [showGrid, setShowGrid] = useState(true);
  const [showLegend, setShowLegend] = useState(true);
  const [eventName, setEventName] = useState('Evento Festival');
  const [eventDate, setEventDate] = useState('2026-06-28');
  const [eventVenue, setEventVenue] = useState('Parque Bicentenario');
  const [backendStatus, setBackendStatus] = useState('');

  const [orgTexts, setOrgTexts] = useState({
    who: 'Fundada en 2018, Reduciendo Daño es una ONG líder en implementación y formulación de políticas e insumos de reducción de daños en Chile, siendo pionera en la fabricación, distribución de implementos, reactivos y servicios de análisis de sustancias psicoactivas en el país. La Organización desarrolla proyectos de intervención en terreno orientados a fiestas, espacios de ocio y eventos donde existe consumo de sustancias psicoactivas. Nuestro objetivo es acercar herramientas de prevención, reducción de riesgos y educación preventiva, promoviendo decisiones informadas, el autocuidado y espacios más seguros.',
    goal: 'El proyecto busca informar, orientar y acompañar a personas que consuman o planeen consumir sustancias, mediante estrategias enfocadas en la seguridad, el cuidado informado y la prevención durante eventos y actividades recreativas.'
  });

  const svgRef = useRef<SVGSVGElement>(null);
  const selectedElement = elements.find(e => e.id === selectedId);

  useEffect(() => {
    try {
      localStorage.setItem(PLANO_CHECKED_ITEMS_KEY, JSON.stringify(checkedItems));
    } catch {
      // localStorage no disponible (modo privado, cuota, etc.) — no bloquear la UI
    }
  }, [checkedItems]);

  const applyPreset = (p: PackId) => {
    setPreset(p);
    setElements(buildElements(p));
    setSelectedId(null);
    setCheckedItems([]);
    try {
      localStorage.removeItem(PLANO_CHECKED_ITEMS_KEY);
    } catch {
      // localStorage no disponible — ignorar
    }
  };

  const selectElementAndBringToFront = (id: string) => {
    // Seleccionar NO debe cambiar capas. El orden se controla con botones explícitos.
    setSelectedId(id);
  };

  const toggleVisible = (id: string) => {
    setElements(els => {
      const next = els.map(el => el.id === id ? { ...el, visible: !el.visible } : el);
      syncChecklistFromElements(next);
      return next;
    });
  };

  const removeElement = (id: string) => {
    setElements(els => {
      const next = els.filter(el => el.id !== id);
      syncChecklistFromElements(next);
      return next;
    });
    if (selectedId === id) setSelectedId(null);
  };

  const addElement = (zoneType: string) => {
    const id = `zone-${Date.now()}`;
    const newEl: Element = {
      id,
      type: 'rect',
      x: 600 + Math.random() * 500,
      y: 600 + Math.random() * 400,
      w: 600,
      h: 300,
      label: ZONE_LABELS[zoneType] || zoneType,
      color: ZONE_COLORS[zoneType] || '#555',
      visible: true
    };
    setElements(prev => {
      const next = [...prev, newEl];
      syncChecklistFromElements(next);
      return next;
    });
    setSelectedId(id);
  };

  const addSymbol = (st: TechnicalSymbolKey) => {
    const spec = SYMBOL_BY_KEY[st] || SYMBOL_BY_KEY.power;
    const id = `symbol-${st}-${Date.now()}`;
    const newEl: Element = {
      ...makeSymbolElement(st, `symbol-${Date.now()}`),
      id,
      x: spec.x + Math.round(Math.random() * 240),
      y: spec.y + Math.round(Math.random() * 180),
    };
    setElements(prev => {
      const next = [...prev, newEl];
      syncChecklistFromElements(next);
      return next;
    });
    setSelectedId(id);
  };

  const duplicateSelected = () => {
    if (!selectedElement) return;
    const dup: Element = { ...selectedElement, id: `${selectedElement.id}-copy-${Date.now()}`, x: selectedElement.x + 100, y: selectedElement.y + 100 };
    setElements(prev => [...prev, dup]);
    setSelectedId(dup.id);
  };

  const moveLayer = (dir: 'up' | 'down') => {
    if (!selectedId) return;
    const i = elements.findIndex(e => e.id === selectedId);
    const target = dir === 'up' ? i + 1 : i - 1;
    if (target < 0 || target >= elements.length) return;
    const next = [...elements];
    [next[i], next[target]] = [next[target], next[i]];
    setElements(next);
  };

  const layerPriority = (el: Element) => {
    if (el.id === 'entrada') return 40;
    if (el.type === 'symbol') return 30;
    if (el.type === 'rect') return 10;
    return 20;
  };

  const orderLayersByPriority = () => {
    setElements(prev => [...prev].sort((a, b) => {
      const pa = layerPriority(a);
      const pb = layerPriority(b);
      if (pa !== pb) return pa - pb;
      if (a.y !== b.y) return a.y - b.y;
      if (a.x !== b.x) return a.x - b.x;
      return a.id.localeCompare(b.id);
    }));
  };

  const alignSelected = (mode: 'left' | 'centerX' | 'right' | 'top' | 'centerY' | 'bottom') => {
    if (!selectedId) return;
    const frame = PLANO_FRAME;
    setElements(prev => prev.map(el => {
      if (el.id !== selectedId) return el;
      if (mode === 'left') return { ...el, x: frame.x };
      if (mode === 'centerX') return { ...el, x: Math.round(frame.x + (frame.w - el.w) / 2) };
      if (mode === 'right') return { ...el, x: frame.x + frame.w - el.w };
      if (mode === 'top') return { ...el, y: frame.y };
      if (mode === 'centerY') return { ...el, y: Math.round(frame.y + (frame.h - el.h) / 2) };
      if (mode === 'bottom') return { ...el, y: frame.y + frame.h - el.h };
      return el;
    }));
  };

  const snap = (value: number) => Math.round(value / GRID) * GRID;

  const autoArrangePlano = () => {
    const frame = PLANO_FRAME;
    const rectArea = { x: frame.x + 120, y: frame.y + 220, w: 1800, h: frame.h - 360 };
    const symbolArea = { x: frame.x + 2020, y: frame.y + 220, w: 740, h: frame.h - 360 };
    const rectGap = 80;
    const symbolGapX = 230;
    const symbolGapY = 185;
    let rectX = rectArea.x;
    let rectY = rectArea.y;
    let rowH = 0;
    let symbolIndex = 0;

    setElements(prev => prev.map(el => {
      if (!el.visible) return el;
      if (el.id === 'entrada') {
        return { ...el, x: snap(frame.x + (frame.w - el.w) / 2), y: frame.y + 70 };
      }
      if (el.type === 'symbol') {
        const col = symbolIndex % 3;
        const row = Math.floor(symbolIndex / 3);
        symbolIndex += 1;
        return {
          ...el,
          x: snap(symbolArea.x + col * symbolGapX),
          y: snap(Math.min(symbolArea.y + row * symbolGapY, frame.y + frame.h - el.h - 40)),
        };
      }
      if (rectX + el.w > rectArea.x + rectArea.w) {
        rectX = rectArea.x;
        rectY += rowH + rectGap;
        rowH = 0;
      }
      const next = { ...el, x: snap(rectX), y: snap(Math.min(rectY, rectArea.y + rectArea.h - el.h)) };
      rectX += el.w + rectGap;
      rowH = Math.max(rowH, el.h);
      return next;
    }).sort((a, b) => {
      const pa = layerPriority(a);
      const pb = layerPriority(b);
      if (pa !== pb) return pa - pb;
      if (a.y !== b.y) return a.y - b.y;
      if (a.x !== b.x) return a.x - b.x;
      return a.id.localeCompare(b.id);
    }));
    setLegendPos({ x: 1990, y: 120 });
  };

  const resetLegendPosition = () => setLegendPos({ x: 1990, y: 120 });

  const onMouseDown = useCallback((e: React.MouseEvent, id: string) => {
    e.preventDefault();
    const svg = svgRef.current;
    if (!svg) return;
    selectElementAndBringToFront(id);

    const pt = svg.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    const start = pt.matrixTransform(svg.getScreenCTM()!.inverse());
    const el = elements.find(x => x.id === id)!;
    const startX = el.x; const startY = el.y;

    const move = (me: MouseEvent) => {
      const mpt = svg.createSVGPoint();
      mpt.x = me.clientX; mpt.y = me.clientY;
      const mp = mpt.matrixTransform(svg.getScreenCTM()!.inverse());
      setElements(prev => prev.map(x =>
        x.id === id ? { ...x, x: Math.round((startX + (mp.x - start.x)) / 20) * 20, y: Math.round((startY + (mp.y - start.y)) / 20) * 20 } : x
      ));
    };
    const up = () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
  }, [elements]);

  const onTouchStart = useCallback((e: React.TouchEvent, id: string) => {
    e.stopPropagation();
    const touch = e.touches[0];
    const svg = svgRef.current;
    if (!svg) return;
    selectElementAndBringToFront(id);

    const pt = svg.createSVGPoint();
    pt.x = touch.clientX; pt.y = touch.clientY;
    const start = pt.matrixTransform(svg.getScreenCTM()!.inverse());
    const el = elements.find(x => x.id === id)!;
    const startX = el.x; const startY = el.y;

    const move = (te: TouchEvent) => {
      if (te.touches.length === 0) return;
      const t = te.touches[0];
      const mpt = svg.createSVGPoint();
      mpt.x = t.clientX; mpt.y = t.clientY;
      const mp = mpt.matrixTransform(svg.getScreenCTM()!.inverse());
      setElements(prev => prev.map(x =>
        x.id === id ? { ...x, x: Math.round((startX + (mp.x - start.x)) / 20) * 20, y: Math.round((startY + (mp.y - start.y)) / 20) * 20 } : x
      ));
    };
    const end = () => {
      window.removeEventListener('touchmove', move);
      window.removeEventListener('touchend', end);
    };
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend', end);
  }, [elements]);

  // ─── Render Symbol (Procedural SVG without Emojis) ───
  const renderSymbolGlyph = (key: string, fill: string) => {
    switch (key) {
      case 'scan':
        return <><rect x="28" y="36" width="104" height="84" rx="8" fill="none" stroke={fill} strokeWidth="9" strokeDasharray="12 8"/><path d="M42 58 H118 M42 82 H92 M42 106 H108" stroke={fill} strokeWidth="7" strokeLinecap="round"/></>;
      case 'terrain':
        return <><path d="M22 112 C48 76 70 86 92 54 C110 30 126 42 140 70" fill="none" stroke={fill} strokeWidth="10" strokeLinecap="round"/><path d="M24 122 H138" stroke={fill} strokeWidth="8" strokeLinecap="round"/></>;
      case 'circulation':
        return <><path d="M34 80 H124" stroke={fill} strokeWidth="10" strokeLinecap="round"/><path d="M104 58 L128 80 L104 102" fill="none" stroke={fill} strokeWidth="10" strokeLinecap="round" strokeLinejoin="round"/><circle cx="48" cy="48" r="14" fill={fill}/><circle cx="78" cy="122" r="14" fill={fill}/></>;
      case 'sensory':
        return <><path d="M104 30 C68 38 50 66 58 96 C66 126 96 140 128 124 C82 120 66 76 104 30 Z" fill={fill}/><circle cx="42" cy="46" r="5" fill={fill}/><circle cx="132" cy="62" r="5" fill={fill}/></>;
      case 'tent':
        return <><path d="M22 122 L80 34 L138 122 Z" fill="none" stroke={fill} strokeWidth="10" strokeLinejoin="round"/><path d="M80 34 V122 M48 122 L80 78 L112 122" stroke={fill} strokeWidth="8" fill="none" strokeLinecap="round"/></>;
      case 'table':
        return <><rect x="28" y="54" width="104" height="42" rx="6" fill="none" stroke={fill} strokeWidth="10"/><path d="M46 96 V130 M114 96 V130" stroke={fill} strokeWidth="9" strokeLinecap="round"/></>;
      case 'chairs':
        return <><path d="M44 48 V112 H88 M88 112 V134" fill="none" stroke={fill} strokeWidth="10" strokeLinecap="round"/><path d="M94 48 V112 H128 M128 112 V134" fill="none" stroke={fill} strokeWidth="10" strokeLinecap="round"/></>;
      case 'rack':
        return <><rect x="24" y="24" width="112" height="112" rx="8" fill="none" stroke={fill} strokeWidth="9"/><path d="M24 62 H136 M24 98 H136 M62 24 V136 M98 24 V136" stroke={fill} strokeWidth="6" opacity="0.45"/></>;
      case 'trash':
        return <><path d="M50 52 H110 L102 134 H58 Z" fill="none" stroke={fill} strokeWidth="9" strokeLinejoin="round"/><path d="M42 52 H118 M64 38 H96 M70 72 V116 M90 72 V116" stroke={fill} strokeWidth="8" strokeLinecap="round"/></>;
      case 'power':
        return <><circle cx="80" cy="80" r="55" fill="none" stroke={fill} strokeWidth="9"/><path d="M88 28 L52 88 H82 L72 132 L112 70 H82 Z" fill={fill}/></>;
      case 'light':
        return <><circle cx="80" cy="66" r="34" fill="none" stroke={fill} strokeWidth="9"/><path d="M62 100 H98 M66 120 H94 M72 136 H88" stroke={fill} strokeWidth="8" strokeLinecap="round"/><path d="M80 14 V28 M34 34 L44 44 M126 34 L116 44" stroke={fill} strokeWidth="7" strokeLinecap="round"/></>;
      case 'water':
        return <><path d="M80 24 C116 70 126 92 110 118 C94 144 58 144 48 116 C38 88 58 66 80 24 Z" fill="none" stroke={fill} strokeWidth="10"/><path d="M62 106 C68 122 88 128 102 112" stroke={fill} strokeWidth="7" strokeLinecap="round"/></>;
      case 'heating':
        return <><rect x="42" y="30" width="76" height="104" rx="12" fill="none" stroke={fill} strokeWidth="9"/><path d="M62 54 V110 M80 54 V110 M98 54 V110" stroke={fill} strokeWidth="8" strokeLinecap="round"/></>;
      case 'contact':
        return <><circle cx="80" cy="52" r="24" fill="none" stroke={fill} strokeWidth="9"/><path d="M38 132 C44 98 116 98 122 132" fill="none" stroke={fill} strokeWidth="10" strokeLinecap="round"/></>;
      case 'security':
        return <><path d="M80 22 L124 40 V76 C124 104 106 126 80 140 C54 126 36 104 36 76 V40 Z" fill="none" stroke={fill} strokeWidth="9" strokeLinejoin="round"/><path d="M62 80 L76 94 L102 62" fill="none" stroke={fill} strokeWidth="9" strokeLinecap="round" strokeLinejoin="round"/></>;
      case 'medical':
        return <><path d="M80 136 C34 96 28 66 48 46 C62 32 78 42 80 54 C82 42 100 32 114 46 C134 66 126 98 80 136 Z" fill="none" stroke={fill} strokeWidth="9"/><path d="M80 58 V106 M56 82 H104" stroke={fill} strokeWidth="9" strokeLinecap="round"/></>;
      case 'food':
        return <><path d="M54 28 V76 M70 28 V76 M62 76 V134" stroke={fill} strokeWidth="9" strokeLinecap="round"/><path d="M104 28 C124 48 122 82 104 94 V134" fill="none" stroke={fill} strokeWidth="9" strokeLinecap="round"/></>;
      case 'extinguisher':
        return <><rect x="60" y="50" width="42" height="88" rx="9" fill="none" stroke={fill} strokeWidth="9"/><path d="M70 50 V34 H94 V50 M94 62 H120 M120 62 L134 52" stroke={fill} fill="none" strokeWidth="8" strokeLinecap="round"/><path d="M70 82 H92" stroke={fill} strokeWidth="7" strokeLinecap="round"/></>;
      case 'testeo':
        return <><circle cx="80" cy="80" r="58" fill={fill} fillOpacity="0.16" stroke={fill} strokeWidth="9"/><path d="M60 42 H100 M80 42 V82 L112 126 H48 L80 82" fill="none" stroke={fill} strokeWidth="9" strokeLinejoin="round"/></>;
      case 'contencion':
        return <><circle cx="80" cy="80" r="58" fill={fill} fillOpacity="0.16" stroke={fill} strokeWidth="9"/><path d="M80 120 C44 88 44 62 62 52 C74 46 80 56 80 64 C80 56 90 46 102 52 C120 62 116 90 80 120 Z" fill={fill}/></>;
      default:
        return <><circle cx="80" cy="80" r="54" fill="none" stroke={fill} strokeWidth="9"/><text x="80" y="92" textAnchor="middle" fontSize="42" fill={fill} fontWeight="black">?</text></>;
    }
  };

  const renderSymbol = (el: Element, isPrint = false) => {
    const isSelected = !isPrint && el.id === selectedId;
    const fill = isPrint ? '#000000' : el.color;

    return (
      <g
        key={el.id}
        transform={`translate(${el.x},${el.y})`}
        onMouseDown={isPrint ? undefined : (e) => { e.stopPropagation(); onMouseDown(e, el.id); }}
        onTouchStart={isPrint ? undefined : (e) => { e.stopPropagation(); onTouchStart(e, el.id); }}
        onClick={isPrint ? undefined : (e) => { e.stopPropagation(); selectElementAndBringToFront(el.id); }}
        className={isPrint ? undefined : "cursor-move"}
        opacity={el.visible ? 1 : 0.2}
      >
        <rect width={el.w} height={el.h} fill="transparent" stroke={isSelected ? '#fff' : 'none'} strokeWidth={5} />
        <svg x={0} y={0} width={el.w} height={el.h} viewBox="0 0 160 160" overflow="visible">
          {renderSymbolGlyph(el.symbolKey || 'unknown', fill)}
        </svg>
        <text x={el.w / 2} y={el.h + 30} textAnchor="middle" fontSize="30" fill={fill} fontWeight="bold" fontFamily="monospace">
          {el.label.toUpperCase()}
        </text>
        {isSelected && (
          <rect x={-10} y={-10} width={el.w + 20} height={el.h + 20} rx={12} fill="none" stroke="#10b981" strokeWidth={10} strokeDasharray="20 10" />
        )}
      </g>
    );
  };

  const clampLegendPos = (x: number, y: number) => {
    const frame = PLANO_FRAME;
    const legendWidth = 900;
    const legendHeight = Math.min(900, Math.max(220, 160 + Math.ceil(visibleLegendSymbols.length / 2) * 84));
    return {
      x: Math.min(Math.max(x, frame.x), frame.x + frame.w - legendWidth),
      y: Math.min(Math.max(y, frame.y), frame.y + frame.h - legendHeight),
    };
  };

  const onLegendMouseDown = (e: React.MouseEvent) => {
    const svg = svgRef.current;
    if (!svg) return;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    const start = pt.matrixTransform(svg.getScreenCTM()!.inverse());
    const lx = legendPos.x; const ly = legendPos.y;

    const move = (me: MouseEvent) => {
      const mpt = svg.createSVGPoint();
      mpt.x = me.clientX; mpt.y = me.clientY;
      const mp = mpt.matrixTransform(svg.getScreenCTM()!.inverse());
      setLegendPos(clampLegendPos(lx + (mp.x - start.x), ly + (mp.y - start.y)));
    };
    const up = () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    e.stopPropagation();
  };

  const onLegendTouchStart = (e: React.TouchEvent) => {
    const svg = svgRef.current;
    if (!svg) return;
    const touch = e.touches[0];
    const pt = svg.createSVGPoint();
    pt.x = touch.clientX; pt.y = touch.clientY;
    const start = pt.matrixTransform(svg.getScreenCTM()!.inverse());
    const lx = legendPos.x; const ly = legendPos.y;

    const move = (te: TouchEvent) => {
      if (te.touches.length === 0) return;
      const t = te.touches[0];
      const mpt = svg.createSVGPoint();
      mpt.x = t.clientX; mpt.y = t.clientY;
      const mp = mpt.matrixTransform(svg.getScreenCTM()!.inverse());
      setLegendPos(clampLegendPos(lx + (mp.x - start.x), ly + (mp.y - start.y)));
    };
    const end = () => {
      window.removeEventListener('touchmove', move);
      window.removeEventListener('touchend', end);
    };
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend', end);
    e.stopPropagation();
  };

  const escapeHtml = (value: string) => value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  const symbolIconMarkup = (key: string, color: string, cx: number, cy: number, scale: number) => {
    const sw = Math.max(5, 7 * scale);
    const c = color;
    const x = (n: number) => cx + (n - 80) * scale;
    const y = (n: number) => cy + (n - 80) * scale;
    switch (key) {
      case 'power':
        return `<path d="M ${x(88)} ${y(28)} L ${x(52)} ${y(88)} H ${x(82)} L ${x(72)} ${y(132)} L ${x(112)} ${y(70)} H ${x(82)} Z" fill="${c}"/>`;
      case 'water':
        return `<path d="M ${x(80)} ${y(24)} C ${x(116)} ${y(70)} ${x(126)} ${y(92)} ${x(110)} ${y(118)} C ${x(94)} ${y(144)} ${x(58)} ${y(144)} ${x(48)} ${y(116)} C ${x(38)} ${y(88)} ${x(58)} ${y(66)} ${x(80)} ${y(24)} Z" fill="none" stroke="${c}" stroke-width="${sw}"/>`;
      case 'table':
        return `<rect x="${x(28)}" y="${y(54)}" width="${104*scale}" height="${42*scale}" rx="${6*scale}" fill="none" stroke="${c}" stroke-width="${sw}"/><path d="M ${x(46)} ${y(96)} V ${y(130)} M ${x(114)} ${y(96)} V ${y(130)}" stroke="${c}" stroke-width="${sw}" stroke-linecap="round"/>`;
      case 'chairs':
        return `<path d="M ${x(44)} ${y(48)} V ${y(112)} H ${x(88)} M ${x(88)} ${y(112)} V ${y(134)} M ${x(94)} ${y(48)} V ${y(112)} H ${x(128)} M ${x(128)} ${y(112)} V ${y(134)}" fill="none" stroke="${c}" stroke-width="${sw}" stroke-linecap="round"/>`;
      case 'tent':
        return `<path d="M ${x(22)} ${y(122)} L ${x(80)} ${y(34)} L ${x(138)} ${y(122)} Z M ${x(80)} ${y(34)} V ${y(122)}" fill="none" stroke="${c}" stroke-width="${sw}" stroke-linejoin="round"/>`;
      case 'security':
        return `<path d="M ${x(80)} ${y(22)} L ${x(124)} ${y(40)} V ${y(76)} C ${x(124)} ${y(104)} ${x(106)} ${y(126)} ${x(80)} ${y(140)} C ${x(54)} ${y(126)} ${x(36)} ${y(104)} ${x(36)} ${y(76)} V ${y(40)} Z" fill="none" stroke="${c}" stroke-width="${sw}"/><path d="M ${x(62)} ${y(80)} L ${x(76)} ${y(94)} L ${x(102)} ${y(62)}" fill="none" stroke="${c}" stroke-width="${sw}" stroke-linecap="round"/>`;
      case 'medical':
        return `<path d="M ${x(80)} ${y(58)} V ${y(106)} M ${x(56)} ${y(82)} H ${x(104)}" stroke="${c}" stroke-width="${sw}" stroke-linecap="round"/><path d="M ${x(80)} ${y(136)} C ${x(34)} ${y(96)} ${x(28)} ${y(66)} ${x(48)} ${y(46)} C ${x(62)} ${y(32)} ${x(78)} ${y(42)} ${x(80)} ${y(54)} C ${x(82)} ${y(42)} ${x(100)} ${y(32)} ${x(114)} ${y(46)} C ${x(134)} ${y(66)} ${x(126)} ${y(98)} ${x(80)} ${y(136)} Z" fill="none" stroke="${c}" stroke-width="${sw}"/>`;
      case 'extinguisher':
        return `<rect x="${x(60)}" y="${y(50)}" width="${42*scale}" height="${88*scale}" rx="${9*scale}" fill="none" stroke="${c}" stroke-width="${sw}"/><path d="M ${x(70)} ${y(50)} V ${y(34)} H ${x(94)} V ${y(50)} M ${x(94)} ${y(62)} H ${x(120)} L ${x(134)} ${y(52)}" stroke="${c}" fill="none" stroke-width="${sw}" stroke-linecap="round"/>`;
      case 'testeo':
        return `<circle cx="${cx}" cy="${cy}" r="${58*scale}" fill="${c}" fill-opacity="0.12" stroke="${c}" stroke-width="${sw}"/><path d="M ${x(60)} ${y(42)} H ${x(100)} M ${x(80)} ${y(42)} V ${y(82)} L ${x(112)} ${y(126)} H ${x(48)} L ${x(80)} ${y(82)}" fill="none" stroke="${c}" stroke-width="${sw}"/>`;
      case 'contencion':
        return `<circle cx="${cx}" cy="${cy}" r="${58*scale}" fill="${c}" fill-opacity="0.12" stroke="${c}" stroke-width="${sw}"/><path d="M ${x(80)} ${y(120)} C ${x(44)} ${y(88)} ${x(44)} ${y(62)} ${x(62)} ${y(52)} C ${x(74)} ${y(46)} ${x(80)} ${y(56)} ${x(80)} ${y(64)} C ${x(80)} ${y(56)} ${x(90)} ${y(46)} ${x(102)} ${y(52)} C ${x(120)} ${y(62)} ${x(116)} ${y(90)} ${x(80)} ${y(120)} Z" fill="${c}"/>`;
      default:
        return `<circle cx="${cx}" cy="${cy}" r="${48*scale}" fill="none" stroke="${c}" stroke-width="${sw}"/><text x="${cx}" y="${cy + 11*scale}" text-anchor="middle" font-size="${36*scale}" font-family="Arial" font-weight="900" fill="${c}">${escapeHtml(key.slice(0, 2).toUpperCase())}</text>`;
    }
  };

  const symbolPrintMarkup = (el: Element) => {
    const label = escapeHtml(el.label.toUpperCase());
    const color = escapeHtml(el.color || '#111111');
    const cx = el.x + el.w / 2;
    const cy = el.y + el.h / 2;
    const scale = Math.max(0.7, Math.min(el.w, el.h) / 170);
    return `
      <g>
        ${symbolIconMarkup(el.symbolKey || 'symbol', color, cx, cy, scale)}
        <text x="${cx}" y="${el.y + el.h + 34}" text-anchor="middle" font-size="28" font-family="Arial, sans-serif" font-weight="700" fill="${color}">${label}</text>
      </g>`;
  };

  const buildPrintableMapSvg = () => {
    const pal = RD_PALETTE[exportTheme];
    const visible = elements.filter(el => el.visible);
    const mapContent = visible.map(el => {
      const label = escapeHtml(el.label.toUpperCase());
      if (el.type === 'symbol') return symbolPrintMarkup(el);
      return `
        <g>
          <rect x="${el.x}" y="${el.y}" width="${el.w}" height="${el.h}" rx="16" fill="${escapeHtml(el.color)}" fill-opacity="0.48" stroke="${escapeHtml(el.color)}" stroke-width="8"/>
          <text x="${el.x + el.w / 2}" y="${el.y + el.h / 2}" text-anchor="middle" dominant-baseline="middle" font-size="42" font-family="Arial, sans-serif" font-weight="900" fill="${pal.text}">${label}</text>
        </g>`;
    }).join('\n');

    const printCanvasWidth = 2970;
    const printCanvasHeight = 2100;
    const legendWidth = 900;
    const legendHeight = Math.min(900, Math.max(220, 160 + Math.ceil(visibleLegendSymbols.length / 2) * 84));
    const legendX = Math.min(Math.max(legendPos.x, 0), Math.max(0, printCanvasWidth - legendWidth));
    const legendY = Math.min(Math.max(legendPos.y, 0), Math.max(0, printCanvasHeight - legendHeight));
    const legendRows = visibleLegendSymbols.map((el, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = legendX + 48 + col * 410;
      const y = legendY + 160 + row * 84;
      const color = escapeHtml(el.color || '#111111');
      return `
        <g>
          ${symbolIconMarkup(el.symbolKey || 'symbol', color, x + 22, y - 16, 0.36)}
          <text x="${x + 64}" y="${y}" font-size="26" font-family="Arial, sans-serif" font-weight="800" fill="${pal.text}">${escapeHtml(el.label.toUpperCase()).slice(0, 18)}</text>
        </g>`;
    }).join('\n');

    return `
      <svg viewBox="0 0 ${printCanvasWidth} ${printCanvasHeight}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
        <rect width="${printCanvasWidth}" height="${printCanvasHeight}" fill="${pal.mapBg}"/>
        <rect x="${PLANO_FRAME.x}" y="${PLANO_FRAME.y}" width="${PLANO_FRAME.w}" height="${PLANO_FRAME.h}" fill="none" stroke="${pal.muted}" stroke-width="5" stroke-dasharray="30 20" rx="20"/>
        ${mapContent}
        ${iconCategoryHeaders.map(h => `<text x="${h.x}" y="${h.y - 22}" font-size="30" font-family="Arial, sans-serif" font-weight="900" fill="${pal.accent}" style="letter-spacing:0.06em">${escapeHtml(h.category.toUpperCase())}</text>`).join('\n')}
        <g transform="translate(0,0)">
          <rect x="${legendX}" y="${legendY}" width="${legendWidth}" height="${legendHeight}" rx="30" fill="${pal.panel}" fill-opacity="0.96" stroke="${pal.borde}" stroke-width="5"/>
          <text x="${legendX + 450}" y="${legendY + 80}" text-anchor="middle" font-size="40" font-family="Arial, sans-serif" font-weight="900" fill="${pal.accent}">LEYENDA TÉCNICA</text>
          ${legendRows}
        </g>
        <text x="100" y="2060" font-size="34" font-family="Arial, sans-serif" font-weight="900" fill="${pal.text}">${escapeHtml(`${eventName.toUpperCase()} · ${eventVenue.toUpperCase()} · ${eventDate}`)}</text>
      </svg>`;
  };

  const printRider = () => {
    const pal = RD_PALETTE[exportTheme];
    const checklistHtml = CHECKLIST_SECTIONS.map(section => `
      <section class="box">
        <h3>${escapeHtml(section.title)}</h3>
        <ul>
          ${section.items.map(item => `<li><span class="check">${checkedItems.includes(item.text) ? 'X' : ''}</span>${escapeHtml(item.text)}</li>`).join('')}
        </ul>
      </section>`).join('');

    // Cotizacion del pack seleccionado unicamente (precio plano, sin fan-out de presets).
    const pack = calcCostos(preset);
    const inclusionesHtml = `<ul>${pack.inclusiones.map(i => `<li>${escapeHtml(i)}</li>`).join('')}</ul>`;
    const proporcionesHtml = pack.proporciones ? `
      <table class="cot">
        <thead><tr><th>Distribución del pack</th><th class="num">%</th><th class="num">Monto</th></tr></thead>
        <tbody>
          ${pack.proporciones.map(p => `<tr><td>${escapeHtml(p.label)}</td><td class="num">${p.pct}%</td><td class="num">${formatCLP(p.monto)}</td></tr>`).join('')}
        </tbody>
      </table>` : '';
    const cotizacionHtml = `
      <table class="cot">
        <tbody>
          <tr class="tot"><td>Precio del pack</td><td class="num">${formatCLP(pack.precio)} / día</td></tr>
          <tr><td>Voluntarios</td><td class="num">${pack.voluntarios}</td></tr>
          <tr><td>$ por voluntario</td><td class="num">${formatCLP(pack.porVoluntario)}</td></tr>
          <tr><td>Superficie / stands</td><td class="num">${pack.m2} m² · ${pack.stands} stand(s)</td></tr>
        </tbody>
      </table>
      <h3 style="margin-top:8px">Inclusiones</h3>
      ${inclusionesHtml}
      ${proporcionesHtml}
      <p class="note">Valores referenciales en CLP; ajustables por evento. Pack: <strong>${escapeHtml(pack.label)}</strong>.</p>`;

    const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>Rider Plano PDF</title>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { margin: 0; background: ${pal.bg}; color: ${pal.text}; font-family: Arial, Helvetica, sans-serif; font-size: 13px; }
  .page { width: 210mm; min-height: 297mm; padding: 18mm; page-break-after: always; break-after: page; overflow: hidden; background: ${pal.bg}; display: flex; flex-direction: column; gap: 14px; }
  .page-body { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; justify-content: center; gap: 14px; }
  .page:last-child { page-break-after: auto; break-after: auto; }
  header { border-bottom: 4px solid ${pal.accent}; padding-bottom: 12px; display: flex; justify-content: space-between; align-items: end; }
  .brand { display: flex; align-items: center; gap: 12px; }
  .logo svg { height: 84px; width: auto; display: block; }
  .page-header-mini { border-bottom: 4px solid ${pal.accent}; padding-bottom: 12px; display: flex; align-items: center; gap: 12px; }
  h1 { font-size: 34px; margin: 0; font-weight: 900; font-style: italic; letter-spacing: -1px; white-space: nowrap; }
  h2 { font-size: 24px; margin: 0 0 10px; font-weight: 900; text-transform: uppercase; color: ${pal.accent}; }
  h3 { font-size: 13px; margin: 0 0 6px; font-weight: 900; text-transform: uppercase; border-bottom: 1px solid ${pal.borde}; padding-bottom: 4px; }
  p { margin: 0 0 12px; line-height: 1.65; }
  .muted { color: ${pal.muted}; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .box { border: 1px solid ${pal.borde}; padding: 16px; border-radius: 8px; break-inside: avoid; }
  ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 9px; }
  li { display: flex; gap: 9px; align-items: center; }
  .check { width: 17px; height: 17px; border: 1px solid ${pal.accent}; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900; flex: 0 0 auto; color: ${pal.accent}; }
  .map-frame { border: 1px solid ${pal.borde}; padding: 6mm; display: flex; justify-content: center; background: ${pal.mapBg}; }
  .map-frame svg { width: 100%; height: auto; display: block; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { border: 1px solid ${pal.borde}; padding: 12px; text-align: left; }
  th { background: ${pal.th}; font-weight: 900; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
  .cot td.cur, .cot th.cur { background: ${pal.th}; color: ${pal.accent}; font-weight: 900; }
  .cot tr.tot td { font-weight: 900; color: ${pal.total}; font-size: 13px; }
  .note { font-size: 11px; color: ${pal.muted}; margin-top: 6px; }
</style>
</head>
<body>
  <main class="page">
    <header>
      <div class="brand"><span class="logo">${RD_LOGO[exportTheme]}</span><div><h1>RIDER TÉCNICO RD</h1><p class="muted">Documentación de Intervención en Terreno — ONG Reduciendo Daño</p></div></div>
      <div><strong>ORGANIZACIÓN RD</strong><br/><span class="muted">Servicio de Testeo y Reducción de Daño v2026</span></div>
    </header>
    <div class="page-body">
      <section>
        <h2>1. Antecedentes</h2>
        <p><strong>Quiénes Somos:</strong> ${escapeHtml(orgTexts.who)}</p>
        <p><strong>Objetivo del Servicio:</strong> ${escapeHtml(orgTexts.goal)}</p>
        <p><strong>Evento:</strong> ${escapeHtml(eventName)} · <strong>Ubicación:</strong> ${escapeHtml(eventVenue)} · <strong>Fecha:</strong> ${escapeHtml(eventDate)}</p>
      </section>
      <section>
        <h2>2. Requerimientos Operativos</h2>
        <div class="grid">${checklistHtml}</div>
      </section>
    </div>
  </main>
  <main class="page">
    <div class="page-header-mini"><span class="logo">${RD_LOGO[exportTheme]}</span><h1 style="font-size:22px">RIDER TÉCNICO RD</h1></div>
    <div class="page-body">
      <h2>3. Esquema de Distribución del Stand</h2>
      <div class="map-frame">${buildPrintableMapSvg()}</div>
    </div>
  </main>
  <main class="page">
    <div class="page-header-mini"><span class="logo">${RD_LOGO[exportTheme]}</span><h1 style="font-size:22px">RIDER TÉCNICO RD</h1></div>
    <div class="page-body">
      <h2>4. Cotización — ${escapeHtml(calcCostos(preset).label)}</h2>
      ${cotizacionHtml}
    </div>
  </main>
</body>
</html>`;

    const iframe = document.createElement('iframe');
    iframe.style.position = 'fixed';
    iframe.style.right = '0';
    iframe.style.bottom = '0';
    iframe.style.width = '0';
    iframe.style.height = '0';
    iframe.style.border = '0';
    iframe.setAttribute('title', 'Rider PDF print frame');
    document.body.appendChild(iframe);
    const doc = iframe.contentWindow?.document;
    if (!doc) return;
    doc.open();
    doc.write(html);
    doc.close();
    setTimeout(() => {
      iframe.contentWindow?.focus();
      iframe.contentWindow?.print();
      setTimeout(() => iframe.remove(), 3000);
    }, 350);
  };

  const syncElementsFromChecked = (items: string[], baseElements = elements) => {
    const wanted = items.map(item => REQUIREMENT_SYMBOL_MAP[item]).filter(Boolean);
    const requirementKeys = new Set(Object.values(REQUIREMENT_SYMBOL_MAP));
    let next = baseElements
      .filter(el => {
        if (!(el.id || '').startsWith('req-')) return true;
        return Boolean(el.symbolKey && wanted.includes(el.symbolKey));
      })
      .map(el => {
        if (!el.symbolKey || !requirementKeys.has(el.symbolKey)) return el;
        if (wanted.includes(el.symbolKey)) return { ...el, visible: true };
        return { ...el, visible: false };
      });
    wanted.forEach(key => {
      const hasVisibleSymbol = next.some(el => el.symbolKey === key && el.visible);
      if (!hasVisibleSymbol) next.push({ ...makeSymbolElement(key, 'req'), id: `req-${key}` });
    });
    return next;
  };

  const syncChecklistFromElements = (nextElements: Element[]) => {
    const visibleRequirementKeys = new Set(
      nextElements
        .filter(el => el.visible && el.symbolKey && (el.type === 'symbol' || (el.id || '').startsWith('req-')))
        .map(el => el.symbolKey as string)
    );
    const mapEntries = Object.entries(REQUIREMENT_SYMBOL_MAP);
    setCheckedItems(prev => {
      const manual = prev.filter(item => !REQUIREMENT_SYMBOL_MAP[item]);
      const fromMap = mapEntries
        .filter(([, key]) => visibleRequirementKeys.has(key))
        .map(([item]) => item);
      return Array.from(new Set([...manual, ...fromMap]));
    });
  };

  const toggleCheck = (item: string) => {
    const nextChecked = checkedItems.includes(item)
      ? checkedItems.filter(x => x !== item)
      : [...checkedItems, item];
    setCheckedItems(nextChecked);
    setElements(prev => syncElementsFromChecked(nextChecked, prev));
  };

  const handleGoToPlano = () => {
    setElements(prev => syncElementsFromChecked(checkedItems, prev));
    setPage('map');
  };

  const checkAll = () => {
    const all = CHECKLIST_SECTIONS.flatMap(s => s.items).map(i => i.text);
    const nextChecked = checkedItems.length === all.length ? [] : all;
    setCheckedItems(nextChecked);
    setElements(prev => syncElementsFromChecked(nextChecked, prev));
  };

  // ─── Export Checklist as Markdown ───
  const exportChecklistMarkdown = () => {
    let md = `# RIDER TÉCNICO RD - CHECKLIST\n\n`;
    md += `**Evento:** ${eventName}\n`;
    md += `**Fecha:** ${eventDate}\n`;
    md += `**Lugar:** ${eventVenue}\n`;
    md += `**Pack Comercial:** ${PACKS[preset].label} (${formatCLP(PACKS[preset].precio)})\n\n`;
    md += `## 1. Antecedentes de la Organización\n\n`;
    md += `**Quiénes somos:** ${orgTexts.who}\n\n`;
    md += `**Objetivo del servicio:** ${orgTexts.goal}\n\n`;
    md += `## 2. Requerimientos Operativos\n\n`;
    CHECKLIST_SECTIONS.forEach(sec => {
      md += `### ${sec.title}\n`;
      sec.items.forEach(item => {
        const isChecked = checkedItems.includes(item.text) ? '[x]' : '[ ]';
        md += `- ${isChecked} ${item.text}\n`;
      });
      md += `\n`;
    });
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `checklist_rider_${eventName.replace(/\s+/g, '_').toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ─── Export SVG ───
  const exportSVG = () => {
    if (!svgRef.current) return;
    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `plano_${eventName.replace(/\s+/g, '_').toLowerCase()}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Deuda: el motor Python (src/flujo/plano/*) solo conoce under/base/mainstream.
  // Se mapea aqui el pack elegido solo para la llamada demo; no cambia el modelo de PACKS.
  const PACK_TO_BACKEND_PRESET: Record<PackId, string> = { INFO: 'under', TESTEO: 'base', COMPLETO: 'mainstream' };

  const loadFromBackend = async (presetId: PackId = preset) => {
    if (window.location.protocol === 'file:') {
      applyPreset(presetId);
      setBackendStatus(`Modo demo con pack ${presetId}. Abre via py -m flujo app para usar APIs.`);
      return;
    }
    setBackendStatus('Consultando motor Python...');
    try {
      const response = await fetch('/api/plano/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evento: {
            nombre: eventName || 'Evento',
            fecha: eventDate,
            preset: PACK_TO_BACKEND_PRESET[presetId],
            ubicacion: eventVenue || 'Por definir'
          },
        }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const zones = Array.isArray(data?.layout?.zones) ? data.layout.zones : [];
      const mapped: Element[] = zones.map((zone: any, index: number) => {
        const zoneType = zone.type === 'stand' ? 'informativo' : zone.type === 'descanso' ? 'descanso' : zone.type === 'testeo' ? 'testeo' : zone.type === 'mesa' ? 'informativo' : 'circulacion';
        return {
          id: `api-${index}-${zoneType}`,
          type: 'rect',
          x: Number(zone.x) * 4 || 300,
          y: Number(zone.y) * 4 || 300,
          w: Number(zone.w) * 4 || 560,
          h: Number(zone.h) * 4 || 300,
          label: String(zone.label || ZONE_LABELS[zoneType] || zoneType),
          color: ZONE_COLORS[zoneType] || '#555',
          visible: true,
        };
      });
      if (mapped.length) {
        setElements(mapped);
        setSelectedId(mapped[0].id);
      }
      setBackendStatus(`Motor Python OK con pack ${presetId}: ${mapped.length} elementos cargados.`);
    } catch (error) {
      setBackendStatus(`No se pudo usar /api/plano/render: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const totalChecks = CHECKLIST_SECTIONS.flatMap(s => s.items).length;
  const completedChecks = checkedItems.length;
  const visibleLegendSymbols = elements
    .filter(el => el.visible && el.type === 'symbol' && el.symbolKey)
    .reduce<Element[]>((acc, el) => {
      if (!acc.some(item => item.symbolKey === el.symbolKey)) acc.push(el);
      return acc;
    }, []);

  const iconCategoryHeaders = (() => {
    const groups: Record<string, Element[]> = {};
    elements.filter(el => el.visible && el.type === 'symbol' && el.category).forEach(el => {
      (groups[el.category as string] = groups[el.category as string] || []).push(el);
    });
    return Object.entries(groups).map(([category, els]) => ({
      category,
      x: Math.min(...els.map(e => e.x)),
      y: Math.min(...els.map(e => e.y)),
    }));
  })();

  const NAV_TABS: { key: Page; label: string }[] = [
    { key: 'req', label: '☑ Checklist' },
    { key: 'map', label: '🗺 Mapa' },
    { key: 'config', label: '⚙ Config' },
  ];

  return (
    <div className="space-y-6">
      {/* Screen View (Interactive App Tool) */}
      <div className="flex items-center justify-between print:hidden">
        <div>
          <h3 className="text-2xl font-bold flex items-center gap-2">
            Rider RD · Herramienta de Plano
            <span className="text-xs bg-emerald-500/20 text-emerald-400 font-black px-2 py-0.5 rounded-full uppercase tracking-wider">v0.49.0</span>
          </h3>
          <p className="text-zinc-400 text-sm mt-1">
            Documento operativo para intervención en terreno — Reduciendo Daño Chile
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPage('req')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 border",
              page === 'req' ? "bg-white text-black border-white" : "bg-zinc-900 border-zinc-800 text-zinc-300 hover:bg-zinc-800"
            )}
          >
            <FileText className="w-4 h-4" />
            1. Requerimientos
          </button>
          <button
            onClick={() => setPage('map')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 border",
              page === 'map' ? "bg-white text-black border-white" : "bg-zinc-900 border-zinc-800 text-zinc-300 hover:bg-zinc-800"
            )}
          >
            <Layers className="w-4 h-4" />
            2. Distribución
          </button>
          <button
            onClick={() => setPage('config')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 border",
              page === 'config' ? "bg-white text-black border-white" : "bg-zinc-900 border-zinc-800 text-zinc-300 hover:bg-zinc-800"
            )}
          >
            <Settings className="w-4 h-4" />
            Ajustes ONG
          </button>
          <button
            onClick={() => loadFromBackend()}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 bg-emerald-950/40 border border-emerald-800/70 text-emerald-200 hover:bg-emerald-900/50"
          >
            <RefreshCw className="h-4 w-4" />
            Motor Python
          </button>
          <button
            onClick={() => setExportTheme(t => t === 'dark' ? 'white' : 'dark')}
            title="Tema del PDF exportado (RD dark / white)"
            className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-xs font-bold text-zinc-300 hover:bg-zinc-800 transition-colors"
          >
            <Moon className="h-4 w-4" /> Tema: {exportTheme === 'dark' ? 'Dark' : 'White'}
          </button>
          <button
            onClick={printRider}
            className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-xs font-bold text-zinc-300 hover:bg-zinc-800 transition-colors"
          >
            <Printer className="h-4 w-4" /> Imprimir Rider
          </button>
        </div>
      </div>
      {backendStatus && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/70 px-4 py-2 text-xs text-zinc-400 print:hidden">
          {backendStatus}
        </div>
      )}

      {/* Pack selector */}
      <div className="flex gap-2 flex-wrap bg-zinc-900/20 border border-zinc-800/80 p-3 rounded-xl items-center print:hidden">
        <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mr-2">Packs de Servicio:</span>
        {ALL_PACKS.map(p => (
          <button
            key={p}
            onClick={() => applyPreset(p)}
            className={cn(
              'rounded-lg border px-4 py-2 text-xs font-bold uppercase tracking-widest transition-colors text-left',
              preset === p
                ? 'border-emerald-500 bg-emerald-950/60 text-emerald-300'
                : 'border-zinc-700 bg-zinc-900 text-zinc-400 hover:border-zinc-600 hover:text-zinc-200'
            )}
          >
            <span className="block">{PACKS[p].label}</span>
            <span className="block text-[9px] font-normal normal-case tracking-normal opacity-70">{formatCLP(PACKS[p].precio)} · {PACKS[p].desc}</span>
          </button>
        ))}
        <button
          onClick={() => applyPreset(preset)}
          className="ml-auto flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" /> Reset
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-zinc-800 pb-0 print:hidden">
        {NAV_TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setPage(key)}
            className={cn(
              'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors -mb-px border-b-2 flex items-center gap-2',
              page === key
                ? 'border-emerald-500 text-emerald-400 bg-zinc-900/50'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            )}
          >
            {key === 'req' && <FileText className="w-4 h-4" />}
            {key === 'map' && <Layers className="w-4 h-4" />}
            {key === 'config' && <Settings className="w-4 h-4" />}
            {label}
          </button>
        ))}
      </div>

      {/* ── Checklist tab (17 items) ── */}
      {page === 'req' && (
        <div className="space-y-4 print:hidden">
          {/* Antecedentes Card */}
          <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/30">
            <h3 className="text-sm font-black uppercase text-zinc-400 tracking-wider mb-4">Antecedentes del Evento</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-[10px] uppercase tracking-widest text-zinc-500 block mb-1 font-bold">Nombre del Evento</label>
                <input
                  value={eventName}
                  onChange={e => setEventName(e.target.value)}
                  className="w-full bg-black/40 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
                />
              </div>
              <div>
                <label className="text-[10px] uppercase tracking-widest text-zinc-500 block mb-1 font-bold">Fecha del Evento</label>
                <input
                  type="date"
                  value={eventDate}
                  onChange={e => setEventDate(e.target.value)}
                  className="w-full bg-black/40 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
                />
              </div>
              <div>
                <label className="text-[10px] uppercase tracking-widest text-zinc-500 block mb-1 font-bold">Ubicación / Local</label>
                <input
                  value={eventVenue}
                  onChange={e => setEventVenue(e.target.value)}
                  className="w-full bg-black/40 border border-zinc-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-zinc-600"
                />
              </div>
            </div>
          </div>

          {/* Modalidades Cards */}
          <div className="grid grid-cols-3 gap-4">
            <ModalidadCard
              icon={<Heart className="w-5 h-5 text-emerald-400" />}
              title="Stand Informativo"
              description="Personas capacitadas para orientar y entregar consejos preventivos. Material educativo, protectores auditivos, suplementos pre/post."
              color={ZONE_COLORS.informativo}
            />
            <ModalidadCard
              icon={<AlertTriangle className="w-5 h-5 text-yellow-500" />}
              title="Stand de Testeo"
              description="Análisis colorimétricos de sustancias gratuito. Equipo liderado por analistas químicos y químicos farmacéuticos."
              color={ZONE_COLORS.testeo}
            />
            <ModalidadCard
              icon={<Coffee className="w-5 h-5 text-purple-400" />}
              title="Contención"
              description="Rondas preventivas en terreno. Contención psicológica y atención en situaciones de crisis o desregulación emocional."
              color={ZONE_COLORS.contencion}
            />
          </div>

          <div className="flex items-center justify-between">
            <h2 className="font-bold text-sm text-zinc-400 uppercase tracking-widest">Requerimientos Operativos (17 items)</h2>
            <button
              onClick={checkAll}
              className="text-xs text-zinc-500 hover:text-zinc-200 transition-colors"
            >
              {checkedItems.length === CHECKLIST_SECTIONS.flatMap(s => s.items).length ? 'Desmarcar todo' : 'Marcar todo'}
            </button>
          </div>
          
          <div className="grid gap-4 md:grid-cols-2">
            {CHECKLIST_SECTIONS.map(s => (
              <div key={s.title} className="rounded-2xl border border-zinc-800 bg-zinc-900/45 p-5 group hover:border-emerald-500/20 transition-all">
                <div className="flex items-center gap-2 mb-4 border-b border-zinc-800/80 pb-1">
                  <span className="text-emerald-500">{renderRequirementIcon(s.iconName, "w-4 h-4")}</span>
                  <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400">{s.title}</h3>
                </div>
                <ul className="space-y-2">
                  {s.items.map(item => (
                    <li key={item.text}>
                      <label className="flex items-center gap-3 cursor-pointer group/item">
                        <input
                          type="checkbox"
                          checked={checkedItems.includes(item.text)}
                          onChange={() => toggleCheck(item.text)}
                          className="hidden"
                        />
                        <span
                          className={cn(
                            'h-4 w-4 shrink-0 rounded border-2 flex items-center justify-center transition-colors',
                            checkedItems.includes(item.text)
                              ? 'border-emerald-500 bg-emerald-500'
                              : 'border-zinc-600 group-hover/item:border-zinc-400'
                          )}
                        >
                          {checkedItems.includes(item.text) && (
                            <svg className="h-2.5 w-2.5 text-black" viewBox="0 0 10 10" fill="none">
                              <path d="M2 5l3 3 3-5" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          )}
                        </span>
                        <div className="flex items-center gap-2 overflow-hidden flex-1">
                          {renderRequirementIcon(item.icon, "w-3.5 h-3.5 text-zinc-500 group-hover/item:text-zinc-300")}
                          <span className={cn('text-xs transition-colors truncate', checkedItems.includes(item.text) ? 'text-zinc-500 line-through' : 'text-zinc-300')}>
                            {item.text}
                          </span>
                        </div>
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between rounded-xl border border-zinc-800/60 bg-zinc-900/20 px-6 py-4">
            <span className="text-xs text-zinc-500 uppercase tracking-widest font-mono">
              {completedChecks} / {totalChecks} Requerimientos completados
            </span>
            <button
              onClick={exportChecklistMarkdown}
              className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-xs font-bold text-zinc-300 hover:bg-zinc-800 transition-all active:scale-[0.98]"
            >
              <Download className="w-3.5 h-3.5" /> Exportar Checklist (.md)
            </button>
          </div>

          <button
            onClick={handleGoToPlano}
            className="w-full py-5 bg-emerald-500 hover:bg-emerald-400 text-black font-black rounded-3xl shadow-xl shadow-emerald-500/10 transition-transform active:scale-[0.98] flex items-center justify-center gap-3 text-base"
          >
            Ir al Plano de Distribución (Sincronizar Selección)
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* ── Map tab ── */}
      {page === 'map' && (
        <div className="grid grid-cols-4 gap-6 print:hidden">
          {/* SVG Canvas and Controls */}
          <div className="col-span-3 space-y-4">
            <div className="flex items-center justify-between px-1">
              <div className="flex items-center gap-1.5">
                <button onClick={() => setZoom(z => Math.min(z + 0.15, 2.5))} className="p-2 bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white" title="Zoom +"><Plus className="w-3.5 h-3.5"/></button>
                <button onClick={() => setZoom(z => Math.max(z - 0.15, 0.4))} className="p-2 bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white" title="Zoom -"><Trash2 className="w-3.5 h-3.5"/></button>
                <button onClick={() => setZoom(1)} className="p-2 bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white" title="Reset Zoom"><RotateCcw className="w-3.5 h-3.5"/></button>
                <div className="w-px h-5 bg-zinc-800 mx-1" />
                <button onClick={() => setShowGrid(!showGrid)} className={cn("p-2 border rounded-lg transition-colors text-xs font-bold", showGrid ? "bg-zinc-800 border-zinc-700 text-white" : "bg-zinc-900 border-zinc-800 text-zinc-500")}>Grilla</button>
                <button onClick={() => setShowLegend(!showLegend)} className={cn("p-2 border rounded-lg transition-colors text-xs font-bold", showLegend ? "bg-zinc-800 border-zinc-700 text-white" : "bg-zinc-900 border-zinc-800 text-zinc-500")}>Leyenda</button>
                <button onClick={autoArrangePlano} className="p-2 border border-emerald-700/60 bg-emerald-950/40 rounded-lg transition-colors text-xs font-bold text-emerald-300 hover:bg-emerald-900/50">Auto ordenar</button>
                <button onClick={orderLayersByPriority} className="p-2 border border-sky-700/60 bg-sky-950/40 rounded-lg transition-colors text-xs font-bold text-sky-300 hover:bg-sky-900/50">Orden capas</button>
                <button onClick={resetLegendPosition} className="p-2 border border-zinc-800 bg-zinc-900 rounded-lg transition-colors text-xs font-bold text-zinc-500 hover:text-zinc-300">Reset leyenda</button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-zinc-600 mr-2">{Math.round(zoom * 100)}%</span>
                <button onClick={exportSVG} className="flex items-center gap-1.5 p-2 bg-zinc-900 border border-zinc-800 rounded-lg text-xs font-bold hover:bg-zinc-800 text-zinc-400 hover:text-white"><Download className="w-3.5 h-3.5"/> SVG</button>
              </div>
            </div>

            {/* SVG Canvas wrapper */}
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950 overflow-hidden relative" style={{ height: "650px" }}>
              <div className="w-full h-full overflow-auto flex items-center justify-center p-4">
                <div className="relative bg-[#09090b] border border-zinc-800 shadow-2xl transition-all" style={{ width: 800, height: 565, transform: `scale(${zoom})`, transformOrigin: "center" }}>
                  <svg
                    ref={svgRef}
                    viewBox="0 0 2970 2100"
                    className="w-full h-full"
                    onClick={() => setSelectedId(null)}
                  >
                    {/* Grid pattern */}
                    {showGrid && (
                      <g opacity={0.08}>
                        {Array.from({ length: 150 }, (_, i) => (
                          <line key={`gv${i}`} x1={i * 20} y1={0} x2={i * 20} y2={2100} stroke="#555" strokeWidth={i % 5 === 0 ? 3 : 1} />
                        ))}
                        {Array.from({ length: 110 }, (_, i) => (
                          <line key={`gh${i}`} x1={0} y1={i * 20} x2={2970} y2={i * 20} stroke="#555" strokeWidth={i % 5 === 0 ? 3 : 1} />
                        ))}
                      </g>
                    )}

                    {/* Boundary frame */}
                    <rect x={PLANO_FRAME.x} y={PLANO_FRAME.y} width={PLANO_FRAME.w} height={PLANO_FRAME.h} fill="none" stroke="#3f3f46" strokeWidth={5} strokeDasharray="30 20" rx={20} />

                    {/* Elements */}
                    {elements.filter(el => el.visible).map(el => {
                      if (el.type === 'symbol') {
                        return renderSymbol(el);
                      }
                      return (
                        <g
                          key={el.id}
                          transform={`translate(${el.x},${el.y})`}
                          onMouseDown={(e) => { e.stopPropagation(); onMouseDown(e, el.id); }}
                          onTouchStart={(e) => { e.stopPropagation(); onTouchStart(e, el.id); }}
                          onClick={(e) => { e.stopPropagation(); selectElementAndBringToFront(el.id); }}
                          className="cursor-move"
                        >
                          <rect
                            width={el.w}
                            height={el.h}
                            rx={16}
                            fill={el.color}
                            fillOpacity={0.48}
                            style={{ mixBlendMode: 'screen' }}
                            stroke={el.id === selectedId ? '#ffffff' : el.color}
                            strokeWidth={el.id === selectedId ? 10 : 5}
                          />
                          <text x={el.w / 2} y={el.h / 2} textAnchor="middle" dominantBaseline="central" fontSize={42} fill="white" fontWeight="bold">
                            {el.label.toUpperCase()}
                          </text>
                          <text x={el.w / 2} y={el.h / 2 + 50} textAnchor="middle" dominantBaseline="central" fontSize={24} fill="#ffffff80" fontWeight="bold" fontFamily="monospace">
                            {el.w}×{el.h}
                          </text>
                          {el.id === selectedId && (
                            <rect x={-5} y={-10} width={el.w + 10} height={el.h + 20} rx={16} fill="none" stroke="#10b981" strokeWidth={5} strokeDasharray="15 10" />
                          )}
                        </g>
                      );
                    })}

                    {/* Encabezados de categoria sobre cada fila de iconos */}
                    {iconCategoryHeaders.map(h => (
                      <text key={`cat-${h.category}`} x={h.x} y={h.y - 22} fontSize={30} fill="#e879f9" fontWeight="900" fontFamily="monospace" style={{ letterSpacing: '0.06em' }}>
                        {h.category.toUpperCase()}
                      </text>
                    ))}

                    {/* Draggable Legend */}
                    {showLegend && (
                      <g
                        transform={`translate(${legendPos.x},${legendPos.y})`}
                        onMouseDown={onLegendMouseDown}
                        onTouchStart={onLegendTouchStart}
                        className="cursor-grab"
                      >
                        <rect width={900} height={Math.min(900, Math.max(220, 160 + Math.ceil(visibleLegendSymbols.length / 2) * 84))} rx={30} fill="#18181bcc" stroke="#3f3f46" strokeWidth={5} />
                        <text x={450} y={80} textAnchor="middle" fontSize={40} fill="#a1a1aa" fontWeight="black" fontFamily="monospace" style={{ letterSpacing: '0.08em' }}>
                          LEYENDA TÉCNICA
                        </text>
                        {visibleLegendSymbols.map((el, i) => {
                          const fill = el.color;
                          const col = i % 2;
                          const row = Math.floor(i / 2);
                          return (
                            <g key={`legend-${el.id}`} transform={`translate(${48 + col * 410},${160 + row * 84})`}>
                              <svg x={0} y={0} width={58} height={58} viewBox="0 0 160 160">
                                {renderSymbolGlyph(el.symbolKey || 'unknown', fill)}
                              </svg>
                              <text x={82} y={40} fontSize={26} fill="#a1a1aa" fontWeight="bold" fontFamily="sans-serif">{el.label.toUpperCase().slice(0, 18)}</text>
                            </g>
                          );
                        })}
                      </g>
                    )}

                    {/* Title block */}
                    <g transform="translate(100, 2020)">
                      <text fill="#888" fontSize={36} fontWeight={900} fontFamily="Inter, sans-serif">{eventName.toUpperCase()}</text>
                      <text x={0} y={50} fill="#555" fontSize={28} fontFamily="Inter, sans-serif">{`${eventVenue.toUpperCase()} · ${eventDate}`}</text>
                      <text x={2770} y={0} textAnchor="end" fill="#aaa" fontSize={24} fontFamily="monospace">Reduciendo Daño Chile · Rider Operativo</text>
                    </g>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar Controls */}
          <aside className="space-y-4">
              {/* Elements List */}
              <div className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl space-y-3">
                <h4 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">Zonas de Montaje</h4>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(ZONE_LABELS).filter(([k]) => !['power','heating','rack','extinguisher','water'].includes(k)).map(([key, label]) => (
                    <button
                      key={key}
                      onClick={() => addElement(key)}
                      className="flex items-center gap-2 px-2.5 py-2 bg-zinc-800/50 border border-zinc-800 rounded-lg text-[10px] font-medium hover:bg-zinc-800 transition-colors text-left"
                    >
                      <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: ZONE_COLORS[key] }} />
                      <span className="truncate">{label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Add Symbols */}
              <div className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl">
                <h4 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-3">Símbolos Técnicos</h4>
                <div className="grid grid-cols-4 gap-2 max-h-80 overflow-y-auto pr-1">
                  {SYMBOL_CATALOG.map(spec => (
                    <button
                      key={spec.key}
                      onClick={() => addSymbol(spec.key)}
                      title={spec.label}
                      className="flex flex-col items-center p-2 bg-zinc-800/30 border border-zinc-800 rounded-xl hover:bg-zinc-800 group transition-all"
                    >
                      {renderRequirementIcon(spec.icon, "w-4 h-4 text-zinc-300")}
                      <span className="mt-1.5 text-[7px] uppercase font-black opacity-50 group-hover:opacity-100 truncate max-w-[58px]">{spec.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Property Editor with Color Picker */}
              {selectedElement && (
                <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl space-y-4 shadow-2xl">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">Propiedades</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-[10px] text-zinc-500 block mb-1">Nombre / Texto Interno</label>
                      <input
                        value={selectedElement.label}
                        onChange={e => setElements(prev => prev.map(el => el.id === selectedId ? { ...el, label: e.target.value } : el))}
                        className="w-full bg-black/40 border border-zinc-800 rounded px-2.5 py-1.5 text-xs focus:outline-none focus:border-zinc-600"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-[10px] text-zinc-500 block mb-1">Ancho (px)</label>
                        <input
                          type="number"
                          value={selectedElement.w}
                          onChange={e => {
                            const val = parseInt(e.target.value) || 0;
                            setElements(prev => prev.map(el => el.id === selectedId ? { ...el, w: val } : el));
                          }}
                          className="w-full bg-black/40 border border-zinc-800 rounded px-2.5 py-1.5 text-xs focus:outline-none focus:border-zinc-600"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-zinc-500 block mb-1">Alto (px)</label>
                        <input
                          type="number"
                          value={selectedElement.h}
                          onChange={e => {
                            const val = parseInt(e.target.value) || 0;
                            setElements(prev => prev.map(el => el.id === selectedId ? { ...el, h: val } : el));
                          }}
                          className="w-full bg-black/40 border border-zinc-800 rounded px-2.5 py-1.5 text-xs focus:outline-none focus:border-zinc-600"
                        />
                      </div>
                    </div>

                    {/* Color Picker */}
                    <div>
                      <label className="text-[10px] text-zinc-500 block mb-1.5">Color del Elemento</label>
                      <div className="flex gap-1.5 flex-wrap">
                        {Object.entries({ ...ZONE_COLORS, black: '#111827', white: '#f8fafc', pink: '#ec4899', cyan: '#06b6d4' }).map(([key, val]) => (
                          <button
                            key={key}
                            onClick={() => setElements(prev => prev.map(el => el.id === selectedId ? { ...el, color: val } : el))}
                            title={ZONE_LABELS[key] || key}
                            className={cn(
                              "w-5 h-5 rounded-full border-2 transition-all",
                              selectedElement.color === val ? "border-white scale-125" : "border-transparent hover:scale-110"
                            )}
                            style={{ background: val }}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Alignment buttons */}
                    <div className="space-y-2 border-t border-zinc-800/80 pt-3">
                      <label className="text-[10px] text-zinc-500 block">Alinear al marco / ordenar</label>
                      <div className="grid grid-cols-3 gap-2">
                        <button onClick={() => alignSelected('left')} className="py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700">Izq</button>
                        <button onClick={() => alignSelected('centerX')} className="py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700">Centro</button>
                        <button onClick={() => alignSelected('right')} className="py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700">Der</button>
                        <button onClick={() => alignSelected('top')} className="py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700">Arriba</button>
                        <button onClick={() => alignSelected('centerY')} className="py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700">Medio</button>
                        <button onClick={() => alignSelected('bottom')} className="py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700">Abajo</button>
                      </div>
                      <button onClick={autoArrangePlano} className="w-full py-1.5 bg-emerald-950/50 border border-emerald-800 rounded text-[9px] font-black uppercase text-emerald-300 hover:bg-emerald-900/50">Auto ordenar plano</button>
                      <button onClick={orderLayersByPriority} className="w-full py-1.5 bg-sky-950/50 border border-sky-800 rounded text-[9px] font-black uppercase text-sky-300 hover:bg-sky-900/50">Ordenar capas base</button>
                    </div>

                    {/* Layer Reordering buttons */}
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => moveLayer('up')}
                        className="flex items-center justify-center gap-1 py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700"
                      >
                        <Layers className="w-3 h-3" /> Subir Capa
                      </button>
                      <button
                        onClick={() => moveLayer('down')}
                        className="flex items-center justify-center gap-1 py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[9px] font-black uppercase hover:bg-zinc-700"
                      >
                        <Layers className="w-3 h-3" /> Bajar Capa
                      </button>
                    </div>

                    <div className="flex items-center gap-2 pt-2 border-t border-zinc-800/80">
                      <button onClick={duplicateSelected} className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-zinc-800 border border-zinc-700 rounded text-[10px] font-medium hover:bg-zinc-700 transition-colors">
                        <Copy className="w-3 h-3" /> Duplicar
                      </button>
                      <button onClick={() => selectedId && removeElement(selectedId)} className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-red-900/20 text-red-400 border border-red-900/30 rounded text-[10px] font-medium hover:bg-red-900/30 transition-colors">
                        <Trash2 className="w-3 h-3" /> Eliminar
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Layers List */}
              <div className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl space-y-3">
                <h4 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">Capas ({elements.length})</h4>
                <div className="space-y-1 max-h-48 overflow-y-auto">
                  {[...elements].reverse().map(el => (
                    <div
                      key={el.id}
                      onClick={() => selectElementAndBringToFront(el.id)}
                      className={cn(
                        "w-full flex items-center gap-2 px-2 py-1.5 rounded text-left text-[10px] transition-colors cursor-pointer",
                        selectedId === el.id ? "bg-zinc-800 text-white" : "text-zinc-400 hover:bg-zinc-800/30"
                      )}
                    >
                      <div className="w-2 h-2 rounded-sm flex-shrink-0" style={{ background: el.color }} />
                      <span className="truncate flex-1">{el.label}</span>
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          toggleVisible(el.id);
                        }}
                        className="p-0.5 hover:text-white"
                      >
                        {el.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Navigation button back */}
              <button
                onClick={() => setPage('req')}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-xs font-medium hover:bg-zinc-800 transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
                Volver a Requerimientos
              </button>
            </aside>
          </div>
        )}

        {/* ── Config tab ── */}
        {page === 'config' && (
          <div className="space-y-4">
            <h2 className="font-bold text-sm text-zinc-400 uppercase tracking-widest">Configuración de la ONG</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/45 p-5 space-y-4">
                <h3 className="text-sm font-bold uppercase tracking-widest text-emerald-500">Personalización de Textos</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-[10px] uppercase tracking-widest text-zinc-500 block mb-1 font-bold">Quiénes Somos</label>
                    <textarea value={orgTexts.who} onChange={e => setOrgTexts({...orgTexts, who: e.target.value})} className="w-full bg-black/40 border border-zinc-800 p-4 rounded-xl text-xs leading-relaxed outline-none focus:border-zinc-600 min-h-[100px]" />
                  </div>
                  <div>
                    <label className="text-[10px] uppercase tracking-widest text-zinc-500 block mb-1 font-bold">Objetivo del Servicio</label>
                    <textarea value={orgTexts.goal} onChange={e => setOrgTexts({...orgTexts, goal: e.target.value})} className="w-full bg-black/40 border border-zinc-800 p-4 rounded-xl text-xs leading-relaxed outline-none focus:border-zinc-600 min-h-[100px]" />
                  </div>
                </div>
              </div>
              
              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/45 p-5 space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500">Integración CLI</h3>
                <div className="space-y-2">
                  {[
                    'py -m flujo app',
                    'py -m flujo health',
                    `py -m flujo portal --repo-url https://github.com/ligereza/vibecodeine`,
                  ].map(cmd => (
                    <code key={cmd} className="block rounded-lg bg-black/40 px-3 py-2 text-[10px] text-zinc-400 break-all">
                      {cmd}
                    </code>
                  ))}
                </div>
                <div className="rounded-xl border border-zinc-800 bg-zinc-950/50 p-3">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-600 mb-1">Notas</p>
                  <p className="text-xs text-zinc-500 leading-relaxed">
                    El plano se genera en el de forma local. Para una versión dinámica con datos reales de jobs,
                    conecta el backend levantando la aplicación con <code className="text-zinc-400">py -m flujo app</code>.
                  </p>
                </div>
                <button
                  onClick={() => setPage('req')}
                  className="w-full py-4 bg-zinc-800 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-zinc-700 transition-all"
                >
                  Guardar y Volver
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

// ─── Sub-components ───

function ModalidadCard({ icon, title, description, color }: { icon: React.ReactNode; title: string; description: string; color: string }) {
  return (
    <div className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-colors group">
      <div className="w-9 h-9 rounded-lg flex items-center justify-center mb-3" style={{ background: color + '25', color }}>
        {icon}
      </div>
      <h4 className="text-sm font-bold text-white mb-2">{title}</h4>
      <p className="text-xs text-zinc-400 leading-relaxed">{description}</p>
    </div>
  );
}
