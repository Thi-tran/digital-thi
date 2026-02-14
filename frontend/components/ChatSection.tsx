import React from 'react';

interface ChatSectionProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export const ChatSection: React.FC<ChatSectionProps> = ({ title, subtitle, children }) => {
  return (
    <div className="flex flex-col items-center gap-8 text-center">
      <div>
        <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">{title}</h2>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">{subtitle}</p>
      </div>
      <div className="w-full">{children}</div>
    </div>
  );
};

export default ChatSection;
