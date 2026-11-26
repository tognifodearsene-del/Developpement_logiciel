const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const TOKEN_KEY = "optistack_token";

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

async function request(path, options = {}) {
  const token = getStoredToken();
  const headers = { ...(options.headers || {}) };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = `Erreur HTTP ${response.status}`;
    try {
      const payload = await response.json();
      if (payload?.detail) {
        detail =
          typeof payload.detail === "string"
            ? payload.detail
            : JSON.stringify(payload.detail);
      }
    } catch {
      // Ignore JSON parsing failure on non-JSON error responses
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const api = {
  register: (data) =>
    request("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data) =>
    request("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => request("/auth/me"),

  getInventory: () => request("/inventory"),
  createSoftware: (data) =>
    request("/inventory", { method: "POST", body: JSON.stringify(data) }),
  deleteSoftware: (id) => request(`/inventory/${id}`, { method: "DELETE" }),
  importCsv: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/inventory/import-csv", { method: "POST", body: formData });
  },

  runAnalysis: () => request("/analysis/run", { method: "POST" }),
  getReports: () => request("/analysis/reports"),
  getReportDetail: (id) => request(`/analysis/reports/${id}`),

  async downloadReport(reportId, format) {
    const token = getStoredToken();
    const response = await fetch(
      `${API_BASE}/reports/${reportId}/export?format=${format}`,
      {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );
    if (!response.ok) {
      throw new Error(`Impossible d'exporter le rapport (${response.status})`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `optistack-rapport-${reportId}.${format}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  },
};
