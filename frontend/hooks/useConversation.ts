'use client';

import { useState, useCallback } from 'react';
import { ConversationMessage } from '@/types';

interface UseConversationReturn {
  messages: ConversationMessage[];
  addMessage: (content: string, isUser: boolean) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export const useConversation = (): UseConversationReturn => {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = useCallback((content: string, isUser: boolean) => {
    const newMessage: ConversationMessage = {
      id: `msg-${Date.now()}`,
      content,
      timestamp: new Date(),
      isUser,
    };

    setMessages((prev) => [...prev, newMessage]);
  }, []);

  return {
    messages,
    addMessage,
    isLoading,
    setIsLoading,
  };
};

export default useConversation;
