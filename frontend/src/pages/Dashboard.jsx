import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Layers, Server, CheckCircle2, AlertCircle, RefreshCw, Cpu, Database,
  Cloud, Activity, ChevronRight
} from "lucide-react";
import apiService from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function Dashboard() {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [modules, setModules] = useState([]);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getHealth();
      setHealth(data);
    } catch (err) {
      setError(err.message || "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const [mods, logs] = await Promise.all([
        apiService.getModules({ limit: 5 }),
        apiService.getAuditLogs({ limit: 10 }),
      ]);
      setModules(mods);
      setAuditLogs(logs);
    } catch (_) {
      // non-fatal
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchSummary();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">CloudModX Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            Cloud-Native Module Lifecycle Management — Production on EC2 + RDS
          </p>
        </div>
        <button
          onClick={() => { fetchHealth(); fetchSummary(); }}
          disabled={loading}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* API */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between">
            <div className="p-3 bg-sky-50 text-sky-600 rounded-lg"><Server className="w-5 h-5" /></div>
            <StatusBadge status={health?.status || (loading ? "Checking" : "Offline")} />
          </div>
          <div className="mt-4">
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">FastAPI Backend</p>
            <p className="text-lg font-bold text-gray-800 mt-1">{health?.service || "CloudModX Backend"}</p>
            <p className="text-xs text-gray-500 mt-1">
              v{health?.version || "—"} | {health?.environment || "—"}
            </p>
          </div>
        </div>

        {/* Database */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between">
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg"><Database className="w-5 h-5" /></div>
            <StatusBadge status={health?.database_connected ? "Connected" : "Checking"} />
          </div>
          <div className="mt-4">
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">PostgreSQL (RDS)</p>
            <p className="text-lg font-bold text-gray-800 mt-1">Private RDS Instance</p>
            <p className="text-xs text-gray-500 mt-1">
              {health?.database_connected ? "Active — ap-south-1" : "Verifying connection..."}
            </p>
          </div>
        </div>

        {/* Modules Summary */}
        <div
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 cursor-pointer hover:border-sky-300 transition-colors"
          onClick={() => navigate("/modules")}
        >
          <div className="flex items-center justify-between">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg"><Layers className="w-5 h-5" /></div>
            <ChevronRight className="w-4 h-4 text-gray-300" />
          </div>
          <div className="mt-4">
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Module Registry</p>
            <p className="text-lg font-bold text-gray-800 mt-1">
              {modules.length} Module{modules.length !== 1 ? "s" : ""}
            </p>
            <p className="text-xs text-sky-600 mt-1 hover:underline">View all →</p>
          </div>
        </div>
      </div>

      {/* Health + Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Health detail */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-base font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-sky-600" />
            <span>System Health</span>
          </h3>
          {loading ? (
            <div className="py-8 text-center text-gray-400 text-sm">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-sky-500" />
              Checking /api/health...
            </div>
          ) : error ? (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Backend Unreachable</p>
                <p className="mt-0.5 text-xs text-amber-700">Ensure FastAPI is running.</p>
                <p className="mt-1 font-mono text-[11px] text-amber-900 bg-amber-100/50 p-1.5 rounded">{error}</p>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs overflow-x-auto">
              <pre>{JSON.stringify(health, null, 2)}</pre>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-base font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Activity className="w-4 h-4 text-emerald-600" />
            <span>Recent Activity</span>
          </h3>
          {auditLogs.length === 0 ? (
            <div className="py-8 text-center text-gray-400 text-sm">
              <Activity className="w-6 h-6 mx-auto mb-2 text-gray-300" />
              No activity yet — create a module to get started.
            </div>
          ) : (
            <ul className="space-y-3">
              {auditLogs.map((log) => (
                <li key={log.id} className="flex items-start space-x-3 text-xs">
                  <span className="w-1.5 h-1.5 rounded-full bg-sky-400 mt-1.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <span className="font-medium text-gray-800">{log.action}</span>
                    <span className="ml-2 text-gray-400 capitalize">{log.resource_type}</span>
                    {log.details && (
                      <p className="text-[10px] text-gray-400 truncate mt-0.5">{JSON.stringify(log.details)}</p>
                    )}
                  </div>
                  <span className="flex-shrink-0 text-gray-300 text-[10px]">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Architecture info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center space-x-2">
            <Cloud className="w-4 h-4 text-sky-600" />
            <span>Production Architecture</span>
          </h3>
          <ul className="space-y-2.5 text-xs text-gray-600">
            {[
              ["Frontend", "React + Nginx on EC2 — port 80"],
              ["Backend", "FastAPI + SQLAlchemy — internal port 8000"],
              ["Database", "PostgreSQL — private RDS (ap-south-1)"],
              ["Storage", "S3 artifact bucket — IAM role access"],
              ["Observability", "CloudWatch logs + alarms (EC2 + RDS)"],
            ].map(([label, desc]) => (
              <li key={label} className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-500 mt-1.5" />
                <span><strong>{label}:</strong> {desc}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Platform Core Capabilities</span>
          </h3>
          <ul className="space-y-2 text-xs text-gray-600">
            {[
              "Module registry with full lifecycle (Draft → Review → Active → Archived)",
              "Semantic versioning with release notes & changelogs",
              "Multi-part binary package upload streamed to Amazon S3",
              "Deterministic deployment engine (Pending → Running → Success/Failed)",
              "Actionable failure capture with granular error diagnostics",
              "1-click instant rollback restoring previous verified stable releases",
              "Tamper-evident audit trail persisted in Amazon RDS PostgreSQL",
              "Real-time operational observability with Amazon CloudWatch alarms",
            ].map((f) => (
              <li key={f}>✅ {f}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
