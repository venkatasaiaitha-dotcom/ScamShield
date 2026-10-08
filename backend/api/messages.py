from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from ..models.schemas import IncomingMessage, MessageAnalysis, URLAnalysisResult
from ..agents.scamshield_agent import scamshield_agent
from ..connectors.demo_connector import DEMO_SCENARIOS
from ..services.url_analyzer import URLAnalyzer
from ..services.image_analyzer import ImageAnalyzer
from ..ml.classifier import classifier
from ..security.deps import get_current_user, verify_webhook_auth
from ..security.rate_limiter import rate_limit
from ..database import get_user_by_email, get_campaigns
from ..config import ADMIN_EMAIL

router = APIRouter(prefix="/api", tags=["Messages & Analysis"])

EXPO_DRILL_SCENARIOS = [
    {
        "id": "DRILL_FAKE_KYC",
        "title": "1. Fake Bank KYC Phishing (Multi-Stage Kill Chain)",
        "scenario_type": "FAKE_KYC",
        "sender": "SBI-ALERT",
        "channel": "SMS",
        "content": "Dear Customer, Your SBI NetBanking KYC has expired today. Your account and card will be deactivated in 12 hours. Update KYC immediately at: http://sbi-kyc-verify-portal.in/login",
        "key_features": ["Attack Chain: Credential Theft (Stage 3)", "Typosquatting (.in/login deceptive path)", "Adversary Next-Move Forecast"]
    },
    {
        "id": "DRILL_UPI_SCAM",
        "title": "2. Electricity Bill Cutoff (UPI Payment Entity Mismatch)",
        "scenario_type": "UTILITY_IMPERSONATION",
        "sender": "BESCOM-POWER",
        "channel": "SMS",
        "content": "Dear Consumer, Electricity power will be disconnected tonight at 9:30 PM due to unpaid bill of ₹1,480. Pay immediately via UPI to electricity-billdesk@okaxis to avoid penalty.",
        "key_features": ["UPI Payment Safety: HIGH RISK DO NOT PAY", "Critical Mismatch: BESCOM vs Personal Axis VPA", "Psychological Panic Deadline"]
    },
    {
        "id": "DRILL_JOB_SCAM",
        "title": "3. Part-Time Telegram Job Trap (Hinglish Code-Mix)",
        "scenario_type": "JOB_SCAM",
        "sender": "+91-98765-43210",
        "channel": "WHATSAPP",
        "content": "Part-Time Work From Home! Rozana ₹3,000 se ₹8,000 kamaye YouTube videos like karke. Joining ke liye turant ₹499 registration kit fee UPI karein quick-work@ybl par.",
        "key_features": ["Indian Multilingual: Hinglish Detected", "Advance Fee Trap", "Attack Chain: Trust Building ➔ Payment Attempt"]
    },
    {
        "id": "DRILL_COURIER_SCAM",
        "title": "4. Courier Delivery Interception (Quishing QR & Redirection)",
        "scenario_type": "DELIVERY_SCAM",
        "sender": "IndiaPost-Notice",
        "channel": "SMS",
        "content": "Your parcel #AMZ-9918 could not be delivered due to incomplete street address. Update address within 24 hours at http://indiapost-update-address.top/redirection or package will be returned.",
        "key_features": ["Scam DNA: Phishing URL (.top TLD)", "Short-fuse Artificial Deadline", "Redirection Trap"]
    },
    {
        "id": "DRILL_INVESTMENT_SCAM",
        "title": "5. Crypto / High-Yield Scheme (Greed Bait & Advance Loss)",
        "scenario_type": "INVESTMENT_SCAM",
        "sender": "CryptoYield-VIP",
        "channel": "WHATSAPP",
        "content": "Guaranteed 200% return in 48 hours! Institutional algorithmic crypto pool. Send minimum ₹10,000 to pool wallet VPA cryptopool@ybl before slot expires.",
        "key_features": ["Attack Chain: Payment Attempt (Stage 4)", "Financial Greed Bait", "Unverified Crypto VPA Handle"]
    }
]

class ScenarioRequest(BaseModel):
    scenario_type: Optional[str] = Field("RANDOM", max_length=50)

