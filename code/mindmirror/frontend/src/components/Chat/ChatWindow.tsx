import React, { useRef, useEffect } from 'react';
import type { Message, Expression } from '../../types';
import MessageBubble from './MessageBubble';
import Avatar from '../Avatar/Avatar';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  currentExpression: Expression;
}

export default function ChatWindow({ messages, isLoading, currentExpression }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-2 py-4 space-y-1">
      {/* 欢迎区域 */}
      {messages.length <= 1 && (
        <div className="flex flex-col items-center py-6 text-center">
          <div className="w-16 h-1 rounded-full bg-lavender-200 dark:bg-lavender-700 mb-4" />
          <p className="text-sm text-gray-400 dark:text-gray-500">
            今天的心情，从这里开始
          </p>
        </div>
      )}

      {/* 消息列表 */}
      {messages.map((msg, idx) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          isLatest={idx === messages.length - 1}
        />
      ))}

      {/* 加载状态 */}
      {isLoading && (
        <div className="flex gap-3 px-4 py-2" style={{ animation: 'fadeSlideIn 0.3s ease-out' }}>
          <div className="flex-shrink-0 mt-1">
            <Avatar expression="thinking" size={40} />
          </div>
          <div
            className="px-4 py-3 bg-white dark:bg-gray-800 rounded-2xl rounded-bl-md"
            style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
          >
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 bg-lavender-400 rounded-full" style={{ animation: 'dotPulse 1.4s ease-in-out 0s infinite' }} />
              <span className="w-2 h-2 bg-lavender-400 rounded-full" style={{ animation: 'dotPulse 1.4s ease-in-out 0.2s infinite' }} />
              <span className="w-2 h-2 bg-lavender-400 rounded-full" style={{ animation: 'dotPulse 1.4s ease-in-out 0.4s infinite' }} />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />

      <style>{`
        @keyframes dotPulse {
          0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1.2); }
        }
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
