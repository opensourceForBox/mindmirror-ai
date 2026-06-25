import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { useChat } from './hooks/useChat';
import { useEmotion } from './hooks/useEmotion';
import { useWebcam } from './hooks/useWebcam';
import { useAudio } from './hooks/useAudio';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import ChatWindow from './components/Chat/ChatWindow';
import InputArea from './components/Chat/InputArea';
import QuickAssessment from './components/Assessment/QuickAssessment';
import DailyCheckin from './components/Topics/DailyCheckin';
import TopicSuggestion from './components/Topics/TopicSuggestion';
import Login from './pages/Login';
import Register from './pages/Register';
import Assessment from './pages/Assessment';
import ParentDashboard from './pages/ParentDashboard';
import type { EmotionData } from './types';

// ─── 路由守卫：未认证 → /login ─────────────────────────────────────────────────
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
      >
        <div className="text-white text-lg font-medium animate-pulse">加载中...</div>
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

// ─── 家长路由守卫：需认证且 role=parent ────────────────────────────────────────
function ParentRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, user } = useAuth();
  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #10b981 100%)' }}
      >
        <div className="text-white text-lg font-medium animate-pulse">加载中...</div>
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role !== 'parent') return <Navigate to="/" replace />;
  return <>{children}</>;
}

// ─── 已认证后的主界面 ─────────────────────────────────────────────────────────
function MainPage() {
  const { user, logout } = useAuth();
  const USER_ID = user ? String(user.id) : uuidv4();

  const { messages, sendMessage, isLoading, currentEmotion: chatEmotion, currentExpression, riskLevel: chatRisk } =
    useChat(USER_ID);
  const { trend: emotionTrend, loading: emotionLoading } = useEmotion(USER_ID);

  const { videoRef, isActive: cameraActive, connecting: cameraConnecting, emotion: videoEmotion, toggleCamera, error: cameraError } =
    useWebcam(USER_ID);

  const { isActive: micActive, emotion: audioEmotion, toggleRecording, error: micError } =
    useAudio();

  const [showAssessment, setShowAssessment] = useState(false);
  const [showCheckin, setShowCheckin] = useState(true);
  const [showTopics, setShowTopics] = useState(false);

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

  useEffect(() => {
    if (!cameraActive && !micActive) {
      const timer = setTimeout(() => setDisplayEmotion(chatEmotion), 1000);
      return () => clearTimeout(timer);
    }
  }, [cameraActive, micActive, chatEmotion]);

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

  const handleCheckinComplete = () => {
    setShowCheckin(false);
    setShowTopics(true);
  };

  const handleSelectTopic = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <div className="flex flex-col h-screen bg-warm-50 dark:bg-gray-900">
      {/* 顶部导航：显示用户名 + 退出 */}
      <div className="flex items-center justify-end px-4 py-2 bg-white border-b border-gray-100">
        <span className="text-sm text-gray-600 mr-3">你好，{user?.username}</span>
        <button
          onClick={logout}
          className="text-sm text-gray-500 hover:text-red-500 transition"
        >
          退出
        </button>
      </div>

      <Header onAssessmentClick={() => setShowAssessment(true)} />

      <div className="flex flex-1 overflow-hidden flex-col md:flex-row">
        <div className="w-full md:w-[30%] md:min-w-[280px] md:max-w-[360px] flex-shrink-0 order-2 md:order-1">
          <Sidebar
            expression={currentExpression}
            emotion={currentEmotion}
            riskLevel={riskLevel}
            emotionTrend={emotionTrend}
            emotionLoading={emotionLoading}
            isSpeaking={isLoading}
          />
        </div>

        <div className="flex-1 flex flex-col min-w-0 order-1 md:order-2">
          {/* 签到与话题推荐区域 */}
          {(showCheckin || showTopics) && (
            <div className="px-4 pt-3 pb-2 space-y-3 border-b border-gray-100 bg-white/80 backdrop-blur-sm">
              {showCheckin && (
                <div className="max-w-md mx-auto md:mx-0">
                  <DailyCheckin onCheckinComplete={handleCheckinComplete} />
                </div>
              )}
              {showTopics && (
                <TopicSuggestion onSelectTopic={handleSelectTopic} />
              )}
              {showTopics && (
                <button
                  onClick={() => setShowTopics(false)}
                  className="text-xs text-gray-400 hover:text-gray-600 transition px-1"
                >
                  收起推荐
                </button>
              )}
            </div>
          )}

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

      {showAssessment && (
        <QuickAssessment
          onComplete={handleAssessmentComplete}
          onClose={() => setShowAssessment(false)}
        />
      )}
    </div>
  );
}

// ─── 根组件 ─────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/assessment"
          element={
            <ProtectedRoute>
              <Assessment />
            </ProtectedRoute>
          }
        />
        <Route
          path="/parent"
          element={
            <ParentRoute>
              <ParentDashboard />
            </ParentRoute>
          }
        />
        {/* 未知路由重定向到首页 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
