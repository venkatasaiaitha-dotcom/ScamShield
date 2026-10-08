from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from ..database import (
    save_community_report,
    get_community_reports,
    upvote_community_report
)
from ..security.deps import get_current_user
from ..security.rate_limiter import rate_limit

router = APIRouter(prefix="/api/community", tags=["Community Threat Radar"])

class CommunityReportRequest(BaseModel):
    threat_title: str = Field(..., min_length=3, max_length=150)
    sender: Optional[str] = Field("Unknown", max_length=200)
    category: str = Field(..., max_length=50)
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field("HIGH", max_length=20)
    indicators: Optional[List[str]] = Field(default_factory=list)

@router.get(
    "/feed",
    dependencies=[Depends(rate_limit(max_requests=60, window_seconds=60, group="comm_feed"))]
)
async def list_community_feed(limit: int = 30):
    """
    Returns latest crowdsourced scam reports from the ScamShield community radar.
    Allows users to see emerging threats before they receive them.
    """
    return get_community_reports(limit=limit)

@router.post(
    "/report",
    dependencies=[Depends(rate_limit(max_requests=20, window_seconds=60, group="comm_report"))]
)
async def submit_community_report(
    req: CommunityReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Publishes an identified scam threat to the community radar so other
    users and organizations are protected against identical patterns.
    """
    user_id = current_user.get("id", "anonymous")
    result = save_community_report(user_id, req.model_dump())
    return {
        "status": "success",
        "message": "Threat successfully reported to the ScamShield Community Radar",
        "report_id": result.get("id")
    }

@router.post(
    "/{report_id}/upvote",
    dependencies=[Depends(rate_limit(max_requests=30, window_seconds=60, group="comm_upvote"))]
)
async def upvote_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Upvotes a confirmed scam pattern. High-upvote items trigger priority heuristics.
    """
    new_count = upvote_community_report(report_id)
    return {"status": "success", "report_id": report_id, "upvotes": new_count}
