// profiles.ts — definicion declarativa de los perfiles/workspaces del hub.
// Extraido de AppShell.tsx (que tenia el modo cableado en ternarios repetidos
// por todo el componente) para poder: 1) agregar perfiles nuevos sin tocar el
// shell, 2) tener un perfil "oculto" de distribucion (rd-plano) que no
// aparece en el selector pero sigue siendo un perfil valido.
//
// Cada perfil trae ya armadas las clases de Tailwind que antes se decidian
// con `mode === 'x' ? ... : ...` en el render. Nada de logica de color queda
// en AppShell: solo lee `profile.accent.*`.

import {
  LayoutDashboard, Boxes, ClipboardList, Calculator,
  TerminalSquare, Map, Shapes, Heart, Music, Cpu, Radio, Lightbulb, Layers, Camera, Clapperboard,
  type LucideIcon,
} from 'lucide-react';

export type AppView =
  | 'hub'
  | 'jobs'
  | 'intake'
  | 'quote'
  | 'commands'
  | 'plano'
  | 'visualizer'
  | 'events'
  | 'resolume'
  | 'mapping'
  | 'show'
  | 'cultura';

export type WorkspaceMode = 'rd' | 'studio' | 'cultura' | 'rd-plano';

export interface NavItem {
  view: AppView;
  icon: LucideIcon;
  label: string;
  desc: string;
  // true = permite editar/crear contenido dentro de la app (editor, formulario
  // con salida real); false = consulta o generador de comandos copy/paste.
  edit: boolean;
}

// Clases ya armadas para no repetir ternarios de color en el shell.
export interface ProfileAccent {
  // Boton del selector de workspace cuando esta activo.
  selectorActive: string;
  // Color del icono de nav cuando el item esta activo.
  accentText: string;
  // Badge "edit" junto al label del nav item.
  editBadge: string;
  // Badge de perfil en el header mobile (solo color; el resto de clases
  // -- rounded-md/px/py/tamano de fuente -- son compartidas en AppShell).
  mobileBadge: string;
  // Color del icono en el footer del sidebar.
  footerIcon: string;
}

export interface Profile {
  id: WorkspaceMode;
  /** Label del boton selector, ej "Modo RD". */
  label: string;
  /** Badge corto para mobile, ej "RD". */
  shortLabel: string;
  /** Descripcion de 1 linea bajo el selector de workspace. */
  tagline: string;
  /** Texto del footer del sidebar, ej "Reduciendo Dano". */
  footerLabel: string;
  /** Titulo de la primera seccion de nav (los items editables), ej "Edicion RD". */
  navTitle: string;
  selectorIcon: LucideIcon;
  footerIcon: LucideIcon;
  accent: ProfileAccent;
  nav: NavItem[];
  /**
   * true = perfil de distribucion: no aparece en el selector de workspace del
   * hub normal. Se llega a el por querystring (?perfil=) o localStorage, nunca
   * cambiando de perfil a mano dentro de la app.
   */
  hidden?: boolean;
}

// Editables primero: son las herramientas que producen trabajo dentro de la app.
const RD_NAV: NavItem[] = [
  { view: 'hub', icon: LayoutDashboard, label: 'Dashboard', desc: 'Vista general RD', edit: false },
  { view: 'plano', icon: Map, label: 'Plano / Rider', desc: 'Editor de layout de evento', edit: true },
  { view: 'visualizer', icon: Shapes, label: 'SVG Studio', desc: 'Galeria + editor visual', edit: true },
  { view: 'quote', icon: Calculator, label: 'Cotizacion', desc: 'Presupuesto editable', edit: true },
  { view: 'intake', icon: ClipboardList, label: 'Intake', desc: 'Parsear pedidos y crear jobs', edit: true },
  { view: 'jobs', icon: Boxes, label: 'Jobs / Suplementos', desc: 'Estado de trabajos', edit: false },
];

const STUDIO_NAV: NavItem[] = [
  { view: 'hub', icon: LayoutDashboard, label: 'Dashboard', desc: 'Vista general Studio', edit: false },
  { view: 'visualizer', icon: Shapes, label: 'SVG Studio', desc: 'Galeria + editor visual', edit: true },
  { view: 'show', icon: Clapperboard, label: 'Show kit', desc: 'Setlist, cues y registros de show', edit: true },
  { view: 'mapping', icon: Lightbulb, label: 'Mapping LED', desc: 'Rigging / pixel mapping', edit: true },
  { view: 'events', icon: Camera, label: 'Eventos / IG', desc: 'Comando flyer-auto', edit: false },
  { view: 'resolume', icon: Radio, label: 'Resolume / Chataigne', desc: 'Comando SMPTE/OSC', edit: false },
  { view: 'commands', icon: TerminalSquare, label: 'Comandos', desc: 'CLI reference', edit: false },
];

// Cultura: ala de arte-investigacion (tapiz, tilde, psicosis, precursor).
// Por ahora un solo panel de consulta; las herramientas ganan panel al madurar.
const CULTURA_NAV: NavItem[] = [
  { view: 'hub', icon: LayoutDashboard, label: 'Dashboard', desc: 'Vista general Cultura', edit: false },
  { view: 'cultura', icon: Layers, label: 'Cultura', desc: 'Instrumentos y lineas de obra', edit: false },
];

