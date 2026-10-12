from meta_lead_quality_analyzer.analyzers import (
    CompletionSpeedAnalyzer,
    CRMStageMatchAnalyzer,
    CustomQuestionAnalyzer,
    DisposableEmailAnalyzer,
    PhoneValidator,
)
from meta_lead_quality_analyzer.models import (
    CRMDealRow,
    MetaLeadRow,
    QualityCategory,
    Severity,
)


def test_disposable_email_analyzer():
    leads = [
        MetaLeadRow(
            lead_id="l1",
            created_time="2026-10-12T10:00:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Disposable User",
            email="burn@tempmail.com",
            phone_number="555-123-4567",
            completion_time_sec=20.0,
        ),
        MetaLeadRow(
            lead_id="l2",
            created_time="2026-10-12T10:01:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Valid User",
            email="sarah@legitbusiness.com",
            phone_number="555-123-4567",
            completion_time_sec=20.0,
        ),
    ]
    analyzer = DisposableEmailAnalyzer()
    findings = analyzer.analyze(leads)

    assert len(findings) == 1
    assert findings[0].category == QualityCategory.DISPOSABLE_EMAIL
    assert findings[0].severity == Severity.CRITICAL
    assert findings[0].lead_id == "l1"


def test_phone_validator():
    leads = [
        MetaLeadRow(
            lead_id="l1",
            created_time="2026-10-12T10:00:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Repeated Phone",
            email="test1@legit.com",
            phone_number="5555555555",
            completion_time_sec=20.0,
        ),
        MetaLeadRow(
            lead_id="l2",
            created_time="2026-10-12T10:01:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Short Phone",
            email="test2@legit.com",
            phone_number="1234",
            completion_time_sec=20.0,
        ),
        MetaLeadRow(
            lead_id="l3",
            created_time="2026-10-12T10:02:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Valid Phone",
            email="test3@legit.com",
            phone_number="415-322-8901",
            completion_time_sec=20.0,
        ),
    ]
    analyzer = PhoneValidator()
    findings = analyzer.analyze(leads)

    assert len(findings) == 2
    assert all(f.category == QualityCategory.INVALID_PHONE for f in findings)


def test_completion_speed_analyzer():
    leads = [
        MetaLeadRow(
            lead_id="l1",
            created_time="2026-10-12T10:00:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Bot Clicker",
            email="test1@legit.com",
            phone_number="415-322-8901",
            completion_time_sec=2.4,
        ),
        MetaLeadRow(
            lead_id="l2",
            created_time="2026-10-12T10:01:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Human Lead",
            email="test2@legit.com",
            phone_number="415-322-8901",
            completion_time_sec=28.5,
        ),
    ]
    analyzer = CompletionSpeedAnalyzer()
    findings = analyzer.analyze(leads)

    assert len(findings) == 1
    assert findings[0].category == QualityCategory.SPEED_CLICKER_BOT
    assert findings[0].severity == Severity.HIGH


def test_custom_question_analyzer():
    leads = [
        MetaLeadRow(
            lead_id="l1",
            created_time="2026-10-12T10:00:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Gibberish Answer",
            email="test1@legit.com",
            phone_number="415-322-8901",
            completion_time_sec=15.0,
            custom_answer_timeline="asdf",
        )
    ]
    analyzer = CustomQuestionAnalyzer()
    findings = analyzer.analyze(leads)

    assert len(findings) == 1
    assert findings[0].category == QualityCategory.GIBBERISH_CUSTOM_ANSWER


def test_crm_stage_match_analyzer():
    leads = [
        MetaLeadRow(
            lead_id="l1",
            created_time="2026-10-12T10:00:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Qual Lead",
            email="qual@legit.com",
            phone_number="415-322-8901",
            completion_time_sec=30.0,
            cost_per_lead=30.0,
        ),
        MetaLeadRow(
            lead_id="l2",
            created_time="2026-10-12T10:01:00Z",
            campaign_name="Test",
            ad_name="Test Ad",
            form_name="Form",
            full_name="Junk Lead",
            email="junk@legit.com",
            phone_number="415-322-8901",
            completion_time_sec=30.0,
            cost_per_lead=30.0,
        ),
    ]
    deals = [
        CRMDealRow(lead_id="l1", crm_stage="Qualified", opportunity_value=5000.0),
        CRMDealRow(lead_id="l2", crm_stage="Disqualified_Bad_Phone", opportunity_value=0.0),
    ]

    analyzer = CRMStageMatchAnalyzer()
    findings, total_spend, fe_cpl, qual_count, true_cpql, junk_count, junk_pct, crm_disq = analyzer.analyze(leads, deals)

    assert total_spend == 60.0
    assert fe_cpl == 30.0
    assert qual_count == 1
    assert true_cpql == 60.0  # $60 spend / 1 qualified lead = $60 CPQL
    assert junk_count == 1
    assert junk_pct == 50.0
    assert len(findings) == 1
