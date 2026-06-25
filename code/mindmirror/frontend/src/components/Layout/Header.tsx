import React from 'react';

interface HeaderProps {
  onAssessmentClick?: () => void;
}

export default function Header({ onAssessmentClick }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 py-3 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-100 dark:border-gray-700">
      {/* Logo & Title */}
      <div className="flex items-center gap-3">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: 'linear-gradient(135deg, #7C5CFC, #A177FF)' }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12" />
            <path d="M12 6v6l4 2" />
            <circle cx="12" cy="12" r="3" fill="white" opacity="0.3" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-bold text-gray-800 dark:text-gray-100">
            MindMirror AI
          </h1>
          <p className="text-xs text-gray-400 dark:text-gray-500 -mt-0.5">
            你的心理健康伙伴
          </p>
        </div>
      </div>

      {/* 右侧操作区 */}
      <div className="flex items-center gap-2">
        {onAssessmentClick && (
          <button
            onClick={onAssessmentClick}
            className="px-3 py-1.5 rounded-xl text-sm font-medium
              bg-lavender-50 dark:bg-lavender-900/20 text-lavender-600 dark:text-lavender-400
              hover:bg-lavender-100 dark:hover:bg-lavender-900/30
              transition-colors duration-200"
          >
            快速评估
          </button>
        )}

        {/* 健康指示灯 */}
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-green-50 dark:bg-green-900/20">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-green-600 dark:text-green-400">在线</span>
        </div>
      </div>
    </header>
  );
}
