"""End-to-end API integration tests for OptiStack V1 endpoints."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import User


REPO_ROOT = Path(__file__).resolve().parents[3]


def _register_and_auth_headers(client: TestClient, email: str = "dsi@pme.fr") -> dict[str, str]:
    resp = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Yassine Tourbi",
            "company_name": "OptiPME",
        },
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_auth_register_login_and_me(client: TestClient) -> None:
    headers = _register_and_auth_headers(client, "sami@pme.fr")

    dup = client.post(
        "/api/auth/register",
        json={
            "email": "sami@pme.fr",
            "password": "Password123!",
            "full_name": "Sami",
            "company_name": "OptiPME",
        },
    )
    assert dup.status_code == 409

    bad_login = client.post("/api/auth/login", json={"email": "sami@pme.fr", "password": "wrong"})
    assert bad_login.status_code == 401

    good_login = client.post(
        "/api/auth/login", json={"email": "sami@pme.fr", "password": "Password123!"}
    )
    assert good_login.status_code == 200

    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "sami@pme.fr"
    assert client.get("/api/auth/me").status_code == 401


def test_inventory_crud_and_csv_import_and_analysis_export(client: TestClient) -> None:
    headers = _register_and_auth_headers(client)

    # Empty inventory cannot run analysis
    empty_run = client.post("/api/analysis/run", headers=headers)
    assert empty_run.status_code == 400

    # Manual add, update, delete
    create_resp = client.post(
        "/api/inventory",
        headers=headers,
        json={
            "name": "Custom App",
            "category": "CRM",
            "vendor": "Acme",
            "licenses_purchased": 10,
            "licenses_used": 4,
            "monthly_cost_total": 200.0,
        },
    )
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]
    assert create_resp.json()["is_underutilized"] is True

    bad_update = client.put(
        f"/api/inventory/{item_id}",
        headers=headers,
        json={"licenses_used": 25},
    )
    assert bad_update.status_code == 422

    del_resp = client.delete(f"/api/inventory/{item_id}", headers=headers)
    assert del_resp.status_code == 204

    # CSV import using sample_inventory.csv
    sample_csv = (REPO_ROOT / "data" / "sample_inventory.csv").read_bytes()
    import_resp = client.post(
        "/api/inventory/import-csv",
        headers=headers,
        files={"file": ("sample_inventory.csv", sample_csv, "text/csv")},
    )
    assert import_resp.status_code == 200
    assert import_resp.json()["imported_count"] == 8
    assert import_resp.json()["skipped_count"] == 0

    inv_resp = client.get("/api/inventory", headers=headers)
    assert inv_resp.status_code == 200
    assert inv_resp.json()["total_software_count"] == 8
    assert inv_resp.json()["total_monthly_cost"] == 4770.0
    assert inv_resp.json()["total_annual_cost"] == 57240.0

    # Run analysis and verify Top 3+ recommendations
    run_resp = client.post("/api/analysis/run", headers=headers)
    assert run_resp.status_code == 201
    report = run_resp.json()
    report_id = report["id"]
    assert report["recommendation_count"] == 8
    assert report["total_estimated_annual_savings"] > 0
    assert report["recommendations"][0]["priority_rank"] == 1

    # List and retrieve reports
    list_reports = client.get("/api/analysis/reports", headers=headers)
    assert list_reports.status_code == 200
    assert len(list_reports.json()) == 1

    detail_resp = client.get(f"/api/analysis/reports/{report_id}", headers=headers)
    assert detail_resp.status_code == 200

    # Export CSV & PDF
    csv_export = client.get(f"/api/reports/{report_id}/export?format=csv", headers=headers)
    assert csv_export.status_code == 200
    assert "priority_rank,software_name" in csv_export.text

    pdf_export = client.get(f"/api/reports/{report_id}/export?format=pdf", headers=headers)
    assert pdf_export.status_code == 200
    assert pdf_export.content.startswith(b"%PDF-1.4")


def test_alternatives_admin_access_control(client: TestClient, db_session: Session) -> None:
    user_headers = _register_and_auth_headers(client, "client@pme.fr")

    list_resp = client.get("/api/alternatives?category=BI", headers=user_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 2

    payload = {
        "target_software": "Tableau",
        "category": "BI & Analytics",
        "alternative_name": "Apache Superset",
        "vendor_or_license": "Apache-2.0",
        "is_open_source": True,
        "estimated_monthly_cost_per_user": 2.0,
        "estimated_migration_cost": 800.0,
        "feature_match_score": 87,
        "description": "Alternative BI open-source.",
    }
    forbidden = client.post("/api/alternatives", headers=user_headers, json=payload)
    assert forbidden.status_code == 403

    admin = User(
        email="admin@optistack.io",
        password_hash=hash_password("AdminPass123!"),
        full_name="Admin OptiStack",
        company_name="OptiStack",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()

    login_resp = client.post(
        "/api/auth/login", json={"email": "admin@optistack.io", "password": "AdminPass123!"}
    )
    admin_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    created = client.post("/api/alternatives", headers=admin_headers, json=payload)
    assert created.status_code == 201
    assert created.json()["target_software"] == "Tableau"
