import re
from typing import List

from meta_lead_quality_analyzer.models import MetaLeadRow, QualityCategory, QualityFinding, Severity

REPEATED_DIGIT_REGEX = re.compile(r"^(\d)\1{6,}$")
SEQUENTIAL_REGEX = re.compile(r"^(?:0123456789|1234567890|9876543210|0987654321)")


class PhoneValidator:
    """Validates phone number validity, detects repeated dummy digits and spam patterns."""

    def analyze(self, leads: List[MetaLeadRow]) -> List[QualityFinding]:
        findings: List[QualityFinding] = []

        for lead in leads:
            raw_phone = lead.phone_number.strip()
            digits_only = re.sub(r"\D", "", raw_phone)

            if len(digits_only) < 7:
                findings.append(
                    QualityFinding(
                        id=f"phone-short-{lead.lead_id}",
                        category=QualityCategory.INVALID_PHONE,
                        severity=Severity.CRITICAL,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Incomplete Phone Number: '{raw_phone}'",
                        description=f"Phone number contains only {len(digits_only)} digits.",
                        metric_detail=f"Length {len(digits_only)} < minimum 7 digits",
                        recommended_action="Enable phone validation format requirements in Meta Instant Form settings.",
                    )
                )
                continue

            if REPEATED_DIGIT_REGEX.match(digits_only):
                findings.append(
                    QualityFinding(
                        id=f"phone-repeated-{lead.lead_id}",
                        category=QualityCategory.INVALID_PHONE,
                        severity=Severity.CRITICAL,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Repeated Dummy Digits Phone: '{raw_phone}'",
                        description=f"Phone number consists of repeated identical digits '{raw_phone}'.",
                        metric_detail="Failed heuristic: identical digit sequence",
                        recommended_action="Tag as uncontactable junk in CRM and exclude from sales outreach queue.",
                    )
                )
                continue

            if SEQUENTIAL_REGEX.match(digits_only):
                findings.append(
                    QualityFinding(
                        id=f"phone-seq-{lead.lead_id}",
                        category=QualityCategory.INVALID_PHONE,
                        severity=Severity.CRITICAL,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Sequential Fake Digits Phone: '{raw_phone}'",
                        description=f"Phone number consists of sequential keyboard numbers '{raw_phone}'.",
                        metric_detail="Failed heuristic: sequential digits",
                        recommended_action="Require SMS OTP confirmation or landing page phone verification.",
                    )
                )
                continue

            # Check suspicious dummy area code in US numbers
            if len(digits_only) == 10 and digits_only.startswith(("555", "000")):
                findings.append(
                    QualityFinding(
                        id=f"phone-dummy-area-{lead.lead_id}",
                        category=QualityCategory.INVALID_PHONE,
                        severity=Severity.HIGH,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Fictional / Reserved Area Code Phone: '{raw_phone}'",
                        description=f"Phone number uses reserved/fictional prefix '{digits_only[:3]}'.",
                        metric_detail="Area code match: 555 / 000 prefix",
                        recommended_action="Exclude lead from sales commission quotas and mark disqualified.",
                    )
                )

        return findings
