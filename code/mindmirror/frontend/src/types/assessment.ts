/** 量表选项 */
export interface ScaleOption {
  label: string;
  value: number;
}

/** 量表题目 */
export interface ScaleQuestion {
  id: number;
  text: string;
}

/** 量表简要信息 */
export interface ScaleBrief {
  scale_type: string;
  name: string;
  title: string;
  description: string;
  category: string;
  question_count: number;
  estimated_minutes: number;
}

/** 量表完整信息 */
export interface ScaleDetail {
  scale_type: string;
  name: string;
  title: string;
  description: string;
  category: string;
  questions: ScaleQuestion[];
  options: ScaleOption[];
  reverse_items: number[];
}

/** 提交答案请求 */
export interface AssessmentSubmitRequest {
  scale_type: string;
  answers: number[];
}

/** 测评结果 */
export interface AssessmentResult {
  score: number;
  raw_score: number | null;
  interpretation: string;
  level: string;
  suggestions: string[];
  scale_type: string;
  created_at: string | null;
}

/** 历史记录单项 */
export interface AssessmentHistoryItem {
  id: number;
  scale_type: string;
  scale_name: string;
  total_score: number;
  interpretation: string | null;
  created_at: string;
}

/** 历史记录分页响应 */
export interface AssessmentHistoryResponse {
  total: number;
  items: AssessmentHistoryItem[];
  page: number;
  page_size: number;
}

/** 历史记录详情 */
export interface AssessmentDetailResponse {
  id: number;
  scale_type: string;
  scale_name: string;
  answers: number[];
  total_score: number;
  interpretation: string | null;
  created_at: string;
}

/** 趋势图数据点 */
export interface AssessmentTrendPoint {
  date: string;
  score: number;
  interpretation: string;
}
