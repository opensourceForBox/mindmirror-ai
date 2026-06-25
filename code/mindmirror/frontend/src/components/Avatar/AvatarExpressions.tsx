import React from 'react';
import type { Expression } from '../../types';

interface AvatarExpressionsProps {
  expression: Expression;
}

// 眼睛组件
function Eyes({ expression }: { expression: Expression }) {
  const isThinking = expression === 'thinking';
  const isHappy = expression === 'happy' || expression === 'encouraging';
  const isConcerned = expression === 'concerned';

  return (
    <g className="avatar-eyes" style={{ transition: 'all 0.3s ease' }}>
      {/* 左眼 */}
      {isThinking ? (
        // 闭眼 - 弧线
        <path
          d="M 65 105 Q 75 100 85 105"
          fill="none"
          stroke="#4A3B6B"
          strokeWidth="3"
          strokeLinecap="round"
        />
      ) : (
        <g>
          <ellipse cx="75" cy="105" rx={isHappy ? 10 : 12} ry={isHappy ? 7 : 12} fill="#4A3B6B" />
          {!isHappy && <circle cx="78" cy="101" r="4" fill="white" opacity="0.8" />}
          {isHappy && (
            <path
              d="M 65 103 Q 75 97 85 103"
              fill="none"
              stroke="#4A3B6B"
              strokeWidth="3"
              strokeLinecap="round"
            />
          )}
        </g>
      )}

      {/* 右眼 */}
      {isThinking ? (
        <path
          d="M 115 105 Q 125 100 135 105"
          fill="none"
          stroke="#4A3B6B"
          strokeWidth="3"
          strokeLinecap="round"
        />
      ) : (
        <g>
          <ellipse cx="125" cy="105" rx={isHappy ? 10 : 12} ry={isHappy ? 7 : 12} fill="#4A3B6B" />
          {!isHappy && <circle cx="128" cy="101" r="4" fill="white" opacity="0.8" />}
          {isHappy && (
            <path
              d="M 115 103 Q 125 97 135 103"
              fill="none"
              stroke="#4A3B6B"
              strokeWidth="3"
              strokeLinecap="round"
            />
          )}
        </g>
      )}

      {/* 担忧眉毛 */}
      {isConcerned && (
        <g>
          <path d="M 62 88 Q 75 93 88 90" fill="none" stroke="#6B5B8D" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M 112 90 Q 125 93 138 88" fill="none" stroke="#6B5B8D" strokeWidth="2.5" strokeLinecap="round" />
        </g>
      )}

      {/* 同理心微皱眉 */}
      {expression === 'empathy' && (
        <g>
          <path d="M 64 90 Q 75 87 86 90" fill="none" stroke="#6B5B8D" strokeWidth="2" strokeLinecap="round" />
          <path d="M 114 90 Q 125 87 136 90" fill="none" stroke="#6B5B8D" strokeWidth="2" strokeLinecap="round" />
        </g>
      )}
    </g>
  );
}

// 嘴巴组件
function Mouth({ expression }: { expression: Expression }) {
  const isHappy = expression === 'happy';
  const isEncouraging = expression === 'encouraging';
  const isConcerned = expression === 'concerned';
  const isEmpathy = expression === 'empathy';
  const isThinking = expression === 'thinking';

  return (
    <g className="avatar-mouth" style={{ transition: 'all 0.3s ease' }}>
      {isHappy && (
        // 开心 - 大微笑
        <path
          d="M 75 140 Q 100 165 125 140"
          fill="none"
          stroke="#E87B9F"
          strokeWidth="3"
          strokeLinecap="round"
        />
      )}

      {isEncouraging && (
        // 鼓励 - 大笑张嘴
        <g>
          <path
            d="M 75 135 Q 100 170 125 135"
            fill="#FFB6C8"
            stroke="#E87B9F"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <path
            d="M 82 135 Q 100 138 118 135"
            fill="none"
            stroke="white"
            strokeWidth="3"
            strokeLinecap="round"
          />
        </g>
      )}

      {isConcerned && (
        // 担忧 - 微向下
        <path
          d="M 80 148 Q 100 142 120 148"
          fill="none"
          stroke="#D4849E"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
      )}

      {isEmpathy && (
        // 同理心 - 微皱+微笑
        <path
          d="M 78 142 Q 100 155 122 142"
          fill="none"
          stroke="#E87B9F"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
      )}

      {isThinking && (
        // 思考 - 小圆圈嘴
        <ellipse cx="100" cy="145" rx="6" ry="5" fill="#E87B9F" />
      )}

      {expression === 'neutral' && (
        // 默认 - 温暖微笑
        <path
          d="M 80 142 Q 100 158 120 142"
          fill="none"
          stroke="#E87B9F"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
      )}
    </g>
  );
}

// 腮红
function Blush({ expression }: { expression: Expression }) {
  const show = expression === 'happy' || expression === 'encouraging' || expression === 'empathy';
  return show ? (
    <g style={{ transition: 'opacity 0.3s ease' }}>
      <ellipse cx="60" cy="130" rx="12" ry="8" fill="#FFB6C8" opacity="0.4" />
      <ellipse cx="140" cy="130" rx="12" ry="8" fill="#FFB6C8" opacity="0.4" />
    </g>
  ) : null;
}

// 鼓励手势 - 竖拇指
function ThumbUp() {
  return (
    <g className="avatar-thumb" style={{ animation: 'thumbBounce 0.6s ease-in-out infinite' }}>
      <circle cx="170" cy="170" r="14" fill="#FFF0D4" stroke="#E8C97A" strokeWidth="1.5" />
      <rect x="166" y="150" width="8" height="20" rx="4" fill="#FFF0D4" stroke="#E8C97A" strokeWidth="1.5" />
      <path d="M 160 170 L 180 170" stroke="#E8C97A" strokeWidth="1" opacity="0.5" />
    </g>
  );
}

// 点头动画（thinking时）
function NoddingHead() {
  return (
    <style>{`
      .avatar-head-group {
        animation: nodAnim 1.2s ease-in-out infinite;
        transform-origin: 100px 180px;
      }
      @keyframes nodAnim {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(4px); }
      }
    `}</style>
  );
}

export default function AvatarExpressions({ expression }: AvatarExpressionsProps) {
  const isThinking = expression === 'thinking';
  const isEncouraging = expression === 'encouraging';

  return (
    <g className={isThinking ? 'avatar-head-group' : ''}>
      {isThinking && <NoddingHead />}

      {/* 脸部背景 - 圆润脸型 */}
      <ellipse cx="100" cy="115" rx="65" ry="68" fill="#FFF0E0" />
      <ellipse cx="100" cy="115" rx="65" ry="68" fill="url(#faceGradient)" />

      {/* 头发 */}
      <path
        d="M 35 90 Q 40 40 100 35 Q 160 40 165 90 Q 165 70 150 60 Q 130 48 100 45 Q 70 48 50 60 Q 35 70 35 90"
        fill="#7C5CFC"
      />
      {/* 刘海 */}
      <path
        d="M 50 75 Q 60 65 75 72 Q 85 62 100 68 Q 115 62 125 72 Q 140 65 150 75"
        fill="#9B7DFC"
      />

      {/* 耳朵 */}
      <ellipse cx="38" cy="115" rx="10" ry="14" fill="#FFE8D0" />
      <ellipse cx="162" cy="115" rx="10" ry="14" fill="#FFE8D0" />

      <Eyes expression={expression} />
      <Mouth expression={expression} />
      <Blush expression={expression} />

      {/* 鼓励手势 */}
      {isEncouraging && <ThumbUp />}
    </g>
  );
}
