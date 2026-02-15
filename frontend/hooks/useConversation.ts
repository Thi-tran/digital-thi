'use client';

import { useState, useCallback, useEffect } from 'react';
import { ConversationMessage } from '@/types';

interface UseConversationReturn {
  messages: ConversationMessage[];
  addMessage: (content: string, isUser: boolean) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  sessionId: string;
}

export const useConversation = (): UseConversationReturn => {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');

  // Initialize session ID on mount
  useEffect(() => {
    const storedSessionId = localStorage.getItem('chat_session_id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('chat_session_id', newSessionId);
      setSessionId(newSessionId);
    }
  }, []);

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
    sessionId,
  };
};

export default useConversation;
