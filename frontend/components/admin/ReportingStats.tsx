import React from 'react';

interface StatItem {
  label: string;
  value: string | number;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
}

const ReportingStats: React.FC = () => {
  const stats: StatItem[] = [
    {
      label: 'Total Conversations',
      value: '1,247',
      change: '+12.5% vs last month',
      changeType: 'positive',
    },
    {
      label: 'Active Users',
      value: '856',
      change: '+8.2% vs last month',
      changeType: 'positive',
    },
    {
      label: 'Avg. Messages per Chat',
      value: '11.3',
      change: '-2.1% vs last month',
      changeType: 'negative',
    },
    {
      label: 'Response Rate',
      value: '98.7%',
      change: '+1.3% vs last month',
      changeType: 'positive',
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
          <p
            className={`text-xs flex items-center gap-1 ${stat.changeType === 'positive'
                ? 'text-emerald-400'
                : stat.changeType === 'negative'
                  ? 'text-red-400'
                  : 'text-zinc-500'
              }`}
          >
            {stat.changeType === 'positive' && '↑'}
            {stat.changeType === 'negative' && '↓'}
            {stat.change}
          </p>
        </div>
      ))}
    </div>
  );
};

export default ReportingStats;
