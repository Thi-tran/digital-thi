'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const AdminSidebar: React.FC = () => {
  const pathname = usePathname();

  const navItems: NavItem[] = [
    {
      label: 'Users',
      href: '/admin/users',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm0 1c-2.21 0-4 1.79-4 4v2h8v-2c0-2.21-1.79-4-4-4z" />
        </svg>
      ),
    },
    {
      label: 'Reporting',
      href: '/admin/reporting',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="w-56 bg-zinc-900 border-r border-zinc-800 flex flex-col">
      {/* Logo/Header */}
      <div className="p-6 border-b border-zinc-800">
        <h2 className="text-sm font-semibold text-zinc-100">Admin Portal</h2>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${isActive
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                }`}
            >
              {item.icon}
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-800">
        <button className="w-full px-4 py-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors text-left">
          Back to Chat
        </button>
      </div>
    </div>
  );
};

export default AdminSidebar;
