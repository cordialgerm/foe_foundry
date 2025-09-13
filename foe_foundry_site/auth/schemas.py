"""Response schemas for authentication endpoints."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class UserInfo(BaseModel):
    """User information response."""

    id: int
    email: str
    display_name: Optional[str]
    profile_picture: Optional[str]
    tier: str
    account_type: str


class CreditsInfo(BaseModel):
    """Credits information response."""

    credits_remaining: int
    credits_limit: int


class AnonymousInfo(BaseModel):
    """Anonymous user information response."""

    id: str
    tier: str


class AuthMeResponse(BaseModel):
    """Response for /auth/me endpoint."""

    authenticated: bool
    user: Optional[UserInfo] = None
    anonymous: Optional[AnonymousInfo] = None
    credits: CreditsInfo


class AuthStatusResponse(BaseModel):
    """Response for /auth/status endpoint."""

    authenticated: bool
    tier: str
    credits_remaining: int
    can_generate: bool


class AuthGoogleResponse(BaseModel):
    """Response for Google authentication."""

    detail: str
    user: UserInfo


class LogoutResponse(BaseModel):
    """Response for logout endpoint."""

    detail: str
