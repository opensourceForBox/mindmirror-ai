import React, { useEffect, useState } from 'react';
import { assessmentApi } from '../../services/assessmentApi';
import ResultChart from './ResultChart';
import type { ScaleDetail, AssessmentResult, AssessmentHistoryItem } from '../../types/assessment';

interface ScaleFormProps {
  scaleType: string;
  onBack: () => void;
}

export default function ScaleForm({ scaleType, onBack }: ScaleFormProps) {
  const [scale, setScale] = useState<ScaleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [direction, setDirection] = useState<'next' | 'prev'>('next');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [history, setHistory] = useState<AssessmentHistoryItem[] | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    assessmentApi
      .getScaleDetail(scaleType)
      .then((data) => {
        if (!cancelled) {
          setScale(data);
          setAnswers(new Array(data.questions.length).fill(-1));
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : '加载量表失败');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [scaleType]);

  const handleAnswer = async (value: number) => {
    if (!scale || submitting) return;
    const newAnswers = [...answers];
    newAnswers[currentIndex] = value;
    setAnswers(newAnswers);

    if (currentIndex === scale.questions.length - 1) {
      setSubmitting(true);
      try {
        const data = await assessmentApi.submit({
          scale_type: scaleType,
          answers: newAnswers,
        });
        setResult(data);
        setHistoryLoading(true);
        assessmentApi
          .getHistory(1, 20)
          .then((res) => {
            setHistory(
              res.items
                .filter((item) => item.scale_type === scaleType)
                .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
            );
          })
          .catch(() => setHistory([]))
          .finally(() => setHistoryLoading(false));
      } catch (e) {
        setError(e instanceof Error ? e.message : '提交失败');
      } finally {
        setSubmitting(false);
      }
    } else {
      setDirection('next');
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setDirection('prev');
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleRestart = () => {
    setCurrentIndex(0);
    setAnswers(new Array(scale?.questions.length ?? 0).fill(-1));
    setResult(null);
    setHistory(null);
    setError(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-lavender-50 to-warm-50">
        <div className="text-lavender-600 text-lg font-medium animate-pulse">加载量表中...</div>
      </div>
    );
  }

  if (error && !scale) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-lavender-50 to-warm-50 p-6">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-red-50 flex items-center justify-center text-red-500">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">出错了</h3>
          <p className="text-gray-500 mb-6">{error}</p>
          <button
            onClick={onBack}
            className="px-6 py-2 rounded-xl bg-lavender-500 text-white font-medium hover:bg-lavender-600 transition"
          >
            返回量表列表
          </button>
        </div>
      </div>
    );
  }

  if (!scale) return null;

  if (result) {
    return (
      <ResultChart
        result={result}
        scaleName={scale.title}
        history={history}
        historyLoading={historyLoading}
        onBack={handleRestart}
      />
    );
  }

  const currentQuestion = scale.questions[currentIndex];
  const progress = ((currentIndex + 1) / scale.questions.length) * 100;
  const answeredCount = answers.filter((a) => a >= 0).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-lavender-50 via-white to-warm-50 p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        {/* 顶部导航 */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onBack}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-lavender-600 transition"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 18l-6-6 6-6" />
            </svg>
            返回列表
          </button>
          <span className="text-sm text-gray-400">
            {scale.title} · 第 {currentIndex + 1} / {scale.questions.length} 题
          </span>
        </div>

        {/* 进度区域 */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg shadow-lavender-100/50 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-lavender-700">测评进度</span>
            <span className="text-sm text-gray-400">{Math.round(progress)}%</span>
          </div>
          <div className="h-2.5 bg-lavender-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-lavender-400 to-lavender-600 rounded-full"
              style={{ width: `${progress}%`, transition: 'width 0.4s ease' }}
            />
          </div>
        </div>

        {/* 题目卡片 */}
        <div
          key={currentIndex}
          className={`bg-white rounded-3xl p-6 md:p-10 shadow-xl shadow-lavender-100/50 ${
            direction === 'next' ? 'animate-fadeInRight' : 'animate-fadeInLeft'
          }`}
        >
          <div className="mb-8">
            <span className="inline-block px-3 py-1 rounded-full bg-lavender-50 text-lavender-600 text-xs font-medium mb-4">
              问题 {currentQuestion.id}
            </span>
            <h2 className="text-xl md:text-2xl font-semibold text-gray-800 leading-relaxed">
              {currentQuestion.text}
            </h2>
            <p className="text-sm text-gray-400 mt-3">请选择最符合你最近状态的选项</p>
          </div>

          {/* 选项 */}
          <div className="space-y-3">
            {scale.options.map((opt, idx) => {
              const selected = answers[currentIndex] === opt.value;
              return (
                <button
                  key={opt.value}
                  onClick={() => handleAnswer(opt.value)}
                  disabled={submitting}
                  className={`w-full text-left px-5 py-4 rounded-2xl text-base transition-all duration-200 border-2 flex items-center gap-4
                    ${
                      selected
                        ? 'bg-lavender-50 border-lavender-500 text-lavender-800 shadow-md'
                        : 'bg-gray-50 border-transparent text-gray-700 hover:bg-lavender-50/60 hover:border-lavender-200'
                    }`}
                  style={{ animationDelay: `${idx * 60}ms` }}
                >
                  <span
                    className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold transition
                    ${selected ? 'bg-lavender-500 text-white' : 'bg-white text-gray-400 border border-gray-200'}`}
                  >
                    {String.fromCharCode(65 + idx)}
                  </span>
                  <span className="flex-1">{opt.label}</span>
                  {selected && (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-lavender-500">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </button>
              );
            })}
          </div>

          {/* 底部操作 */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-100">
            <button
              onClick={handlePrev}
              disabled={currentIndex === 0}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition
                ${
                  currentIndex === 0
                    ? 'text-gray-300 cursor-not-allowed'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              上一题
            </button>
            <span className="text-sm text-gray-400">
              已答 {answeredCount} / {scale.questions.length} 题
            </span>
          </div>
        </div>
      </div>

      {submitting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm">
          <div className="bg-white rounded-2xl px-8 py-6 shadow-2xl flex flex-col items-center">
            <div className="w-10 h-10 border-3 border-lavender-200 border-t-lavender-500 rounded-full animate-spin mb-3" />
            <p className="text-gray-600 font-medium">正在生成结果...</p>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeInRight {
          from { opacity: 0; transform: translateX(24px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeInLeft {
          from { opacity: 0; transform: translateX(-24px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-fadeInRight {
          animation: fadeInRight 0.35s ease-out;
        }
        .animate-fadeInLeft {
          animation: fadeInLeft 0.35s ease-out;
        }
      `}</style>
    </div>
  );
}
