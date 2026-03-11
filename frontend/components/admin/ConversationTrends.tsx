'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface TrendData {
  month: string;
  conversations: number;
}

interface ConversationTrendsProps {
  data?: TrendData[];
}

const ConversationTrends: React.FC<ConversationTrendsProps> = ({ data }) => {
  const defaultData: TrendData[] = [
    { month: 'Jan', conversations: 90 },
    { month: 'Feb', conversations: 140 },
    { month: 'Mar', conversations: 200 },
    { month: 'Apr', conversations: 250 },
    { month: 'May', conversations: 310 },
    { month: 'Jun', conversations: 360 },
  ];

  const chartData = data || defaultData;

  return (
    <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-zinc-100 mb-4">
        Conversation Trends
      </h3>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
            <XAxis dataKey="month" stroke="#a1a1aa" />
            <YAxis stroke="#a1a1aa" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#27272a',
                border: '1px solid #3f3f46',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#e4e4e7' }}
            />
            <Line
              type="monotone"
              dataKey="conversations"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ fill: '#10b981', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ConversationTrends;
