from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "LOW"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH = "HIGH"

class ScamCategory(str, Enum):
    NORMAL = "NORMAL"
    PHISHING = "PHISHING"
    FAKE_KYC = "FAKE_KYC"
    BANK_IMPERSONATION = "BANK_IMPERSONATION"
    DELIVERY_SCAM = "DELIVERY_SCAM"
    JOB_SCAM = "JOB_SCAM"
    INVESTMENT_SCAM = "INVESTMENT_SCAM"
    LOTTERY_PRIZE = "LOTTERY_PRIZE"
    GOVERNMENT_IMPERSONATION = "GOVERNMENT_IMPERSONATION"
    ACCOUNT_SUSPENSION = "ACCOUNT_SUSPENSION"
    TECH_SUPPORT = "TECH_SUPPORT"
    UPI_FRAUD = "UPI_FRAUD"
    WHATSAPP_FAMILY_IMPERSONATION = "WHATSAPP_FAMILY_IMPERSONATION"
    UTILITY_IMPERSONATION = "UTILITY_IMPERSONATION"
    SUSPICIOUS_OTHER = "SUSPICIOUS_OTHER"

class URLAnalysisResult(BaseModel):
    url: str
    domain: str
    is_https: bool
    is_ip_address: bool
    is_shortener: bool
    is_lookalike: bool
    suspicious_flags: List[str] = Field(default_factory=list)
    risk_contribution: int = 0

class AnalysisReason(BaseModel):
    title: str
    description: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH

class ActionRecommendations(BaseModel):
    donts: List[str] = Field(default_factory=list)
    dos: List[str] = Field(default_factory=list)

class IncomingMessage(BaseModel):
    id: Optional[str] = None
    source: str = Field(default="DEMO", max_length=50)
    sender: str = Field(..., max_length=320)
    recipient: Optional[str] = Field(default="User", max_length=320)
    timestamp: Optional[str] = Field(default=None, max_length=50)
    content: str = Field(..., min_length=1, max_length=100000)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MessageAnalysis(BaseModel):
    id: str
    message_id: str
    source: str
    sender: str
    content_preview: str
    full_content: Optional[str] = None
    timestamp: str
    risk_score: int  # 0 to 100
    risk_level: RiskLevel
    category: ScamCategory
    summary: str
    reasons: List[AnalysisReason] = Field(default_factory=list)
    recommendations: ActionRecommendations
    urls_detected: List[URLAnalysisResult] = Field(default_factory=list)
    technical_details: Dict[str, Any] = Field(default_factory=dict)

class AlertItem(BaseModel):
    id: str
    analysis_id: str
    risk_level: RiskLevel
    risk_score: int
    category: ScamCategory
    sender: str
    summary: str
    timestamp: str
    is_read: bool = False
    reasons_summary: List[str] = Field(default_factory=list)

class MessageSource(BaseModel):
    id: str
    name: str
    source_type: str
    status: str  # CONNECTED, DISCONNECTED, RESTRICTED
    permission_status: str  # GRANTED, REQUIRED, UNSUPPORTED
    permission_info: str
    description: str
    icon: str
    message_count: int = 0
    last_synced: Optional[str] = None

class AgentStatusResponse(BaseModel):
    protection_active: bool
    status_label: str
    monitoring_sources: List[str]
    messages_checked: int
    threats_detected: int
    high_risk_count: int
    suspicious_count: int
    last_active: str

class SettingsModel(BaseModel):
    protection_enabled: bool = True
    appearance: str = Field(default="light", pattern="^(light|dark|system)$")
    auto_alert_high: bool = True
    auto_alert_suspicious: bool = True
    high_risk_threshold: int = Field(default=70, ge=50, le=95)
    suspicious_threshold: int = Field(default=30, ge=10, le=60)
    privacy_minimal_metadata: bool = True
    data_retention_days: int = Field(default=30, ge=1, le=365)
    sound_alerts: bool = True
