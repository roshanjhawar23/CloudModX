import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6">
      <div className="p-4 bg-amber-50 rounded-full text-amber-500 mb-4">
        <AlertTriangle className="w-10 h-10" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900">404 - Page Not Found</h2>
      <p className="text-gray-500 text-sm mt-2 max-w-md">
        The requested page does not exist in the CloudModX platform.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex items-center space-x-2 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Dashboard</span>
      </Link>
    </div>
  );
}
