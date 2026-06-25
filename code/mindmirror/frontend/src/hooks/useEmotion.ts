import { useState, useEffect, useCallback } from 'react';
import { chatApi } from '../services/api';
import type { EmotionTrend, EmotionTrendPoint, RiskLevel } from '../types';

interface UseEmotionReturn {
  trend: EmotionTrend | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
  latestPoint: EmotionTrendPoint | null;
  trendDirection: 'improving' | 'stable' | 'declining' | null;
}

export function useEmotion(sessionId: string): UseEmotionReturn {
  const [trend, setTrend] = useState<EmotionTrend | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrend = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await chatApi.getEmotionTrend(sessionId);
      setTrend(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取情绪趋势失败');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (sessionId) fetchTrend();
  }, [sessionId, fetchTrend]);

  const latestPoint = trend?.data_points?.length
    ? trend.data_points[trend.data_points.length - 1]
    : null;

  return {
    trend,
    loading,
    error,
    refresh: fetchTrend,
    latestPoint,
    trendDirection: trend?.trend ?? null,
  };
}
