from typing import List, Tuple

from meta_lead_quality_analyzer.models import (
    CRMDealRow,
    MetaLeadRow,
    QualityCategory,
    QualityFinding,
    Severity,
)

DISQUALIFIED_STAGES = {
    "disqualified_bad_phone",
    "disqualified_spam_email",
    "disqualified_no_budget",
    "disqualified_fake_info",
    "disqualified",
    "no_show",
}

QUALIFIED_STAGES = {
    "qualified",
    "proposal",
    "negotiation",
    "won",
    "closed_won",
}


class CRMStageMatchAnalyzer:
    """Matches Meta leads to downstream CRM deal stages and calculates economic qualification metrics."""

    def analyze(
        self, leads: List[MetaLeadRow], deals: List[CRMDealRow]
    ) -> Tuple[List[QualityFinding], float, float, int, float, int, float, int]:
        """
        Returns:
            (findings, total_spend, front_end_cpl, qualified_count, true_cpql, junk_count, junk_pct, crm_disqualified_count)
        """
        findings: List[QualityFinding] = []
        deal_by_lead_id = {d.lead_id: d for d in deals}

        total_spend = sum(lead.cost_per_lead for lead in leads)
        total_leads = len(leads)
        front_end_cpl = (total_spend / total_leads) if total_leads > 0 else 0.0

        qualified_count = 0
        crm_disqualified_count = 0

        for lead in leads:
            deal = deal_by_lead_id.get(lead.lead_id)
            if not deal:
                continue

            stage = deal.crm_stage.strip().lower()
            if stage in QUALIFIED_STAGES:
                qualified_count += 1
            elif stage in DISQUALIFIED_STAGES:
                crm_disqualified_count += 1
                findings.append(
                    QualityFinding(
                        id=f"crm-disqualified-{lead.lead_id}",
                        category=QualityCategory.CRM_DISQUALIFICATION,
                        severity=Severity.HIGH,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"CRM Disqualification: '{deal.crm_stage}'",
                        description=(
                            f"Lead marked '{deal.crm_stage}' in CRM pipeline. "
                            f"Campaign '{lead.campaign_name}' paid ${lead.cost_per_lead:.2f} for this unviable lead."
                        ),
                        metric_detail=f"CRM Stage: {deal.crm_stage} | Spend: ${lead.cost_per_lead:.2f}",
                        recommended_action=(
                            "Send 'Disqualified' offline event back to Meta CAPI to deprioritize lookalike audience matching."
                        ),
                    )
                )

        true_cpql = (total_spend / qualified_count) if qualified_count > 0 else total_spend
        junk_count = crm_disqualified_count
        junk_pct = round((junk_count / total_leads * 100), 1) if total_leads > 0 else 0.0

        return (
            findings,
            total_spend,
            round(front_end_cpl, 2),
            qualified_count,
            round(true_cpql, 2),
            junk_count,
            junk_pct,
            crm_disqualified_count,
        )
