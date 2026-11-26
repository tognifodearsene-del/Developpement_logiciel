"""Unit tests for CSV inventory parsing and validation."""

from pathlib import Path

from app.services.csv_parser import parse_inventory_csv


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_parse_sample_inventory_csv_success() -> None:
    sample_path = REPO_ROOT / "data" / "sample_inventory.csv"
    items, errors = parse_inventory_csv(sample_path.read_bytes())

    assert len(errors) == 0
    assert len(items) == 8
    assert items[0].name == "Power BI Pro"
    assert items[0].licenses_purchased == 30
    assert items[0].licenses_used == 14
    assert items[0].monthly_cost_total == 300.0


def test_parse_semicolon_bom_csv_with_comma_decimals() -> None:
    csv_payload = (
        "\ufeffname;category;vendor;licenses_purchased;licenses_used;monthly_cost_total\n"
        "Slack Business+;Communication;Salesforce;20;10;250,50\n"
    ).encode("utf-8")

    items, errors = parse_inventory_csv(csv_payload)

    assert len(errors) == 0
    assert len(items) == 1
    assert items[0].monthly_cost_total == 250.5


def test_parse_csv_missing_required_column() -> None:
    csv_payload = b"name,category,licenses_purchased\nPower BI,BI,10\n"
    items, errors = parse_inventory_csv(csv_payload)

    assert items == []
    assert len(errors) == 1
    assert errors[0].line == 1
    assert "Colonnes obligatoires manquantes" in errors[0].message


def test_parse_csv_partial_invalid_rows_reports_line_numbers() -> None:
    csv_payload = (
        "name,category,vendor,licenses_purchased,licenses_used,monthly_cost_total\n"
        "ValidApp,CRM,Acme,10,8,100\n"
        "BrokenApp,CRM,Acme,5,9,100\n"
        "NegativeCost,CRM,Acme,5,3,-20\n"
    ).encode("utf-8")

    items, errors = parse_inventory_csv(csv_payload)

    assert len(items) == 1
    assert items[0].name == "ValidApp"
    assert [err.line for err in errors] == [3, 4]


def test_parse_csv_empty_and_bad_encoding() -> None:
    assert parse_inventory_csv(b"   ")[1][0].line == 1
    assert "Encodage invalide" in parse_inventory_csv(b"\xff\xfe\x00")[1][0].message
