import React from 'react';
import { Cloud, Server, ShieldCheck } from 'lucide-react';

export default function Header({ systemStatus }) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-30">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-sky-600 text-white p-2 rounded-lg shadow-sm">
            <Cloud className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">CloudModX</h1>
            <p className="text-xs text-gray-500">College Cloud-Native Module Lifecycle Platform</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                systemStatus?.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'
              }`}
            />
            <span className="font-medium text-gray-700">
              API: {systemStatus?.status || 'Connecting...'}
            </span>
          </div>

          <div className="hidden sm:flex items-center space-x-1 text-xs text-gray-500 bg-gray-100 px-2.5 py-1 rounded">
            <Server className="w-3.5 h-3.5" />
            <span>v{systemStatus?.version || '0.1.0'} ({systemStatus?.environment || 'AWS'})</span>
          </div>
        </div>
      </div>
    </header>
  );
}
