'use client';

import AdminHeader from '@/components/admin/AdminHeader';
import ReportingStats from '@/components/admin/ReportingStats';
import ConversationTrends from '@/components/admin/ConversationTrends';
import PopularTopics from '@/components/admin/PopularTopics';

export default function ReportingPage() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <AdminHeader
        title="Reporting & Analytics"
        subtitle="Track performance and engagement metrics"
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <ReportingStats />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ConversationTrends />
          <PopularTopics />
        </div>
      </div>
    </div>
  );
}
