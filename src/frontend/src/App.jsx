import { useCallback, useEffect, useState } from "react";
import { api, getStoredToken, setStoredToken } from "./api/client";
import AnalysisSection from "./components/AnalysisSection";
import AuthView from "./components/AuthView";
import InventorySection from "./components/InventorySection";

export default function App() {
  const [user, setUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(Boolean(getStoredToken()));
  const [activeTab, setActiveTab] = useState("analysis");
  const [inventory, setInventory] = useState(null);
  const [reportsList, setReportsList] = useState([]);
  const [activeReport, setActiveReport] = useState(null);
  const [runningAnalysis, setRunningAnalysis] = useState(false);
  const [globalError, setGlobalError] = useState("");

  const loadWorkspaceData = useCallback(async () => {
    try {
      const [invData, reports] = await Promise.all([
        api.getInventory(),
        api.getReports(),
      ]);
      setInventory(invData);
      setReportsList(reports);
      if (reports.length > 0) {
        const detail = await api.getReportDetail(reports[0].id);
        setActiveReport(detail);
      } else {
        setActiveReport(null);
      }
    } catch (err) {
      setGlobalError(err.message);
    }
  }, []);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setCheckingAuth(false);
      return;
    }
    api
      .me()
      .then((profile) => {
        setUser(profile);
        return loadWorkspaceData();
      })
      .catch(() => {
        setStoredToken(null);
        setUser(null);
      })
      .finally(() => setCheckingAuth(false));
  }, [loadWorkspaceData]);

  async function handleAuthSuccess(authPayload) {
    setStoredToken(authPayload.access_token);
    setUser(authPayload.user);
    setGlobalError("");
    await loadWorkspaceData();
  }

  function handleLogout() {
    setStoredToken(null);
    setUser(null);
    setInventory(null);
    setReportsList([]);
    setActiveReport(null);
  }

  async function handleRunAnalysis() {
    setGlobalError("");
    setRunningAnalysis(true);
    try {
      const detail = await api.runAnalysis();
      setActiveReport(detail);
      const reports = await api.getReports();
      setReportsList(reports);
      setActiveTab("analysis");
    } catch (err) {
      setGlobalError(err.message);
    } finally {
      setRunningAnalysis(false);
    }
  }

  async function handleSelectReport(reportId) {
    setGlobalError("");
    try {
      const detail = await api.getReportDetail(reportId);
      setActiveReport(detail);
    } catch (err) {
      setGlobalError(err.message);
    }
  }

  async function handleExport(reportId, format) {
    setGlobalError("");
    try {
      await api.downloadReport(reportId, format);
    } catch (err) {
      setGlobalError(err.message);
    }
  }

  if (checkingAuth) {
    return (
      <div className="auth-wrapper">
        <p>Chargement de votre espace OptiStack...</p>
      </div>
    );
  }

  if (!user) {
    return <AuthView api={api} onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-badge">OS</span>
          <div>
            <div className="brand-title">OptiStack</div>
            <div className="brand-subtitle">
              SaaS d&apos;optimisation des licences logicielles
            </div>
          </div>
        </div>
        <div className="topbar-actions">
          <span className="user-pill">
            {user.full_name} • <strong>{user.company_name}</strong>
          </span>
          <button
            type="button"
            className="btn btn-outline-light"
            onClick={handleLogout}
          >
            Déconnexion
          </button>
        </div>
      </header>

      <main className="main-content">
        {globalError && <div className="alert alert-error">{globalError}</div>}

        <section className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-label">Logiciels suivis</div>
            <div className="kpi-value">
              {inventory?.total_software_count ?? 0}
            </div>
            <div className="kpi-sub">
              {inventory?.underutilized_count ?? 0} sous-utilisé(s) (&lt; 70%)
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Dépense mensuelle</div>
            <div className="kpi-value">
              {(inventory?.total_monthly_cost ?? 0).toFixed(0)} €
            </div>
            <div className="kpi-sub">
              {(inventory?.total_annual_cost ?? 0).toFixed(0)} € / an
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Utilisation moyenne</div>
            <div className="kpi-value">
              {(inventory?.average_utilization_rate ?? 0).toFixed(1)}%
            </div>
            <div className="kpi-sub">Seuil cible : 70%</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Économies potentielles</div>
            <div className="kpi-value accent-green">
              {activeReport
                ? `${activeReport.total_estimated_annual_savings.toFixed(0)} €`
                : "—"}
            </div>
            <div className="kpi-sub">
              {activeReport?.global_roi_percent != null
                ? `ROI estimé : ${activeReport.global_roi_percent.toFixed(1)}%`
                : "Lancez une analyse"}
            </div>
          </div>
        </section>

        <div className="tabs">
          <button
            type="button"
            className={`tab-btn ${activeTab === "analysis" ? "active" : ""}`}
            onClick={() => setActiveTab("analysis")}
          >
            Dashboard & Recommandations ROI
          </button>
          <button
            type="button"
            className={`tab-btn ${activeTab === "inventory" ? "active" : ""}`}
            onClick={() => setActiveTab("inventory")}
          >
            Parc Logiciel & Import CSV
          </button>
        </div>

        {activeTab === "analysis" ? (
          <AnalysisSection
            report={activeReport}
            reportsList={reportsList}
            running={runningAnalysis}
            onRunAnalysis={handleRunAnalysis}
            onSelectReport={handleSelectReport}
            onExport={handleExport}
            hasInventory={(inventory?.total_software_count ?? 0) > 0}
          />
        ) : (
          <InventorySection
            inventory={inventory}
            api={api}
            onInventoryChanged={loadWorkspaceData}
          />
        )}
      </main>
    </div>
  );
}
