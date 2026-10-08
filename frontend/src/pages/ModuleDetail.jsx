import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, RefreshCw, AlertCircle, Plus, Upload, Rocket,
  GitBranch, Package, ChevronRight, Check, X, RotateCcw, Activity, Clock
} from "lucide-react";
import StatusBadge from "../components/StatusBadge";
import apiService from "../services/api";

const STATUS_TRANSITIONS = {
  draft: ["review"],
  review: ["draft", "active"],
  active: ["archived"],
  archived: [],
};

function NewVersionModal({ moduleId, onClose, onCreated }) {
  const [form, setForm] = useState({ version: "", release_notes: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const v = await apiService.createVersion(moduleId, form);
      onCreated(v);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X className="w-5 h-5" />
        </button>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <GitBranch className="w-5 h-5 text-sky-600" />
          <span>New Version</span>
        </h3>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Version <span className="text-red-500">*</span></label>
            <input value={form.version} onChange={(e) => setForm((p) => ({ ...p, version: e.target.value }))} required
              placeholder="e.g. 1.0.0 or v1.0.0"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Release Notes / Changelog</label>
            <textarea value={form.release_notes} onChange={(e) => setForm((p) => ({ ...p, release_notes: e.target.value }))} rows={3}
              placeholder="What changes in this release..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500" />
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 rounded-lg border border-gray-300 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" disabled={loading}
              className="px-4 py-2 text-sm bg-sky-600 hover:bg-sky-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50">
              {loading ? "Creating..." : "Create Version"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ArtifactUploadModal({ moduleId, versionId, versionTag, onClose, onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const artifact = await apiService.uploadArtifact(moduleId, versionId, file);
      onUploaded(artifact);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X className="w-5 h-5" />
        </button>
        <h3 className="text-lg font-semibold text-gray-900 mb-1 flex items-center space-x-2">
          <Upload className="w-5 h-5 text-sky-600" />
          <span>Upload Release Artifact</span>
        </h3>
        <p className="text-xs text-gray-500 mb-4">Version: <span className="font-mono font-semibold">{versionTag}</span></p>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">Select package file (tar.gz, zip, etc.)</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-sky-400 transition-colors">
              <input type="file" onChange={(e) => setFile(e.target.files[0])} className="hidden" id="artifact-file" />
              <label htmlFor="artifact-file" className="cursor-pointer">
                <Package className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                {file ? (
                  <p className="text-xs font-medium text-sky-700">{file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
                ) : (
                  <p className="text-xs text-gray-500">Click to browse or drop package file</p>
                )}
              </label>
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 rounded-lg border border-gray-300 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" disabled={loading || !file}
              className="px-4 py-2 text-sm bg-sky-600 hover:bg-sky-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50">
              {loading ? "Uploading to S3..." : "Upload Artifact"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ModuleDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [module, setModule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusUpdating, setStatusUpdating] = useState(false);
  const [deployingId, setDeployingId] = useState(null);
  const [rollingBack, setRollingBack] = useState(false);
  const [modal, setModal] = useState(null);
  const [toast, setToast] = useState(null);

  const showToast = (msg, isError = false) => {
    setToast({ msg, isError });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchModule = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getModule(id);
      setModule(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchModule(); }, [fetchModule]);

  const handleStatusChange = async (newStatus) => {
    setStatusUpdating(true);
    try {
      await apiService.updateModuleStatus(id, newStatus);
      await fetchModule();
      showToast(`Status updated to ${newStatus}`);
    } catch (err) {
      showToast(err.message, true);
    } finally {
      setStatusUpdating(false);
    }
  };

  const handleDeploy = async (versionId) => {
    setDeployingId(versionId);
    try {
      const result = await apiService.createDeployment({
        module_id: Number(id),
        version_id: Number(versionId),
        environment: module.environment || "production",
      });
      await fetchModule();
      if (result.status === "failed") {
        showToast(`Deployment Failed: ${result.error_message}`, true);
      } else {
        showToast("Deployment succeeded! Module promoted to Active.");
      }
    } catch (err) {
      showToast(err.message, true);
    } finally {
      setDeployingId(null);
    }
  };

  const handleRollback = async () => {
    if (!window.confirm("Roll back this module to its previous stable deployed version?")) {
      return;
    }
    setRollingBack(true);
    try {
      const res = await apiService.rollbackModule(id, { environment: module.environment || "production" });
      await fetchModule();
      showToast(`Rollback Succeeded: ${res.error_message || "Reverted to previous version"}`);
    } catch (err) {
      showToast(err.message, true);
    } finally {
      setRollingBack(false);
    }
  };

  const handleVersionCreated = () => {
    setModal(null);
    fetchModule();
    showToast("New version registered");
  };

  const handleArtifactUploaded = () => {
    setModal(null);
    fetchModule();
    showToast("Artifact uploaded to S3 & registered");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-gray-400">
        <RefreshCw className="w-6 h-6 animate-spin mr-2 text-sky-500" />
        <span className="text-sm">Loading module...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-10 text-center">
        <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
        <p className="text-sm text-red-600 mb-3">{error}</p>
        <button onClick={() => navigate("/modules")} className="text-xs text-sky-600 hover:underline">
          Back to Modules
        </button>
      </div>
    );
  }

  const transitions = STATUS_TRANSITIONS[module.status?.toLowerCase()] || [];
  const successfulDeployments = (module.deployments || []).filter((d) => d.status === "success");
  const canRollback = (module.deployments || []).length > 1 && successfulDeployments.length > 0;

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div className={`fixed bottom-6 right-6 z-50 flex items-center space-x-2 px-4 py-3 rounded-lg shadow-xl text-sm font-medium transition-all max-w-md
          ${toast.isError ? "bg-red-600 text-white" : "bg-emerald-600 text-white"}`}>
          {toast.isError ? <AlertCircle className="w-5 h-5 flex-shrink-0" /> : <Check className="w-5 h-5 flex-shrink-0" />}
          <span className="truncate">{toast.msg}</span>
        </div>
      )}

      {/* Modals */}
      {modal === "version" && (
        <NewVersionModal moduleId={id} onClose={() => setModal(null)} onCreated={handleVersionCreated} />
      )}
      {modal?.type === "artifact" && (
        <ArtifactUploadModal
          moduleId={id}
          versionId={modal.versionId}
          versionTag={modal.versionTag}
          onClose={() => setModal(null)}
          onUploaded={handleArtifactUploaded}
        />
      )}

      {/* Breadcrumb */}
      <button onClick={() => navigate("/modules")}
        className="inline-flex items-center space-x-1 text-sm text-gray-500 hover:text-sky-600 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Modules</span>
      </button>

      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <h2 className="text-2xl font-bold text-gray-900">{module.name}</h2>
              <StatusBadge status={module.status} />
            </div>
            {module.description && <p className="text-sm text-gray-500 mt-1">{module.description}</p>}
            <div className="flex flex-wrap gap-x-6 gap-y-1 mt-3 text-xs text-gray-500">
              {module.technology && <span><span className="font-medium text-gray-700">Tech:</span> {module.technology}</span>}
              {module.architecture && <span><span className="font-medium text-gray-700">Arch:</span> {module.architecture}</span>}
              {module.environment && <span><span className="font-medium text-gray-700">Env:</span> {module.environment}</span>}
              {module.repository_url && (
                <a href={module.repository_url} target="_blank" rel="noreferrer" className="text-sky-600 hover:underline"
                  onClick={(e) => e.stopPropagation()}>
                  Repository ↗
                </a>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2 flex-shrink-0">
            {canRollback && (
              <button
                onClick={handleRollback}
                disabled={rollingBack}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-amber-300 text-amber-800 bg-amber-50 hover:bg-amber-100 transition-colors disabled:opacity-50"
                title="Rollback to previous stable version"
              >
                <RotateCcw className={`w-3.5 h-3.5 ${rollingBack ? "animate-spin" : ""}`} />
                <span>{rollingBack ? "Rolling back..." : "Rollback"}</span>
              </button>
            )}
            {transitions.length > 0 && (
              <div className="flex items-center space-x-1.5">
                <span className="text-xs text-gray-500">Transition:</span>
                {transitions.map((s) => (
                  <button key={s} onClick={() => handleStatusChange(s)} disabled={statusUpdating}
                    className="px-3 py-1.5 text-xs font-medium rounded-lg border border-sky-300 text-sky-700 hover:bg-sky-50 transition-colors disabled:opacity-50 capitalize">
                    {statusUpdating ? <RefreshCw className="w-3 h-3 animate-spin" /> : s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Versions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-base font-semibold text-gray-900 flex items-center space-x-2">
            <GitBranch className="w-4 h-4 text-sky-600" />
            <span>Versions & Releases</span>
            <span className="ml-1 text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
              {module.versions?.length || 0}
            </span>
          </h3>
          <button onClick={() => setModal("version")}
            className="inline-flex items-center space-x-1 px-3 py-1.5 bg-sky-600 hover:bg-sky-700 text-white text-xs font-medium rounded-lg transition-colors">
            <Plus className="w-3.5 h-3.5" />
            <span>New Version</span>
          </button>
        </div>

        {!module.versions?.length ? (
          <div className="py-10 text-center text-gray-400">
            <GitBranch className="w-7 h-7 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">No versions yet.</p>
            <button onClick={() => setModal("version")} className="mt-2 text-xs text-sky-600 hover:underline">
              Create the first version
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {module.versions.map((v) => (
              <div key={v.id} className="px-6 py-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm font-semibold text-gray-900">{v.version}</span>
                    </div>
                    {v.release_notes && <p className="text-xs text-gray-500 mt-1">{v.release_notes}</p>}
                    <p className="text-[10px] text-gray-400 mt-0.5">Registered {new Date(v.created_at).toLocaleString()}</p>

                    {/* Artifact Info */}
                    {v.artifact ? (
                      <div className="mt-2 flex items-center space-x-2 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-2.5 py-1 w-fit">
                        <Package className="w-3.5 h-3.5" />
                        <span className="font-medium">{v.artifact.filename}</span>
                        <span className="text-emerald-600">({(v.artifact.size_bytes / 1024).toFixed(1)} KB)</span>
                        <span className="text-emerald-500 uppercase text-[10px] font-semibold">{v.artifact.storage_provider}</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => setModal({ type: "artifact", versionId: v.id, versionTag: v.version })}
                        className="mt-2 inline-flex items-center space-x-1 text-xs text-sky-700 bg-sky-50 border border-sky-200 hover:bg-sky-100 px-2.5 py-1 rounded transition-colors">
                        <Upload className="w-3 h-3" />
                        <span>Upload package artifact to S3</span>
                      </button>
                    )}
                  </div>

                  <button
                    onClick={() => handleDeploy(v.id)}
                    disabled={deployingId === v.id}
                    className="flex-shrink-0 inline-flex items-center space-x-1 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium rounded-lg transition-colors shadow-sm disabled:opacity-50">
                    {deployingId === v.id ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Rocket className="w-3.5 h-3.5" />}
                    <span>{deployingId === v.id ? "Deploying..." : "Deploy"}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Deployment History Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-base font-semibold text-gray-900 flex items-center space-x-2">
            <Rocket className="w-4 h-4 text-emerald-600" />
            <span>Deployment History & Pipeline Executions</span>
            <span className="ml-1 text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
              {module.deployments?.length || 0}
            </span>
          </h3>
        </div>

        {!module.deployments?.length ? (
          <div className="py-8 text-center text-gray-400 text-xs">
            No deployments executed yet for this module.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-600">
              <thead className="bg-gray-50 text-gray-700 uppercase tracking-wider border-b border-gray-200 text-[10px]">
                <tr>
                  <th className="px-6 py-3">ID</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Environment</th>
                  <th className="px-6 py-3">Version Target</th>
                  <th className="px-6 py-3">Details / Diagnostics</th>
                  <th className="px-6 py-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {module.deployments.map((d) => (
                  <tr key={d.id} className={d.status === "failed" ? "bg-rose-50/40" : ""}>
                    <td className="px-6 py-3 font-mono font-medium text-gray-800">#{d.id}</td>
                    <td className="px-6 py-3">
                      <StatusBadge status={d.status} />
                    </td>
                    <td className="px-6 py-3 font-medium text-gray-700 uppercase text-[11px]">{d.environment}</td>
                    <td className="px-6 py-3 font-mono">
                      {module.versions?.find((v) => v.id === d.version_id)?.version || `Version #${d.version_id}`}
                    </td>
                    <td className="px-6 py-3">
                      {d.error_message ? (
                        <span className={d.status === "failed" ? "text-rose-700 font-medium" : "text-purple-700"}>
                          {d.error_message}
                        </span>
                      ) : (
                        <span className="text-emerald-700">Verified & active</span>
                      )}
                    </td>
                    <td className="px-6 py-3 text-gray-400">
                      {new Date(d.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Audit Log / Activity */}
      {module.audit_logs?.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-base font-semibold text-gray-900 flex items-center space-x-2">
              <Activity className="w-4 h-4 text-sky-600" />
              <span>Activity & Audit Trail</span>
            </h3>
          </div>
          <ul className="divide-y divide-gray-100">
            {module.audit_logs.map((log) => (
              <li key={log.id} className="px-6 py-3 flex items-start space-x-3 text-xs text-gray-500">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-400 mt-1.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <span className="font-semibold text-gray-800">{log.action}</span>
                  {log.details && <span className="ml-2 text-gray-400 font-mono text-[11px]">{log.details}</span>}
                </div>
                <span className="text-gray-300 text-[10px] flex-shrink-0">{new Date(log.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
