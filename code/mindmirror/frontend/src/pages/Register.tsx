import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Register() {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuth();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState<'child' | 'parent'>('child');
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);

    if (password !== confirmPassword) {
      setLocalError('两次输入的密码不一致');
      return;
    }
    if (password.length < 6) {
      setLocalError('密码长度至少为 6 位');
      return;
    }

    setSubmitting(true);
    try {
      await register({ username, email, password, role });
      navigate('/', { replace: true });
    } catch {
      // error 已通过 useAuth 管理
    } finally {
      setSubmitting(false);
    }
  };

  const displayError = localError || error;

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 py-8"
      style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
    >
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8">
        {/* Logo / 标题 */}
        <div className="text-center mb-8">
          <div
            className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
            style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}
          >
            <span className="text-white text-2xl">✨</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">创建账号</h1>
          <p className="text-gray-500 mt-1 text-sm">加入 MindMirror，开启心灵健康之旅</p>
        </div>

        {/* 错误提示 */}
        {displayError && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">
            {displayError}
          </div>
        )}

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 用户名 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              type="text"
              required
              minLength={2}
              maxLength={50}
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="你的名字"
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
            />
          </div>

          {/* 邮箱 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
            />
          </div>

          {/* 密码 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="至少 6 位"
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
            />
          </div>

          {/* 确认密码 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="再次输入密码"
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
            />
          </div>

          {/* 角色选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">我是</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setRole('child')}
                className="rounded-lg border-2 py-3 text-sm font-medium transition-all duration-200"
                style={{
                  borderColor: role === 'child' ? '#764ba2' : '#e5e7eb',
                  background: role === 'child' ? 'rgba(118,75,162,0.08)' : 'white',
                  color: role === 'child' ? '#764ba2' : '#6b7280',
                }}
              >
                🧒 孩子
                <span className="block text-xs mt-0.5 opacity-70">我想找人聊天</span>
              </button>
              <button
                type="button"
                onClick={() => setRole('parent')}
                className="rounded-lg border-2 py-3 text-sm font-medium transition-all duration-200"
                style={{
                  borderColor: role === 'parent' ? '#764ba2' : '#e5e7eb',
                  background: role === 'parent' ? 'rgba(118,75,162,0.08)' : 'white',
                  color: role === 'parent' ? '#764ba2' : '#6b7280',
                }}
              >
                👨‍👩‍👧 家长
                <span className="block text-xs mt-0.5 opacity-70">关注孩子心理健康</span>
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg py-3 text-white font-semibold text-sm transition-all duration-200 disabled:opacity-60"
            style={{
              background: submitting ? '#a78bfa' : 'linear-gradient(135deg, #667eea, #764ba2)',
              cursor: submitting ? 'not-allowed' : 'pointer',
            }}
          >
            {submitting ? '注册中...' : '注册'}
          </button>
        </form>

        {/* 登录链接 */}
        <p className="mt-6 text-center text-sm text-gray-500">
          已有账号？{' '}
          <Link
            to="/login"
            className="font-semibold text-purple-600 hover:text-purple-700 transition"
          >
            立即登录
          </Link>
        </p>
      </div>
    </div>
  );
}
