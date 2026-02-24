'use client';

import { useState, useCallback, useEffect } from 'react';
import { ConversationMessage } from '@/types';

interface UseConversationReturn {
  messages: ConversationMessage[];
  addMessage: (content: string, isUser: boolean) => void;
  updateLastMessage: (content: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  sessionId: string;
  streamMessage: (message: string, sessionId: string) => Promise<void>;
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

  const updateLastMessage = useCallback((content: string) => {
    setMessages((prev) => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1].content = content;
      }
      return updated;
    });
  }, []);

  const streamMessage = useCallback(async (message: string, sessionId: string) => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      if (!response.body) {
        throw new Error('Response body is empty');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let streamedContent = '';

      // Add initial empty message for streaming
      addMessage('', false);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        streamedContent += chunk;

        // Update the last message with accumulated content
        updateLastMessage(streamedContent);
      }
    } catch (error) {
      console.error('Error streaming chat response:', error);
      addMessage('Sorry, there was an error processing your request. Please try again.', false);
    }
  }, [addMessage, updateLastMessage]);

  return {
    messages,
    addMessage,
    updateLastMessage,
    isLoading,
    setIsLoading,
    sessionId,
    streamMessage,
  };
};

export default useConversation;
