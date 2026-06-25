import { API_BASE } from '../utils/constants';
import { getToken } from './authService';
import type {
  ScaleBrief,
  ScaleDetail,
  AssessmentSubmitRequest,
  AssessmentResult,
  AssessmentHistoryResponse,
  AssessmentDetailResponse,
} from '../types/assessment';

async function authRequest<T>(url: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as Record<string, string>).detail ?? `请求失败 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const assessmentApi = {
  /** 获取所有量表列表 */
  getScales: () => authRequest<ScaleBrief[]>('/assessment/scales'),

  /** 获取单个量表完整题目 */
  getScaleDetail: (scaleType: string) =>
    authRequest<ScaleDetail>(`/assessment/scales/${scaleType}`),

  /** 提交答案并评分 */
  submit: (data: AssessmentSubmitRequest) =>
    authRequest<AssessmentResult>('/assessment/submit', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /** 获取测评历史 */
  getHistory: (page = 1, pageSize = 10) =>
    authRequest<AssessmentHistoryResponse>(
      `/assessment/history?page=${page}&page_size=${pageSize}`
    ),

  /** 获取单次测评详情 */
  getDetail: (id: number) => authRequest<AssessmentDetailResponse>(`/assessment/history/${id}`),
};
