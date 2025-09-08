"""
Geo-location API routes for cookie consent functionality.
Provides a proxy to external geo-location services to avoid CORS issues.
"""

import logging
from typing import Dict, Any

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/geo")


@router.get("/location")
async def get_location() -> Dict[str, Any]:
    """
    Proxy endpoint for geo-location detection.
    
    Returns country code and other location data from ipapi.co
    without CORS restrictions.
    
    Returns:
        Dict containing country_code and other location information
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://ipapi.co/json/")
            response.raise_for_status()
            data = response.json()
            
            # Validate that we got the expected data structure
            if not isinstance(data, dict) or "country_code" not in data:
                log.warning(f"Unexpected response from ipapi.co: {data}")
                # Return fallback data that will trigger consent banner
                return {"country_code": None, "error": "Invalid response format"}
            
            return data
            
    except httpx.TimeoutException:
        log.warning("Timeout when fetching geo-location from ipapi.co")
        # Return fallback that triggers consent banner
        return {"country_code": None, "error": "timeout"}
    except httpx.HTTPStatusError as e:
        log.warning(f"HTTP error from ipapi.co: {e.response.status_code}")
        # Return fallback that triggers consent banner
        return {"country_code": None, "error": f"http_error_{e.response.status_code}"}
    except (httpx.ConnectError, httpx.NetworkError) as e:
        log.warning(f"Network error when fetching geo-location: {e}")
        # Return fallback that triggers consent banner (safe default)
        return {"country_code": None, "error": "network_error"}
    except Exception as e:
        log.error(f"Unexpected error fetching geo-location: {e}")
        # Return fallback that triggers consent banner
        return {"country_code": None, "error": "unexpected_error"}


@router.get("/test")
async def test_endpoint() -> Dict[str, Any]:
    """
    Test endpoint to verify the geo API is working.
    Returns a mock response that simulates a GDPR country for testing.
    """
    return {
        "country_code": "DE",  # Germany (GDPR country)
        "country": "Germany",
        "city": "Test City",
        "test": True
    }