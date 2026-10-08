import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Modules from './pages/Modules';
import ModuleDetail from './pages/ModuleDetail';
import NotFound from './pages/NotFound';

function HealthCheckView({ systemStatus }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
      <h2 className="text-xl font-bold text-gray-900">API Health Diagnostics</h2>
      <p className="text-xs text-gray-500">Live response from <code>GET /api/health</code></p>
      <div className="bg-slate-900 text-emerald-400 p-4 rounded-lg font-mono text-xs overflow-x-auto">
        <pre>{JSON.stringify(systemStatus, null, 2)}</pre>
      </div>
    </div>
  );
}

function DocsPlaceholder() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
      <h2 className="text-xl font-bold text-gray-900">CloudModX Architecture & Docs</h2>
      <p className="text-sm text-gray-600">
        Refer to <code>docs/architecture.md</code> and root <code>README.md</code> for full system design, local setup instructions, and lifecycle documentation.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <MainLayout>
      {({ systemStatus }) => (
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/modules" element={<Modules />} />
          <Route path="/modules/:id" element={<ModuleDetail />} />
          <Route
            path="/health-check"
            element={<HealthCheckView systemStatus={systemStatus} />}
          />
          <Route path="/docs" element={<DocsPlaceholder />} />
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      )}
    </MainLayout>
  );
}
