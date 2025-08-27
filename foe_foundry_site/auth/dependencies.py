"""Authentication utilities and dependencies."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from .database import get_session
from .models import AnonymousSession, User


@dataclass
class CreditValidationResponse:
    is_valid: bool
    remaining_credits: int
    error_message: str | None = None

    def to_json_data(self) -> dict:
        return asdict(self)

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_data())


# OAuth configuration from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
PATREON_CLIENT_ID = os.getenv("PATREON_CLIENT_ID")
PATREON_CLIENT_SECRET = os.getenv("PATREON_CLIENT_SECRET")
PATREON_REDIRECT_URI = os.getenv(
    "PATREON_REDIRECT_URI", "http://127.0.0.1:8080/auth/patreon/callback"
)
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI", "http://127.0.0.1:8080/auth/discord/callback"
)
SESSION_SECRET = os.getenv("SESSION_SECRET", "supersecret-change-in-production")


class AuthContext:
    """Authentication context for requests."""

    def __init__(
        self,
        user: Optional[User] = None,
        anon_session: Optional[AnonymousSession] = None,
    ):
        self.user = user
        self.anon_session = anon_session
        self.is_authenticated = user is not None
        self.is_anonymous = user is None

    def can_use_credits(self, amount: int = 1) -> bool:
        """Check if the user/session can use credits."""
        if self.user:
            return self.user.can_use_credits(amount)
        elif self.anon_session:
            return self.anon_session.can_use_credits(amount)
        return False

    def use_credits(self, amount: int = 1) -> bool:
        """Use credits if available."""
        if self.user:
            return self.user.use_credits(amount)
        elif self.anon_session:
            return self.anon_session.use_credits(amount)
        return False

    @property
    def credits_remaining(self) -> int:
        """Get remaining credits."""
        if self.user:
            if self.user.patron_tier.value == "platinum":
                return -1  # Unlimited
            return self.user.credits_remaining
        elif self.anon_session:
            return AnonymousSession.get_credit_limit() - self.anon_session.credits_used
        return 0

    def credit_limit(self) -> int:
        """Get total credit limit."""
        if self.user:
            if self.user.patron_tier.value == "platinum":
                return -1
            return self.user.get_monthly_credit_limit()
        elif self.anon_session:
            return AnonymousSession.get_credit_limit()
        return 0

    @property
    def tier_name(self) -> str:
        """Get user tier name for display."""
        if self.user:
            return self.user.patron_tier.value.title()
        return "Anonymous"


def get_current_user_optional(
    request: Request, session: Annotated[Session, Depends(get_session)]
) -> Optional[User]:
    """Get current user from session if authenticated."""
    if "user" not in request.session:
        return None

    user_data = request.session["user"]
    if not isinstance(user_data, dict) or "id" not in user_data:
        return None

    user = session.get(User, user_data["id"])
    if user:
        # Reset credits if needed
        if user.reset_credits_if_needed():
            session.add(user)
            session.commit()
            session.refresh(user)

    return user


def get_or_create_anon_session(
    request: Request, session: Annotated[Session, Depends(get_session)]
) -> AnonymousSession:
    """Get or create anonymous session."""
    anon_id = request.session.get("anon_id")

    if not anon_id:
        anon_id = str(uuid.uuid4())
        request.session["anon_id"] = anon_id

    # Try to get existing session
    anon_session = session.get(AnonymousSession, anon_id)

    if not anon_session:
        anon_session = AnonymousSession(anon_id=anon_id)
        session.add(anon_session)
        session.commit()
        session.refresh(anon_session)

    return anon_session


def get_auth_context(
    request: Request, session: Annotated[Session, Depends(get_session)]
) -> AuthContext:
    """Get authentication context for the current request."""
    user = get_current_user_optional(request, session)

    if user:
        return AuthContext(user=user)
    else:
        anon_session = get_or_create_anon_session(request, session)
        return AuthContext(anon_session=anon_session)


def require_auth(
    auth_context: Annotated[AuthContext, Depends(get_auth_context)],
) -> User:
    """Require authentication, raise 401 if not authenticated."""
    if not auth_context.is_authenticated or auth_context.user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return auth_context.user


def require_credits(
    auth_context: Annotated[AuthContext, Depends(get_auth_context)], amount: int = 1
):
    """Require sufficient credits for the operation."""

    response = validate_credits(auth_context, amount)
    if not response.is_valid:
        return

    raise HTTPException(status_code=402, detail=response.to_json_str())


def validate_credits(auth_context: AuthContext, cost: int) -> CreditValidationResponse:
    """
    Validate if user has sufficient credits.

    Returns:
        None if credits are sufficient, otherwise returns error response data
    """
    credits_remaining = auth_context.get_credits_remaining()
    if not auth_context.can_use_credits(cost):
        if auth_context.is_anonymous:
            message = f"Insufficient credits. Need {cost}, have {credits_remaining}. Create an account for more credits!"
        else:
            message = f"Insufficient credits. Need {cost}, have {credits_remaining}."

        return CreditValidationResponse(
            is_valid=False, remaining_credits=credits_remaining, error_message=message
        )

    return CreditValidationResponse(is_valid=True, remaining_credits=credits_remaining)


# Type aliases for dependency injection
AuthContextDep = Annotated[AuthContext, Depends(get_auth_context)]
SessionDep = Annotated[Session, Depends(get_session)]
RequireAuthDep = Annotated[User, Depends(require_auth)]
