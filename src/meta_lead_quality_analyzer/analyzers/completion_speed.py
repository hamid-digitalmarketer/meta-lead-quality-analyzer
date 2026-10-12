from typing import List

from meta_lead_quality_analyzer.models import MetaLeadRow, QualityCategory, QualityFinding, Severity


class CompletionSpeedAnalyzer:
    """Detects bot submissions and accidental instant-form auto-fill mis-clicks based on submission duration."""

    def __init__(self, speed_threshold_sec: float = 5.0):
        self.speed_threshold_sec = speed_threshold_sec

    def analyze(self, leads: List[MetaLeadRow]) -> List[QualityFinding]:
        findings: List[QualityFinding] = []

        for lead in leads:
            duration = lead.completion_time_sec
            if duration <= 0:
                continue

            if duration < self.speed_threshold_sec:
                findings.append(
                    QualityFinding(
                        id=f"speed-bot-{lead.lead_id}",
                        category=QualityCategory.SPEED_CLICKER_BOT,
                        severity=Severity.HIGH,
                        lead_id=lead.lead_id,
                        lead_name=lead.full_name,
                        title=f"Sub-5-Second Instant Form Submission ({duration:.1f}s)",
                        description=(
                            f"Lead submitted full Instant Form in {duration:.1f} seconds. "
                            "Typical human engagement on multi-field forms requires 15–40 seconds. "
                            "This pattern strongly indicates auto-fill mis-clicks or bot scraping."
                        ),
                        metric_detail=f"Duration: {duration:.1f}s < threshold {self.speed_threshold_sec:.1f}s",
                        recommended_action=(
                            "Enable Meta Instant Form 'Higher Intent' review step (slide to submit), "
                            "or add custom multiple-choice gating questions that cannot be auto-filled."
                        ),
                    )
                )

        return findings
