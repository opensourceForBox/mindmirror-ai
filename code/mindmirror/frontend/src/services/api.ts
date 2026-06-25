import { API_BASE } from '../utils/constants';
import type { ChatRequest, ChatResponse, ChatHistory, EmotionTrend, EmotionData } from '../types';

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
    return res.json();
  },

  healthCheck: () =>
    request<{ status: string }>('/emotion/health'),
};

export const healthApi = {
  check: () =>
    request<{ status: string }>('/health'),
};
