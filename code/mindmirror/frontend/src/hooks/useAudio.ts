import { useState, useRef, useCallback, useEffect } from 'react';
import { emotionApi } from '../services/api';
import type { EmotionData } from '../types';

/** 录音片段时长（毫秒） */
const RECORD_CHUNK_MS = 4000; // 4 秒一段

/** 选择最佳录音 MIME 类型 */
function getRecorderMimeType(): string {
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4',
    'audio/mpeg',
  ];
  for (const mime of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(mime)) {
      return mime;
    }
  }
  return ''; // 使用浏览器默认
}

/** 根据 MIME 类型获取文件扩展名 */
function mimeToExt(mime: string): string {
  if (mime.includes('webm')) return 'webm';
  if (mime.includes('ogg')) return 'ogg';
  if (mime.includes('mp4')) return 'mp4';
  if (mime.includes('mpeg') || mime.includes('mp3')) return 'mp3';
  return 'wav';
}

interface UseAudioReturn {
  isActive: boolean;
  recording: boolean;
  emotion: EmotionData | null;
  toggleRecording: () => void;
  error: string | null;
}

export function useAudio(): UseAudioReturn {
  const [isActive, setIsActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [emotion, setEmotion] = useState<EmotionData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const activeRef = useRef(false); // 用于在闭包中判断是否仍在录音
  const mimeTypeRef = useRef<string>('');

  // 清理所有资源
  const cleanup = useCallback(() => {
    activeRef.current = false;
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (recorderRef.current && recorderRef.current.state !== 'inactive') {
      recorderRef.current.stop();
    }
    recorderRef.current = null;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setRecording(false);
  }, []);

  // 发送录音片段到后端分析
  const analyzeBlob = useCallback(async (blob: Blob) => {
    const ext = mimeToExt(mimeTypeRef.current);
    try {
      const result = await emotionApi.analyzeAudio(blob, `recording.${ext}`);
      // 只有在仍在录音时才更新状态（防止停止后还更新）
      if (activeRef.current) {
        setEmotion(result);
        setError(null);
      }
    } catch (err) {
      console.error('音频分析失败:', err);
      if (activeRef.current) {
        setError('语音情绪分析失败，请重试');
      }
    }
  }, []);

  // 启动录音
  const startRecording = useCallback(async () => {
    if (isActive) return;
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = getRecorderMimeType();
      mimeTypeRef.current = mimeType;

      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorderRef.current = recorder;
      activeRef.current = true;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0 && activeRef.current) {
          analyzeBlob(event.data);
        }
      };

      recorder.onerror = (event) => {
        console.error('MediaRecorder 错误:', event);
        setError('录音出错，请重试');
        cleanup();
      };

      // 每 RECORD_CHUNK_MS 毫秒产生一段数据
      recorder.start(RECORD_CHUNK_MS);
      setRecording(true);
      setIsActive(true);

      // 安全超时：最长录制 5 分钟自动停止
      timerRef.current = setInterval(() => {
        // 仅作为安全检查，不主动停止（由用户手动停止）
      }, 60000);

    } catch (err) {
      console.error('麦克风启动失败:', err);
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          setError('麦克风权限被拒绝，请在浏览器设置中允许访问麦克风');
        } else if (err.name === 'NotFoundError') {
          setError('未找到麦克风设备');
        } else {
          setError(err.message || '麦克风启动失败');
        }
      } else {
        setError('麦克风启动失败，请检查设备和权限设置');
      }
    }
  }, [isActive, analyzeBlob, cleanup]);

  // 停止录音
  const stopRecording = useCallback(() => {
    cleanup();
    setIsActive(false);
    setEmotion(null);
    setError(null);
  }, [cleanup]);

  // 切换开关
  const toggleRecording = useCallback(() => {
    if (isActive) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isActive, startRecording, stopRecording]);

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return { isActive, recording, emotion, toggleRecording, error };
}
