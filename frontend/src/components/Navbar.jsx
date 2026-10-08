import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Layers, Activity, FileText, Database } from 'lucide-react';

export default function Navbar() {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Modules (Lifecycle)', path: '/modules', icon: Layers },
    { name: 'API Health', path: '/health-check', icon: Activity },
    { name: 'Documentation', path: '/docs', icon: FileText },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 min-h-screen flex flex-col p-4 border-r border-slate-800">
      <div className="mb-6 px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Navigation
      </div>
      <nav className="space-y-1.5 flex-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-sky-600 text-white shadow'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="pt-4 border-t border-slate-800 text-xs text-slate-400 space-y-2 px-2">
        <div className="flex items-center space-x-2">
          <Database className="w-3.5 h-3.5 text-sky-400" />
          <span>Amazon RDS PostgreSQL</span>
        </div>
        <div className="text-[11px] text-slate-500">
          CloudModX Production MVP
        </div>
      </div>
    </aside>
  );
}