class URLCheckRequest(BaseModel):
    url: str = Field(..., min_length=3, max_length=2048)

class MessageCheckRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=100000)
    sender: Optional[str] = Field("Manual Inspection", max_length=320)

class ImageCheckRequest(BaseModel):
    image_b64: Optional[str] = Field(None, max_length=5000000)
    extracted_text: Optional[str] = Field(None, max_length=50000)
    qr_payload: Optional[str] = Field(None, max_length=5000)

@router.get("/messages/scenarios")
async def list_scenarios():
    """Lists available demo scenarios for live interactive testing"""
    return DEMO_SCENARIOS

@router.get("/expo/drills")
async def list_expo_drills():
    """Returns 5 predefined Expo Demo / Cyber Drill test scenarios"""
    return EXPO_DRILL_SCENARIOS

@router.get("/campaigns")
async def list_scam_campaigns(limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Returns active Scam DNA campaigns with variant counts and community immunity stats"""
    return get_campaigns(limit)

@router.post("/messages/incoming")
async def receive_incoming_message(
    msg: IncomingMessage,
    current_user: dict = Depends(get_current_user)
):
    """
    Receives incoming message from any connected source and runs it
    through the ScamShield AI Agent under the user's isolated tenancy.
    """
    user_id = current_user.get("id")
    res = await scamshield_agent.process_incoming_message(
        msg.model_dump(),
        default_source=msg.source,
        user_id=user_id
    )
    return res

@router.post("/messages/simulate-scenario")
async def simulate_scenario(
    req: ScenarioRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Triggers an incoming message simulation from preset test scenarios
    or random stream to demonstrate the proactive AI agent in action.
    """
    user_id = current_user.get("id")
    generated = scamshield_agent.demo_connector.generate_scenario(req.scenario_type)
    res = await scamshield_agent.process_incoming_message(
        generated,
        default_source="DEMO",
        user_id=user_id
    )
    return res

@router.post(
    "/analyze/message",
    dependencies=[Depends(rate_limit(max_requests=30, window_seconds=60, group="analyze_msg"))]
)
async def analyze_message_direct(
    req: MessageCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Ad-hoc manual inspection endpoint if user explicitly requests analysis.
    Protected with authentication, length constraints, and rate limiting.
    """
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be blank.")
    res = classifier.process(req.content, req.sender or "Manual Inspection")
    return res

@router.post(
    "/analyze/url",
    dependencies=[Depends(rate_limit(max_requests=25, window_seconds=60, group="analyze_url"))]
)
async def analyze_url_direct(
    req: URLCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Safe server-side URL inspection endpoint protected with SSRF filters,
    strict length bounds, and sliding-window rate limiting.
    """
    clean_url = req.url.strip()
    if not clean_url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    res = URLAnalyzer.analyze_url(clean_url)
    return res

@router.post(
    "/analyze/image",
    dependencies=[Depends(rate_limit(max_requests=25, window_seconds=60, group="analyze_img"))]
)
async def analyze_image_direct(
    req: ImageCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Visual and QR Code / Quishing threat inspection endpoint.
    Detects QR phishing links, payment redirects, and image-based text lures.
    """
    res = ImageAnalyzer.analyze_qr_or_image(
        image_data_b64=req.image_b64,
        extracted_text=req.extracted_text,
        qr_payload=req.qr_payload
    )
    return res

@router.post(
    "/webhook",
    dependencies=[
        Depends(verify_webhook_auth),
        Depends(rate_limit(max_requests=60, window_seconds=60, group="webhook"))
    ]
)
async def incoming_webhook(
    msg: IncomingMessage,
    x_user_email: Optional[str] = Header(None)
):
    """
    Part 6: Secure webhook receiver for third-party messaging integrations.
    Requires constant-time HMAC / bearer token verification.
    """
    user_id = None
    if x_user_email:
        user = get_user_by_email(x_user_email)
        if user:
            user_id = user.get("id")

    res = await scamshield_agent.process_incoming_message(
        msg.model_dump(),
        default_source="WEBHOOK",
        user_id=user_id
    )
    return {
        "status": "received",
        "analysis_id": res.get("id"),
        "risk_level": res.get("risk_level"),
        "risk_score": res.get("risk_score")
    }
