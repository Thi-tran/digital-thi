'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Header,
  Message,
  InputField,
  SuggestionGrid,
  ChatSection,
} from '@/components';
import { useConversation, useChatScroll } from '@/hooks';
import { INITIAL_SUGGESTIONS, GREETING_MESSAGE } from '@/constants/suggestions';
import { SuggestionButton } from '@/types';
import { personalAvatar } from '@/components/Avatar';

export const ChatPage: React.FC = () => {
  const { messages, addMessage, isLoading, isStreaming, isLoadingHistory, setIsLoading, sessionId, streamMessage } = useConversation();
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState(INITIAL_SUGGESTIONS);
  const lastUserMessageRef = useRef<HTMLDivElement>(null);

  const { scrollContainerRef, showSpacer, triggerSpacer } = useChatScroll({
    messagesLength: messages.length,
    lastUserMessageRef,
  });

  useEffect(() => {
    fetch('/api/chat', { method: 'GET' }).catch(() => { });
  }, []);

  const handleSuggestionClick = async (suggestion: SuggestionButton) => {
    if (isLoading || !sessionId) return;

    triggerSpacer();
    addMessage(suggestion.text, true);
    setIsLoading(true);
    setSuggestions([]); // Hide suggestions after first interaction

    await streamMessage(suggestion.text, sessionId);
    setIsLoading(false);
  };

  const handleInputSubmit = async () => {
    if (!inputValue.trim() || isLoading || !sessionId) return;

    triggerSpacer();
    addMessage(inputValue, true);
    setIsLoading(true);
    setSuggestions([]); // Hide suggestions after first interaction

    const userInput = inputValue;
    setInputValue('');

    await streamMessage(userInput, sessionId);
    setIsLoading(false);
  };

  // Hide suggestions when history is loaded or user has sent messages
  const showInitialState = messages.length === 0 && !isLoadingHistory;

  // Find the index of the last user message for attaching the ref
  const lastUserMessageIndex = messages.reduce((last, msg, i) => msg.isUser ? i : last, -1);

  return (
    <div className="flex h-screen flex-col bg-white dark:bg-zinc-950">
      <Header title="Digital Tarmo" />

      <div ref={scrollContainerRef} className="flex flex-1 flex-col overflow-y-auto">
        <div className="space-y-4 px-6 py-8">

          <Message
            content={GREETING_MESSAGE}
            isUser={false}
            avatarSrc={personalAvatar}
            avatarAlt="Digital Tarmo"
            timestamp={new Date()}
          />

          {isLoadingHistory ? (
            <div className="flex flex-1 items-center justify-center px-6 py-12">
              <div className="flex items-center gap-3 text-zinc-400 dark:text-zinc-500">
                <div className="flex gap-1">
                  <div className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce" />
                  <div className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce delay-100" />
                  <div className="h-2 w-2 rounded-full bg-zinc-400 animate-bounce delay-200" />
                </div>
                <span className="text-sm">Loading previous conversation...</span>
              </div>
            </div>
          ) : showInitialState ? (
            <div className="flex flex-1 items-center justify-center px-6 py-12">
              <ChatSection title="Ask me anything" subtitle="Click a suggestion below or type your own question">
                <SuggestionGrid
                  suggestions={suggestions}
                  onSelect={handleSuggestionClick}
                  isLoading={isLoading}
                />
              </ChatSection>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <Message
                  key={message.id}
                  ref={index === lastUserMessageIndex ? lastUserMessageRef : undefined}
                  content={message.content}
                  isUser={message.isUser}
                  avatarSrc={!message.isUser ? personalAvatar : undefined}
                  avatarAlt="Digital Tarmo"
                  timestamp={message.timestamp}
                />
              ))}

              {isLoading && !isStreaming && (
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

              {/* Spacer so the last user message can scroll to the top — hidden on first load and after user scrolls up */}
              {showSpacer && <div className="h-screen" />}
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
