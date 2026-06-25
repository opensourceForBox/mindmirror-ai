import React from 'react';
import type { EmotionData, RiskLevel } from '../../types';
import { RISK_COLORS, RISK_LABELS, EMOTION_LABELS } from '../../utils/constants';

interface EmotionIndicatorProps {
  emotion: EmotionData | null;
  riskLevel: RiskLevel | string;
}

export default function EmotionIndicator({ emotion, riskLevel }: EmotionIndicatorProps) {
  const valence = emotion?.valence ?? 0;
  const confidence = emotion?.confidence ?? 0;
  const primaryEmotion = emotion?.primary_emotion ?? 'neutral';
  const level = (riskLevel || 'low') as RiskLevel;

  // 将 valence (-1 to 1) 转为角度 (-90 to 90)
  const angle = valence * 90;
  const color = RISK_COLORS[level];
  const emotionLabel = EMOTION_LABELS[primaryEmotion] || primaryEmotion;

  return (
    <div className="flex flex-col items-center gap-3 p-4">
      {/* 仪表盘 */}
      <div className="relative" style={{ width: 120, height: 70 }}>
        <svg viewBox="0 0 120 70" width="120" height="70">
          {/* 背景弧 */}
          <path
            d="M 10 65 A 50 50 0 0 1 110 65"
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="8"
            strokeLinecap="round"
            className="dark:stroke-gray-600"
          />

          {/* 三色弧段 */}
          <path d="M 10 65 A 50 50 0 0 1 35 25" fill="none" stroke="#F87171" strokeWidth="8" strokeLinecap="round" opacity="0.3" />
          <path d="M 35 25 A 50 50 0 0 1 85 25" fill="none" stroke="#FBBF24" strokeWidth="8" strokeLinecap="round" opacity="0.3" />
          <path d="M 85 25 A 50 50 0 0 1 110 65" fill="none" stroke="#4ADE80" strokeWidth="8" strokeLinecap="round" opacity="0.3" />

          {/* 指针 */}
          <line
            x1="60"
            y1="65"
            x2={60 + 38 * Math.cos(((angle - 90) * Math.PI) / 180)}
            y2={65 + 38 * Math.sin(((angle - 90) * Math.PI) / 180)}
            stroke={color}
            strokeWidth="3"
            strokeLinecap="round"
            style={{ transition: 'all 0.5s ease' }}
          />
          <circle cx="60" cy="65" r="5" fill={color} style={{ transition: 'fill 0.5s ease' }} />
        </svg>
      </div>

      {/* 情绪标签 */}
      <div className="text-center">
        <p className="text-lg font-semibold" style={{ color, transition: 'color 0.5s ease' }}>
          {emotionLabel}
        </p>
        {emotion && (
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            置信度 {Math.round(confidence * 100)}%
          </p>
        )}
      </div>

      {/* 风险等级 */}
      <div
        className="px-3 py-1 rounded-full text-xs font-medium"
        style={{
          background: `${color}20`,
          color,
          transition: 'all 0.5s ease',
        }}
      >
        {RISK_LABELS[level]}
      </div>

      {!emotion && (
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          开始对话后将自动检测情绪
        </p>
      )}
    </div>
  );
}
