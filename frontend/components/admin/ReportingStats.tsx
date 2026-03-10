import React from 'react';

interface StatItem {
  label: string;
  value: string | number;
}

interface ReportingStatsProps {
  totalConversations?: number;
  activeUsers?: number;
  avgMessagesPerChat?: number;
  responseRate?: number;
}

const ReportingStats: React.FC<ReportingStatsProps> = ({
  totalConversations = 1247,
  activeUsers = 856,
  avgMessagesPerChat = 11.3,
  responseRate = 98.7,
}) => {
  const stats: StatItem[] = [
    {
      label: 'Total Conversations',
      value: totalConversations.toLocaleString(),
    },
    {
      label: 'Active Users',
      value: activeUsers.toLocaleString(),
    },
    {
      label: 'Avg. Messages per Chat',
      value: avgMessagesPerChat,
    },
    {
      label: 'Response Rate',
      value: `${responseRate}%`,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-6"
        >
          <p className="text-sm text-zinc-400 mb-3">{stat.label}</p>
          <p className="text-3xl font-bold text-zinc-100 mb-2">{stat.value}</p>
        </div>
      ))}
    </div>
  );
};

export default ReportingStats;
