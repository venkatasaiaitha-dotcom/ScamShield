from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from ..models.schemas import IncomingMessage, MessageAnalysis, URLAnalysisResult
from ..agents.scamshield_agent import scamshield_agent
from ..connectors.demo_connector import DEMO_SCENARIOS
from ..services.url_analyzer import URLAnalyzer
from ..ml.classifier import classifier
from ..security.deps import get_current_user, verify_webhook_auth
from ..security.rate_limiter import rate_limit
from ..database import get_user_by_email
from ..config import ADMIN_EMAIL

router = APIRouter(prefix="/api", tags=["Messages & Analysis"])

class ScenarioRequest(BaseModel):
    scenario_type: Optional[str] = Field("RANDOM", max_length=50)

class URLCheckRequest(BaseModel):
    url: str = Field(..., min_length=3, max_length=2048)

class MessageCheckRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=100000)
    sender: Optional[str] = Field("Manual Inspection", max_length=320)

@router.get("/messages/scenarios")
async def list_scenarios():
    """Lists available demo scenarios for live interactive testing"""
    return DEMO_SCENARIOS

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
