import { useState, useRef, useCallback } from 'react';
import { emotionApi } from '../services/api';
import type { EmotionData } from '../types';

interface UseWebcamReturn {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  isActive: boolean;
  analyzing: boolean;
  startCamera: () => Promise<void>;
  stopCamera: () => void;
  captureAndAnalyze: () => Promise<EmotionData | null>;
  error: string | null;
}

export function useWebcam(): UseWebcamReturn {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startCamera = useCallback(async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsActive(true);
    } catch (err) {
      setError('无法访问摄像头，请检查权限设置');
      console.error('Camera error:', err);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsActive(false);
  }, []);

  const captureAndAnalyze = useCallback(async (): Promise<EmotionData | null> => {
    if (!videoRef.current || !isActive) return null;

    setAnalyzing(true);
    try {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('Canvas context failed');
      ctx.drawImage(videoRef.current, 0, 0);

      const blob = await new Promise<Blob>((resolve, reject) => {
        canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('Blob failed'))), 'image/jpeg', 0.8);
      });

      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
      const result = await emotionApi.analyzeImage(file);
      return result;
    } catch (err) {
      setError('情绪分析失败');
      console.error('Analysis error:', err);
      return null;
    } finally {
      setAnalyzing(false);
    }
  }, [isActive]);

  return { videoRef, isActive, analyzing, startCamera, stopCamera, captureAndAnalyze, error };
}
