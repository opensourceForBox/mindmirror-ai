import { API_BASE } from '../utils/constants';
import type { ChatRequest, ChatResponse, ChatHistory, EmotionTrend, EmotionData, RiskLevel } from '../types';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API Error ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

/** 后端 EmotionResponse 格式（统一字段） */
export interface EmotionApiResponse {
  dominant_emotion: string;
  dominant_emotion_cn: string;
  emotion_scores: Record<string, number>;
  confidence: number;
  valence: number;
  arousal: number;
  risk_level: string;
  crisis_signals: string[];
  source: string;
}

/** 将后端 EmotionApiResponse 转为前端 EmotionData */
export function toEmotionData(resp: EmotionApiResponse): EmotionData {
  return {
    primary_emotion: resp.dominant_emotion,
    confidence: resp.confidence,
    valence: resp.valence,
    arousal: resp.arousal,
    risk_level: resp.risk_level as RiskLevel,
    timestamp: new Date().toISOString(),
  };
}

export const chatApi = {
  sendMessage: (sessionId: string, message: string, emotionData?: Partial<EmotionData>) => {
    const body: ChatRequest = {
      session_id: sessionId,
      message,
      emotion_data: emotionData,
    };
    return request<ChatResponse>('/chat/message', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  getHistory: (sessionId: string) =>
    request<ChatHistory>(`/chat/history/${sessionId}`),

  getEmotionTrend: (sessionId: string) =>
    request<EmotionTrend>(`/chat/emotion-trend/${sessionId}`),
};

export const emotionApi = {
  analyzeImage: async (file: File): Promise<EmotionData> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/emotion/analyze/image`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`Emotion API Error ${res.status}`);
    const data: EmotionApiResponse = await res.json();
    return toEmotionData(data);
  },

  analyzeAudio: async (blob: Blob, filename = 'recording.wav'): Promise<EmotionData> => {
    const formData = new FormData();
    formData.append('file', blob, filename);
    const res = await fetch(`${API_BASE}/emotion/analyze/audio`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`Audio API Error ${res.status}`);
    const data: EmotionApiResponse = await res.json();
    return toEmotionData(data);
  },

  healthCheck: () =>
    request<{ status: string }>('/emotion/health'),
};

export const videoApi = {
  /** 注册用户（成人，自动授予视频权限） */
  registerUser: (userId: string) =>
    request<{ allowed: boolean; user_id: string }>('/video/permission', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, age: 25, parental_consent: false }),
    }),

  /** 创建视频处理会话，返回 video_session_id */
  createSession: (userId: string) =>
    request<{ session_id: string; user_id: string }>(`/video/session?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
    }),
};

export const healthApi = {
  check: () =>
    request<{ status: string }>('/health'),
};
