from pathlib import Path

from meta_lead_quality_analyzer.models import (
    LeadAuditResult,
    LeadQualitySummary,
    QualityCategory,
    QualityFinding,
    Severity,
)
from meta_lead_quality_analyzer.report import ReportGenerator


def test_generate_reports(tmp_path: Path):
    finding = QualityFinding(
        id="f1",
        category=QualityCategory.DISPOSABLE_EMAIL,
        severity=Severity.CRITICAL,
        lead_id="l101",
        lead_name="Disposable Lead",
        title="Disposable Email",
        description="Found mailinator",
        metric_detail="mailinator.com",
        recommended_action="Exclude",
    )
    summary = LeadQualitySummary(
        total_leads_audited=10,
        total_ad_spend=285.0,
        front_end_cpl=28.5,
        qualified_leads_count=5,
        true_cpql=57.0,
        junk_lead_count=2,
        junk_lead_rate_pct=20.0,
        disposable_email_count=1,
        invalid_phone_count=1,
        speed_clicker_count=1,
        crm_disqualified_count=2,
    )
    audit = LeadAuditResult(
        audit_id="audit-lead-123",
        created_at="2026-10-12T10:00:00Z",
        summary=summary,
        findings=[finding],
    )

    reporter = ReportGenerator(tmp_path)
    res = reporter.generate_all(audit)

    assert res["html"].exists()
    assert res["json"].exists()
    assert res["csv"].exists()

    html_content = res["html"].read_text(encoding="utf-8")
    assert "audit-lead-123" in html_content
    assert "Disposable Email" in html_content
