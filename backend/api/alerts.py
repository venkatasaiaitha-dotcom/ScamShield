from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any

from ..database import get_alerts, mark_alert_read, mark_all_alerts_read, delete_alert
from ..models.schemas import AlertItem
from ..security.deps import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertItem])
async def list_alerts(
    unread_only: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Part 20: Returns user-specific alerts."""
    return get_alerts(user_id=current_user["id"], unread_only=unread_only)

@router.post("/{alert_id}/read")
async def mark_read(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    updated = mark_alert_read(alert_id, user_id=current_user["id"])
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return {"status": "success", "id": alert_id, "is_read": True}

@router.post("/mark-all-read")
async def mark_all_read(current_user: Dict[str, Any] = Depends(get_current_user)):
    mark_all_alerts_read(user_id=current_user["id"])
    return {"status": "success", "message": "All alerts marked as read"}

@router.delete("/{alert_id}")
async def remove_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    deleted = delete_alert(alert_id, user_id=current_user["id"])
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return {"status": "success", "id": alert_id, "message": "Alert deleted"}
