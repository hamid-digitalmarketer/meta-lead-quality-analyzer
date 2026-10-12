import sqlite3
from pathlib import Path
from typing import List, Optional

from meta_lead_quality_analyzer.models import (
    LeadAuditResult,
    LeadQualitySummary,
    QualityCategory,
    QualityFinding,
    Severity,
)


class SQLiteStorage:
    def __init__(self, db_path: str | Path = "reports/lead_quality.sqlite"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audits (
                    audit_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    total_leads_audited INTEGER,
                    total_ad_spend REAL,
                    front_end_cpl REAL,
                    qualified_leads_count INTEGER,
                    true_cpql REAL,
                    junk_lead_count INTEGER,
                    junk_lead_rate_pct REAL,
                    disposable_email_count INTEGER,
                    invalid_phone_count INTEGER,
                    speed_clicker_count INTEGER,
                    crm_disqualified_count INTEGER
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    audit_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    lead_id TEXT NOT NULL,
                    lead_name TEXT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    metric_detail TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    FOREIGN KEY (audit_id) REFERENCES audits (audit_id)
                )
                """
            )
            conn.commit()

    def save_audit(self, audit: LeadAuditResult) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO audits (
                    audit_id, created_at, total_leads_audited, total_ad_spend,
                    front_end_cpl, qualified_leads_count, true_cpql, junk_lead_count,
                    junk_lead_rate_pct, disposable_email_count, invalid_phone_count,
                    speed_clicker_count, crm_disqualified_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.audit_id,
                    audit.created_at,
                    audit.summary.total_leads_audited,
                    audit.summary.total_ad_spend,
                    audit.summary.front_end_cpl,
                    audit.summary.qualified_leads_count,
                    audit.summary.true_cpql,
                    audit.summary.junk_lead_count,
                    audit.summary.junk_lead_rate_pct,
                    audit.summary.disposable_email_count,
                    audit.summary.invalid_phone_count,
                    audit.summary.speed_clicker_count,
                    audit.summary.crm_disqualified_count,
                ),
            )
            for f in audit.findings:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO findings (
                        id, audit_id, category, severity, lead_id, lead_name,
                        title, description, metric_detail, recommended_action
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f.id,
                        audit.audit_id,
                        f.category.value,
                        f.severity.value,
                        f.lead_id,
                        f.lead_name,
                        f.title,
                        f.description,
                        f.metric_detail,
                        f.recommended_action,
                    ),
                )
            conn.commit()

    def get_latest_audit(self) -> Optional[LeadAuditResult]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audits ORDER BY created_at DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return None

            audit_id = row["audit_id"]
            cursor.execute("SELECT * FROM findings WHERE audit_id = ?", (audit_id,))
            finding_rows = cursor.fetchall()

            findings: List[QualityFinding] = []
            for fr in finding_rows:
                findings.append(
                    QualityFinding(
                        id=fr["id"],
                        category=QualityCategory(fr["category"]),
                        severity=Severity(fr["severity"]),
                        lead_id=fr["lead_id"],
                        lead_name=fr["lead_name"],
                        title=fr["title"],
                        description=fr["description"],
                        metric_detail=fr["metric_detail"],
                        recommended_action=fr["recommended_action"],
                    )
                )

            summary = LeadQualitySummary(
                total_leads_audited=row["total_leads_audited"],
                total_ad_spend=row["total_ad_spend"],
                front_end_cpl=row["front_end_cpl"],
                qualified_leads_count=row["qualified_leads_count"],
                true_cpql=row["true_cpql"],
                junk_lead_count=row["junk_lead_count"],
                junk_lead_rate_pct=row["junk_lead_rate_pct"],
                disposable_email_count=row["disposable_email_count"],
                invalid_phone_count=row["invalid_phone_count"],
                speed_clicker_count=row["speed_clicker_count"],
                crm_disqualified_count=row["crm_disqualified_count"],
            )

            return LeadAuditResult(
                audit_id=audit_id,
                created_at=row["created_at"],
                summary=summary,
                findings=findings,
            )
