import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const navigate = useNavigate();
  const { login, error, clearError } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setSubmitting(true);
    try {
      await login({ email, password });
      navigate('/', { replace: true });
    } catch {
      // error 已通过 useAuth 管理
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
    >
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8">
        {/* Logo / 标题 */}
        <div className="text-center mb-8">
          <div
            className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
            style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}
          >
            <span className="text-white text-2xl">🧠</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">欢迎回来</h1>
          <p className="text-gray-500 mt-1 text-sm">登录 MindMirror，继续你的心灵旅程</p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="space-y-4">
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              type="password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="输入密码"
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
            />
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
            {submitting ? '登录中...' : '登录'}
          </button>
        </form>

        {/* 注册链接 */}
        <p className="mt-6 text-center text-sm text-gray-500">
          还没有账号？{' '}
          <Link
            to="/register"
            className="font-semibold text-purple-600 hover:text-purple-700 transition"
          >
            立即注册
          </Link>
        </p>
      </div>
    </div>
  );
}
