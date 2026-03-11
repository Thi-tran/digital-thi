'use client';

import React from 'react';
import { signOut } from 'next-auth/react';

interface AdminHeaderProps {
  title: string;
  subtitle: string;
}

const AdminHeader: React.FC<AdminHeaderProps> = ({ title, subtitle }) => {
  const handleLogout = async () => {
    await signOut({ redirect: true, callbackUrl: '/login' });
  };

  return (
    <div className="border-b border-zinc-800 bg-zinc-900/50 px-6 py-6 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-100">{title}</h1>
        <p className="text-sm text-zinc-400 mt-1">{subtitle}</p>
      </div>

      <button
        onClick={handleLogout}
        className="px-4 py-2 bg-red-600/10 hover:bg-red-600/20 border border-red-600/30 text-red-400 hover:text-red-300 rounded-md text-sm font-medium transition-colors duration-200"
      >
        Logout
      </button>
    </div>
  );
};

export default AdminHeader;
