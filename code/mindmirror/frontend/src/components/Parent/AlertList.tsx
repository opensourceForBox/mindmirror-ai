import React, { useState } from 'react';
import type { AlertItem } from '../../services/parentApi';

interface AlertListProps {
  alerts: AlertItem[];
  childId: number;
  onMarkRead?: (childId: number, alertId: number) => void;
}

const severityConfig = {
  critical: {
    label: '紧急',
    bg: 'bg-rose-50',
    border: 'border-rose-200',
    text: 'text-rose-700',
    badge: 'bg-rose-500',
  },
  high: {
    label: '高风险',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    text: 'text-orange-700',
    badge: 'bg-orange-500',
  },
  medium: {
    label: '中等风险',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
    badge: 'bg-amber-500',
  },
  low: {
    label: '低风险',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-700',
    badge: 'bg-emerald-500',
  },
};

export default function AlertList({ alerts, childId, onMarkRead }: AlertListProps) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (alerts.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
        暂无风险告警，孩子状态平稳
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => {
        const config = severityConfig[alert.severity] ?? severityConfig.medium;
        const isExpanded = expandedId === alert.id;

        return (
          <div
            key={alert.id}
            className={`rounded-xl border ${config.border} ${config.bg} overflow-hidden transition-all`}
          >
            <button
              onClick={() => setExpandedId(isExpanded ? null : alert.id)}
              className="w-full px-4 py-3 text-left"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${config.badge}`} />
                  <span className={`text-sm font-semibold ${config.text}`}>
                    {config.label}
                  </span>
                  {!alert.is_read && (
                    <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-600">
                      未读
                    </span>
                  )}
                </div>
                <span className="text-xs text-slate-400">
                  {alert.created_at ? formatDateTime(alert.created_at) : ''}
                </span>
              </div>
              <p className={`mt-1 text-sm ${config.text} line-clamp-1`}>
                {alert.message}
              </p>
            </button>

            {isExpanded && (
              <div className="border-t border-slate-100 bg-white/60 px-4 py-3">
                <p className="text-sm leading-relaxed text-slate-700">
                  {alert.message}
                </p>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-slate-400">
                    类型：{alertTypeLabel(alert.alert_type)}
                  </span>
                  {!alert.is_read && onMarkRead && (
                    <button
                      onClick={() => onMarkRead(childId, alert.id)}
                      className="rounded-lg bg-white px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm ring-1 ring-slate-200 hover:bg-slate-50"
                    >
                      标记已读
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function alertTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    crisis: '危机信号',
    high_risk: '高风险',
    mood_decline: '情绪低落',
    self_harm: '自我伤害',
  };
  return labels[type] ?? type;
}

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
}

function pad(n: number): string {
  return n < 10 ? `0${n}` : String(n);
}
