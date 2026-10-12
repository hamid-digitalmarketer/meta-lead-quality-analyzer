import csv
from pathlib import Path
from typing import List, Optional

from meta_lead_quality_analyzer.models import CRMDealRow, MetaLeadRow


def _parse_float(val: Optional[str], default: float = 0.0) -> float:
    if not val or val.strip() == "":
        return default
    try:
        return float(val.strip().replace("$", "").replace(",", ""))
    except ValueError:
        return default


def load_meta_leads(csv_path: Path | str) -> List[MetaLeadRow]:
    path = Path(csv_path)
    rows: List[MetaLeadRow] = []
    with open(path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                MetaLeadRow(
                    lead_id=r.get("lead_id", "").strip(),
                    created_time=r.get("created_time", "").strip(),
                    campaign_name=r.get("campaign_name", "").strip(),
                    ad_name=r.get("ad_name", "").strip(),
                    form_name=r.get("form_name", "").strip(),
                    full_name=r.get("full_name", "").strip(),
                    email=r.get("email", "").strip(),
                    phone_number=r.get("phone_number", "").strip(),
                    completion_time_sec=_parse_float(r.get("completion_time_sec"), 0.0),
                    custom_answer_timeline=r.get("custom_answer_timeline") or None,
                    custom_answer_budget=r.get("custom_answer_budget") or None,
                    cost_per_lead=_parse_float(r.get("cost_per_lead"), 0.0),
                )
            )
    return rows


def load_crm_deals(csv_path: Path | str) -> List[CRMDealRow]:
    path = Path(csv_path)
    rows: List[CRMDealRow] = []
    with open(path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                CRMDealRow(
                    lead_id=r.get("lead_id", "").strip(),
                    crm_stage=r.get("crm_stage", "").strip(),
                    opportunity_value=_parse_float(r.get("opportunity_value"), 0.0),
                    closed_date=r.get("closed_date") or None,
                )
            )
    return rows
