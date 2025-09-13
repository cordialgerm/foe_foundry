"""Authentication routes for Google One Tap and Patreon OAuth."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlmodel import select

from .database import check_database_health
from .dependencies import (
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
    DISCORD_REDIRECT_URI,
    GOOGLE_CLIENT_ID,
    PATREON_CLIENT_ID,
    PATREON_CLIENT_SECRET,
    PATREON_REDIRECT_URI,
    AuthContextDep,
    SessionDep,
)
from .models import AccountType, PatronStatus, PatronTier, User
from .schemas import (
    AnonymousInfo,
    AuthGoogleResponse,
    AuthMeResponse,
    AuthStatusResponse,
    CreditsInfo,
    LogoutResponse,
    UserInfo,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
log = logging.getLogger(__name__)


@router.get("/demo")
def auth_demo():
    """Serve the authentication demo page."""
    return FileResponse("demo_auth.html", media_type="text/html")


@router.post("/google", response_model=AuthGoogleResponse)
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
    return AuthGoogleResponse(
        detail="Google login successful",
        user=UserInfo(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            profile_picture=user.profile_picture,
            tier=user.patron_tier.value,
            account_type=user.account_type.value,
        ),
    )


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
                "https://www.patreon.com/api/oauth2/token", data=token_data
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
                headers=headers,
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


@router.get("/discord")
def login_discord():
    """Redirect to Discord OAuth authorization."""
    if not DISCORD_CLIENT_ID or not DISCORD_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Discord OAuth not configured")

    url = (
        f"https://discord.com/api/oauth2/authorize?response_type=code"
        f"&client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&scope=identify%20email"
    )
    return RedirectResponse(url)


@router.get("/discord/callback")
async def discord_callback(
    request: Request,
    code: str = Query(...),
    session: SessionDep = None,
):
    """Handle Discord OAuth callback."""
    if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Discord OAuth not configured")

    # Exchange code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        try:
            token_resp = await client.post(
                "https://discord.com/api/oauth2/token",
                data=token_data,
                auth=(DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_json = token_resp.json()
            access_token = token_json.get("access_token")

            if not access_token:
                log.error(f"Discord token exchange failed: {token_json}")
                raise HTTPException(status_code=400, detail="Discord OAuth failed")

            # Get user identity
            headers = {"Authorization": f"Bearer {access_token}"}
            user_resp = await client.get(
                "https://discord.com/api/users/@me", headers=headers
            )
            user_data = user_resp.json()

        except Exception as e:
            log.error(f"Discord API error: {e}")
            raise HTTPException(status_code=400, detail="Failed to fetch Discord data")

    # Extract user information
    email = user_data.get("email")
    username = user_data.get("username")
    discriminator = user_data.get("discriminator")
    discord_id = user_data.get("id")
    avatar_hash = user_data.get("avatar")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Discord")

    # Build display name and profile picture
    display_name = (
        f"{username}#{discriminator}"
        if discriminator and discriminator != "0"
        else username
    )
    profile_picture = None
    if avatar_hash:
        profile_picture = (
            f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png"
        )

    # Check if user exists
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        # Create new user with Discord data
        user = User(
            email=email,
            display_name=display_name,
            profile_picture=profile_picture,
            discord_id=discord_id,
            account_type=AccountType.DISCORD,
        )
        session.add(user)
    else:
        # Update existing user with Discord data
        user.display_name = display_name or user.display_name
        user.profile_picture = profile_picture or user.profile_picture
        user.discord_id = discord_id
        user.updated_at = datetime.now(timezone.utc)

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

    log.info(f"Discord login successful for user {user.email}")

    # Redirect to a success page or homepage
    return RedirectResponse("/", status_code=302)


@router.post("/logout", response_model=LogoutResponse)
def logout(request: Request):
    """Log out the current user."""
    request.session.clear()
    return LogoutResponse(detail="Logged out successfully")


@router.get("/me", response_model=AuthMeResponse)
def get_current_user(auth_context: AuthContextDep):
    """Get current user information."""
    if auth_context.is_authenticated and auth_context.user:
        user = auth_context.user
        return AuthMeResponse(
            authenticated=True,
            user=UserInfo(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                profile_picture=user.profile_picture,
                tier=user.patron_tier.value,
                account_type=user.account_type.value,
            ),
            credits=CreditsInfo(
                credits_remaining=auth_context.credits_remaining,
                credits_limit=auth_context.credit_limit(),
            ),
        )
    else:
        return AuthMeResponse(
            authenticated=False,
            anonymous=AnonymousInfo(
                id=auth_context.anon_session.anon_id,
                tier="anonymous",
            ),
            credits=CreditsInfo(
                credits_remaining=auth_context.credits_remaining,
                credits_limit=auth_context.credit_limit(),
            ),
        )


@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status(auth_context: AuthContextDep):
    """Get authentication status for frontend."""
    return AuthStatusResponse(
        authenticated=auth_context.is_authenticated,
        tier=auth_context.tier_name.lower(),
        credits_remaining=auth_context.credits_remaining,
        can_generate=auth_context.can_use_credits(1),
    )


@router.get("/health")
def database_health():
    """Health check endpoint for database connectivity."""
    is_healthy = check_database_health()
    if is_healthy:
        return {"status": "healthy", "database": "connected"}
    else:
        raise HTTPException(status_code=503, detail="Database connection failed")
