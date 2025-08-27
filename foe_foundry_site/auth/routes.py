"""Authentication routes for Google One Tap and Patreon OAuth."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlmodel import select

from .dependencies import (
    AuthContextDep,
    GOOGLE_CLIENT_ID,
    PATREON_CLIENT_ID,
    PATREON_CLIENT_SECRET,
    PATREON_REDIRECT_URI,
    RequireAuthDep,
    SessionDep,
)
from .models import AccountType, PatronStatus, PatronTier, User

router = APIRouter(prefix="/auth", tags=["authentication"])
log = logging.getLogger(__name__)


@router.post("/google")
async def auth_google(
    request: Request,
    credential: str = Form(...),
    session: SessionDep = None,
):
    """Google One Tap authentication endpoint."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(
            credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except Exception as e:
        log.error(f"Google token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    email = idinfo.get("email")
    name = idinfo.get("name")
    picture = idinfo.get("picture")
    google_id = idinfo.get("sub")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")
    
    # Check if user exists
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        # Create new user
        user = User(
            email=email,
            display_name=name,
            profile_picture=picture,
            google_id=google_id,
            account_type=AccountType.GOOGLE,
        )
        session.add(user)
    else:
        # Update existing user with Google info
        user.display_name = name or user.display_name
        user.profile_picture = picture or user.profile_picture
        user.google_id = google_id
        user.updated_at = datetime.now(timezone.utc)
        
        # Check if this user has Patreon data by email matching
        if not user.patreon_id:
            # Could potentially match Patreon data here if we had it
            pass
    
    # Reset credits if needed
    user.reset_credits_if_needed()
    session.commit()
    session.refresh(user)
    
    # Set session
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "tier": user.patron_tier.value,
    }
    
    log.info(f"Google login successful for user {user.email}")
    return JSONResponse({"detail": "Google login successful", "user": {
        "email": user.email,
        "display_name": user.display_name,
        "tier": user.patron_tier.value,
        "credits_remaining": user.get_credits_remaining(),
    }})


@router.get("/patreon")
def login_patreon():
    """Redirect to Patreon OAuth authorization."""
    if not PATREON_CLIENT_ID or not PATREON_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Patreon OAuth not configured")
    
    url = (
        f"https://www.patreon.com/oauth2/authorize?response_type=code"
        f"&client_id={PATREON_CLIENT_ID}&redirect_uri={PATREON_REDIRECT_URI}"
        f"&scope=identity%20identity.email%20identity.memberships"
    )
    return RedirectResponse(url)


@router.get("/patreon/callback")
async def patreon_callback(
    request: Request,
    code: str = Query(...),
    session: SessionDep = None,
):
    """Handle Patreon OAuth callback."""
    if not PATREON_CLIENT_ID or not PATREON_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Patreon OAuth not configured")
    
    # Exchange code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": PATREON_CLIENT_ID,
        "client_secret": PATREON_CLIENT_SECRET,
        "redirect_uri": PATREON_REDIRECT_URI,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            token_resp = await client.post(
                "https://www.patreon.com/api/oauth2/token", 
                data=token_data
            )
            token_json = token_resp.json()
            access_token = token_json.get("access_token")
            
            if not access_token:
                log.error(f"Patreon token exchange failed: {token_json}")
                raise HTTPException(status_code=400, detail="Patreon OAuth failed")
            
            # Get user identity
            headers = {"Authorization": f"Bearer {access_token}"}
            user_resp = await client.get(
                "https://www.patreon.com/api/oauth2/v2/identity?"
                "include=memberships,campaign"
                "&fields[user]=email,full_name"
                "&fields[member]=patron_status,pledge_relationship_start,campaign_lifetime_support_cents"
                "&fields[campaign]=creation_name",
                headers=headers
            )
            user_data = user_resp.json()
            
        except Exception as e:
            log.error(f"Patreon API error: {e}")
            raise HTTPException(status_code=400, detail="Failed to fetch Patreon data")
    
    # Extract user information
    user_attrs = user_data.get("data", {}).get("attributes", {})
    email = user_attrs.get("email")
    name = user_attrs.get("full_name")
    patreon_id = user_data.get("data", {}).get("id")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Patreon")
    
    # Determine patron tier from memberships
    patron_tier = PatronTier.FREE
    patron_status = None
    
    relationships = user_data.get("data", {}).get("relationships", {})
    memberships = relationships.get("memberships", {}).get("data", [])
    
    if memberships:
        # For simplicity, just check if they have any active membership
        # In a real implementation, you'd check the pledge amount or tier
        patron_tier = PatronTier.GOLD  # Simplified logic
        patron_status = PatronStatus.ACTIVE
    
    # Check if user exists
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        # Create new user with Patreon data
        user = User(
            email=email,
            display_name=name,
            patreon_id=patreon_id,
            account_type=AccountType.PATREON,
            patron_tier=patron_tier,
            patron_status=patron_status,
        )
        session.add(user)
    else:
        # Update existing user with Patreon data
        user.display_name = name or user.display_name
        user.patreon_id = patreon_id
        user.patron_tier = patron_tier
        user.patron_status = patron_status
        user.updated_at = datetime.now(timezone.utc)
    
    # Reset credits based on new tier
    user.credits_remaining = user.get_monthly_credit_limit()
    user.credits_last_reset = datetime.now(timezone.utc)
    
    session.commit()
    session.refresh(user)
    
    # Set session
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "tier": user.patron_tier.value,
    }
    
    log.info(f"Patreon login successful for user {user.email} with tier {patron_tier}")
    
    # Redirect to a success page or homepage
    return RedirectResponse("/", status_code=302)


@router.post("/logout")
def logout(request: Request):
    """Log out the current user."""
    request.session.clear()
    return JSONResponse({"detail": "Logged out successfully"})


@router.get("/me")
def get_current_user(auth_context: AuthContextDep):
    """Get current user information."""
    if auth_context.is_authenticated:
        user = auth_context.user
        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "profile_picture": user.profile_picture,
                "tier": user.patron_tier.value,
                "credits_remaining": auth_context.get_credits_remaining(),
                "account_type": user.account_type.value,
            }
        }
    else:
        return {
            "authenticated": False,
            "anonymous": {
                "tier": "anonymous",
                "credits_remaining": auth_context.get_credits_remaining(),
                "credits_limit": auth_context.anon_session.get_credit_limit(),
            }
        }


@router.get("/status")
def get_auth_status(auth_context: AuthContextDep):
    """Get authentication status for frontend."""
    return {
        "authenticated": auth_context.is_authenticated,
        "tier": auth_context.get_tier_name().lower(),
        "credits_remaining": auth_context.get_credits_remaining(),
        "can_generate": auth_context.can_use_credits(1),
    }