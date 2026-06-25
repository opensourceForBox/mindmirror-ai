import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import EmotionTimeline from '../components/Parent/EmotionTimeline';
import AlertList from '../components/Parent/AlertList';
import {
  parentApi,
  type ChildInfo,
  type EmotionSummary,
  type AlertItem,
  type ProfileSummary,
  type MoodHistoryPoint,
} from '../services/parentApi';

export default function ParentDashboard() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  const [children, setChildren] = useState<ChildInfo[]>([]);
  const [selectedChildId, setSelectedChildId] = useState<number | null>(null);
  const [emotionSummary, setEmotionSummary] = useState<EmotionSummary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [profile, setProfile] = useState<ProfileSummary | null>(null);
  const [moodHistory, setMoodHistory] = useState<MoodHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 权限校验：仅家长可访问
  useEffect(() => {
    if (!isLoading && isAuthenticated && user?.role !== 'parent') {
      navigate('/', { replace: true });
    }
  }, [isLoading, isAuthenticated, user, navigate]);

  // 加载孩子列表
  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'parent') return;

    let cancelled = false;
    setLoading(true);

    parentApi
      .getChildren()
      .then((data) => {
        if (cancelled) return;
        setChildren(data);
        if (data.length > 0) {
          setSelectedChildId(data[0].id);
        }
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : '加载失败');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, user]);

  // 加载选中孩子的详细数据
  useEffect(() => {
    if (!selectedChildId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([
      parentApi.getEmotionSummary(selectedChildId),
      parentApi.getAlerts(selectedChildId),
      parentApi.getProfileSummary(selectedChildId),
      parentApi.getMoodHistory(selectedChildId),
    ])
      .then(([emotion, alertsData, profileData, mood]) => {
        if (cancelled) return;
        setEmotionSummary(emotion);
        setAlerts(alertsData);
        setProfile(profileData);
        setMoodHistory(mood);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : '加载孩子数据失败');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedChildId]);

  const handleMarkAlertRead = async (childId: number, alertId: number) => {
    try {
      await parentApi.markAlertRead(childId, alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, is_read: true } : a))
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : '标记已读失败');
    }
  };

  if (isLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-sky-50 to-emerald-50">
        <div className="text-lg font-medium text-slate-600">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-sky-50 to-emerald-50">
        <div className="rounded-2xl bg-white p-8 shadow-lg">
          <h1 className="mb-2 text-xl font-semibold text-slate-800">加载失败</h1>
          <p className="text-slate-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  const selectedChild = children.find((c) => c.id === selectedChildId);

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-emerald-50">
      {/* 顶部导航 */}
      <header className="sticky top-0 z-10 border-b border-white/50 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-emerald-500 text-white shadow-md">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">家长守护中心</h1>
              <p className="text-xs text-slate-500">MindMirror AI 家庭心理健康守护</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {children.length > 1 && (
              <div className="hidden items-center gap-2 md:flex">
                <span className="text-sm text-slate-500">选择孩子：</span>
                <select
                  value={selectedChildId ?? ''}
                  onChange={(e) => setSelectedChildId(Number(e.target.value))}
                  className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-sky-500 focus:outline-none"
                >
                  {children.map((child) => (
                    <option key={child.id} value={child.id}>
                      {child.username}
                    </option>
                  ))}
                </select>
              </div>
            )}
            <span className="text-sm text-slate-600">{user?.username}</span>
            <button
              onClick={() => navigate('/')}
              className="text-sm text-slate-500 hover:text-sky-600"
            >
              返回首页
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        {children.length === 0 ? (
          <div className="rounded-2xl bg-white p-8 text-center shadow-sm">
            <h2 className="text-lg font-medium text-slate-700">暂无绑定孩子</h2>
            <p className="mt-2 text-sm text-slate-500">
              您可以在个人设置中绑定孩子账号，开始守护孩子的心理健康。
            </p>
          </div>
        ) : (
          <>
            {/* 移动端孩子选择器 */}
            {children.length > 1 && (
              <div className="mb-4 md:hidden">
                <label className="mb-1 block text-sm text-slate-500">选择孩子</label>
                <select
                  value={selectedChildId ?? ''}
                  onChange={(e) => setSelectedChildId(Number(e.target.value))}
                  className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-sky-500 focus:outline-none"
                >
                  {children.map((child) => (
                    <option key={child.id} value={child.id}>
                      {child.username}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* 概览卡片 */}
            <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <SummaryCard
                title="近7天平均心情"
                value={
                  emotionSummary?.avg_mood !== null && emotionSummary?.avg_mood !== undefined
                    ? `${emotionSummary.avg_mood}/10`
                    : '--'
                }
                subtitle={trendText(emotionSummary?.mood_trend)}
                color="sky"
              />
              <SummaryCard
                title="近7天对话次数"
                value={emotionSummary?.conversation_count ?? 0}
                subtitle="主动倾诉是疗愈的开始"
                color="emerald"
              />
              <SummaryCard
                title="主导情绪"
                value={
                  emotionSummary?.dominant_emotions.length
                    ? emotionSummary.dominant_emotions.slice(0, 2).join('、')
                    : '暂无数据'
                }
                subtitle="基于对话情绪摘要"
                color="indigo"
              />
              <SummaryCard
                title="未读告警"
                value={alerts.filter((a) => !a.is_read).length}
                subtitle="建议及时关注"
                color={alerts.some((a) => !a.is_read) ? 'rose' : 'slate'}
              />
            </div>

            {/* 主内容区 */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              {/* 左侧：情绪趋势 + 心理档案 */}
              <div className="space-y-6 lg:col-span-2">
                <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100">
                  <EmotionTimeline
                    data={moodHistory}
                    childName={selectedChild?.username}
                    height={260}
                  />
                </section>

                <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100">
                  <h2 className="mb-4 text-lg font-semibold text-slate-800">
                    心理档案摘要
                  </h2>
                  {profile ? (
                    <div className="grid gap-4 sm:grid-cols-2">
                      <InfoRow label="性格特点" value={profile.personality_summary} />
                      <InfoRow
                        label="关注议题"
                        value={
                          profile.active_issues.length
                            ? profile.active_issues.join('、')
                            : '暂无持续关注议题'
                        }
                      />
                      <InfoRow
                        label="兴趣爱好"
                        value={
                          profile.interests.length
                            ? profile.interests.join('、')
                            : '暂无记录'
                        }
                      />
                      <InfoRow
                        label="偏好应对方式"
                        value={
                          (profile.coping_styles?.preferred as string) || '暂无记录'
                        }
                      />
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">暂无档案数据</p>
                  )}
                </section>
              </div>

              {/* 右侧：告警列表 */}
              <div className="space-y-6">
                <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100">
                  <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-slate-800">风险告警</h2>
                    {alerts.some((a) => !a.is_read) && (
                      <span className="rounded-full bg-rose-100 px-2 py-0.5 text-xs font-medium text-rose-600">
                        {alerts.filter((a) => !a.is_read).length} 条未读
                      </span>
                    )}
                  </div>
                  <AlertList
                    alerts={alerts}
                    childId={selectedChildId ?? 0}
                    onMarkRead={handleMarkAlertRead}
                  />
                </section>

                <section className="rounded-2xl bg-gradient-to-br from-sky-500 to-emerald-500 p-5 text-white shadow-md">
                  <h3 className="mb-2 font-semibold">给家长的建议</h3>
                  <ul className="space-y-2 text-sm leading-relaxed opacity-95">
                    <li>• 保持开放、非评判的沟通态度</li>
                    <li>• 关注孩子的情绪变化而非只问成绩</li>
                    <li>• 如发现危机信号，请第一时间陪伴并寻求专业帮助</li>
                    <li>• 尊重孩子隐私，对话内容仅显示摘要</li>
                  </ul>
                </section>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function SummaryCard({
  title,
  value,
  subtitle,
  color,
}: {
  title: string;
  value: React.ReactNode;
  subtitle: string;
  color: 'sky' | 'emerald' | 'indigo' | 'rose' | 'slate';
}) {
  const colorClasses = {
    sky: 'from-sky-50 to-sky-100 text-sky-700',
    emerald: 'from-emerald-50 to-emerald-100 text-emerald-700',
    indigo: 'from-indigo-50 to-indigo-100 text-indigo-700',
    rose: 'from-rose-50 to-rose-100 text-rose-700',
    slate: 'from-slate-50 to-slate-100 text-slate-700',
  };

  return (
    <div className={`rounded-2xl bg-gradient-to-br p-5 shadow-sm ${colorClasses[color]}`}>
      <p className="text-sm font-medium opacity-80">{title}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
      <p className="mt-1 text-xs opacity-70">{subtitle}</p>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4">
      <p className="mb-1 text-xs font-medium text-slate-400">{label}</p>
      <p className="text-sm font-medium text-slate-700">{value}</p>
    </div>
  );
}

function trendText(trend?: 'improving' | 'stable' | 'declining') {
  switch (trend) {
    case 'improving':
      return '心情呈上升趋势';
    case 'declining':
      return '心情呈下降趋势';
    default:
      return '心情相对平稳';
  }
}
