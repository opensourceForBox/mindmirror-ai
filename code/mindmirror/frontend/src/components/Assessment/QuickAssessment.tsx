import React, { useState } from 'react';

interface AssessmentQuestion {
  id: string;
  text: string;
  options: { label: string; value: number }[];
}

interface QuickAssessmentProps {
  onComplete?: (results: { score: number; answers: Record<string, number> }) => void;
  onClose?: () => void;
}

const QUESTIONS: AssessmentQuestion[] = [
  {
    id: 'mood',
    text: '过去一周，你的整体心情如何？',
    options: [
      { label: '很好，精力充沛', value: 4 },
      { label: '还不错', value: 3 },
      { label: '一般般', value: 2 },
      { label: '有些低落', value: 1 },
      { label: '很糟糕', value: 0 },
    ],
  },
  {
    id: 'sleep',
    text: '你的睡眠质量怎么样？',
    options: [
      { label: '睡得很好', value: 4 },
      { label: '偶尔失眠', value: 3 },
      { label: '经常睡不好', value: 2 },
      { label: '很难入睡', value: 1 },
      { label: '几乎不睡', value: 0 },
    ],
  },
  {
    id: 'stress',
    text: '学习或生活压力大吗？',
    options: [
      { label: '没什么压力', value: 4 },
      { label: '有一点，能应对', value: 3 },
      { label: '比较大', value: 2 },
      { label: '压力很大', value: 1 },
      { label: '快承受不了了', value: 0 },
    ],
  },
  {
    id: 'social',
    text: '和朋友/家人的关系如何？',
    options: [
      { label: '很融洽', value: 4 },
      { label: '还行', value: 3 },
      { label: '有些摩擦', value: 2 },
      { label: '关系紧张', value: 1 },
      { label: '很孤独', value: 0 },
    ],
  },
];

export default function QuickAssessment({ onComplete, onClose }: QuickAssessmentProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});

  const current = QUESTIONS[currentIndex];
  const isLast = currentIndex === QUESTIONS.length - 1;
  const progress = ((currentIndex) / QUESTIONS.length) * 100;

  const handleAnswer = (value: number) => {
    const newAnswers = { ...answers, [current.id]: value };
    setAnswers(newAnswers);

    if (isLast) {
      const totalScore = Object.values(newAnswers).reduce((a, b) => a + b, 0);
      onComplete?.({ score: totalScore, answers: newAnswers });
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4">
      <div
        className="bg-white dark:bg-gray-800 rounded-3xl w-full max-w-md p-6 shadow-2xl"
        style={{ animation: 'scaleIn 0.3s ease-out' }}
      >
        {/* 关闭按钮 */}
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
            快速心理评估
          </h3>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          )}
        </div>

        {/* 进度条 */}
        <div className="h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full mb-6 overflow-hidden">
          <div
            className="h-full bg-lavender-500 rounded-full"
            style={{ width: `${progress}%`, transition: 'width 0.3s ease' }}
          />
        </div>

        {/* 问题 */}
        <p className="text-base text-gray-700 dark:text-gray-200 mb-5">
          {current.text}
        </p>

        {/* 选项 */}
        <div className="space-y-2">
          {current.options.map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleAnswer(opt.value)}
              className="w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-200
                bg-gray-50 dark:bg-gray-700/50 hover:bg-lavender-50 dark:hover:bg-lavender-900/20
                text-gray-700 dark:text-gray-200 hover:text-lavender-700 dark:hover:text-lavender-300
                border border-transparent hover:border-lavender-200 dark:hover:border-lavender-700"
            >
              {opt.label}
            </button>
          ))}
        </div>

        <p className="text-xs text-gray-400 dark:text-gray-500 mt-4 text-center">
          第 {currentIndex + 1} / {QUESTIONS.length} 题
        </p>
      </div>

      <style>{`
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  );
}
