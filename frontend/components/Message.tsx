import React from 'react';
import { Avatar } from './Avatar';

interface MessageProps {
  content: string;
  isUser: boolean;
  avatarSrc?: string;
  avatarAlt?: string;
  timestamp?: Date;
}

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

      <div className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`max-w-xs rounded-lg px-4 py-2.5 text-sm leading-relaxed ${isUser
              ? 'bg-blue-600 text-white'
              : 'bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100'
            }`}
        >
          {content}
        </div>
        {timestamp && (
          <span className="text-xs text-zinc-500 dark:text-zinc-400">{timeString}</span>
        )}
      </div>
    </div>
  );
};

export default Message;
