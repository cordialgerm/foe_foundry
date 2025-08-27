"""Example showing how to use the new @credits decorator with FastAPI endpoints."""

from fastapi import FastAPI, Request
from foe_foundry_site.auth import credits

app = FastAPI()

@app.get("/api/example")
@credits(1)  # Require 1 credit to access this endpoint
async def example_endpoint(request: Request):
    """Example endpoint that requires 1 credit."""
    return {"message": "This endpoint costs 1 credit"}

@app.get("/api/expensive")
@credits(5)  # Require 5 credits to access this endpoint
async def expensive_endpoint(request: Request):
    """Example endpoint that requires 5 credits."""
    return {"message": "This endpoint costs 5 credits"}

@app.get("/api/free")
async def free_endpoint():
    """Example endpoint that doesn't require credits."""
    return {"message": "This endpoint is free"}

# The @credits decorator will:
# 1. Check if the user has sufficient credits before calling the function
# 2. Return a 402 Payment Required error if insufficient credits
# 3. Automatically deduct credits after successful execution
# 4. Handle both anonymous users and authenticated users
# 5. Support unlimited credits for Platinum tier users