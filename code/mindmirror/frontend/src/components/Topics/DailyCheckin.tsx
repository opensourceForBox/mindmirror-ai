import React, { useState, useEffect } from 'react';
import { topicsApi, type CheckinResponse, type TodayCheckinStatus } from '../../services/api';

interface DailyCheckinProps {
  onCheckinComplete?: (result: CheckinResponse) => void;
}

const MOOD_OPTIONS = [
  { score: 1, emoji: '😢', label: '很差' },
  { score: 2, emoji: '😟', label: '不太好' },
  { score: 3, emoji: '😐', label: '一般' },
  { score: 4, emoji: '😊', label: '不错' },
  { score: 5, emoji: '😄', label: '很好' },
];

export default function DailyCheckin({ onCheckinComplete }: DailyCheckinProps) {
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<CheckinResponse | null>(null);
  const [todayStatus, setTodayStatus] = useState<TodayCheckinStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 检查今日是否已签到
  useEffect(() => {
    topicsApi.getTodayStatus()
      .then(setTodayStatus)
      .catch(() => {/* 未登录则忽略 */});
  }, []);

  const handleSubmit = async () => {
    if (selectedMood === null) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await topicsApi.checkin(selectedMood, note.trim() || undefined);
      setResult(res);
      onCheckinComplete?.(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : '签到失败，请稍后再试');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 已签到状态
  if (todayStatus?.checked_in || result) {
    const streakDays = result?.streak_days ?? todayStatus?.streak_days ?? 0;
    const mood = result?.mood_score ?? todayStatus?.mood_score;
    const moodEmoji = MOOD_OPTIONS.find((m) => m.score === mood)?.emoji ?? '✨';
    return (
      <div className="rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-100 p-6 text-center shadow-sm">
        <div className="text-4xl mb-2">{moodEmoji}</div>
        <h3 className="text-lg font-semibold text-amber-800 mb-1">今日已签到</h3>
        {streakDays > 0 && (
          <p className="text-sm text-amber-600">
            已连续签到 <span className="font-bold text-amber-700">{streakDays}</span> 天
          </p>
        )}
        {result?.message && (
          <p className="mt-2 text-sm text-amber-700 italic">{result.message}</p>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-100 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-purple-800 mb-1 text-center">
        今日心情签到
      </h3>
      <p className="text-sm text-purple-500 mb-4 text-center">
        记录此刻的心情，开启美好的一天
      </p>

      {/* 情绪表情选择 */}
      <div className="flex justify-center gap-3 mb-4">
        {MOOD_OPTIONS.map(({ score, emoji, label }) => (
          <button
            key={score}
            onClick={() => setSelectedMood(score)}
            className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-all duration-200 ${
              selectedMood === score
                ? 'bg-white shadow-md scale-110 ring-2 ring-purple-300'
                : 'hover:bg-white/60 hover:scale-105'
            }`}
            title={label}
          >
            <span className="text-3xl">{emoji}</span>
            <span className="text-xs text-purple-600">{label}</span>
          </button>
        ))}
      </div>

      {/* 可选文字输入 */}
      <input
        type="text"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="一句话描述此刻的心情（可选）"
        maxLength={500}
        className="w-full rounded-xl border border-purple-200 bg-white/70 px-4 py-2 text-sm text-purple-800 placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-300 mb-4"
      />

      {/* 签到按钮 */}
      <button
        onClick={handleSubmit}
        disabled={selectedMood === null || isSubmitting}
        className="w-full rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 py-2.5 text-white font-medium shadow-sm transition-all duration-200 hover:shadow-md hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSubmitting ? '签到中...' : '签到 ✨'}
      </button>

      {error && (
        <p className="mt-2 text-sm text-red-500 text-center">{error}</p>
      )}
    </div>
  );
}
