import React from 'react';
import AdminSidebar from '@/components/admin/AdminSidebar';
import { Providers } from '../providers';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Providers>
      <div className="flex h-screen bg-zinc-950">
        <AdminSidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          {children}
        </div>
      </div>
    </Providers>
  );
}
