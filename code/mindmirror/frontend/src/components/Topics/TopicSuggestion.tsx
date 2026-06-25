import React, { useState, useEffect } from 'react';
import { topicsApi, type TopicRecommendation } from '../../services/api';

interface TopicSuggestionProps {
  onSelectTopic?: (prompt: string) => void;
}

export default function TopicSuggestion({ onSelectTopic }: TopicSuggestionProps) {
  const [topics, setTopics] = useState<TopicRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    topicsApi.getRecommendations()
      .then(setTopics)
      .catch(() => {/* 接口异常静默处理 */})
      .finally(() => setLoading(false));
  }, []);

  const handleClick = (topic: TopicRecommendation) => {
    setSelectedId(topic.id);
    onSelectTopic?.(topic.prompt);
  };

  if (loading) {
    return (
      <div className="flex gap-3 overflow-x-auto pb-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="flex-shrink-0 w-48 h-28 rounded-2xl bg-gray-100 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (topics.length === 0) return null;

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-500 mb-2 px-1">
        今日推荐话题
      </h3>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {topics.map((topic) => (
          <button
            key={topic.id}
            onClick={() => handleClick(topic)}
            className={`flex-shrink-0 w-48 rounded-2xl p-4 text-left transition-all duration-200 border ${
              selectedId === topic.id
                ? 'bg-purple-100 border-purple-300 shadow-md'
                : 'bg-white border-gray-100 shadow-sm hover:shadow-md hover:border-purple-200 hover:-translate-y-0.5'
            }`}
          >
            <div className="text-2xl mb-2">{topic.icon}</div>
            <h4 className="text-sm font-semibold text-gray-800 mb-0.5">
              {topic.name}
            </h4>
            <p className="text-xs text-gray-500 line-clamp-2">
              {topic.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
