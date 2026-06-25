import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
} from 'recharts';

export interface MoodPoint {
  date: string;
  mood_score: number;
  label?: string;
}

interface EmotionTimelineProps {
  data: MoodPoint[];
  childName?: string;
  height?: number;
}

export default function EmotionTimeline({
  data,
  childName = '孩子',
  height = 240,
}: EmotionTimelineProps) {
  const chartData = useMemo(() => {
    return data.map((d) => ({
      ...d,
      displayDate: formatDateLabel(d.date),
      isLow: d.mood_score <= 2,
    }));
  }, [data]);

  const lowestPoint = useMemo(() => {
    if (chartData.length === 0) return null;
    return chartData.reduce((min, p) => (p.mood_score < min.mood_score ? p : min));
  }, [chartData]);

  if (chartData.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500"
        style={{ height }}
      >
        近7天暂无心情记录
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-600">
          {childName} 近7天心情趋势
        </span>
        {lowestPoint && lowestPoint.mood_score <= 2 && (
          <span className="rounded-full bg-rose-100 px-2 py-0.5 text-xs font-medium text-rose-600">
            检测到异常低点
          </span>
        )}
      </div>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: -8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="displayDate"
              tick={{ fontSize: 12, fill: '#64748b' }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={false}
            />
            <YAxis
              domain={[0.5, 5.5]}
              ticks={[1, 2, 3, 4, 5]}
              tick={{ fontSize: 12, fill: '#64748b' }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: '1px solid #e2e8f0',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
              formatter={(value: number) => [`心情分：${value}`, '']}
              labelFormatter={(label: string) => `${label}`}
            />
            <Line
              type="monotone"
              dataKey="mood_score"
              stroke="#0ea5e9"
              strokeWidth={3}
              dot={{ r: 4, fill: '#0ea5e9', strokeWidth: 2, stroke: '#fff' }}
              activeDot={{ r: 6 }}
            />
            {lowestPoint && lowestPoint.mood_score <= 2 && (
              <ReferenceDot
                x={lowestPoint.displayDate}
                y={lowestPoint.mood_score}
                r={6}
                fill="#f43f5e"
                stroke="#fff"
                strokeWidth={2}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 flex justify-between text-xs text-slate-400">
        <span>1 = 很低落</span>
        <span>5 = 很开心</span>
      </div>
    </div>
  );
}

function formatDateLabel(isoDate: string): string {
  const d = new Date(isoDate);
  if (Number.isNaN(d.getTime())) return isoDate;
  return `${d.getMonth() + 1}/${d.getDate()}`;
}
