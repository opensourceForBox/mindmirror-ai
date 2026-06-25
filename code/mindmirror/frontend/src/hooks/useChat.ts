import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { chatApi } from '../services/api';
import { INITIAL_GREETING } from '../utils/constants';
import type { Message, EmotionData, Expression } from '../types';

interface UseChatReturn {
  messages: Message[];
  sendMessage: (text: string) => Promise<void>;
  isLoading: boolean;
  currentEmotion: EmotionData | null;
  currentExpression: Expression;
  riskLevel: string;
}

function createGreeting(): Message {
  return {
    id: uuidv4(),
    role: 'assistant',
    content: INITIAL_GREETING,
    timestamp: new Date().toISOString(),
  };
}

export function useChat(sessionId: string): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([createGreeting()]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState<EmotionData | null>(null);
  const [currentExpression, setCurrentExpression] = useState<Expression>('neutral');
  const [riskLevel, setRiskLevel] = useState<string>('low');

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: Message = {
      id: uuidv4(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setCurrentExpression('thinking');

    try {
      const response = await chatApi.sendMessage(sessionId, text.trim(), currentEmotion || undefined);

      const aiMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.reply,
        timestamp: new Date().toISOString(),
        emotion: response.emotion,
      };

      setMessages((prev) => [...prev, aiMsg]);

      if (response.emotion) {
        setCurrentEmotion(response.emotion);
        setRiskLevel(response.emotion.risk_level);
      }

      if (response.suggested_expression) {
        setCurrentExpression(response.suggested_expression);
      } else {
        setCurrentExpression('neutral');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: '抱歉，我遇到了一点小问题，请稍后再试。',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
      setCurrentExpression('concerned');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, isLoading, currentEmotion]);

  return { messages, sendMessage, isLoading, currentEmotion, currentExpression, riskLevel };
}
