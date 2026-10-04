from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from pydantic import BaseModel

from ..database import get_sources, update_source_status
from ..models.schemas import MessageSource
from ..security.deps import get_current_user

router = APIRouter(prefix="/api/sources", tags=["Sources"])

@router.get("", response_model=List[MessageSource])
async def list_sources(current_user: Dict[str, Any] = Depends(get_current_user)):
    return get_sources(user_id=current_user["id"])

@router.post("/{source_id}/connect")
async def connect_source(
    source_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    sources = get_sources(user_id=current_user["id"])
    matched = [s for s in sources if s["id"] == source_id]
    if not matched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.")

    target = matched[0]
    if target["source_type"] == "MESSAGING_API":
        update_source_status(current_user["id"], source_id, "CONNECTED", "GRANTED")
        return {
            "status": "success",
            "source_id": source_id,
            "message": "Messaging webhook channel authorized and connected."
        }

    update_source_status(current_user["id"], source_id, "CONNECTED", "GRANTED")
    return {"status": "success", "source_id": source_id, "state": "CONNECTED"}

@router.post("/{source_id}/disconnect")
async def disconnect_source(
    source_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    update_source_status(current_user["id"], source_id, "DISCONNECTED", "REQUIRED")
    return {"status": "success", "source_id": source_id, "state": "DISCONNECTED"}
