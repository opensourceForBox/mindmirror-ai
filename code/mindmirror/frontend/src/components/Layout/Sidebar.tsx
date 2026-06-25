import React from 'react';
import type { Expression, EmotionData, RiskLevel, EmotionTrend } from '../../types';
import Avatar3D from '../Avatar3D';
import EmotionIndicator from '../Emotion/EmotionIndicator';
import EmotionChart from '../Emotion/EmotionChart';

interface SidebarProps {
  expression: Expression;
  emotion: EmotionData | null;
  riskLevel: RiskLevel | string;
  emotionTrend: EmotionTrend | null;
  emotionLoading: boolean;
  /** AI 正在生成回复时为 true, 驱动 3D 头像嘴巴动画 */
  isSpeaking?: boolean;
}

export default function Sidebar({
  expression,
  emotion,
  riskLevel,
  emotionTrend,
  emotionLoading,
  isSpeaking = false,
}: SidebarProps) {
  return (
    <aside className="flex flex-col items-center gap-4 p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-r border-gray-100 dark:border-gray-700 overflow-y-auto">
      {/* 3D 头像区域 */}
      <div className="py-4">
        <Avatar3D emotion={expression} isSpeaking={isSpeaking} size={160} />
      </div>

      {/* 分割线 */}
      <div className="w-16 h-px bg-gray-200 dark:bg-gray-700" />

      {/* 情绪指示器 */}
      <EmotionIndicator emotion={emotion} riskLevel={riskLevel} />

      {/* 分割线 */}
      <div className="w-16 h-px bg-gray-200 dark:bg-gray-700" />

      {/* 情绪趋势图 */}
      <EmotionChart trend={emotionTrend} loading={emotionLoading} />

      {/* 底部提示 */}
      <div className="mt-auto pt-4 text-center">
        <p className="text-xs text-gray-400 dark:text-gray-500">
          所有对话内容安全加密
        </p>
        <div className="flex items-center justify-center gap-1 mt-1">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-gray-400">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <span className="text-xs text-gray-400 dark:text-gray-500">隐私保护</span>
        </div>
      </div>
    </aside>
  );
}
