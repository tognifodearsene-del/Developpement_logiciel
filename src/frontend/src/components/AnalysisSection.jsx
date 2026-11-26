export default function AnalysisSection({
  report,
  reportsList,
  running,
  onRunAnalysis,
  onSelectReport,
  onExport,
  hasInventory,
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Analyse & Calcul de ROI</h2>
            <p className="kpi-sub" style={{ margin: 0 }}>
              Benchmark automatique des alternatives open-source ou plus
              économiques.
            </p>
          </div>
          <div
            style={{
              display: "flex",
              gap: "0.6rem",
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            {reportsList.length > 0 && (
              <select
                aria-label="Sélectionner un rapport"
                value={report?.id ?? ""}
                onChange={(e) => onSelectReport(Number(e.target.value))}
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "0.5rem 0.7rem",
                }}
              >
                {reportsList.map((r) => (
                  <option key={r.id} value={r.id}>
                    Rapport #{r.id} (
                    {new Date(r.created_at).toLocaleDateString("fr-FR")})
                  </option>
                ))}
              </select>
            )}
            <button
              type="button"
              className="btn btn-primary"
              disabled={!hasInventory || running}
              onClick={onRunAnalysis}
            >
              {running ? "Analyse en cours..." : "Lancer l'analyse ROI"}
            </button>
            {report && (
              <>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => onExport(report.id, "csv")}
                >
                  Exporter CSV
                </button>
                <button
                  type="button"
                  className="btn btn-success"
                  onClick={() => onExport(report.id, "pdf")}
                >
                  Exporter PDF
                </button>
              </>
            )}
          </div>
        </div>

        {!report ? (
          <p className="kpi-sub">
            {hasInventory
              ? "Cliquez sur « Lancer l'analyse ROI » pour générer vos recommandations."
              : "Ajoutez ou importez des logiciels dans l'onglet Parc Logiciel pour démarrer l'analyse."}
          </p>
        ) : (
          <>
            <div className="kpi-grid" style={{ marginBottom: "1.25rem" }}>
              <div className="kpi-card">
                <div className="kpi-label">Coût actuel / an</div>
                <div className="kpi-value">
                  {report.total_current_annual_cost.toFixed(0)} €
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Économies estimées / an</div>
                <div className="kpi-value accent-green">
                  {report.total_estimated_annual_savings.toFixed(0)} €
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Coût de transition</div>
                <div className="kpi-value">
                  {report.total_migration_cost.toFixed(0)} €
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">ROI global (12 mois)</div>
                <div className="kpi-value accent-blue">
                  {report.global_roi_percent !== null
                    ? `${report.global_roi_percent.toFixed(1)}%`
                    : "Immédiat"}
                </div>
                <div className="kpi-sub">
                  Retour en{" "}
                  {report.payback_months !== null
                    ? `${report.payback_months.toFixed(1)} mois`
                    : "N/A"}
                </div>
              </div>
            </div>

            {report.recommendations.length > 0 && (
              <div style={{ marginBottom: "1.5rem" }}>
                <h3 className="card-title" style={{ marginBottom: "0.75rem" }}>
                  Top 3 des économies prioritaires (Actuel vs Projeté)
                </h3>
                {report.recommendations.slice(0, 3).map((rec) => {
                  const projectedPct =
                    rec.current_annual_cost > 0
                      ? Math.min(
                          100,
                          (rec.projected_annual_cost /
                            rec.current_annual_cost) *
                            100
                        )
                      : 0;
                  const savingsPct = Math.max(0, 100 - projectedPct);
                  return (
                    <div className="bar-row" key={rec.id}>
                      <div className="bar-label">
                        <span>
                          #{rec.priority_rank} {rec.software_name} →{" "}
                          {rec.alternative_name}
                        </span>
                        <span style={{ color: "var(--success)" }}>
                          -{rec.annual_savings.toFixed(0)} €/an (
                          {rec.roi_percent !== null
                            ? `ROI ${rec.roi_percent.toFixed(0)}%`
                            : "Immédiat"}
                          )
                        </span>
                      </div>
                      <div
                        className="bar-track"
                        title="Vert: coût projeté | Bleu: économie annuelle"
                      >
                        <div
                          className="bar-projected"
                          style={{ width: `${projectedPct}%` }}
                        />
                        <div
                          className="bar-savings"
                          style={{ width: `${savingsPct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Rang</th>
                    <th>Logiciel actuel</th>
                    <th>Alternative recommandée</th>
                    <th>Coût actuel / an</th>
                    <th>Coût projeté / an</th>
                    <th>Économie / an</th>
                    <th>ROI 12 mois</th>
                    <th>Détail</th>
                  </tr>
                </thead>
                <tbody>
                  {report.recommendations.map((rec) => (
                    <tr key={rec.id}>
                      <td>
                        <span className="badge badge-info">
                          #{rec.priority_rank}
                        </span>
                      </td>
                      <td>
                        <strong>{rec.software_name}</strong>
                        <div className="kpi-sub">{rec.category}</div>
                      </td>
                      <td>
                        <strong>{rec.alternative_name}</strong>
                        <div className="kpi-sub">
                          {rec.is_open_source ? "Open Source" : "Commercial"} •
                          Match {rec.feature_match_score}%
                        </div>
                      </td>
                      <td>{rec.current_annual_cost.toFixed(2)} €</td>
                      <td>{rec.projected_annual_cost.toFixed(2)} €</td>
                      <td style={{ color: "var(--success)", fontWeight: 700 }}>
                        {rec.annual_savings.toFixed(2)} €
                      </td>
                      <td>
                        {rec.roi_percent !== null
                          ? `${rec.roi_percent.toFixed(1)}%`
                          : "Immédiat"}
                        {rec.payback_months !== null && (
                          <div className="kpi-sub">
                            {rec.payback_months.toFixed(1)} mois
                          </div>
                        )}
                      </td>
                      <td style={{ maxWidth: "280px", fontSize: "0.82rem" }}>
                        {rec.rationale}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
