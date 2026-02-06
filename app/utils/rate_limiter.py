"""
Simple in-memory rate limiter.
Resets on server restart.
"""
from datetime import datetime, timedelta
from typing import Dict
from app.config import get_settings

settings = get_settings()

# In-memory storage for rate limits
# Format: {identifier: {"count": int, "reset_time": datetime}}
rate_limit_storage: Dict[str, dict] = {}


def check_rate_limit(identifier: str) -> bool:
    """
    Check if the given identifier (IP or session) is within rate limits.
    
    Returns True if request is allowed, False if rate limited.
    """
    now = datetime.now()
    
    if identifier not in rate_limit_storage:
        # First request from this identifier
        rate_limit_storage[identifier] = {
            "count": 1,
            "reset_time": now + timedelta(days=1)
        }
        return True
    
    entry = rate_limit_storage[identifier]
    
    # Check if we need to reset
    if now >= entry["reset_time"]:
        rate_limit_storage[identifier] = {
            "count": 1,
            "reset_time": now + timedelta(days=1)
        }
        return True
    
    # Check if under limit
    if entry["count"] < settings.rate_limit_per_day:
        entry["count"] += 1
        return True
    
    return False


def get_remaining_requests(identifier: str) -> int:
    """Get the number of remaining requests for an identifier."""
    if identifier not in rate_limit_storage:
        return settings.rate_limit_per_day
    
    entry = rate_limit_storage[identifier]
    now = datetime.now()
    
    if now >= entry["reset_time"]:
        return settings.rate_limit_per_day
    
    return max(0, settings.rate_limit_per_day - entry["count"])
