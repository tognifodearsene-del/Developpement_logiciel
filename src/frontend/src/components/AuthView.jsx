import { useState } from "react";

/**
 * Écran d'authentification V1 permettant de basculer entre Connexion et Création de compte.
 */
export default function AuthView({ onAuthSuccess, api }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result =
        mode === "login"
          ? await api.login({ email, password })
          : await api.register({
              email,
              password,
              full_name: fullName,
              company_name: companyName || "PME Demo",
            });
      onAuthSuccess(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="card auth-card">
        <div className="card-header">
          <div>
            <h1 className="card-title" style={{ fontSize: "1.35rem" }}>
              OptiStack SaaS
            </h1>
            <p className="kpi-sub" style={{ margin: 0 }}>
              Optimisation des licences logicielles et calcul de ROI
            </p>
          </div>
          <span className="badge badge-info">V1 MVP</span>
        </div>

        <div className="tabs" style={{ marginBottom: "1rem" }}>
          <button
            type="button"
            className={`tab-btn ${mode === "login" ? "active" : ""}`}
            onClick={() => setMode("login")}
          >
            Connexion
          </button>
          <button
            type="button"
            className={`tab-btn ${mode === "register" ? "active" : ""}`}
            onClick={() => setMode("register")}
          >
            Créer un compte
          </button>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: "1rem" }}>
            {error}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === "register" && (
            <>
              <div className="field">
                <label htmlFor="full-name">Nom complet</label>
                <input
                  id="full-name"
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ex : Arsène Tognifodé"
                />
              </div>
              <div className="field">
                <label htmlFor="company-name">Entreprise (PME)</label>
                <input
                  id="company-name"
                  type="text"
                  required
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Ex : NovaTech PME"
                />
              </div>
            </>
          )}

          <div className="field">
            <label htmlFor="email">Email professionnel</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="dsi@entreprise.fr"
            />
          </div>

          <div className="field">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Minimum 6 caractères"
            />
          </div>

          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading
              ? "Chargement..."
              : mode === "login"
                ? "Se connecter"
                : "Créer mon espace"}
          </button>
        </form>
      </div>
    </div>
  );
}
