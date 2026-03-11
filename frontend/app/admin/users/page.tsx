'use client';

import React, { useState, useEffect } from 'react';
import AdminHeader from '@/components/admin/AdminHeader';
import UsersTable from '@/components/admin/UsersTable';
import ConversationView from '@/components/admin/ConversationView';

interface User {
  session_id: string;
  conversation_count: number;
  last_active: string;
  joined_date: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/users', { method: 'GET' });
        const data = await response.json();
        setUsers(data.users || []);
        setFilteredUsers(data.users || []);
      } catch (error) {
        console.error('Failed to fetch users:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  useEffect(() => {
    const filtered = users.filter(user =>
      user.session_id.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredUsers(filtered);
  }, [searchQuery, users]);

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
  };

  const handleViewConversation = (sessionId: string) => {
    console.log('Viewing conversation for session:', sessionId);
    setSelectedSessionId(sessionId);
  };

  const handleCloseConversation = () => {
    setSelectedSessionId(null);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <AdminHeader title="Users" subtitle="Manage visitors who have interacted with your digital CV" />
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-zinc-400">Loading users...</p>
          </div>
        ) : (
            <UsersTable
              users={filteredUsers}
              searchQuery={searchQuery}
              onSearchChange={handleSearchChange}
              onViewConversation={handleViewConversation}
            />
        )}
      </div>

      {selectedSessionId && (
        <ConversationView
          sessionId={selectedSessionId}
          onClose={handleCloseConversation}
        />
      )}
    </div>
  );
}
