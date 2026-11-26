"""CSV and PDF export services for analysis reports."""

import csv
import io
import textwrap
import unicodedata

from app.models import AnalysisReport


def export_report_csv(report: AnalysisReport) -> bytes:
    """Serialize an AnalysisReport and its recommendations as UTF-8-SIG CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "priority_rank",
            "software_name",
            "category",
            "alternative_name",
            "is_open_source",
            "current_annual_cost_eur",
            "projected_annual_cost_eur",
            "annual_savings_eur",
            "migration_cost_eur",
            "roi_percent",
            "payback_months",
            "rationale",
        ]
    )

    for rec in report.recommendations:
        writer.writerow(
            [
                rec.priority_rank,
                rec.software_item.name,
                rec.software_item.category,
                rec.alternative.alternative_name,
                "Oui" if rec.alternative.is_open_source else "Non",
                f"{rec.current_annual_cost:.2f}",
                f"{rec.projected_annual_cost:.2f}",
                f"{rec.annual_savings:.2f}",
                f"{rec.migration_cost:.2f}",
                f"{rec.roi_percent:.2f}" if rec.roi_percent is not None else "Immediat",
                f"{rec.payback_months:.2f}" if rec.payback_months is not None else "-",
                rec.rationale,
            ]
        )

    return output.getvalue().encode("utf-8-sig")


def _ascii_safe(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf_from_lines(lines: list[str]) -> bytes:
    """Generate a lightweight, valid single/multi-page PDF 1.4 document with Helvetica."""
    lines_per_page = 46
    pages_lines = [lines[i : i + lines_per_page] for i in range(0, len(lines), lines_per_page)] or [["Rapport vide"]]

    objects: list[bytes] = []
    # 1: Catalog, 2: Pages, 3: Font
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    page_obj_ids: list[int] = []
    next_id = 4
    page_entries: list[tuple[int, int, bytes]] = []

    for page_lines in pages_lines:
        content_ops = ["BT", "/F1 10 Tf", "45 780 Td", "15 TL"]
        for idx, line in enumerate(page_lines):
            escaped = _ascii_safe(line)
            if idx == 0:
                content_ops.append(f"({escaped}) Tj")
            else:
                content_ops.append(f"T* ({escaped}) Tj")
        content_ops.append("ET")
        stream_bytes = "\n".join(content_ops).encode("ascii")

        page_id = next_id
        content_id = next_id + 1
        next_id += 2
        page_obj_ids.append(page_id)
        page_entries.append((page_id, content_id, stream_bytes))

    kids_ref = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
    objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids_ref}] /Count {len(page_obj_ids)} >>\nendobj\n".encode("ascii"))
    objects.append(b"3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    for page_id, content_id, stream_bytes in page_entries:
        page_obj = (
            f"{page_id} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>\n"
            f"endobj\n"
        ).encode("ascii")
        content_obj = (
            f"{content_id} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii")
            + stream_bytes
            + b"\nendstream\nendobj\n"
        )
        objects.append(page_obj)
        objects.append(content_obj)

    buffer = io.BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets: list[int] = [0]
    for obj in objects:
        offsets.append(buffer.tell())
        buffer.write(obj)

    xref_pos = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        buffer.write(f"{off:010d} 00000 n \n".encode("ascii"))

    buffer.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    return buffer.getvalue()


def export_report_pdf(report: AnalysisReport) -> bytes:
    """Export an AnalysisReport to a structured PDF document."""
    roi_label = f"{report.global_roi_percent:.1f}%" if report.global_roi_percent is not None else "Immediat"
    payback_label = f"{report.payback_months:.1f} mois" if report.payback_months is not None else "N/A"
    company = report.owner.company_name if report.owner else "PME"

    lines = [
        f"OPTISTACK - RAPPORT D'OPTIMISATION LOGICIELLE (#{report.id})",
        f"Entreprise : {company} | Date : {report.created_at.strftime('%Y-%m-%d %H:%M UTC')}",
        "-" * 78,
        f"Cout annuel actuel          : {report.total_current_annual_cost:.2f} EUR",
        f"Economies annuelles estimees: {report.total_estimated_annual_savings:.2f} EUR",
        f"Cout total de transition    : {report.total_migration_cost:.2f} EUR",
        f"ROI global sur 12 mois      : {roi_label}",
        f"Delai de retour (Payback)   : {payback_label}",
        "-" * 78,
        "RECOMMANDATIONS PRIORITAIRES :",
        "",
    ]

    for rec in report.recommendations:
        rec_roi = f"{rec.roi_percent:.1f}%" if rec.roi_percent is not None else "Immediat"
        lines.append(
            f"#{rec.priority_rank} {rec.software_item.name} -> {rec.alternative.alternative_name} "
            f"({'Open Source' if rec.alternative.is_open_source else 'Commercial'})"
        )
        lines.append(
            f"   Actuel: {rec.current_annual_cost:.2f} EUR/an | Projete: {rec.projected_annual_cost:.2f} EUR/an | "
            f"Economie: {rec.annual_savings:.2f} EUR/an | ROI: {rec_roi}"
        )
        for wrapped in textwrap.wrap(f"   Motif: {rec.rationale}", width=82):
            lines.append(wrapped)
        lines.append("")

    return _build_pdf_from_lines(lines)
