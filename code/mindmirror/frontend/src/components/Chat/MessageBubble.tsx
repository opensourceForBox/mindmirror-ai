import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { Message } from '../../types';
import Avatar from '../Avatar/Avatar';

interface MessageBubbleProps {
  message: Message;
  isLatest: boolean;
}

export default function MessageBubble({ message, isLatest }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-3 px-4 py-2 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
      style={{ animation: 'fadeSlideIn 0.3s ease-out' }}
    >
      {/* 头像 */}
      {!isUser && (
        <div className="flex-shrink-0 mt-1">
          <Avatar expression="neutral" size={40} />
        </div>
      )}

      {/* 消息气泡 */}
      <div
        className={`
          max-w-[75%] px-4 py-3 text-base leading-relaxed
          ${isUser
            ? 'bg-lavender-500 text-white rounded-2xl rounded-br-md'
            : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 rounded-2xl rounded-bl-md'
          }
        `}
        style={{
          boxShadow: isUser
            ? '0 2px 8px rgba(124, 92, 252, 0.2)'
            : '0 2px 8px rgba(0, 0, 0, 0.06)',
        }}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc pl-5 mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal pl-5 mb-2">{children}</ol>,
                strong: ({ children }) => <strong className="font-semibold text-lavender-600 dark:text-lavender-400">{children}</strong>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* 时间戳 */}
      <span className="self-end text-xs text-gray-400 dark:text-gray-500 flex-shrink-0 mb-1">
        {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </span>

      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
