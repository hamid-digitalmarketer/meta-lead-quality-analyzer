import hashlib
import json
import time
from pathlib import Path
from typing import List

from meta_lead_quality_analyzer.models import CRMDealRow, MetaLeadRow


def _sha256(val: str) -> str:
    if not val:
        return ""
    return hashlib.sha256(val.strip().lower().encode("utf-8")).hexdigest()


class MetaCAPIOfflineExporter:
    """Exports offline conversion event payloads for Meta Conversions API (CAPI) value optimization."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, leads: List[MetaLeadRow], deals: List[CRMDealRow]) -> Path:
        deals_by_id = {d.lead_id: d for d in deals}
        events = []

        for lead in leads:
            deal = deals_by_id.get(lead.lead_id)
            if not deal:
                continue

            stage = deal.crm_stage.lower()
            event_name = "Lead"
            val = 0.0

            if stage in ("qualified", "proposal"):
                event_name = "QualifiedLead"
                val = deal.opportunity_value or 50.0
            elif stage in ("won", "closed_won"):
                event_name = "Purchase"
                val = deal.opportunity_value or 500.0

            events.append(
                {
                    "event_name": event_name,
                    "event_time": int(time.time()),
                    "action_source": "system_generated",
                    "user_data": {
                        "lead_id": lead.lead_id,
                        "em": [_sha256(lead.email)] if lead.email else [],
                        "ph": [_sha256(lead.phone_number)] if lead.phone_number else [],
                    },
                    "custom_data": {
                        "currency": "USD",
                        "value": val,
                        "crm_stage": deal.crm_stage,
                        "campaign": lead.campaign_name,
                    },
                }
            )

        out_path = self.output_dir / "meta_capi_offline_events.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"data": events}, f, indent=2)

        return out_path
