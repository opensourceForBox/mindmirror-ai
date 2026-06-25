// 表情状态枚举
export type Expression = 'neutral' | 'happy' | 'empathy' | 'thinking' | 'concerned' | 'encouraging';

// 风险等级
export type RiskLevel = 'low' | 'medium' | 'high';

// 情绪数据
export interface EmotionData {
  primary_emotion: string;
  confidence: number;
  valence: number;       // -1 (消极) 到 1 (积极)
  arousal: number;       // 0 (平静) 到 1 (激动)
  risk_level: RiskLevel;
  timestamp: string;
}

// 消息角色
export type MessageRole = 'user' | 'assistant';

// 消息
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  emotion?: EmotionData;
}

// 聊天请求
export interface ChatRequest {
  session_id: string;
  message: string;
  emotion_data?: Partial<EmotionData>;
}

// 聊天响应
export interface ChatResponse {
    response: string;
  emotion?: EmotionData;
  suggested_expression?: Expression;
  session_id: string;
}

// 情绪趋势数据点
export interface EmotionTrendPoint {
  timestamp: string;
  valence: number;
  emotion: string;
  risk_level: RiskLevel;
}

// 情绪趋势
export interface EmotionTrend {
  session_id: string;
  data_points: EmotionTrendPoint[];
  average_valence: number;
  trend: 'improving' | 'stable' | 'declining';
}

// 对话历史
export interface ChatHistory {
  session_id: string;
  messages: Message[];
  created_at: string;
}

// 应用状态
export interface AppState {
  sessionId: string;
  messages: Message[];
  currentEmotion: EmotionData | null;
  currentExpression: Expression;
  riskLevel: RiskLevel;
  isLoading: boolean;
}
