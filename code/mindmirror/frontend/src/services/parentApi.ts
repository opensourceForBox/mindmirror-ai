import { getToken } from './authService';

const API_BASE = '/api';

export interface ChildInfo {
  id: number;
  username: string;
  email: string;
  created_at?: string;
}

export interface EmotionSummary {
  child_name: string;
  avg_mood: number | null;
  mood_trend: 'improving' | 'stable' | 'declining';
  dominant_emotions: string[];
  conversation_count: number;
}

export interface AlertItem {
  id: number;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  is_read: boolean;
  created_at?: string;
}

export interface ProfileSummary {
  user_id: number;
  username: string;
  personality_summary: string;
  active_issues: string[];
  interests: string[];
  coping_styles: Record<string, unknown>;
  total_conversations: number;
  last_updated?: string;
}

export interface DashboardCard {
  child: ChildInfo;
  unread_alerts: number;
  latest_alert?: AlertItem;
  emotion_summary: EmotionSummary;
}

export interface DashboardData {
  parent_name: string;
  children: DashboardCard[];
}

export interface MoodHistoryPoint {
  date: string;
  mood_score: number;
  mood_note?: string | null;
}

async function authRequest<T>(url: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as Record<string, string>).detail ?? `请求失败 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const parentApi = {
  getChildren: () => authRequest<ChildInfo[]>('/parent/children'),

  getEmotionSummary: (childId: number) =>
    authRequest<EmotionSummary>(`/parent/child/${childId}/emotion-summary`),

  getAlerts: (childId: number) =>
    authRequest<AlertItem[]>(`/parent/child/${childId}/alerts`),

  markAlertRead: (childId: number, alertId: number) =>
    authRequest<{ id: number; is_read: boolean }>(
      `/parent/child/${childId}/alerts/${alertId}/read`,
      { method: 'POST' }
    ),

  getProfileSummary: (childId: number) =>
    authRequest<ProfileSummary>(`/parent/child/${childId}/profile`),

  getDashboard: () => authRequest<DashboardData>('/parent/dashboard'),

  getMoodHistory: (childId: number) =>
    authRequest<MoodHistoryPoint[]>(`/parent/child/${childId}/mood-history`),
};
