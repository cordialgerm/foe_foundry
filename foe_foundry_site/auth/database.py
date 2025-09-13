"""Database configuration and connection management."""

from __future__ import annotations

import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

# Database URL from environment, with fallback to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foe_foundry_accounts.db")

# Convert postgres:// to postgresql:// if needed (Heroku compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
    )
elif DATABASE_URL.startswith("postgresql://"):
    # PostgreSQL configuration for production (Render)
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Additional connections when pool is full
        pool_timeout=30,  # Timeout when getting connection from pool
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Validate connections before use
        connect_args={
            "sslmode": "require",  # Render PostgreSQL requires SSL
            "connect_timeout": 10,  # Connection timeout in seconds
        },
    )
else:
    # Generic database (fallback)
    engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """Create database tables if they don't exist."""
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        # Log the error but don't fail startup for connection issues
        import logging

        logging.getLogger(__name__).error(f"Failed to create database tables: {e}")
        raise


def check_database_health() -> bool:
    """Check if database connection is healthy."""
    try:
        with Session(engine) as session:
            # Simple query to test connection
            session.exec("SELECT 1").first()
            return True
    except Exception:
        return False


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    # Ensure tables exist
    create_db_and_tables()
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
