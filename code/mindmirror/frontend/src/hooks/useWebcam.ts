import { useState, useRef, useCallback, useEffect } from 'react';
import { videoApi } from '../services/api';
import type { EmotionData, RiskLevel } from '../types';

/** WebSocket 情绪结果（与后端 FusedEmotionResult 对齐） */
interface WsEmotionPayload {
  dominant_emotion?: string;
  confidence?: number;
  valence?: number;
  arousal?: number;
  risk_level?: string;
  emotion_scores?: Record<string, number>;
}

/** WebSocket 返回的消息格式 */
interface WsMessage {
  type: 'emotion' | 'skip' | 'pong' | 'stopped' | string;
  emotion?: WsEmotionPayload;
  smoothed_emotion?: WsEmotionPayload;
  face_detected?: boolean;
  frame_id?: number;
  timestamp?: string;
  processing_time_ms?: number;
  error?: string;
  code?: string;
}

interface UseWebcamReturn {
  videoRef: React.RefObject<HTMLVideoElement>;
  isActive: boolean;
  connecting: boolean;
  emotion: EmotionData | null;
  toggleCamera: () => void;
  error: string | null;
}

/** 将 WS 情绪 payload 转为前端 EmotionData */
function payloadToEmotionData(payload: WsEmotionPayload | undefined): EmotionData | null {
  if (!payload || !payload.dominant_emotion) return null;
  return {
    primary_emotion: payload.dominant_emotion,
    confidence: payload.confidence ?? 0,
    valence: payload.valence ?? 0,
    arousal: payload.arousal ?? 0,
    risk_level: (payload.risk_level as RiskLevel) ?? 'low',
    timestamp: new Date().toISOString(),
  };
}

const FRAME_INTERVAL_MS = 500; // 2fps

export function useWebcam(userId: string): UseWebcamReturn {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [isActive, setIsActive] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [emotion, setEmotion] = useState<EmotionData | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 清理函数
  const cleanup = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (wsRef.current) {
      try {
        wsRef.current.send(JSON.stringify({ type: 'stop' }));
        wsRef.current.close();
      } catch {
        // ignore
      }
      wsRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  // 截取当前帧为 base64 JPEG
  const captureFrame = useCallback((): string | null => {
    const video = videoRef.current;
    if (!video || video.readyState < 2) return null;

    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
      canvasRef.current.width = 640;
      canvasRef.current.height = 480;
    }
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    // 返回纯 base64（不带 data URI 前缀，后端两种格式都支持）
    return canvas.toDataURL('image/jpeg', 0.75).split(',')[1];
  }, []);

  // 启动摄像头 + WebSocket
  const startCamera = useCallback(async () => {
    if (isActive || connecting) return;
    setConnecting(true);
    setError(null);

    try {
      // 1. 获取摄像头权限
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 },
      });
      streamRef.current = stream;

      // 等待 video 元素挂载
      await new Promise<void>((resolve) => {
        const check = () => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.onloadedmetadata = () => resolve();
          } else {
            setTimeout(check, 50);
          }
        };
        check();
      });

      // 2. 注册视频用户（成人，自动授权）
      await videoApi.registerUser(userId);

      // 3. 创建视频会话
      const { session_id: videoSessionId } = await videoApi.createSession(userId);

      // 4. 建立 WebSocket
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/video/stream/${videoSessionId}?user_id=${encodeURIComponent(userId)}`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const msg: WsMessage = JSON.parse(event.data);
          if (msg.type === 'emotion') {
            // 优先使用平滑结果，否则使用当前帧结果
            const payload = msg.smoothed_emotion ?? msg.emotion;
            const emotionData = payloadToEmotionData(payload);
            if (emotionData) setEmotion(emotionData);
          } else if (msg.type === 'skip') {
            // 帧被帧率控制跳过，可忽略
          } else if (msg.error) {
            console.warn('视频分析警告:', msg.error);
          }
        } catch (parseErr) {
          console.warn('WebSocket 消息解析失败:', parseErr);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket 关闭:', event.code, event.reason);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket 错误:', event);
        setError('视频连接异常，请稍后重试');
      };

      // 等待 WebSocket 连接就绪
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('WebSocket 连接超时')), 8000);
        ws.onopen = () => {
          clearTimeout(timeout);
          resolve();
        };
        ws.onerror = (e) => {
          clearTimeout(timeout);
          reject(e);
        };
      });

      // 5. 开始定时发送帧（2fps）
      intervalRef.current = setInterval(() => {
        if (ws.readyState !== WebSocket.OPEN) return;
        const frameData = captureFrame();
        if (frameData) {
          ws.send(JSON.stringify({ type: 'frame', data: frameData }));
        }
      }, FRAME_INTERVAL_MS);

      setIsActive(true);
    } catch (err) {
      console.error('摄像头启动失败:', err);
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          setError('摄像头权限被拒绝，请在浏览器设置中允许访问摄像头');
        } else if (err.name === 'NotFoundError') {
          setError('未找到摄像头设备');
        } else {
          setError(err.message || '摄像头启动失败');
        }
      } else {
        setError('摄像头启动失败，请检查设备和权限设置');
      }
      cleanup();
    } finally {
      setConnecting(false);
    }
  }, [isActive, connecting, userId, captureFrame, cleanup]);

  // 停止摄像头
  const stopCamera = useCallback(() => {
    cleanup();
    setIsActive(false);
    setEmotion(null);
    setError(null);
  }, [cleanup]);

  // 切换开关
  const toggleCamera = useCallback(() => {
    if (isActive) {
      stopCamera();
    } else {
      startCamera();
    }
  }, [isActive, startCamera, stopCamera]);

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return { videoRef, isActive, connecting, emotion, toggleCamera, error };
}
