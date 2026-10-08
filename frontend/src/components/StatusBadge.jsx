import React from 'react';

export default function StatusBadge({ status }) {
  const getBadgeStyle = (st) => {
    switch (st?.toLowerCase()) {
      case 'active':
      case 'healthy':
      case 'ready':
      case 'success':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'draft':
      case 'development':
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'review':
      case 'pending':
      case 'queued':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'archived':
      case 'error':
      case 'failed':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      case 'rolled_back':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getBadgeStyle(
        status
      )}`}
    >
      {status || 'Unknown'}
    </span>
  );
}
