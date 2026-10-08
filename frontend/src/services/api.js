/**
 * CloudModX API Service
 * Centralized API client for the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders =
    options.body instanceof FormData
      ? {}
      : { 'Content-Type': 'application/json' };

  const config = {
    ...options,
    headers: { ...defaultHeaders, ...options.headers },
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export const apiService = {
  // Health
  getHealth: () => request('/api/health'),
  getRoot: () => request('/'),

  // Modules
  getModules: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/v1/modules${query ? `?${query}` : ''}`);
  },
  getModule: (id) => request(`/api/v1/modules/${id}`),
  createModule: (data) =>
    request('/api/v1/modules', { method: 'POST', body: JSON.stringify(data) }),
  updateModuleStatus: (id, status) =>
    request(`/api/v1/modules/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // Versions
  createVersion: (moduleId, data) =>
    request(`/api/v1/modules/${moduleId}/versions`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Artifacts
  uploadArtifact: (moduleId, versionId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(`/api/v1/modules/${moduleId}/versions/${versionId}/artifact`, {
      method: 'POST',
      body: formData,
    });
  },

  // Deployments
  getDeployments: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/v1/deployments${query ? `?${query}` : ''}`);
  },
  createDeployment: (data) =>
    request('/api/v1/deployments', { method: 'POST', body: JSON.stringify(data) }),
  rollbackDeployment: (data) =>
    request('/api/v1/deployments/rollback', { method: 'POST', body: JSON.stringify(data) }),
  rollbackModule: (moduleId, data = {}) =>
    request(`/api/v1/modules/${moduleId}/rollback`, { method: 'POST', body: JSON.stringify(data) }),

  // Audit Logs
  getAuditLogs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/v1/audit-logs${query ? `?${query}` : ''}`);
  },
};

export default apiService;
