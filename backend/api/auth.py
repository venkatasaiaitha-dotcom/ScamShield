import re
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

from ..security.password import hash_password, verify_password
from ..security.tokens import create_access_token, create_refresh_token, verify_token, hash_token
from ..security.rate_limiter import rate_limit
from ..security.deps import get_current_user
from ..database import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_user_password,
    store_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
    record_audit_log
)
from ..config import IS_DEV, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: Optional[str] = "USER"

class UserLoginRequest(BaseModel):
    email: str = Field(..., max_length=320)
    password: str = Field(..., min_length=1, max_length=100)

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)

class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

@router.post("/register", dependencies=[Depends(rate_limit(max_requests=5, window_seconds=60, group="auth_register"))])
async def register(req: UserRegisterRequest, request: Request, response: Response):
    ip = get_client_ip(request)
    email_clean = req.email.lower().strip()

    # Disallow registration as ADMIN directly via public endpoint
    role = "USER"
    if req.role and req.role.upper() == "ADMIN":
        # Only existing admins can assign admin; public registration defaults to USER
        role = "USER"

    existing = get_user_by_email(email_clean)
    if existing:
        record_audit_log(None, "REGISTER_FAILED_DUPLICATE", "FAILURE", ip, f"Email {email_clean} already registered")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Password validation
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")

    pwd_hash = hash_password(req.password)
    user = create_user(email_clean, pwd_hash, role=role)

    # Issue Tokens
    access_tok = create_access_token({"sub": user["id"], "role": user["role"], "email": user["email"]})
    refresh_tok = create_refresh_token({"sub": user["id"], "type": "refresh"})
    exp_iso = (datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    store_refresh_token(hash_token(refresh_tok), user["id"], exp_iso)

    record_audit_log(user["id"], "REGISTER_SUCCESS", "SUCCESS", ip, f"New user {email_clean} created")

    # Set HttpOnly Cookies
    secure_cookie = not IS_DEV
    response.set_cookie(
        key="access_token",
        value=access_tok,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_tok,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )

    return {
        "status": "success",
        "access_token": access_tok,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@router.post("/login", dependencies=[Depends(rate_limit(max_requests=10, window_seconds=60, group="auth_login"))])
async def login(req: UserLoginRequest, request: Request, response: Response):
    ip = get_client_ip(request)
    email_clean = req.email.lower().strip()

    user = get_user_by_email(email_clean)
    if not user or not verify_password(req.password, user["password_hash"]):
        record_audit_log(user["id"] if user else None, "LOGIN_FAILED", "FAILURE", ip, f"Failed login for {email_clean}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.get("is_active", True):
        record_audit_log(user["id"], "LOGIN_DISABLED_ACCOUNT", "FAILURE", ip, f"Attempted login on disabled account {email_clean}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been disabled."
        )

    # Issue Tokens
    access_tok = create_access_token({"sub": user["id"], "role": user["role"], "email": user["email"]})
    refresh_tok = create_refresh_token({"sub": user["id"], "type": "refresh"})
    exp_iso = (datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    store_refresh_token(hash_token(refresh_tok), user["id"], exp_iso)

    record_audit_log(user["id"], "LOGIN_SUCCESS", "SUCCESS", ip, f"User {email_clean} logged in")

    secure_cookie = not IS_DEV
    response.set_cookie(
        key="access_token",
        value=access_tok,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_tok,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )

    return {
        "status": "success",
        "access_token": access_tok,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@router.post("/refresh")
async def refresh_tokens(request: Request, response: Response, body: Optional[RefreshRequest] = None):
    # Extract refresh token from cookie or request body
    raw_token = request.cookies.get("refresh_token")
    if not raw_token and body and body.refresh_token:
        raw_token = body.refresh_token

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token."
        )

    payload = verify_token(raw_token, expected_type="refresh")
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    user_id = payload["sub"]
    token_h = hash_token(raw_token)
    matched_user_id = is_refresh_token_valid(token_h)
    if not matched_user_id or matched_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Revoked or invalidated refresh token."
        )

    user = get_user_by_id(user_id)
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active.")

    # Issue new access token
    new_access_tok = create_access_token({"sub": user["id"], "role": user["role"], "email": user["email"]})

    secure_cookie = not IS_DEV
    response.set_cookie(
        key="access_token",
        value=new_access_tok,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "status": "success",
        "access_token": new_access_tok,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(request: Request, response: Response, current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    ip = get_client_ip(request)
    raw_refresh = request.cookies.get("refresh_token")
    if raw_refresh:
        revoke_refresh_token(hash_token(raw_refresh))

    response.delete_cookie(key="access_token", samesite="lax")
    response.delete_cookie(key="refresh_token", samesite="lax")

    if current_user:
        record_audit_log(current_user["id"], "LOGOUT", "SUCCESS", ip, f"User {current_user['email']} logged out")

    return {"status": "success", "message": "Successfully logged out."}

@router.get("/me")
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "created_at": current_user.get("created_at")
    }

@router.post("/change-password")
async def change_password(
    req: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None
):
    ip = get_client_ip(request) if request else "127.0.0.1"

    if not verify_password(req.current_password, current_user["password_hash"]):
        record_audit_log(current_user["id"], "PASSWORD_CHANGE_FAILED", "FAILURE", ip, "Incorrect current password")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password."
        )

    if len(req.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long."
        )

    new_hash = hash_password(req.new_password)
    update_user_password(current_user["id"], new_hash)
    record_audit_log(current_user["id"], "PASSWORD_CHANGED", "SUCCESS", ip, "User changed password")

    return {"status": "success", "message": "Password changed successfully."}
