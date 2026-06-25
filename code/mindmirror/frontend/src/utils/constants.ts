import type { Expression, RiskLevel } from '../types';

export const API_BASE = '/api';

export const EXPRESSION_LABELS: Record<Expression, string> = {
  neutral: '平静微笑',
  happy: '开心',
  empathy: '同理心',
  thinking: '思考中...',
  concerned: '担忧',
  encouraging: '鼓励',
};

export const RISK_COLORS: Record<RiskLevel, string> = {
  low: '#4ADE80',
  medium: '#FBBF24',
  high: '#F87171',
};

export const RISK_LABELS: Record<RiskLevel, string> = {
  low: '状态良好',
  medium: '需要关注',
  high: '需要支持',
};

export const EMOTION_LABELS: Record<string, string> = {
  happy: '开心',
  sad: '难过',
  angry: '生气',
  fearful: '害怕',
  disgusted: '厌恶',
  surprised: '惊讶',
  neutral: '平静',
  anxious: '焦虑',
};

export const THEME = {
  lavender: '#7C5CFC',
  warmWhite: '#FFF8F0',
  skyBlue: '#E8F4FD',
  darkBg: '#1F2937',
} as const;

export const INITIAL_GREETING = '你好！我是 MindMirror，你的心理健康伙伴。今天想聊点什么呢？无论是学习压力、朋友关系，还是心情烦闷，都可以跟我说哦。';
