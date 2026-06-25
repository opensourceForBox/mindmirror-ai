import React from 'react';
import type { EmotionTrend } from '../../types';
import { RISK_COLORS } from '../../utils/constants';

interface EmotionChartProps {
  trend: EmotionTrend | null;
  loading: boolean;
}

export default function EmotionChart({ trend, loading }: EmotionChartProps) {
  if (loading) {
    return (
      <div className="p-4 flex items-center justify-center h-32">
        <div className="w-6 h-6 border-2 border-lavender-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!trend || !trend.data_points || trend.data_points.length === 0) {
    return (
      <div className="p-4 text-center">
        <p className="text-sm text-gray-400 dark:text-gray-500">
          暂无情绪趋势数据
        </p>
        <p className="text-xs text-gray-300 dark:text-gray-600 mt-1">
          对话越多，趋势越准确
        </p>
      </div>
    );
  }

  const points = trend.data_points.slice(-10); // 最近10个点
  const width = 280;
  const height = 100;
  const padding = { top: 10, right: 10, bottom: 20, left: 30 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const minVal = -1;
  const maxVal = 1;

  const getX = (i: number) => padding.left + (i / (points.length - 1 || 1)) * chartW;
  const getY = (v: number) => padding.top + chartH - ((v - minVal) / (maxVal - minVal)) * chartH;

  const pathD = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(p.valence)}`)
    .join(' ');

  // 渐变填充路径
  const fillD = `${pathD} L ${getX(points.length - 1)} ${padding.top + chartH} L ${getX(0)} ${padding.top + chartH} Z`;

  const trendColors = {
    improving: '#4ADE80',
    stable: '#FBBF24',
    declining: '#F87171',
  };
  const trendLabels = {
    improving: '好转中',
    stable: '稳定',
    declining: '需关注',
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-600 dark:text-gray-300">情绪趋势</h4>
        <span
          className="text-xs px-2 py-0.5 rounded-full font-medium"
          style={{
            background: `${trendColors[trend.trend]}20`,
            color: trendColors[trend.trend],
          }}
        >
          {trendLabels[trend.trend]}
        </span>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ maxHeight: 120 }}>
        <defs>
          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#7C5CFC" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#7C5CFC" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* 零线 */}
        <line
          x1={padding.left}
          y1={getY(0)}
          x2={padding.left + chartW}
          y2={getY(0)}
          stroke="#E5E7EB"
          strokeWidth="1"
          strokeDasharray="4 2"
          className="dark:stroke-gray-600"
        />

        {/* 填充 */}
        <path d={fillD} fill="url(#chartGradient)" />

        {/* 线条 */}
        <path d={pathD} fill="none" stroke="#7C5CFC" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />

        {/* 数据点 */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={getX(i)}
            cy={getY(p.valence)}
            r="3"
            fill={RISK_COLORS[p.risk_level]}
            stroke="white"
            strokeWidth="1.5"
          />
        ))}

        {/* Y轴标签 */}
        <text x={padding.left - 4} y={getY(1) + 4} textAnchor="end" className="text-[8px] fill-gray-400">+</text>
        <text x={padding.left - 4} y={getY(0) + 4} textAnchor="end" className="text-[8px] fill-gray-400">0</text>
        <text x={padding.left - 4} y={getY(-1) + 4} textAnchor="end" className="text-[8px] fill-gray-400">-</text>
      </svg>
    </div>
  );
}
