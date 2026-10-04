import hmac
import hashlib
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

from .tokens import verify_token
from ..config import SCAMSHIELD_WEBHOOK_SECRET

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Dict[str, Any]:
    from ..database.connection import get_user_by_id
    """
    Extracts and authenticates user from HttpOnly access_token cookie or Bearer token header.
    Returns the authenticated user record or raises 401 Unauthorized.
    """
    token: Optional[str] = None

    # Check HttpOnly cookie first
    if "access_token" in request.cookies:
        token = request.cookies.get("access_token")
    # Fallback to Authorization: Bearer <token>
    elif auth_header and auth_header.credentials:
        token = auth_header.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or have expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = verify_token(token, expected_type="access")
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload["sub"]
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists."
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been disabled."
        )

    return user

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Part 4: Restricts destructive operations to users with ADMIN role.
    Returns HTTP 403 Forbidden with standard safe message if not admin.
    """
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    return current_user

async def get_optional_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[Dict[str, Any]]:
    try:
        return await get_current_user(request, auth_header)
    except HTTPException:
        return None

async def verify_webhook_auth(request: Request) -> bool:
    """
    Part 6: Verifies incoming webhook requests using HMAC or constant-time secret comparison.
    Rejects unauthorized requests with 401 Unauthorized.
    """
    # Check X-Webhook-Signature or Authorization token header
    token = request.headers.get("x-webhook-token") or request.headers.get("x-webhook-signature")
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook authentication token or signature."
        )

    # Constant-time comparison to prevent timing attacks
    expected = SCAMSHIELD_WEBHOOK_SECRET.encode("utf-8")
    provided = token.encode("utf-8")

    if not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature."
        )
    return True
