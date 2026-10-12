import csv
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from meta_lead_quality_analyzer.models import LeadAuditResult


class ReportGenerator:
    """Generates HTML, JSON, and CSV diagnostic audit reports for Meta lead campaigns."""

    def __init__(self, output_dir: Path | str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def export_json(self, audit: LeadAuditResult) -> Path:
        out_file = self.output_dir / f"audit-{audit.audit_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(audit.model_dump(), f, indent=2)
        return out_file

    def export_csv(self, audit: LeadAuditResult) -> Path:
        out_file = self.output_dir / f"audit-{audit.audit_id}.csv"
        fieldnames = [
            "id",
            "category",
            "severity",
            "lead_id",
            "lead_name",
            "title",
            "description",
            "metric_detail",
            "recommended_action",
        ]
        with open(out_file, "w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for finding in audit.findings:
                writer.writerow(
                    {
                        "id": finding.id,
                        "category": finding.category.value,
                        "severity": finding.severity.value,
                        "lead_id": finding.lead_id,
                        "lead_name": finding.lead_name or "",
                        "title": finding.title,
                        "description": finding.description,
                        "metric_detail": finding.metric_detail,
                        "recommended_action": finding.recommended_action,
                    }
                )
        return out_file

    def export_html(self, audit: LeadAuditResult) -> Path:
        template = self.env.get_template("report.html")
        html_content = template.render(audit=audit)
        out_file = self.output_dir / f"audit-{audit.audit_id}.html"
        out_file.write_text(html_content, encoding="utf-8")
        return out_file

    def generate_all(self, audit: LeadAuditResult) -> dict[str, Path]:
        return {
            "html": self.export_html(audit),
            "json": self.export_json(audit),
            "csv": self.export_csv(audit),
        }
