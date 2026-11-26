// Client HTTP centralisé pour communiquer avec l'API FastAPI et gérer le jeton JWT
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

/**
 * Exécute une requête fetch avec injection automatique du Bearer JWT et gestion d'erreurs FastAPI.
 */
async function request(path, options = {}) {
  const token = getStoredToken();
  const headers = { ...(options.headers || {}) };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  // Ne pas forcer Content-Type pour FormData afin que le navigateur génère le boundary multipart
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
      // Ignore les erreurs de parsing JSON si la réponse d'erreur est en texte brut
    }
    throw new Error(detail);
  }

  // Les routes DELETE retournent 204 No Content sans corps JSON
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const api = {
  // Authentification
  register: (data) =>
    request("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data) =>
    request("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => request("/auth/me"),

  // Gestion du parc logiciel (CRUD + import CSV multipart)
  getInventory: () => request("/inventory"),
  createSoftware: (data) =>
    request("/inventory", { method: "POST", body: JSON.stringify(data) }),
  deleteSoftware: (id) => request(`/inventory/${id}`, { method: "DELETE" }),
  importCsv: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/inventory/import-csv", {
      method: "POST",
      body: formData,
    });
  },

  // Analyse ROI et historique des rapports
  runAnalysis: () => request("/analysis/run", { method: "POST" }),
  getReports: () => request("/analysis/reports"),
  getReportDetail: (id) => request(`/analysis/reports/${id}`),

  // Téléchargement binaire CSV/PDF avec authentification par en-tête Authorization
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
