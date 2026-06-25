import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useChat } from './hooks/useChat';
import { useEmotion } from './hooks/useEmotion';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import ChatWindow from './components/Chat/ChatWindow';
import InputArea from './components/Chat/InputArea';
import QuickAssessment from './components/Assessment/QuickAssessment';

const SESSION_ID = uuidv4();

export default function App() {
  const { messages, sendMessage, isLoading, currentEmotion, currentExpression, riskLevel } =
    useChat(SESSION_ID);
  const { trend: emotionTrend, loading: emotionLoading } = useEmotion(SESSION_ID);
  const [showAssessment, setShowAssessment] = useState(false);

  const handleAssessmentComplete = (results: { score: number; answers: Record<string, number> }) => {
    console.log('Assessment results:', results);
    setShowAssessment(false);
    // 可在此处将评估结果发送给后端
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
            onMicClick={() => console.log('Mic clicked - 预留语音输入')}
            onCameraClick={() => console.log('Camera clicked - 预留视频分析')}
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
