from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional, Dict, Any

from ..database import (
    get_analyses,
    get_analysis_by_id,
    delete_analysis,
    clear_user_history,
    wipe_all_data,
    record_audit_log
)
from ..models.schemas import MessageAnalysis
from ..security.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=List[MessageAnalysis])
async def list_history(
    limit: int = Query(50, ge=1, le=100),
    risk: Optional[str] = Query(None, max_length=20),
    search: Optional[str] = Query(None, max_length=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Part 14: Restricts query results strictly to the authenticated user's records."""
    return get_analyses(user_id=current_user["id"], limit=limit, risk_filter=risk, search=search)

@router.api_route("/clear", methods=["POST", "DELETE"])
async def clear_all_system_history(admin_user: Dict[str, Any] = Depends(require_admin)):
    """
    Part 4: Admin-only destructive operation.
    Requires ADMIN privileges. Rejects normal users with 403 Forbidden.
    """
    wipe_all_data()
    record_audit_log(admin_user["id"], "ALL_DATA_WIPED_ADMIN", "SUCCESS", details="Admin wiped all database records")
    return {
        "status": "success",
        "message": "All database analyses and logs have been wiped by administrator."
    }

@router.post("/clear-my-history")
async def clear_my_history(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Allows authenticated user to purge their own personal history."""
    count = clear_user_history(current_user["id"])
    record_audit_log(current_user["id"], "HISTORY_PURGED", "SUCCESS", details=f"Purged {count} personal records")
    return {
        "status": "success",
        "deleted_count": count,
        "message": "Your personal protection logs have been purged."
    }

@router.get("/{analysis_id}", response_model=MessageAnalysis)
async def get_history_detail(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    res = get_analysis_by_id(analysis_id, user_id=current_user["id"])
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found or access denied."
        )
    return res

@router.delete("/{analysis_id}")
async def remove_history_entry(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    deleted = delete_analysis(analysis_id, user_id=current_user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found or access denied."
        )
    record_audit_log(current_user["id"], "HISTORY_DELETED", "SUCCESS", details=f"Record {analysis_id} deleted")
    return {"status": "success", "message": "Record deleted", "id": analysis_id}

