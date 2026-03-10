'use client';

import React from 'react';
import { formatDistance, format } from 'date-fns';
import { toZonedTime } from 'date-fns-tz';

interface User {
  session_id: string;
  conversation_count: number;
  last_active: string;
  joined_date: string;
}

interface UsersTableProps {
  users: User[];
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

const FINLAND_TIMEZONE = 'Europe/Helsinki';

const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  try {
    // Ensure the string is treated as UTC by adding 'Z' if not present
    const utcString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const utcDate = new Date(utcString);
    const zonedDate = toZonedTime(utcDate, FINLAND_TIMEZONE);
    return format(zonedDate, 'dd/MM/yy');
  } catch {
    return '-';
  }
};

const formatLastActive = (dateString: string) => {
  if (!dateString) return '-';
  try {
    // Ensure the string is treated as UTC by adding 'Z' if not present
    const utcString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const utcDate = new Date(utcString);
    const zonedDate = toZonedTime(utcDate, FINLAND_TIMEZONE);
    const nowZoned = toZonedTime(new Date(), FINLAND_TIMEZONE);
    return formatDistance(zonedDate, nowZoned, { addSuffix: true });
  } catch {
    return '-';
  }
};

const UsersTable: React.FC<UsersTableProps> = ({ users, searchQuery, onSearchChange }) => {
  return (
    <div>
      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <svg
            className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Search users by session ID..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-700 bg-zinc-900/50">
              <th className="px-6 py-4 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Session ID
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Conversations
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Last Active
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Joined Date
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {users.length > 0 ? (
              users.map((user, index) => (
                <tr
                  key={user.session_id}
                  className={`border-b border-zinc-700/50 ${index % 2 === 0 ? 'bg-zinc-900/20' : 'bg-zinc-800/20'
                    } hover:bg-zinc-700/20 transition-colors`}
                >
                  <td className="px-6 py-4">
                    <p className="text-sm font-medium text-zinc-100 break-all">
                      {user.session_id}
                    </p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-300">
                    {user.conversation_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-300">
                    {formatLastActive(user.last_active)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-300">
                    {formatDate(user.joined_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button className="text-zinc-400 hover:text-zinc-200 transition-colors">
                      <svg
                        className="w-5 h-5"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path d="M12 8a2 2 0 110-4 2 2 0 010 4zM12 14a2 2 0 110-4 2 2 0 010 4zM12 20a2 2 0 110-4 2 2 0 010 4z" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-zinc-500">
                  No users found matching your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UsersTable;
