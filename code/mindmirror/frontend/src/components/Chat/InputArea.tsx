import React, { useState, useRef, useEffect } from 'react';

interface InputAreaProps {
  onSend: (text: string) => void;
  isLoading: boolean;
  onMicClick?: () => void;
  onCameraClick?: () => void;
}

export default function InputArea({ onSend, isLoading, onMicClick, onCameraClick }: InputAreaProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 自动调整高度
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSend = () => {
    if (!text.trim() || isLoading) return;
    onSend(text);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className="px-4 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-t border-gray-100 dark:border-gray-700"
    >
      <div
        className="flex items-end gap-2 rounded-2xl bg-gray-50 dark:bg-gray-700/50 px-4 py-2"
        style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.04)' }}
      >
        {/* 摄像头按钮 */}
        <button
          onClick={onCameraClick}
          className="flex-shrink-0 p-2 rounded-xl text-gray-400 hover:text-lavender-500 hover:bg-lavender-50 dark:hover:bg-lavender-900/20 transition-all duration-200"
          title="视频情绪分析"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M23 7l-7 5 7 5V7z" />
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
          </svg>
        </button>

        {/* 文本输入 */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="说说你的心情吧..."
          rows={1}
          disabled={isLoading}
          className="flex-1 bg-transparent resize-none outline-none text-base text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 disabled:opacity-50 py-1"
          style={{ maxHeight: 120 }}
        />

        {/* 麦克风按钮 */}
        <button
          onClick={onMicClick}
          className="flex-shrink-0 p-2 rounded-xl text-gray-400 hover:text-lavender-500 hover:bg-lavender-50 dark:hover:bg-lavender-900/20 transition-all duration-200"
          title="语音输入"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </svg>
        </button>

        {/* 发送按钮 */}
        <button
          onClick={handleSend}
          disabled={!text.trim() || isLoading}
          className="flex-shrink-0 p-2 rounded-xl transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed"
          style={{
            background: text.trim() && !isLoading ? '#7C5CFC' : 'transparent',
            color: text.trim() && !isLoading ? 'white' : '#9CA3AF',
          }}
          title="发送"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>

      <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-2">
        Enter 发送 · Shift+Enter 换行
      </p>
    </div>
  );
}
