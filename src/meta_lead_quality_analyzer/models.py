from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class QualityCategory(str, Enum):
    DISPOSABLE_EMAIL = "disposable_email"
    INVALID_PHONE = "invalid_phone"
    SPEED_CLICKER_BOT = "speed_clicker_bot"
    GIBBERISH_CUSTOM_ANSWER = "gibberish_custom_answer"
    CRM_DISQUALIFICATION = "crm_disqualification"
    UNQUALIFIED_DROP_OFF = "unqualified_drop_off"


class QualityFinding(BaseModel):
    id: str
    category: QualityCategory
    severity: Severity
    lead_id: str
    lead_name: Optional[str] = None
    title: str
    description: str
    metric_detail: str
    recommended_action: str


class MetaLeadRow(BaseModel):
    lead_id: str
    created_time: str
    campaign_name: str
    ad_name: str
    form_name: str
    full_name: str
    email: str
    phone_number: str
    completion_time_sec: float
    custom_answer_timeline: Optional[str] = None
    custom_answer_budget: Optional[str] = None
    cost_per_lead: float = 0.0


class CRMDealRow(BaseModel):
    lead_id: str
    crm_stage: str
    opportunity_value: float = 0.0
    closed_date: Optional[str] = None


class LeadQualitySummary(BaseModel):
    total_leads_audited: int
    total_ad_spend: float
    front_end_cpl: float
    qualified_leads_count: int
    true_cpql: float
    junk_lead_count: int
    junk_lead_rate_pct: float
    disposable_email_count: int
    invalid_phone_count: int
    speed_clicker_count: int
    crm_disqualified_count: int


class LeadAuditResult(BaseModel):
    audit_id: str
    created_at: str
    summary: LeadQualitySummary
    findings: List[QualityFinding] = Field(default_factory=list)
