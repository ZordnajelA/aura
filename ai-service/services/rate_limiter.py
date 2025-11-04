"""
Rate Limiter Service - Enforce API rate limits
Tracks requests per minute (RPM) and requests per day (RPD) for free tier
"""

import time
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, Optional
import asyncio

from config import settings


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass


class RateLimiter:
    """
    Token bucket rate limiter for API requests

    Tracks both RPM (requests per minute) and RPD (requests per day)
    For Gemini free tier: 10 RPM, 4000 RPD
    """

    def __init__(
        self,
        rpm_limit: int,
        rpd_limit: int,
        provider: str = "gemini"
    ):
        """
        Initialize rate limiter

        Args:
            rpm_limit: Requests per minute limit
            rpd_limit: Requests per day limit
            provider: Provider name (for tracking)
        """
        self.rpm_limit = rpm_limit
        self.rpd_limit = rpd_limit
        self.provider = provider

        # Track requests in last minute
        self.minute_requests: deque = deque()

        # Track requests in last day
        self.day_requests: deque = deque()

        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire permission to make a request

        Blocks until request can be made within rate limits
        Raises RateLimitExceeded if daily limit is reached

        Usage:
            await rate_limiter.acquire()
            # Make API request
        """
        async with self._lock:
            now = time.time()
            current_date = datetime.now().date()

            # Clean up old requests
            self._cleanup_old_requests(now, current_date)

            # Check daily limit
            if len(self.day_requests) >= self.rpd_limit:
                raise RateLimitExceeded(
                    f"{self.provider} daily limit ({self.rpd_limit} RPD) exceeded. "
                    f"Resets at midnight."
                )

            # Check minute limit
            if len(self.minute_requests) >= self.rpm_limit:
                # Calculate wait time
                oldest_request = self.minute_requests[0]
                wait_time = 60 - (now - oldest_request)

                if wait_time > 0:
                    print(f"Rate limit: waiting {wait_time:.1f}s (RPM: {self.rpm_limit})")
                    await asyncio.sleep(wait_time)

                    # Cleanup after waiting
                    now = time.time()
                    self._cleanup_old_requests(now, current_date)

            # Record this request
            self.minute_requests.append(now)
            self.day_requests.append(current_date)

    def _cleanup_old_requests(self, now: float, current_date: datetime.date) -> None:
        """Remove requests older than tracking window"""
        # Remove requests older than 1 minute
        minute_ago = now - 60
        while self.minute_requests and self.minute_requests[0] < minute_ago:
            self.minute_requests.popleft()

        # Remove requests from previous days
        while self.day_requests and self.day_requests[0] < current_date:
            self.day_requests.popleft()

    def get_usage_stats(self) -> Dict[str, any]:
        """Get current usage statistics"""
        now = time.time()
        current_date = datetime.now().date()
        self._cleanup_old_requests(now, current_date)

        return {
            "provider": self.provider,
            "rpm_used": len(self.minute_requests),
            "rpm_limit": self.rpm_limit,
            "rpm_remaining": max(0, self.rpm_limit - len(self.minute_requests)),
            "rpd_used": len(self.day_requests),
            "rpd_limit": self.rpd_limit,
            "rpd_remaining": max(0, self.rpd_limit - len(self.day_requests)),
        }

    async def check_availability(self) -> bool:
        """
        Check if a request can be made without waiting

        Returns:
            True if request can be made immediately, False otherwise
        """
        async with self._lock:
            now = time.time()
            current_date = datetime.now().date()
            self._cleanup_old_requests(now, current_date)

            # Check daily limit
            if len(self.day_requests) >= self.rpd_limit:
                return False

            # Check minute limit
            if len(self.minute_requests) >= self.rpm_limit:
                return False

            return True


# Global rate limiters
_rate_limiters: Dict[str, RateLimiter] = {}


def get_rate_limiter(provider: str = "gemini") -> RateLimiter:
    """
    Get or create rate limiter for provider

    Args:
        provider: Provider name (gemini, openai, anthropic)

    Returns:
        RateLimiter instance
    """
    global _rate_limiters

    if provider not in _rate_limiters:
        if provider == "gemini":
            _rate_limiters[provider] = RateLimiter(
                rpm_limit=settings.gemini_rpm_limit,
                rpd_limit=settings.gemini_rpd_limit,
                provider=provider
            )
        elif provider == "openai":
            _rate_limiters[provider] = RateLimiter(
                rpm_limit=settings.openai_rpm_limit,
                rpd_limit=10000,  # OpenAI has higher limits
                provider=provider
            )
        elif provider == "anthropic":
            _rate_limiters[provider] = RateLimiter(
                rpm_limit=settings.anthropic_rpm_limit,
                rpd_limit=10000,  # Anthropic has higher limits
                provider=provider
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    return _rate_limiters[provider]
