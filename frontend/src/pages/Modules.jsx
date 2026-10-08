import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Layers, Plus, Search, RefreshCw, X, AlertCircle } from "lucide-react";
import StatusBadge from "../components/StatusBadge";
import apiService from "../services/api";

const ENVIRONMENTS = ["development", "staging", "production"];
const TECHNOLOGIES = ["Python", "Node.js", "Java", "Go", "Ruby", "PHP", "Other"];
const ARCHITECTURES = ["Microservice", "Monolith", "Serverless", "Lambda", "Container"];

function CreateModuleModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    name: "",
    description: "",
    technology: "Python",
    architecture: "Microservice",
    environment: "development",
    repository_url: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const module = await apiService.createModule(form);
      onCreated(module);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X className="w-5 h-5" />
        </button>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Plus className="w-5 h-5 text-sky-600" />
          <span>New Module</span>
        </h3>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Name <span className="text-red-500">*</span></label>
            <input name="name" value={form.name} onChange={handleChange} required placeholder="e.g. User Auth Service"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
            <textarea name="description" value={form.description} onChange={handleChange} rows={2}
              placeholder="Short description..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Technology</label>
              <select name="technology" value={form.technology} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500">
                {TECHNOLOGIES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Architecture</label>
              <select name="architecture" value={form.architecture} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500">
                {ARCHITECTURES.map((a) => <option key={a}>{a}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Environment</label>
              <select name="environment" value={form.environment} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500">
                {ENVIRONMENTS.map((e) => <option key={e}>{e}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Repository URL</label>
              <input name="repository_url" value={form.repository_url} onChange={handleChange}
                placeholder="https://github.com/..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500" />
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 rounded-lg border border-gray-300 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" disabled={loading}
              className="px-4 py-2 text-sm bg-sky-600 hover:bg-sky-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50">
              {loading ? "Creating..." : "Create Module"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Modules() {
  const navigate = useNavigate();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const fetchModules = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getModules();
      setModules(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchModules(); }, [fetchModules]);

  const filtered = modules.filter(
    (m) =>
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      (m.technology || "").toLowerCase().includes(search.toLowerCase()) ||
      (m.environment || "").toLowerCase().includes(search.toLowerCase())
  );

  const handleCreated = (newModule) => {
    setShowCreate(false);
    navigate(`/modules/${newModule.id}`);
  };

  return (
    <div className="space-y-6">
      {showCreate && (
        <CreateModuleModal onClose={() => setShowCreate(false)} onCreated={handleCreated} />
      )}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight flex items-center space-x-2">
            <Layers className="w-6 h-6 text-sky-600" />
            <span>Module Registry</span>
          </h2>
          <p className="text-sm text-gray-500 mt-1">Manage cloud module lifecycle: Draft → Review → Active → Archived</p>
        </div>
        <div className="flex items-center space-x-2">
          <button onClick={fetchModules} disabled={loading}
            className="p-2 text-gray-500 hover:text-sky-600 rounded-lg hover:bg-sky-50 transition-colors disabled:opacity-50" title="Refresh">
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button onClick={() => setShowCreate(true)}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm">
            <Plus className="w-4 h-4" />
            <span>New Module</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex flex-col sm:flex-row gap-3 justify-between items-center bg-gray-50">
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter by name, technology, environment..."
              className="w-full pl-9 pr-4 py-2 text-xs border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-sky-500" />
          </div>
          <span className="text-xs text-gray-500">{filtered.length} module{filtered.length !== 1 ? "s" : ""}</span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-gray-400 text-sm">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-sky-500" />
            Loading modules...
          </div>
        ) : error ? (
          <div className="py-10 px-6 text-center">
            <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
            <p className="text-sm text-red-600">{error}</p>
            <button onClick={fetchModules} className="mt-3 text-xs text-sky-600 hover:underline">Retry</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center text-gray-400">
            <Layers className="w-8 h-8 mx-auto mb-3 text-gray-300" />
            <p className="text-sm font-medium">{modules.length === 0 ? "No modules yet" : "No modules match your filter"}</p>
            {modules.length === 0 && (
              <button onClick={() => setShowCreate(true)} className="mt-3 text-xs text-sky-600 hover:underline">
                Create your first module
              </button>
            )}
          </div>
        ) : (
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-gray-100 text-xs text-gray-700 uppercase tracking-wider border-b border-gray-200">
              <tr>
                <th className="px-6 py-3">Name</th>
                <th className="px-6 py-3">Technology</th>
                <th className="px-6 py-3">Architecture</th>
                <th className="px-6 py-3">Environment</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 text-xs">
              {filtered.map((mod) => (
                <tr key={mod.id} onClick={() => navigate(`/modules/${mod.id}`)}
                  className="hover:bg-sky-50 cursor-pointer transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {mod.name}
                    {mod.description && (
                      <p className="text-[10px] text-gray-400 mt-0.5 truncate max-w-xs">{mod.description}</p>
                    )}
                  </td>
                  <td className="px-6 py-4 text-gray-600">{mod.technology || "—"}</td>
                  <td className="px-6 py-4 text-gray-600">{mod.architecture || "—"}</td>
                  <td className="px-6 py-4 text-gray-600">{mod.environment || "—"}</td>
                  <td className="px-6 py-4"><StatusBadge status={mod.status} /></td>
                  <td className="px-6 py-4 text-gray-400">{new Date(mod.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
