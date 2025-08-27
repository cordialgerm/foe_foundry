"""Database configuration and connection management."""

from __future__ import annotations

import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from .models import User, AnonymousSession, CreditTransaction

# Database URL from environment, with fallback to SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./foe_foundry_accounts.db"
)

# Convert postgres:// to postgresql:// if needed (Heroku compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    # Ensure tables exist
    create_db_and_tables()
    with Session(engine) as session:
        yield session