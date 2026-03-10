'use client';

import React, { useState, useEffect } from 'react';
import { toZonedTime } from 'date-fns-tz';
import { Message } from '@/components';
import { personalAvatar } from '@/components/Avatar';

interface Message {
  id: number;
  user_message: string;
  bot_response: string;
  created_at: string;
}

interface ConversationViewProps {
  sessionId: string;
  onClose: () => void;
}

const FINLAND_TIMEZONE = 'Europe/Helsinki';

const parseTimestampToDate = (dateString: string): Date => {
  if (!dateString) return new Date();
  try {
    const utcString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    return new Date(utcString);
  } catch {
    return new Date();
  }
};

const ConversationView: React.FC<ConversationViewProps> = ({ sessionId, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConversation = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/conversation/${sessionId}`);
        const data = await response.json();
        setMessages(data.messages || []);
      } catch (error) {
        console.error('Failed to fetch conversation:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConversation();
  }, [sessionId]);

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-700 rounded-lg w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="border-b border-zinc-700 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-zinc-100">Conversation</h2>
            <p className="text-sm text-zinc-500 mt-1">Session: {sessionId}</p>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-zinc-400">Loading conversation...</p>
            </div>
          ) : messages.length > 0 ? (
            messages.map((message) => (
              <div key={message.id} className="space-y-2">
                <Message
                  content={message.user_message}
                  isUser={true}
                  timestamp={parseTimestampToDate(message.created_at)}
                />
                <Message
                  content={message.bot_response}
                  isUser={false}
                  avatarSrc={personalAvatar}
                  avatarAlt="Digital Tarmo"
                  timestamp={parseTimestampToDate(message.created_at)}
                />
              </div>
            ))
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-zinc-500">No messages in this conversation.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConversationView;
