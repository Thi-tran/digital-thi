'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Header,
  Message,
  InputField,
  SuggestionGrid,
  ChatSection,
} from '@/components';
import { useConversation } from '@/hooks';
import { INITIAL_SUGGESTIONS, GREETING_MESSAGE } from '@/constants/suggestions';
import { SuggestionButton } from '@/types';
import { personalAvatar } from '@/components/Avatar';

interface ChatPageProps {
  onSuggestionClick?: (suggestion: SuggestionButton) => void;
  onMessageSend?: (message: string) => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ onSuggestionClick, onMessageSend }) => {
  const { messages, addMessage, isLoading, setIsLoading } = useConversation();
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState(INITIAL_SUGGESTIONS);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (message: string) => {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      return data.data.response || 'Sorry, I could not process your request.';
    } catch (error) {
      console.error('Error calling chat API:', error);
      return 'Sorry, there was an error processing your request. Please try again.';
    }
  };

  const handleSuggestionClick = async (suggestion: SuggestionButton) => {
    if (isLoading) return;

    addMessage(suggestion.text, true);
    setIsLoading(true);
    setSuggestions([]); // Hide suggestions after first interaction

    if (onSuggestionClick) {
      onSuggestionClick(suggestion);
    }

    const response = await sendMessage(suggestion.text);
    addMessage(response, false);
    setIsLoading(false);
  };

  const handleInputSubmit = async () => {
    if (!inputValue.trim() || isLoading) return;

    addMessage(inputValue, true);
    setIsLoading(true);
    setSuggestions([]); // Hide suggestions after first interaction

    if (onMessageSend) {
      onMessageSend(inputValue);
    }

    const userInput = inputValue;
    setInputValue('');

    const response = await sendMessage(userInput);
    addMessage(response, false);
    setIsLoading(false);
  };

  const showInitialState = messages.length === 0;

  return (
    <div className="flex h-screen flex-col bg-white dark:bg-zinc-950">
      <Header title="Digital Thi" />

      <div className="flex flex-1 flex-col overflow-y-auto">
        <div className="space-y-4 px-6 py-8">

          <Message
            content={GREETING_MESSAGE}
            isUser={false}
            avatarSrc={personalAvatar}
            avatarAlt="Digital Thi"
            timestamp={new Date()}
          />

          {showInitialState ? (
            <div className="flex flex-1 items-center justify-center px-6 py-12">
              <ChatSection title="Ask me anything about my CV" subtitle="Click a suggestion below or type your own question">
                <SuggestionGrid
                  suggestions={suggestions}
                  onSelect={handleSuggestionClick}
                  isLoading={isLoading}
                />
              </ChatSection>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <Message
                  key={message.id}
                  content={message.content}
                  isUser={message.isUser}
                  avatarSrc={!message.isUser ? personalAvatar : undefined}
                  avatarAlt="Digital Thi"
                  timestamp={message.timestamp}
                />
              ))}

              {isLoading && (
                <div className="flex gap-3">
                  <div className="flex items-center gap-2 rounded-lg bg-zinc-100 px-4 py-2.5 dark:bg-zinc-800">
                    <div className="flex gap-1">
                      <div className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce" />
                      <div className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce delay-100" />
                      <div className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>
      <div className="border-t border-zinc-200 bg-white px-6 py-4 dark:border-zinc-800 dark:bg-zinc-950">
        <InputField
          placeholder="Ask about my experience, skills, projects..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onSubmit={handleInputSubmit}
          isLoading={isLoading}
          icon={
            <svg
              className="h-5 w-5 rotate-90"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          }
        />
      </div>
    </div>
  );
};

export default ChatPage;
