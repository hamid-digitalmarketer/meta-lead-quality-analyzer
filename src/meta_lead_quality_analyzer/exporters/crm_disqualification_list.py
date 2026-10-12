import csv
from pathlib import Path
from typing import List

from meta_lead_quality_analyzer.models import QualityFinding


class CRMDisqualificationExporter:
    """Exports structured exclusion list of low-quality/bot leads for CRM tagging and custom audience suppression."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, findings: List[QualityFinding]) -> Path:
        out_path = self.output_dir / "crm_disqualification_list.csv"
        fieldnames = [
            "lead_id",
            "lead_name",
            "category",
            "severity",
            "title",
            "metric_detail",
            "recommended_action",
        ]

        with open(out_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for finding in findings:
                writer.writerow(
                    {
                        "lead_id": finding.lead_id,
                        "lead_name": finding.lead_name or "",
                        "category": finding.category.value,
                        "severity": finding.severity.value,
                        "title": finding.title,
                        "metric_detail": finding.metric_detail,
                        "recommended_action": finding.recommended_action,
                    }
                )

        return out_path
