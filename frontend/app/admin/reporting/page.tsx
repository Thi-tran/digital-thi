'use client';

import { useEffect, useState } from 'react';
import AdminHeader from '@/components/admin/AdminHeader';
import ReportingStats from '@/components/admin/ReportingStats';
import ConversationTrends from '@/components/admin/ConversationTrends';
import PopularTopics from '@/components/admin/PopularTopics';

interface ReportingData {
  total_conversations: number;
  active_users: number;
  avg_messages_per_chat: number;
  response_rate: number;
  conversation_trends: Array<{ month: string; conversations: number }>;
  popular_topics: Array<{ topic: string; engagement: number }>;
}

export default function ReportingPage() {
  const [data, setData] = useState<ReportingData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReportingData = async () => {
      try {
        const response = await fetch('/api/reporting/stats');
        if (response.ok) {
          const result = await response.json();
          setData(result);
        }
      } catch (error) {
        console.error('Failed to fetch reporting data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReportingData();
  }, []);

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <AdminHeader
        title="Reporting & Analytics"
        subtitle="Track performance and engagement metrics"
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <ReportingStats
          totalConversations={data?.total_conversations}
          activeUsers={data?.active_users}
          avgMessagesPerChat={data?.avg_messages_per_chat}
          responseRate={data?.response_rate}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ConversationTrends data={data?.conversation_trends} />
          <PopularTopics data={data?.popular_topics} />
        </div>
      </div>
    </div>
  );
}
