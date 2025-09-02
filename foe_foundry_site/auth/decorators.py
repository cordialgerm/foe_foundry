"""Credit-based authorization decorators for FastAPI endpoints."""

from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .database import get_session
from .dependencies import get_auth_context, validate_credits


def _resolve_request(args: tuple, kwargs: dict) -> Request:
    """Resolve the FastAPI Request object from args or kwargs."""
    for arg in args:
        if isinstance(arg, Request):
            return arg
    request = kwargs.get("request")
    if not request:
        raise HTTPException(
            status_code=500,
            detail="Credits decorator requires Request parameter",
        )
    return request


def credits(cost: int = 1):
    """
    Decorator that requires a certain number of credits to access an endpoint.

    Args:
        cost: Number of credits required to access this endpoint (default: 1)

    Usage:
        @app.get("/api/generate")
        @credits(1)
        async def generate_monster():
            return {"monster": "data"}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract request from args/kwargs
            request: Request = _resolve_request(args, kwargs)

            # Get database session
            db_gen = get_session()
            db = next(db_gen)

            try:
                # Get authentication context
                auth_context = get_auth_context(request, db)

                # Check if user has sufficient credits using shared validation
                credit_check = validate_credits(auth_context, cost)
                if not credit_check.is_valid:
                    return JSONResponse(
                        status_code=402, content=credit_check.to_json_data()
                    )

                # Call the original function
                result = await func(*args, **kwargs)

                # Deduct credits after successful execution
                auth_context.use_credits(cost)

                # Save changes to database
                if auth_context.user:
                    db.add(auth_context.user)
                elif auth_context.anon_session:
                    db.add(auth_context.anon_session)
                db.commit()

                return result

            finally:
                db.close()

        return wrapper

    return decorator
