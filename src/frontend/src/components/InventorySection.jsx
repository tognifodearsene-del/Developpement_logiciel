import { useState } from "react";

const CATEGORIES = [
  "BI & Analytics",
  "Communication",
  "Gestion de projet",
  "Bureautique",
  "Design",
  "CRM",
  "Visioconférence",
  "Documentation",
  "Autre",
];

const INITIAL_FORM = {
  name: "",
  category: "BI & Analytics",
  vendor: "",
  licenses_purchased: "20",
  licenses_used: "10",
  monthly_cost_total: "250",
};

function downloadTemplateCsv() {
  const sample = [
    "name,category,vendor,licenses_purchased,licenses_used,monthly_cost_total",
    "Power BI Pro,BI & Analytics,Microsoft,30,14,300.00",
    "Slack Business+,Communication,Salesforce,50,32,625.00",
    "Jira Software,Gestion de projet,Atlassian,40,22,320.00",
  ].join("\n");
  const blob = new Blob([sample], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "modele_inventaire_optistack.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export default function InventorySection({ inventory, api, onInventoryChanged }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleManualSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    const purchased = Number(form.licenses_purchased);
    const used = Number(form.licenses_used);
    if (used > purchased) {
      setError("Les licences utilisées ne peuvent pas dépasser les licences achetées.");
      return;
    }

    setSubmitting(true);
    try {
      await api.createSoftware({
        name: form.name,
        category: form.category,
        vendor: form.vendor,
        licenses_purchased: purchased,
        licenses_used: used,
        monthly_cost_total: Number(form.monthly_cost_total),
      });
      setForm(INITIAL_FORM);
      setMessage("Logiciel ajouté à votre parc.");
      await onInventoryChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCsvUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError("");
    setMessage("");
    setImporting(true);
    try {
      const result = await api.importCsv(file);
      const errDetail =
        result.errors?.length > 0
          ? ` (${result.skipped_count} ligne(s) ignorée(s) : ligne ${result.errors[0].line})`
          : "";
      setMessage(`${result.imported_count} logiciel(s) importé(s) avec succès.${errDetail}`);
      await onInventoryChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setImporting(false);
      event.target.value = "";
    }
  }

  async function handleDelete(itemId) {
    setError("");
    setMessage("");
    try {
      await api.deleteSoftware(itemId);
      await onInventoryChanged();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {error && <div className="alert alert-error">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Importer un inventaire CSV</h2>
          <button type="button" className="btn btn-outline" onClick={downloadTemplateCsv}>
            Télécharger modèle CSV
          </button>
        </div>
        <div className="csv-box">
          <div>
            <strong>Format attendu :</strong>{" "}
            <code>name,category,vendor,licenses_purchased,licenses_used,monthly_cost_total</code>
            <div className="kpi-sub">
              Séparateurs virgule <code>,</code> ou point-virgule <code>;</code> supportés (UTF-8).
            </div>
          </div>
          <label className="btn btn-primary" style={{ margin: 0 }}>
            {importing ? "Import en cours..." : "Choisir un fichier CSV"}
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleCsvUpload}
              disabled={importing}
              style={{ display: "none" }}
            />
          </label>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Ajouter un logiciel manuellement</h2>
        </div>
        <form className="form-grid" onSubmit={handleManualSubmit}>
          <div className="field">
            <label htmlFor="sw-name">Logiciel</label>
            <input
              id="sw-name"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Ex : Power BI Pro"
            />
          </div>
          <div className="field">
            <label htmlFor="sw-cat">Catégorie</label>
            <select
              id="sw-cat"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="sw-vendor">Éditeur</label>
            <input
              id="sw-vendor"
              value={form.vendor}
              onChange={(e) => setForm({ ...form, vendor: e.target.value })}
              placeholder="Ex : Microsoft"
            />
          </div>
          <div className="field">
            <label htmlFor="sw-purchased">Licences achetées</label>
            <input
              id="sw-purchased"
              type="number"
              min="1"
              required
              value={form.licenses_purchased}
              onChange={(e) => setForm({ ...form, licenses_purchased: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="sw-used">Licences actives</label>
            <input
              id="sw-used"
              type="number"
              min="0"
              required
              value={form.licenses_used}
              onChange={(e) => setForm({ ...form, licenses_used: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="sw-cost">Coût mensuel (EUR)</label>
            <input
              id="sw-cost"
              type="number"
              min="0"
              step="0.01"
              required
              value={form.monthly_cost_total}
              onChange={(e) => setForm({ ...form, monthly_cost_total: e.target.value })}
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Ajout..." : "Ajouter"}
          </button>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            Parc logiciel actuel ({inventory?.total_software_count ?? 0})
          </h2>
        </div>
        {!inventory || inventory.items.length === 0 ? (
          <p className="kpi-sub">
            Aucun logiciel enregistré pour le moment. Importez <code>data/sample_inventory.csv</code>{" "}
            ou utilisez le formulaire ci-dessus.
          </p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Logiciel</th>
                  <th>Catégorie</th>
                  <th>Licences</th>
                  <th>Utilisation</th>
                  <th>Coût mensuel</th>
                  <th>Coût annuel</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {inventory.items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.name}</strong>
                      {item.vendor && <div className="kpi-sub">{item.vendor}</div>}
                    </td>
                    <td>{item.category}</td>
                    <td>
                      {item.licenses_used} / {item.licenses_purchased}
                    </td>
                    <td>
                      <span
                        className={`badge ${item.is_underutilized ? "badge-warn" : "badge-ok"}`}
                      >
                        {item.utilization_rate.toFixed(0)}%{" "}
                        {item.is_underutilized ? "• Sous-utilisé" : "• Optimal"}
                      </span>
                    </td>
                    <td>{item.monthly_cost_total.toFixed(2)} €</td>
                    <td>
                      <strong>{item.annual_cost.toFixed(2)} €</strong>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-danger-sm"
                        onClick={() => handleDelete(item.id)}
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
