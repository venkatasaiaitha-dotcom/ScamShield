from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..database import get_settings, update_settings, add_audit_log
from ..models.schemas import SettingsModel
from ..security.deps import get_current_user

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=SettingsModel)
async def fetch_settings(current_user: dict = Depends(get_current_user)):
    """Fetch settings isolated for the authenticated user"""
    user_id = current_user.get("id")
    s = get_settings(user_id=user_id)
    return SettingsModel(**s)

@router.post("", response_model=SettingsModel)
async def save_settings(new_settings: SettingsModel, current_user: dict = Depends(get_current_user)):
    """Update settings isolated for the authenticated user"""
    user_id = current_user.get("id")
    update_data = new_settings.model_dump()
    update_settings(update_data, user_id=user_id)
    
    add_audit_log(
        user_id=user_id,
        action="SETTINGS_UPDATE",
        status="SUCCESS",
        details="User preferences updated successfully."
    )
    
    s = get_settings(user_id=user_id)
    return SettingsModel(**s)