// rd-plano: perfil de distribucion para compartir SOLO el editor de Plano/Rider
// con una persona externa (fuera del equipo). Una sola entrada, sin dashboard,
// sin jobs, sin cotizacion. Ver web/src/mainPlano.tsx para el bundle que lo usa.
const RD_PLANO_NAV: NavItem[] = [
  { view: 'plano', icon: Map, label: 'Plano / Rider', desc: 'Editor de layout de evento', edit: true },
];

export const PROFILES: Record<WorkspaceMode, Profile> = {
  rd: {
    id: 'rd',
    label: 'Modo RD',
    shortLabel: 'RD',
    tagline: 'ONG Reduciendo Dano: Suplementos, Cotizaciones, Plano/Rider, SVG Studio.',
    footerLabel: 'Reduciendo Dano',
    navTitle: 'Edicion RD',
    selectorIcon: Heart,
    footerIcon: Heart,
    accent: {
      selectorActive: 'bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 shadow-sm shadow-emerald-900/30',
      accentText: 'text-emerald-400',
      editBadge: 'bg-emerald-900/60 text-emerald-400',
      mobileBadge: 'bg-emerald-900/50 text-emerald-300',
      footerIcon: 'text-emerald-500',
    },
    nav: RD_NAV,
  },
  studio: {
    id: 'studio',
    label: 'Studio',
    shortLabel: 'STUDIO',
    tagline: 'VJ & Club: Comandos, Eventos/IG, SVG Studio eventos, Resolume/Chataigne.',
    footerLabel: 'Studio / Personal',
    navTitle: 'Edicion Studio',
    selectorIcon: Music,
    footerIcon: Cpu,
    accent: {
      selectorActive: 'bg-violet-900/50 text-violet-300 border border-violet-700/50 shadow-sm shadow-violet-900/30',
      accentText: 'text-violet-400',
      editBadge: 'bg-violet-900/60 text-violet-400',
      mobileBadge: 'bg-violet-900/50 text-violet-300',
      footerIcon: 'text-violet-500',
    },
    nav: STUDIO_NAV,
  },
  cultura: {
    id: 'cultura',
    label: 'Cultura',
    shortLabel: 'CULTURA',
    tagline: 'Arte-investigacion: tapiz, tilde, psicosis, precursor. Instrumento -> material -> pieza.',
    footerLabel: 'Cultura / Arte',
    navTitle: 'Cultura',
    selectorIcon: Layers,
    footerIcon: Layers,
    accent: {
      selectorActive: 'bg-amber-900/50 text-amber-300 border border-amber-700/50 shadow-sm shadow-amber-900/30',
      accentText: 'text-amber-400',
      editBadge: 'bg-amber-900/60 text-amber-400',
      mobileBadge: 'bg-amber-900/50 text-amber-300',
      footerIcon: 'text-amber-500',
    },
    nav: CULTURA_NAV,
  },
  'rd-plano': {
    id: 'rd-plano',
    label: 'Plano RD',
    shortLabel: 'PLANO',
    tagline: 'Perfil de distribucion: solo el editor de Plano/Rider, para compartir fuera del equipo.',
    footerLabel: 'Plano RD (compartido)',
    navTitle: 'Plano',
    selectorIcon: Map,
    footerIcon: Map,
    accent: {
      selectorActive: 'bg-sky-900/50 text-sky-300 border border-sky-700/50 shadow-sm shadow-sky-900/30',
      accentText: 'text-sky-400',
      editBadge: 'bg-sky-900/60 text-sky-400',
      mobileBadge: 'bg-sky-900/50 text-sky-300',
      footerIcon: 'text-sky-500',
    },
    nav: RD_PLANO_NAV,
    hidden: true,
  },
};

/** Perfiles visibles en el selector de workspace del hub (excluye hidden). */
export const VISIBLE_PROFILES: Profile[] = Object.values(PROFILES).filter(p => !p.hidden);

export const DEFAULT_PROFILE_ID: WorkspaceMode = 'rd';

export function isWorkspaceMode(value: string | null | undefined): value is WorkspaceMode {
  return !!value && Object.prototype.hasOwnProperty.call(PROFILES, value);
}

export function getProfile(id: string | null | undefined): Profile {
  return isWorkspaceMode(id) ? PROFILES[id] : PROFILES[DEFAULT_PROFILE_ID];
}

// ── Persistencia + seleccion por URL ────────────────────────────────────
// Orden de resolucion: ?perfil=<id> en la querystring manda sobre todo;
// si no viene, localStorage; si no hay nada (o es invalido en cualquiera de
// los dos casos), cae a DEFAULT_PROFILE_ID sin romper.
export const PROFILE_STORAGE_KEY = 'flujo.perfil';

export function resolveInitialProfileId(): WorkspaceMode {
  if (typeof window === 'undefined') return DEFAULT_PROFILE_ID;

  try {
    const fromUrl = new URLSearchParams(window.location.search).get('perfil');
    if (isWorkspaceMode(fromUrl)) return fromUrl;
  } catch {
    // location.search inaccesible -- seguir con localStorage
  }

  try {
    const fromStorage = window.localStorage.getItem(PROFILE_STORAGE_KEY);
    if (isWorkspaceMode(fromStorage)) return fromStorage;
  } catch {
    // localStorage no disponible (modo privado, file://, cuota) -- caer a default
  }

  return DEFAULT_PROFILE_ID;
}

export function persistProfileId(id: WorkspaceMode): void {
  try {
    window.localStorage.setItem(PROFILE_STORAGE_KEY, id);
  } catch {
    // no bloquear la UI si no se puede persistir
  }
}
