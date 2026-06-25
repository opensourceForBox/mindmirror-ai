import React from 'react';
import type { Expression } from '../../types';
import { EXPRESSION_LABELS } from '../../utils/constants';
import AvatarExpressions from './AvatarExpressions';

interface AvatarProps {
  expression: Expression;
  size?: number;
  className?: string;
}

export default function Avatar({ expression, size = 200, className = '' }: AvatarProps) {
  const scale = size / 200;
  const label = EXPRESSION_LABELS[expression];

  return (
    <div className={`flex flex-col items-center gap-2 ${className}`}>
      <div
        className="relative rounded-full overflow-hidden"
        style={{
          width: size,
          height: size,
          background: 'linear-gradient(135deg, #E8DDFF 0%, #FFF8F0 50%, #E8F4FD 100%)',
          boxShadow: '0 8px 32px rgba(124, 92, 252, 0.15), 0 2px 8px rgba(0,0,0,0.06)',
          transition: 'box-shadow 0.3s ease',
        }}
      >
        <svg
          viewBox="0 0 200 200"
          width={size}
          height={size}
          xmlns="http://www.w3.org/2000/svg"
          role="img"
          aria-label={`表情: ${label}`}
        >
          <defs>
            <radialGradient id="faceGradient" cx="50%" cy="40%" r="50%">
              <stop offset="0%" stopColor="#FFF8F0" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#FFE8D0" stopOpacity="0.1" />
            </radialGradient>
          </defs>

          <AvatarExpressions expression={expression} />
        </svg>

        {/* 思考中的光晕动画 */}
        {expression === 'thinking' && (
          <div
            className="absolute inset-0 rounded-full pointer-events-none"
            style={{
              background: 'radial-gradient(circle, rgba(124,92,252,0.08) 0%, transparent 70%)',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        )}
      </div>

      <span
        className="text-sm font-medium px-3 py-1 rounded-full"
        style={{
          background: 'rgba(124, 92, 252, 0.1)',
          color: '#7C5CFC',
          transition: 'all 0.3s ease',
        }}
      >
        {label}
      </span>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.05); }
        }
        @keyframes thumbBounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-5px); }
        }
      `}</style>
    </div>
  );
}
