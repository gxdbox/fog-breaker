const API_BASE = "/api";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API Error: ${res.status} ${body ? `${body}` : res.statusText}`);
  }
  return res.json();
}

export interface ActionItem {
  type: "act" | "watch" | "opportunity";
  text: string;
}

export interface Intelligence {
  id: number;
  title: string;
  content: string;
  url: string | null;
  source_name: string;
  collection_id: number | null;
  profile_id: number | null;
  category: string;
  language: string | null;
  published_at: string | null;
  collected_at: string;
  rating: number | null;
  rating_reason: string | null;
  summary: string | null;
  bullet_summary: string[] | null;
  plain_explanation: string | null;
  action_items: ActionItem[] | null;
  tags: string[] | null;
  potential_impact: string | null;
  is_analyzed: boolean;
  is_duplicate: boolean;
  preference: -1 | 1 | null;
}

export interface Collection {
  id: number;
  name: string;
  source_type: string;
  config: Record<string, unknown>;
  category: string;
  profile_id: number | null;
  poll_interval_minutes: number;
  is_active: boolean;
  last_fetched_at: string | null;
  created_at: string;
}

export interface AlertRule {
  id: number;
  name: string;
  rule_type: string;
  conditions: Record<string, unknown>;
  channels: string[];
  profile_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface AlertLog {
  id: number;
  alert_rule_id: number;
  intelligence_id: number;
  message: string;
  triggered_at: string;
  is_read: boolean;
}

export interface DashboardStats {
  total_intelligences: number;
  today_new: number;
  today_analyzed: number;
  today_alerts: number;
  avg_rating: number | null;
  category_distribution: Record<string, number>;
}

export interface DailyBriefing {
  date: string;
  total_count: number;
  avg_rating: number | null;
  top_intelligences: Intelligence[];
  category_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  ai_summary: string | null;
}

export interface CategorySchemaItem {
  value: string;
  label: string;
}

export interface Profile {
  id: number;
  name: string;
  description: string | null;
  analyzer_prompt: string | null;
  briefing_prompt: string | null;
  category_schema: CategorySchemaItem[] | null;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
}

function withProfile(params: Record<string, string> | undefined, profileId?: number | null): Record<string, string> {
  const p = { ...(params || {}) };
  if (profileId != null) p.profile_id = String(profileId);
  return p;
}

function qs(params: Record<string, string>): string {
  const filtered = Object.entries(params).filter(([, v]) => v !== "" && v != null);
  return filtered.length ? "?" + new URLSearchParams(filtered).toString() : "";
}

export const api = {
  dashboard: {
    stats: (profileId?: number | null) => fetchAPI<DashboardStats>(`/stats${qs(withProfile(undefined, profileId))}`),
    briefing: (profileId?: number | null) => fetchAPI<DailyBriefing>(`/briefing${qs(withProfile(undefined, profileId))}`),
  },
  intelligences: {
    list: (params?: Record<string, string>, profileId?: number | null) =>
      fetchAPI<Intelligence[]>(`/intelligences${qs(withProfile(params, profileId))}`),
    get: (id: number) => fetchAPI<Intelligence>(`/intelligences/${id}`),
    preference: (id: number, preference: -1 | 1 | null) =>
      fetchAPI<Intelligence>(`/intelligences/${id}/preference`, { method: "PATCH", body: JSON.stringify({ preference }) }),
    search: (q: string, profileId?: number | null) =>
      fetchAPI<Intelligence[]>(`/intelligences/search${qs(withProfile({ q }, profileId))}`),
  },
  collections: {
    list: (profileId?: number | null) =>
      fetchAPI<Collection[]>(`/collections${qs(withProfile(undefined, profileId))}`),
    create: (data: Partial<Collection>) => fetchAPI<Collection>("/collections", { method: "POST", body: JSON.stringify(data) }),
    toggle: (id: number) => fetchAPI<Collection>(`/collections/${id}/toggle`, { method: "PATCH" }),
    delete: (id: number) => fetchAPI<void>(`/collections/${id}`, { method: "DELETE" }),
  },
  alerts: {
    rules: (profileId?: number | null) => fetchAPI<AlertRule[]>(`/alerts/rules${qs(withProfile(undefined, profileId))}`),
    createRule: (data: Partial<AlertRule>) => fetchAPI<AlertRule>("/alerts/rules", { method: "POST", body: JSON.stringify(data) }),
    logs: (profileId?: number | null) => fetchAPI<AlertLog[]>(`/alerts/logs${qs(withProfile(undefined, profileId))}`),
    markRead: (id: number) => fetchAPI<void>(`/alerts/logs/${id}/read`, { method: "PATCH" }),
  },
  profiles: {
    list: () => fetchAPI<Profile[]>("/profiles"),
    get: (id: number) => fetchAPI<Profile>(`/profiles/${id}`),
    create: (data: Partial<Profile>) => fetchAPI<Profile>("/profiles", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: Partial<Profile>) => fetchAPI<Profile>(`/profiles/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: number) => fetchAPI<{ ok: boolean }>(`/profiles/${id}`, { method: "DELETE" }),
  },
};
