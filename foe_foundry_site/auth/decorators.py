"""Credit-based authorization decorators for FastAPI endpoints."""

from functools import wraps
from typing import Callable, Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session

from .dependencies import get_auth_context
from .database import get_session


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
            request: Request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Look in kwargs
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Credits decorator requires Request parameter"
                )
            
            # Get database session
            db_gen = get_session()
            db: Session = next(db_gen)
            
            try:
                # Get authentication context
                auth_context = get_auth_context(request, db)
                
                # Check if user has sufficient credits
                if not auth_context.can_use_credits(cost):
                    credits_remaining = auth_context.get_credits_remaining()
                    if auth_context.is_anonymous:
                        message = f"Insufficient credits. Need {cost}, have {credits_remaining}. Create an account for more credits!"
                    else:
                        message = f"Insufficient credits. Need {cost}, have {credits_remaining}."
                    
                    return JSONResponse(
                        status_code=402,
                        content={
                            "detail": message,
                            "credits_required": cost,
                            "credits_available": credits_remaining
                        }
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