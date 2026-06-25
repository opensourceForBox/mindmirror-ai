import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ScaleForm from '../components/Assessment/ScaleForm';
import { assessmentApi } from '../services/assessmentApi';
import type { ScaleBrief, AssessmentHistoryItem } from '../types/assessment';

const SCALE_ICONS: Record<string, React.ReactNode> = {
  phq9: (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z" />
      <path d="M9 10h.01" />
      <path d="M15 10h.01" />
      <path d="M9.5 15a3.5 3.5 0 0 0 5 0" />
    </svg>
  ),
  gad7: (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10Z" />
      <path d="M8 14s1.5 2 4 2 4-2 4-2" />
      <path d="M9 9h.01" />
      <path d="M15 9h.01" />
    </svg>
  ),
  pss10: (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
    </svg>
  ),
  sds: (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M16 13H8" />
      <path d="M16 17H8" />
      <path d="M10 9H8" />
    </svg>
  ),
};

const CARD_COLORS: Record<string, string> = {
  phq9: 'from-rose-50 to-lavender-50 text-rose-500',
  gad7: 'from-amber-50 to-lavender-50 text-amber-500',
  pss10: 'from-sky-50 to-lavender-50 text-sky-500',
  sds: 'from-violet-50 to-lavender-50 text-violet-500',
};

export default function Assessment() {
  const navigate = useNavigate();
  const [scales, setScales] = useState<ScaleBrief[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedScale, setSelectedScale] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<AssessmentHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    assessmentApi
      .getScales()
      .then(setScales)
      .catch((e) => setError(e instanceof Error ? e.message : '加载失败'))
      .finally(() => setLoading(false));
  }, []);

  const openHistory = () => {
    setShowHistory(true);
    setHistoryLoading(true);
    assessmentApi
      .getHistory(1, 50)
      .then((res) =>
        setHistory(
          res.items.sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )
        )
      )
      .catch(() => setHistory([]))
      .finally(() => setHistoryLoading(false));
  };

  if (selectedScale) {
    return <ScaleForm scaleType={selectedScale} onBack={() => setSelectedScale(null)} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-lavender-50 via-white to-warm-50">
      {/* 顶部导航 */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-lavender-100 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-lavender-600 transition"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 18l-6-6 6-6" />
            </svg>
            返回首页
          </button>
          <h1 className="text-lg font-bold text-gray-800">心理测评中心</h1>
          <div className="w-12" />
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 md:px-8 py-8 md:py-12">
        {/* 标题区 */}
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-3">
            了解你的内心状态
          </h2>
          <p className="text-gray-500 max-w-xl mx-auto">
            选择一份经过验证的专业量表，用几分钟时间，更清晰地看见自己的情绪、压力与心理健康状况。
          </p>
        </div>

        {loading ? (
          <div className="text-center py-20 text-lavender-600 animate-pulse">加载量表中...</div>
        ) : error ? (
          <div className="text-center py-20 text-red-500">{error}</div>
        ) : (
          <>
            {/* 量表卡片网格 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
              {scales.map((scale) => (
                <button
                  key={scale.scale_type}
                  onClick={() => setSelectedScale(scale.scale_type)}
                  className="group text-left bg-white rounded-3xl p-6 shadow-lg shadow-lavender-100/40 border border-lavender-100/50
                    hover:shadow-xl hover:shadow-lavender-100/60 hover:-translate-y-1 transition-all duration-300"
                >
                  <div className="flex items-start gap-5">
                    <div
                      className={`w-16 h-16 rounded-2xl flex items-center justify-center bg-gradient-to-br ${
                        CARD_COLORS[scale.scale_type] || 'from-lavender-50 to-lavender-100 text-lavender-500'
                      }`}
                    >
                      {SCALE_ICONS[scale.scale_type] || (
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <circle cx="12" cy="12" r="10" />
                          <path d="M12 16v-4" />
                          <path d="M12 8h.01" />
                        </svg>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-xl font-bold text-gray-800 group-hover:text-lavender-700 transition">
                          {scale.title}
                        </h3>
                        <span className="px-2 py-0.5 rounded-full bg-lavender-50 text-lavender-600 text-xs font-medium">
                          {scale.name}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mb-3 leading-relaxed">{scale.description}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <span className="flex items-center gap-1">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M9 11l3 3L22 4" />
                            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                          </svg>
                          {scale.question_count} 题
                        </span>
                        <span className="flex items-center gap-1">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M12 6v6l4 2" />
                          </svg>
                          约 {scale.estimated_minutes} 分钟
                        </span>
                      </div>
                    </div>
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      className="text-gray-300 group-hover:text-lavender-500 transition mt-1"
                    >
                      <path d="M9 18l6-6-6-6" />
                    </svg>
                  </div>
                </button>
              ))}
            </div>

            {/* 底部历史按钮 */}
            <div className="text-center">
              <button
                onClick={openHistory}
                className="inline-flex items-center gap-2 px-8 py-3 rounded-full bg-white text-lavender-600 font-medium
                  shadow-lg shadow-lavender-100/50 border border-lavender-100 hover:bg-lavender-50 transition"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
                查看历史记录
              </button>
            </div>
          </>
        )}
      </main>

      {/* 历史记录弹窗 */}
      {showHistory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl w-full max-w-lg max-h-[80vh] flex flex-col shadow-2xl animate-scaleIn">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h3 className="text-lg font-bold text-gray-800">测评历史</h3>
              <button
                onClick={() => setShowHistory(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div className="overflow-y-auto p-6">
              {historyLoading ? (
                <div className="flex items-center justify-center py-12 text-gray-400">
                  <div className="w-6 h-6 border-2 border-lavender-200 border-t-lavender-500 rounded-full animate-spin mr-2" />
                  加载中...
                </div>
              ) : history.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="mx-auto mb-3 text-gray-300">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v6l4 2" />
                  </svg>
                  还没有测评记录
                </div>
              ) : (
                <div className="space-y-3">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-4 rounded-2xl bg-gray-50 hover:bg-lavender-50 transition"
                    >
                      <div>
                        <p className="font-medium text-gray-800">{item.scale_name}</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {new Date(item.created_at).toLocaleString('zh-CN')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-lavender-600">{item.total_score} 分</p>
                        <p className="text-xs text-gray-500">{item.interpretation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        .animate-scaleIn {
          animation: scaleIn 0.25s ease-out;
        }
      `}</style>
    </div>
  );
}
