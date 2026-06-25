import React, { useState, useRef, useEffect } from 'react';

interface InputAreaProps {
  onSend: (text: string) => void;
  isLoading: boolean;
  onMicClick?: () => void;
  onCameraClick?: () => void;
  isCameraActive?: boolean;
  isCameraConnecting?: boolean;
  isMicActive?: boolean;
  videoRef?: React.RefObject<HTMLVideoElement>;
  cameraError?: string | null;
  micError?: string | null;
}

export default function InputArea({
  onSend,
  isLoading,
  onMicClick,
  onCameraClick,
  isCameraActive = false,
  isCameraConnecting = false,
  isMicActive = false,
  videoRef,
  cameraError,
  micError,
}: InputAreaProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showPreview, setShowPreview] = useState(false);

  // 自动调整高度
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    }
  }, [text]);

  // 摄像头激活时自动显示预览
  useEffect(() => {
    setShowPreview(isCameraActive);
  }, [isCameraActive]);

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

  // 错误提示（优先显示摄像头错误）
  const displayError = cameraError || micError;

  return (
    <div className="relative">
      {/* 摄像头预览小窗 */}
      {showPreview && isCameraActive && (
        <div
          className="absolute bottom-full mb-2 right-4 rounded-2xl overflow-hidden shadow-lg border border-white/40 dark:border-gray-600"
          style={{ width: 180, height: 135, background: '#000' }}
        >
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ transform: 'scaleX(-1)' }} // 镜像显示
          />
          {/* 关闭预览按钮 */}
          <button
            onClick={() => setShowPreview(false)}
            className="absolute top-1 right-1 w-5 h-5 rounded-full bg-black/50 text-white flex items-center justify-center text-xs hover:bg-black/70 transition-colors"
            title="关闭预览"
          >
            ×
          </button>
          {/* 录制中指示器 */}
          <div className="absolute bottom-1 left-1 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-white text-[10px] font-medium drop-shadow">分析中</span>
          </div>
        </div>
      )}

      {/* 错误提示条 */}
      {displayError && (
        <div className="mx-4 mb-1 px-3 py-1.5 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-100 dark:border-red-800 text-red-600 dark:text-red-400 text-xs">
          {displayError}
        </div>
      )}

      <div className="px-4 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-t border-gray-100 dark:border-gray-700">
        <div
          className="flex items-end gap-2 rounded-2xl bg-gray-50 dark:bg-gray-700/50 px-4 py-2"
          style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.04)' }}
        >
          {/* 摄像头按钮 */}
          <button
            onClick={onCameraClick}
            disabled={isCameraConnecting}
            className={[
              'flex-shrink-0 p-2 rounded-xl transition-all duration-200',
              isCameraConnecting
                ? 'text-lavender-400 cursor-wait animate-pulse'
                : isCameraActive
                ? 'text-red-500 bg-red-50 dark:bg-red-900/30 ring-2 ring-red-400 dark:ring-red-500'
                : 'text-gray-400 hover:text-lavender-500 hover:bg-lavender-50 dark:hover:bg-lavender-900/20',
            ].join(' ')}
            title={isCameraActive ? '关闭摄像头' : '开启视频情绪分析'}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {isCameraActive ? (
                <>
                  {/* 激活状态：带斜线的摄像头图标 */}
                  <path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h2m5.66 0H14a2 2 0 0 1 2 2v3.34l1 1L23 7v10" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </>
              ) : (
                <>
                  <path d="M23 7l-7 5 7 5V7z" />
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
                </>
              )}
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
            className={[
              'flex-shrink-0 p-2 rounded-xl transition-all duration-200 relative',
              isMicActive
                ? 'text-red-500 bg-red-50 dark:bg-red-900/30 ring-2 ring-red-400 dark:ring-red-500'
                : 'text-gray-400 hover:text-lavender-500 hover:bg-lavender-50 dark:hover:bg-lavender-900/20',
            ].join(' ')}
            title={isMicActive ? '停止录音' : '开始语音情绪分析'}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
            {/* 录音中脉冲动画 */}
            {isMicActive && (
              <span
                className="absolute inset-0 rounded-xl animate-ping opacity-20"
                style={{ background: '#EF4444' }}
              />
            )}
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

        {/* 底部状态提示 */}
        <div className="flex items-center justify-between mt-2 px-1">
          <p className="text-xs text-gray-400 dark:text-gray-500">
            Enter 发送 · Shift+Enter 换行
          </p>
          {/* 活跃状态标签 */}
          <div className="flex items-center gap-2">
            {isCameraActive && (
              <span className="flex items-center gap-1 text-xs text-red-500 dark:text-red-400">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                摄像头
              </span>
            )}
            {isMicActive && (
              <span className="flex items-center gap-1 text-xs text-red-500 dark:text-red-400">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                录音中
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
