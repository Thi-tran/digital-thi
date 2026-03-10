'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface TopicData {
  topic: string;
  engagement: number;
}

interface PopularTopicsProps {
  data?: TopicData[];
}

const PopularTopics: React.FC<PopularTopicsProps> = ({ data }) => {
  const defaultData: TopicData[] = [
    { topic: 'Experience', engagement: 500 },
    { topic: 'Skills', engagement: 380 },
    { topic: 'Projects', engagement: 280 },
    { topic: 'Education', engagement: 180 },
    { topic: 'Contact', engagement: 150 },
  ];

  const chartData = data || defaultData;

  return (
    <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-zinc-100 mb-4">
        Popular Topics
      </h3>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
            <XAxis dataKey="topic" stroke="#a1a1aa" />
            <YAxis stroke="#a1a1aa" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#27272a',
                border: '1px solid #3f3f46',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#e4e4e7' }}
            />
            <Bar dataKey="engagement" fill="#10b981" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PopularTopics;
