"""Database models for the account system."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

from . import const


class AccountType(str, Enum):
    """Account type enumeration."""

    GOOGLE = "google"
    PATREON = "patreon"
    DISCORD = "discord"


class PatronTier(str, Enum):
    """Patreon tier enumeration."""

    FREE = "free"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class PatronStatus(str, Enum):
    """Patreon status enumeration."""

    ACTIVE = "active"
    DECLINED = "declined"
    FORMER = "former"


class User(SQLModel, table=True):
    """User model for registered accounts."""

    __tablename__ = "users"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None

    # OAuth provider IDs
    google_id: Optional[str] = Field(default=None, index=True)
    patreon_id: Optional[str] = Field(default=None, index=True)
    discord_id: Optional[str] = Field(default=None, index=True)

    # Account metadata
    account_type: AccountType = Field(default=AccountType.GOOGLE)
    patron_tier: PatronTier = Field(default=PatronTier.FREE)
    patron_status: Optional[PatronStatus] = None

    # Credit system
    credits_remaining: int = Field(
        default=const.FREE_CREDITS
    )  # Free tier gets 50 credits
    credits_last_reset: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_monthly_credit_limit(self) -> int:
        """Get the monthly credit limit based on patron tier."""
        credit_limits = {
            PatronTier.FREE: const.FREE_CREDITS,
            PatronTier.BRONZE: const.BRONZE_CREDITS,
            PatronTier.SILVER: const.SILVER_CREDITS,
            PatronTier.GOLD: const.GOLD_CREDITS,
            PatronTier.PLATINUM: const.PLATINUM_CREDITS,
        }
        return credit_limits.get(self.patron_tier, const.FREE_CREDITS)

    def reset_credits_if_needed(self) -> bool:
        """Reset credits if a month has passed since last reset."""
        now = datetime.now(timezone.utc)
        if (now - self.credits_last_reset).days >= 30:
            self.credits_remaining = self.get_monthly_credit_limit()
            self.credits_last_reset = now
            return True
        return False

    def can_use_credits(self, amount: int = 1) -> bool:
        """Check if user can use the specified amount of credits."""
        if self.patron_tier == PatronTier.PLATINUM:
            return True  # Unlimited
        return self.credits_remaining >= amount

    def use_credits(self, amount: int = 1) -> bool:
        """Use credits if available. Returns True if successful."""
        if self.can_use_credits(amount):
            if self.patron_tier != PatronTier.PLATINUM:
                self.credits_remaining -= amount
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False


class AnonymousSession(SQLModel, table=True):
    """Anonymous session tracking for credit limits."""

    __tablename__ = "anon_sessions"  # type: ignore

    anon_id: str = Field(primary_key=True)
    credits_used: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional: Store analytics client ID for correlation
    analytics_client_id: Optional[str] = None

    @classmethod
    def get_credit_limit(cls) -> int:
        """Get credit limit for anonymous users."""
        return const.ANONYMOUS_CREDITS

    def can_use_credits(self, amount: int = 1) -> bool:
        """Check if anonymous user can use credits."""
        return self.credits_used + amount <= self.get_credit_limit()

    def use_credits(self, amount: int = 1) -> bool:
        """Use credits if available."""
        if self.can_use_credits(amount):
            self.credits_used += amount
            self.last_used = datetime.now(timezone.utc)
            return True
        return False
