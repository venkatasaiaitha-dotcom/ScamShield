from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..database import (
    get_settings,
    update_settings,
    update_source_status,
    wipe_all_data,
    get_stats,
    add_audit_log
)
from ..services.gmail_service import gmail_service
from ..agents.scamshield_agent import scamshield_agent
from ..services.notification_service import notification_service
from ..security.deps import get_current_user, require_admin
from ..config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

router = APIRouter(prefix="/api/gmail", tags=["Gmail Integration"])

class GmailInputRequest(BaseModel):
    sender: str = Field(..., max_length=320, description="Sender email address")
    subject: str = Field(..., max_length=500, description="Email subject line")
    body: str = Field(..., min_length=1, max_length=100000, description="Email body content")

class GmailConnectSessionRequest(BaseModel):
    email: str = Field(..., max_length=320)
    app_password: str = Field(..., max_length=100)

@router.get("/status")
async def get_gmail_status(current_user: dict = Depends(get_current_user)):
    """
    Returns the Gmail integration status for the authenticated user.
    Never exposes stored credentials or plaintext passwords.
    """
    user_id = current_user.get("id")
    settings = get_settings(user_id=user_id)
    email_addr = settings.get("gmail_email", "")
    is_connected = settings.get("gmail_connected", False)
    last_sync = settings.get("gmail_last_sync", "")

    # Mask email address for privacy
    masked_email = ""
    if email_addr and "@" in email_addr:
        parts = email_addr.split("@")
        masked_email = f"{parts[0][:3]}***@{parts[1]}"

    oauth_ready = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    return {
        "connected": bool(is_connected),
        "email": email_addr,
        "masked_email": masked_email,
        "last_sync": last_sync,
        "oauth_configured": oauth_ready,
        "direct_input_ready": True
    }

@router.post("/connect-session")
async def connect_gmail_session(
    req: GmailConnectSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Validates IMAP credentials without storing passwords in plaintext in the database.
    Updates the connected state for the active session.
    """
    if not req.email or not req.app_password:
        raise HTTPException(status_code=400, detail="Gmail address and App Password are required.")

    user_id = current_user.get("id")
    success, message = gmail_service.test_connection(req.email, req.app_password)
    if not success:
        add_audit_log(
            user_id=user_id,
            action="GMAIL_CONNECT_FAIL",
            status="FAILED",
            details=f"Connection attempt failed for {req.email}"
        )
        raise HTTPException(status_code=401, detail=message)

    # Save ONLY email address and connected flag — NEVER store password plaintext
    update_settings({
        "gmail_email": req.email.strip(),
        "gmail_connected": "true",
        "gmail_last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, user_id=user_id)
    update_source_status("src-gmail", "CONNECTED", "GRANTED", user_id=user_id)

    add_audit_log(
        user_id=user_id,
        action="GMAIL_CONNECT",
        status="SUCCESS",
        details=f"Secure connection verified for {req.email}"
    )

    return {
        "status": "success",
        "message": f"Successfully authenticated with Gmail for {req.email}. (Zero plaintext password stored)"
    }

@router.post("/disconnect")
async def disconnect_gmail(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    update_settings({
        "gmail_connected": "false"
    }, user_id=user_id)
    update_source_status("src-gmail", "DISCONNECTED", "REQUIRED", user_id=user_id)
    
    add_audit_log(
        user_id=user_id,
        action="GMAIL_DISCONNECT",
        status="SUCCESS",
        details="Gmail integration disconnected"
    )
    return {"status": "success", "message": "Gmail account disconnected."}

@router.post("/input")
async def input_gmail_message(
    req: GmailInputRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Direct Message Input Inspection Mode.
    Inspects email content (Sender, Subject, Body) through ScamShield's AI Agent
    under the user's isolated tenancy without requiring third-party credentials.
    """
    user_id = current_user.get("id")
    full_content = f"Subject: {req.subject.strip()}\n\n{req.body.strip()}"
    msg_payload = {
        "source": "GMAIL",
        "sender": req.sender.strip() or "Inbound Email",
        "recipient": current_user.get("email", "You"),
        "content": full_content,
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "metadata": {
            "subject": req.subject.strip(),
            "channel": "GMAIL_DIRECT_INPUT"
        }
    }

    res = await scamshield_agent.process_incoming_message(
        msg_payload,
        default_source="GMAIL",
        user_id=user_id
    )
    return res

# Admin / Destructive Wipe Endpoint
@router.post("/wipe-data")
async def wipe_data(admin_user: dict = Depends(require_admin)):
    """
    Part 4: Restricts destructive wipe operation to ADMIN users.
    Normal users receive HTTP 403 Forbidden.
    """
    wipe_all_data()
    stats = get_stats()

    add_audit_log(
        user_id=admin_user.get("id"),
        action="SYSTEM_WIPE_DATA",
        status="SUCCESS",
        details=f"Admin {admin_user.get('email')} wiped all database messages and alerts."
    )

    # Broadcast reset to frontend WebSocket clients
    await notification_service.broadcast("DATA_WIPED", {
        "stats": stats,
        "message": "All database data has been wiped by system administrator."
    })

    return {
        "status": "success",
        "message": "All database messages, alerts, and metrics have been completely wiped out.",
        "stats": stats
    }
