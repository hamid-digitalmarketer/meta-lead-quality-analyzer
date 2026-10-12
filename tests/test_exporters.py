import json
from pathlib import Path

from meta_lead_quality_analyzer.exporters import (
    CRMDisqualificationExporter,
    MetaCAPIOfflineExporter,
)
from meta_lead_quality_analyzer.models import (
    CRMDealRow,
    MetaLeadRow,
    QualityCategory,
    QualityFinding,
    Severity,
)


def test_meta_capi_offline_exporter(tmp_path: Path):
    leads = [
        MetaLeadRow(
            lead_id="l1",
            created_time="2026-10-12T10:00:00Z",
            campaign_name="Test Campaign",
            ad_name="Ad 1",
            form_name="Form 1",
            full_name="Alex Lead",
            email="alex@company.com",
            phone_number="555-123-4567",
            completion_time_sec=30.0,
        )
    ]
    deals = [
        CRMDealRow(lead_id="l1", crm_stage="Qualified", opportunity_value=2500.0)
    ]

    exporter = MetaCAPIOfflineExporter(tmp_path)
    out_file = exporter.export(leads, deals)

    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["event_name"] == "QualifiedLead"
    assert data["data"][0]["custom_data"]["value"] == 2500.0
    assert len(data["data"][0]["user_data"]["em"][0]) == 64  # SHA-256


def test_crm_disqualification_exporter(tmp_path: Path):
    findings = [
        QualityFinding(
            id="f1",
            category=QualityCategory.DISPOSABLE_EMAIL,
            severity=Severity.CRITICAL,
            lead_id="l99",
            lead_name="Bot Lead",
            title="Disposable Email",
            description="Temporary disposable domain used.",
            metric_detail="tempmail.com match",
            recommended_action="Exclude",
        )
    ]

    exporter = CRMDisqualificationExporter(tmp_path)
    out_file = exporter.export(findings)

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "lead_id,lead_name" in content
    assert "l99,Bot Lead" in content
