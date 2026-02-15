import React from 'react';
import { Avatar } from './Avatar';

interface MessageProps {
  content: string;
  isUser: boolean;
  avatarSrc?: string;
  avatarAlt?: string;
  timestamp?: Date;
}

const parseContent = (content: string) => {
  // Split by newlines and bullet points
  const lines = content.split('\n');

  return lines.map((line, idx) => {
    const trimmedLine = line.trim();

    // Handle bullet points
    if (trimmedLine.startsWith('*')) {
      const text = trimmedLine.substring(1).trim();
      // Bold text within **
      const parts = text.split(/\*\*(.*?)\*\*/);

      return (
        <li key={idx} className="ml-4 mb-2">
          {parts.map((part, i) => (
            i % 2 === 1 ? (
              <strong key={i}>{part}</strong>
            ) : (
              <span key={i}>{part}</span>
            )
          ))}
        </li>
      );
    }

    // Handle empty lines
    if (!trimmedLine) {
      return <div key={idx} className="mb-3" />;
    }

    // Handle bold text within **
    const parts = trimmedLine.split(/\*\*(.*?)\*\*/);

    return (
      <p key={idx} className="mb-2 leading-relaxed">
        {parts.map((part, i) => (
          i % 2 === 1 ? (
            <strong key={i}>{part}</strong>
          ) : (
            <span key={i}>{part}</span>
          )
        ))}
      </p>
    );
  });
};

export const Message: React.FC<MessageProps> = ({
  content,
  isUser,
  avatarSrc,
  avatarAlt = 'Avatar',
  timestamp,
}) => {
  const timeString = timestamp
    ? timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    : '';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {!isUser && avatarSrc && <Avatar alt={avatarAlt} size="md" />}

      <div className={`max-w-[80%] flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-lg px-4 py-2.5 text-sm leading-relaxed ${isUser
              ? 'bg-blue-600 text-white'
              : 'bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100'
            }`}
        >
          <div className="space-y-2">
            <ul className="list-disc space-y-1">
              {parseContent(content)}
            </ul>
          </div>
        </div>
        {timestamp && (
          <span className="text-xs text-zinc-500 dark:text-zinc-400">{timeString}</span>
        )}
      </div>
    </div>
  );
};

export default Message;
