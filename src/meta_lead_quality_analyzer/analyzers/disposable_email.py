from typing import List

from meta_lead_quality_analyzer.models import MetaLeadRow, QualityCategory, QualityFinding, Severity

DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "guerrillamail.com",
    "tempmail.com",
    "yopmail.com",
    "throwawaymail.com",
    "sharklasers.com",
    "trashmail.com",
    "getairmail.com",
    "dispostable.com",
    "10minutemail.com",
    "fakemailgenerator.com",
    "temp-mail.org",
    "maildrop.cc",
    "inboxkitten.com",
}

GENERIC_FAKE_EMAILS = {
    "test@test.com",
    "test@gmail.com",
    "noemail@gmail.com",
    "none@none.com",
    "admin@admin.com",
    "asdf@asdf.com",
    "a@a.com",
}


class DisposableEmailAnalyzer:
    """Detects temporary disposable domains, throwaway email providers, and dummy addresses."""

    def analyze(self, leads: List[MetaLeadRow]) -> List[QualityFinding]:
        findings: List[QualityFinding] = []

        for lead in leads:
            email = lead.email.strip().lower()
            if not email or "@" not in email:
                findings.append(
                    QualityFinding(
                        id=f"email-malformed-{lead.lead_id}",
                        category=QualityCategory.DISPOSABLE_EMAIL,
                        severity=Severity.CRITICAL,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Malformed or Empty Email Address: '{lead.email}'",
                        description=f"Lead submitted without a valid email syntax: '{lead.email}'.",
                        metric_detail="Syntax error: missing @ or domain",
                        recommended_action="Enable Instant Form work email verification or add required email validation.",
                    )
                )
                continue

            domain = email.split("@")[-1]
            local_part = email.split("@")[0]

            if domain in DISPOSABLE_DOMAINS:
                findings.append(
                    QualityFinding(
                        id=f"email-disposable-{lead.lead_id}",
                        category=QualityCategory.DISPOSABLE_EMAIL,
                        severity=Severity.CRITICAL,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Disposable Temporary Email Domain: @{domain}",
                        description=f"Lead submitted using temporary burner inbox '{email}'.",
                        metric_detail=f"Known disposable domain blacklist match: {domain}",
                        recommended_action="Block throwaway domains or switch Meta Instant Form from 'More Volume' to 'Higher Intent'.",
                    )
                )
            elif email in GENERIC_FAKE_EMAILS or local_part in ("test", "asdf", "fake", "none"):
                findings.append(
                    QualityFinding(
                        id=f"email-fake-{lead.lead_id}",
                        category=QualityCategory.DISPOSABLE_EMAIL,
                        severity=Severity.HIGH,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Dummy / Fake Email Pattern: '{email}'",
                        description=f"Lead submitted with dummy placeholder email address '{email}'.",
                        metric_detail="Generic dummy address heuristic match",
                        recommended_action="Add custom validation question or switch to landing page lead capture.",
                    )
                )

        return findings
