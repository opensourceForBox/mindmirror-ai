import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useChat } from './hooks/useChat';
import { useEmotion } from './hooks/useEmotion';
import { useWebcam } from './hooks/useWebcam';
import { useAudio } from './hooks/useAudio';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import ChatWindow from './components/Chat/ChatWindow';
import InputArea from './components/Chat/InputArea';
import QuickAssessment from './components/Assessment/QuickAssessment';
import type { EmotionData } from './types';

const USER_ID = uuidv4();

export default function App() {
  const { messages, sendMessage, isLoading, currentEmotion: chatEmotion, currentExpression, riskLevel: chatRisk } =
    useChat(USER_ID);
  const { trend: emotionTrend, loading: emotionLoading } = useEmotion(USER_ID);

  // 摄像头 hook
  const { videoRef, isActive: cameraActive, connecting: cameraConnecting, emotion: videoEmotion, toggleCamera, error: cameraError } =
    useWebcam(USER_ID);

  // 麦克风 hook
  const { isActive: micActive, emotion: audioEmotion, toggleRecording, error: micError } =
    useAudio();

  const [showAssessment, setShowAssessment] = useState(false);

  // 合并情绪：视频/音频情绪优先（实时更新），否则用聊天情绪
  // 使用 ref 跟踪最新更新时间来实现"最新优先"策略
  const [displayEmotion, setDisplayEmotion] = useState<EmotionData | null>(null);
  const lastVideoTs = useRef(0);
  const lastAudioTs = useRef(0);

  useEffect(() => {
    if (videoEmotion) {
      lastVideoTs.current = Date.now();
      setDisplayEmotion(videoEmotion);
    }
  }, [videoEmotion]);

  useEffect(() => {
    if (audioEmotion) {
      lastAudioTs.current = Date.now();
      setDisplayEmotion(audioEmotion);
    }
  }, [audioEmotion]);

  // 当视频/音频情绪不再活跃时，回退到聊天情绪
  useEffect(() => {
    if (!cameraActive && !micActive) {
      // 延迟恢复，避免频繁切换
      const timer = setTimeout(() => {
        setDisplayEmotion(chatEmotion);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [cameraActive, micActive, chatEmotion]);

  // 摄像头/麦克风开启时，聊天情绪不覆盖实时情绪
  useEffect(() => {
    if (!cameraActive && !micActive && chatEmotion) {
      setDisplayEmotion(chatEmotion);
    }
  }, [chatEmotion, cameraActive, micActive]);

  const currentEmotion = displayEmotion ?? chatEmotion;
  const riskLevel = currentEmotion?.risk_level ?? chatRisk;

  const handleAssessmentComplete = (results: { score: number; answers: Record<string, number> }) => {
    console.log('Assessment results:', results);
    setShowAssessment(false);
    if (results.score <= 4) {
      sendMessage('我刚做了一个快速评估，感觉最近状态不太好...');
    } else {
      sendMessage('我刚做了一个快速评估，整体感觉还不错。');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-warm-50 dark:bg-gray-900">
      {/* 顶部导航 */}
      <Header onAssessmentClick={() => setShowAssessment(true)} />

      {/* 主内容区 */}
      <div className="flex flex-1 overflow-hidden flex-col md:flex-row">
        {/* 左侧：头像 + 情绪（移动端在上方，桌面端在左侧） */}
        <div className="w-full md:w-[30%] md:min-w-[280px] md:max-w-[360px] flex-shrink-0 order-2 md:order-1">
          <Sidebar
            expression={currentExpression}
            emotion={currentEmotion}
            riskLevel={riskLevel}
            emotionTrend={emotionTrend}
            emotionLoading={emotionLoading}
          />
        </div>

        {/* 右侧：对话区 */}
        <div className="flex-1 flex flex-col min-w-0 order-1 md:order-2">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            currentExpression={currentExpression}
          />
          <InputArea
            onSend={sendMessage}
            isLoading={isLoading}
            onCameraClick={toggleCamera}
            onMicClick={toggleRecording}
            isCameraActive={cameraActive}
            isCameraConnecting={cameraConnecting}
            isMicActive={micActive}
            videoRef={videoRef}
            cameraError={cameraError}
            micError={micError}
          />
        </div>
      </div>

      {/* 快速评估弹窗 */}
      {showAssessment && (
        <QuickAssessment
          onComplete={handleAssessmentComplete}
          onClose={() => setShowAssessment(false)}
        />
      )}
    </div>
  );
}
