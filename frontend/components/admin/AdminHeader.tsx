import React from 'react';

interface AdminHeaderProps {
  title: string;
  subtitle: string;
}

const AdminHeader: React.FC<AdminHeaderProps> = ({ title, subtitle }) => {
  return (
    <div className="border-b border-zinc-800 bg-zinc-900/50 px-6 py-6">
      <h1 className="text-2xl font-semibold text-zinc-100">{title}</h1>
      <p className="text-sm text-zinc-400 mt-1">{subtitle}</p>
    </div>
  );
};

export default AdminHeader;
