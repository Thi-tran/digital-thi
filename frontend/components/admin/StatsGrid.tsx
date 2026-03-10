import React from 'react';

interface StatCard {
  label: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'neutral';
}

const StatsGrid: React.FC = () => {
  const stats: StatCard[] = [
    {
      label: 'Total Users',
      value: '5',
      change: '+12 this week',
      changeType: 'positive',
    },
    {
      label: 'Active Users',
      value: '4',
      change: '+8% from last month',
      changeType: 'positive',
    },
    {
      label: 'Avg. Conversations',
      value: '12',
      change: 'per user',
      changeType: 'neutral',
    },
    {
      label: 'This Month',
      value: '18',
      change: 'new users',
      changeType: 'neutral',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-6"
        >
          <p className="text-sm text-zinc-400 mb-2">{stat.label}</p>
          <p className="text-3xl font-bold text-zinc-100">{stat.value}</p>
          {stat.change && (
            <p
              className={`text-xs mt-2 ${stat.changeType === 'positive'
                  ? 'text-emerald-400'
                  : 'text-zinc-500'
                }`}
            >
              {stat.changeType === 'positive' && '+ '}{stat.change}
            </p>
          )}
        </div>
      ))}
    </div>
  );
};

export default StatsGrid;
