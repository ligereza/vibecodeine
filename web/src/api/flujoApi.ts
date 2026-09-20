export type Ping = {
  status?: string;
  version?: string;
  root?: string;
  connected?: boolean;
  mode?: string;
  note?: string;
};

export type JobItem = {
  name: string;
  path?: string;
  estado?: string;
  tipo_pieza?: string;
  proyecto?: string;
  pendientes?: string[] | string;
};

export type JobsResponse = {
  jobs: JobItem[];
  count: number;
  connected?: boolean;
  source?: string;
  error?: string;
};

export type ParsePedidoResponse = {
  tipo?: string;
  medidas?: string;
  formato?: string;
  tool?: string;
  pub?: string;
  warnings?: string[];
  match?: boolean;
  source?: string;
  error?: string;
  [key: string]: unknown;
};

export type CreateJobResponse = {
  created?: boolean;
  job_path?: string;
  name?: string;
  next?: string;
  error?: string;
};

export type LearningEpisode = {
  episode_id?: string;
  project_id?: string;
  status?: string;
  phase?: string;
  objective?: string;
  started_at?: string;
  finished_at?: string;
};

export type ProjectLearningSummary = {
  available?: boolean;
  database?: string;
  reason?: string;
  projects?: Record<string, number>;
  episodes?: Record<string, number>;
  rules?: Record<string, number>;
  contracts?: {
    available?: boolean;
    counts?: Record<string, number>;
    statuses?: Record<string, number>;
    reason?: string;
  };
  audits?: {
    available?: boolean;
    latest_run?: string | null;
    statuses?: Record<string, number>;
    attention?: Array<{ contract_id?: string; status?: string; missing?: string[] }>;
    reason?: string;
  };
  latest_abstain?: LearningEpisode | null;
};

export type OperationalAttention = {
  id?: string;
  kind?: string;
  status?: string;
  severity?: 'info' | 'attention' | 'blocked' | string;
  reason?: string;
  next_action?: string;
  ref?: string;
};

export type OperationalComponent = {
  id?: string;
  label?: string;
  status?: 'ready' | 'active' | 'attention' | 'blocked' | string;
  severity?: 'none' | 'info' | 'attention' | 'blocked' | string;
  read_only?: boolean;
  evidence?: Record<string, unknown>;
  next_action?: string;
};

export type OperationalStatus = {
  schema?: 'mak-system-status-v1' | 'mak-operational-status-v1' | string;
  status?: 'ready' | 'attention' | 'blocked' | 'unknown' | string;
  generated_at?: string;
  database?: string;
  read_only?: boolean;
  repo_root?: string | null;
  physical_root?: string | null;
  learning?: ProjectLearningSummary;
  ledger?: Record<string, unknown>;
  components?: Record<string, OperationalComponent>;
  attention?: OperationalAttention[];
  counts?: { attention?: number; blocked?: number; info?: number; components?: number };
  next_actions?: string[];
};

export type HubStatus = {
  status?: string;
  version?: string;
  root?: string;
  has_svg?: boolean;
  has_projects?: boolean;
  connected?: boolean;
  time?: number;
  operational?: OperationalStatus;
};

export type ProjectProbeResponse = {
  ok?: boolean;
  error?: string;
  decision?: Record<string, unknown>;
  probe?: Record<string, unknown>;
  learning?: ProjectLearningSummary;
  recorded?: boolean;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

function isFileMode(): boolean {
  return typeof window !== 'undefined' && window.location.protocol === 'file:';
}

export const demoJobs: JobsResponse = {
  jobs: [
    { name: 'demo_eventos_flyer', estado: 'por-revisar', tipo_pieza: 'flyer', proyecto: 'EVENTOS', pendientes: ['link Instagram', 'confirmar fecha'] },
    { name: 'demo_suplementos_etiqueta', estado: 'en-diseno', tipo_pieza: 'etiqueta', proyecto: 'SUPLEMENTOS', pendientes: ['tabla nutricional'] },
    { name: 'demo_sticker_pack', estado: 'entregado', tipo_pieza: 'sticker', proyecto: 'SUPLEMENTOS', pendientes: [] },
    { name: 'demo_pendon_evento', estado: 'revision', tipo_pieza: 'pendon', proyecto: 'EVENTOS', pendientes: ['ajustar medidas', 'confirmar logo'] },
  ],
  count: 4,
  source: 'demo',
};

export const flujoApi = {
  isFileMode,

  async ping(): Promise<Ping> {
    if (isFileMode()) return { status: 'demo', version: 'offline', connected: false, mode: 'file' };
    try {
      return await request<Ping>('/api/ping');
    } catch {
      // Sin backend no hay version que informar: mentir con una vieja es peor que omitirla.
      return { status: 'demo', version: '', connected: false, note: 'Backend no disponible' };
    }
  },

  async jobs(): Promise<JobsResponse> {
    if (isFileMode()) return demoJobs;
    try {
      return await request<JobsResponse>('/api/list-jobs');
    } catch (error) {
      return { ...demoJobs, error: error instanceof Error ? error.message : String(error) };
    }
  },

  async projectLearning(): Promise<ProjectLearningSummary> {
    if (isFileMode()) return { available: false, reason: 'file_mode' };
    try {
      return await request<ProjectLearningSummary>('/api/project/learning');
    } catch (error) {
      return { available: false, reason: error instanceof Error ? error.message : String(error) };
    }
  },

  async status(): Promise<HubStatus> {
    if (isFileMode()) {
      return {
        status: 'demo',
        connected: false,
        operational: { status: 'unknown', next_actions: ['open the local Hub backend to read MAK status'] },
      };
    }
    try {
      return await request<HubStatus>('/api/status');
    } catch (error) {
      return {
        status: 'unavailable',
        connected: false,
        operational: {
          status: 'unknown',
          next_actions: [error instanceof Error ? error.message : String(error)],
        },
      };
    }
  },

  async projectProbe(project: unknown): Promise<ProjectProbeResponse> {
    if (isFileMode()) return { ok: false, error: 'file_mode' };
    try {
      return await request<ProjectProbeResponse>('/api/project/probe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project }),
      });
    } catch (error) {
      return { ok: false, error: error instanceof Error ? error.message : String(error) };
    }
  },

  async parsePedido(text: string): Promise<ParsePedidoResponse> {
    if (isFileMode()) {
      const low = text.toLowerCase();
      return {
        tipo: low.includes('plano') ? 'plano' : low.includes('suplement') ? 'etiqueta' : 'flyer',
        medidas: low.includes('instagram') ? '1080x1350' : 'segun pedido',
        formato: low.includes('suplement') ? 'sup_etiqueta_165x65' : 'evt_flyer_fisico_10x14',
        tool: low.includes('plano') ? 'plano' : 'render',
        warnings: ['Demo local: abre con py -m flujo app para parse real'],
        match: true,
        source: 'demo',
      };
    }
    return request<ParsePedidoResponse>('/api/parse-real-pedido', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
  },

  async createJobDraft(text: string, name = '', parsed?: ParsePedidoResponse | null): Promise<CreateJobResponse> {
    if (isFileMode()) return { created: false, error: 'Demo local: abre con py -m flujo app para crear jobs reales' };
    return request<CreateJobResponse>('/api/create-job-draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, name, parsed }),
    });
  },
};
