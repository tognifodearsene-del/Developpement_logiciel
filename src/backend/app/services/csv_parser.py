"""Parseur et validateur tolérant pour l'import de fichiers CSV d'inventaire logiciel."""

import csv
import io
from pydantic import ValidationError

from app.schemas import CsvImportError, SoftwareItemCreate


# Colonnes minimales exigées par la spécification dans docs/architecture.md
REQUIRED_COLUMNS = {
    "name",
    "category",
    "licenses_purchased",
    "licenses_used",
    "monthly_cost_total",
}


def _detect_delimiter(sample_text: str) -> str:
    """Détecte automatiquement le séparateur ',' (standard) ou ';' (export Excel français)."""
    first_line = next((line for line in sample_text.splitlines() if line.strip()), "")
    if first_line.count(";") > first_line.count(","):
        return ";"
    return ","


def parse_inventory_csv(content: bytes) -> tuple[list[SoftwareItemCreate], list[CsvImportError]]:
    """Valide un fichier CSV brut et retourne séparément les éléments valides et les erreurs par ligne."""
    try:
        # utf-8-sig supprime automatiquement l'éventuel BOM ajouté par Excel sous Windows
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], [CsvImportError(line=1, message="Encodage invalide : UTF-8 requis")]

    if not text.strip():
        return [], [CsvImportError(line=1, message="Fichier CSV vide")]

    delimiter = _detect_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        return [], [CsvImportError(line=1, message="En-têtes CSV manquants")]

    normalized_headers = [h.strip() if h else "" for h in reader.fieldnames]
    reader.fieldnames = normalized_headers

    missing = sorted(REQUIRED_COLUMNS - set(normalized_headers))
    if missing:
        return [], [
            CsvImportError(
                line=1,
                message=f"Colonnes obligatoires manquantes : {', '.join(missing)}",
            )
        ]

    items: list[SoftwareItemCreate] = []
    errors: list[CsvImportError] = []

    # Numérotation démarrant à 2 car la ligne 1 contient les en-têtes
    for line_num, row in enumerate(reader, start=2):
        # Ignore les lignes vides en fin de fichier
        if not any((v or "").strip() for v in row.values()):
            continue

        raw_cost = (row.get("monthly_cost_total") or "").strip()
        # Supporte les décimales avec virgule (ex. "300,50") lorsque le fichier vient d'Excel FR (;)
        if delimiter == ";" and "," in raw_cost and "." not in raw_cost:
            raw_cost = raw_cost.replace(",", ".")

        try:
            item = SoftwareItemCreate(
                name=(row.get("name") or "").strip(),
                category=(row.get("category") or "").strip(),
                vendor=(row.get("vendor") or "").strip(),
                licenses_purchased=int((row.get("licenses_purchased") or "").strip()),
                licenses_used=int((row.get("licenses_used") or "").strip()),
                monthly_cost_total=float(raw_cost),
            )
            items.append(item)
        except (ValueError, ValidationError) as exc:
            errors.append(CsvImportError(line=line_num, message=str(exc)))

    return items, errors
