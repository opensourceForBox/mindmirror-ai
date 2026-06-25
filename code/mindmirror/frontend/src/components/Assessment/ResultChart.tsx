import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { AssessmentResult, AssessmentHistoryItem } from '../../types/assessment';

interface ResultChartProps {
  result: AssessmentResult;
  scaleName: string;
  history: AssessmentHistoryItem[] | null;
  historyLoading: boolean;
  onBack: () => void;
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function getLevelColor(level: string) {
  switch (level) {
    case 'none':
    case 'low':
    case 'normal':
      return '#4ADE80';
    case 'mild':
    case 'moderate':
      return '#FBBF24';
    case 'moderately_severe':
    case 'high':
      return '#FB923C';
    case 'severe':
      return '#F87171';
    default:
      return '#7C5CFC';
  }
}

export default function ResultChart({
  result,
  scaleName,
  history,
  historyLoading,
  onBack,
}: ResultChartProps) {
  const levelColor = getLevelColor(result.level);

  // 构造趋势数据：历史记录 + 本次结果
  const trendData = React.useMemo(() => {
    const base =
      history?.map((item) => ({
        date: formatDate(item.created_at),
        score: item.total_score,
        interpretation: item.interpretation ?? '',
      })) ?? [];
    if (result.created_at) {
      base.push({
        date: formatDate(result.created_at),
        score: result.score,
        interpretation: result.interpretation,
      });
    }
    return base;
  }, [history, result]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-lavender-50 via-white to-warm-50 p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        <button
          onClick={onBack}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-lavender-600 transition mb-6"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M15 18l-6-6 6-6" />
          </svg>
          重新测评
        </button>

        {/* 分数卡片 */}
        <div className="bg-white rounded-3xl p-8 shadow-xl shadow-lavender-100/50 text-center mb-6">
          <p className="text-sm text-gray-400 mb-2">{scaleName}</p>
          <div
            className="w-28 h-28 mx-auto rounded-full flex flex-col items-center justify-center mb-4"
            style={{ background: `conic-gradient(${levelColor} 0deg, ${levelColor}55 360deg)` }}
          >
            <div className="w-24 h-24 rounded-full bg-white flex flex-col items-center justify-center shadow-sm">
              <span className="text-3xl font-bold text-gray-800">{result.score}</span>
              <span className="text-xs text-gray-400">分</span>
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-1">{result.interpretation}</h2>
          {result.raw_score !== null && result.raw_score !== undefined && (
            <p className="text-sm text-gray-500 mb-4">原始分：{result.raw_score}</p>
          )}
          <span
            className="inline-block px-4 py-1.5 rounded-full text-sm font-medium"
            style={{ backgroundColor: `${levelColor}20`, color: levelColor }}
          >
            测评完成于 {result.created_at ? formatDate(result.created_at) : '刚刚'}
          </span>
        </div>

        {/* 趋势图 */}
        {(historyLoading || (trendData && trendData.length > 1)) && (
          <div className="bg-white rounded-3xl p-6 md:p-8 shadow-xl shadow-lavender-100/50 mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">分数趋势</h3>
            {historyLoading ? (
              <div className="h-64 flex items-center justify-center text-gray-400">
                <div className="w-8 h-8 border-2 border-lavender-200 border-t-lavender-500 rounded-full animate-spin mr-3" />
                加载历史记录...
              </div>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F3F0FF" />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: '#9CA3AF', fontSize: 12 }}
                      axisLine={{ stroke: '#E5E7EB' }}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: '#9CA3AF', fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        borderRadius: 12,
                        border: 'none',
                        boxShadow: '0 8px 30px rgba(124, 92, 252, 0.15)',
                      }}
                      formatter={(value: number, _name, props) => [
                        `${value} 分`,
                        props?.payload?.interpretation,
                      ]}
                      labelStyle={{ color: '#6B7280' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#7C5CFC"
                      strokeWidth={3}
                      dot={{ r: 5, fill: '#7C5CFC', strokeWidth: 2, stroke: '#fff' }}
                      activeDot={{ r: 7 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}

        {/* 改善建议 */}
        <div className="bg-white rounded-3xl p-6 md:p-8 shadow-xl shadow-lavender-100/50 mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7C5CFC" strokeWidth="2">
              <path d="M12 2a10 10 0 1 0 10 10H12V2z" />
              <path d="M12 2a10 10 0 0 1 10 10" />
            </svg>
            改善建议
          </h3>
          <ul className="space-y-3">
            {result.suggestions.map((suggestion, idx) => (
              <li key={idx} className="flex items-start gap-3 text-gray-700">
                <span className="w-6 h-6 rounded-full bg-lavender-100 text-lavender-600 flex items-center justify-center text-xs font-semibold flex-shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span className="leading-relaxed">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* 底部提示 */}
        <p className="text-center text-xs text-gray-400 px-4">
          本测评结果仅供参考，不能替代专业诊断。如感到严重困扰，请及时寻求专业帮助。
        </p>
      </div>
    </div>
  );
}
