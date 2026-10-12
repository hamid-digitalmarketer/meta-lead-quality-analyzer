from typing import List

from meta_lead_quality_analyzer.models import MetaLeadRow, QualityCategory, QualityFinding, Severity

GIBBERISH_ANSWERS = {
    "asdf",
    "asdfg",
    "qwerty",
    "test",
    "testing",
    "idk",
    "none",
    "na",
    "n/a",
    "no",
    "nope",
    ".",
    "..",
    "-",
    "xxx",
    "123",
}


class CustomQuestionAnalyzer:
    """Evaluates user-provided answers to custom qualification questions for low-effort gibberish."""

    def analyze(self, leads: List[MetaLeadRow]) -> List[QualityFinding]:
        findings: List[QualityFinding] = []

        for lead in leads:
            answers = [
                ("timeline", lead.custom_answer_timeline),
                ("budget", lead.custom_answer_budget),
            ]

            for field_name, ans in answers:
                if not ans:
                    continue
                clean = ans.strip().lower()

                if clean in GIBBERISH_ANSWERS or (len(clean) <= 2 and not clean.isdigit()):
                    findings.append(
                        QualityFinding(
                            id=f"gibberish-{field_name}-{lead.lead_id}",
                            category=QualityCategory.GIBBERISH_CUSTOM_ANSWER,
                            severity=Severity.MEDIUM,
                            lead_id=lead.lead_id,
                            lead_name=lead.full_name,
                            title=f"Gibberish / Low-Effort Custom Answer: '{ans}'",
                            description=(
                                f"Custom question '{field_name}' answered with dismissive or nonsense input '{ans}'."
                            ),
                            metric_detail=f"Field '{field_name}' = '{clean}' matched gibberish heuristic",
                            recommended_action=(
                                "Switch free-text custom questions to strict dropdown menus or multiple-choice options."
                            ),
                        )
                    )

        return findings
