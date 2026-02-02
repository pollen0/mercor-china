"""
Redis caching service for Pathway.

Provides caching for:
- Dashboard statistics
- Question templates
- Top candidates lists
- Interview session data
"""
import json
import logging
import redis
from typing import Optional, Any, TypeVar, Callable
from functools import wraps
import hashlib
from ..config import settings

logger = logging.getLogger("pathway.cache")
T = TypeVar('T')


class CacheService:
    """
    Redis-based caching service with automatic serialization.

    Features:
    - Automatic JSON serialization/deserialization
    - Configurable TTL
    - Cache key namespacing
    - Graceful fallback when Redis is unavailable
    """

    # Cache key prefixes for different data types
    PREFIX_DASHBOARD = "dashboard"
    PREFIX_QUESTIONS = "questions"
    PREFIX_TOP_CANDIDATES = "top_candidates"
    PREFIX_INTERVIEW = "interview"
    PREFIX_EMPLOYER = "employer"

    # TTL presets (in seconds)
    TTL_SHORT = 60  # 1 minute
    TTL_MEDIUM = 300  # 5 minutes
    TTL_LONG = 3600  # 1 hour
    TTL_DAY = 86400  # 24 hours

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._available = False

    @property
    def client(self) -> Optional[redis.Redis]:
        """Lazy initialization of Redis client."""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_timeout=2,
                    socket_connect_timeout=2,
                )
                # Test connection
                self._client.ping()
                self._available = True
                logger.info("Redis cache connected successfully")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(f"Redis not available, caching disabled: {e}")
                self._available = False
                self._client = None
        return self._client

    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if self._client is None:
            # Try to connect
            _ = self.client
        return self._available

    def _make_key(self, prefix: str, *args) -> str:
        """Create a cache key with prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args if arg is not None]
        return ":".join(key_parts)

    def _serialize(self, value: Any) -> str:
        """Serialize a value to JSON string."""
        return json.dumps(value, ensure_ascii=False, default=str)

    def _deserialize(self, value: str) -> Any:
        """Deserialize a JSON string to value."""
        return json.loads(value)

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/unavailable
        """
        if not self.is_available:
            return None

        try:
            value = self.client.get(key)
            if value is not None:
                return self._deserialize(value)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.debug(f"Cache get error: {e}")
        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (defaults to config setting)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            ttl = ttl or settings.cache_ttl_seconds
            serialized = self._serialize(value)
            self.client.setex(key, ttl, serialized)
            return True
        except (redis.RedisError, TypeError) as e:
            logger.debug(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.is_available:
            return False

        try:
            self.client.delete(key)
            return True
        except redis.RedisError as e:
            logger.debug(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., "dashboard:*")

        Returns:
            Number of keys deleted
        """
        if not self.is_available:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
        except redis.RedisError as e:
            logger.debug(f"Cache delete pattern error: {e}")
        return 0

    # ============ DASHBOARD CACHING ============

    def get_dashboard_stats(self, employer_id: str) -> Optional[dict]:
        """Get cached dashboard stats for an employer."""
        key = self._make_key(self.PREFIX_DASHBOARD, employer_id)
        return self.get(key)

    def set_dashboard_stats(self, employer_id: str, stats: dict) -> bool:
        """Cache dashboard stats for an employer."""
        key = self._make_key(self.PREFIX_DASHBOARD, employer_id)
        return self.set(key, stats, ttl=self.TTL_MEDIUM)

    def invalidate_dashboard(self, employer_id: str) -> bool:
        """Invalidate dashboard cache for an employer."""
        key = self._make_key(self.PREFIX_DASHBOARD, employer_id)
        return self.delete(key)

    # ============ QUESTIONS CACHING ============

    def get_questions(self, job_id: Optional[str] = None) -> Optional[list]:
        """Get cached questions for a job (or defaults)."""
        key = self._make_key(self.PREFIX_QUESTIONS, job_id or "defaults")
        return self.get(key)

    def set_questions(self, questions: list, job_id: Optional[str] = None) -> bool:
        """Cache questions for a job."""
        key = self._make_key(self.PREFIX_QUESTIONS, job_id or "defaults")
        return self.set(key, questions, ttl=self.TTL_LONG)

    def invalidate_questions(self, job_id: Optional[str] = None) -> bool:
        """Invalidate questions cache."""
        if job_id:
            key = self._make_key(self.PREFIX_QUESTIONS, job_id)
            return self.delete(key)
        else:
            # Invalidate all questions cache
            return self.delete_pattern(f"{self.PREFIX_QUESTIONS}:*") > 0

    # ============ TOP CANDIDATES CACHING ============

    def get_top_candidates(self, job_id: str, limit: int = 10) -> Optional[list]:
        """Get cached top candidates for a job."""
        key = self._make_key(self.PREFIX_TOP_CANDIDATES, job_id, str(limit))
        return self.get(key)

    def set_top_candidates(self, job_id: str, candidates: list, limit: int = 10) -> bool:
        """Cache top candidates for a job."""
        key = self._make_key(self.PREFIX_TOP_CANDIDATES, job_id, str(limit))
        return self.set(key, candidates, ttl=self.TTL_MEDIUM)

    def invalidate_top_candidates(self, job_id: str) -> int:
        """Invalidate top candidates cache for a job."""
        pattern = f"{self.PREFIX_TOP_CANDIDATES}:{job_id}:*"
        return self.delete_pattern(pattern)

    # ============ INTERVIEW CACHING ============

    def get_interview_session(self, session_id: str) -> Optional[dict]:
        """Get cached interview session data."""
        key = self._make_key(self.PREFIX_INTERVIEW, session_id)
        return self.get(key)

    def set_interview_session(self, session_id: str, session_data: dict) -> bool:
        """Cache interview session data."""
        key = self._make_key(self.PREFIX_INTERVIEW, session_id)
        return self.set(key, session_data, ttl=self.TTL_MEDIUM)

    def invalidate_interview(self, session_id: str) -> bool:
        """Invalidate interview session cache."""
        key = self._make_key(self.PREFIX_INTERVIEW, session_id)
        return self.delete(key)


def cached(
    prefix: str,
    ttl: int = 300,
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Decorator to cache function results.

    Args:
        prefix: Cache key prefix
        ttl: Time-to-live in seconds
        key_builder: Optional function to build cache key from args

    Usage:
        @cached("dashboard", ttl=300)
        async def get_dashboard_stats(employer_id: str):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key builder - hash all arguments
                key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
                key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
                cache_key = f"{prefix}:{key_hash}"

            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl=ttl)
            return result

        return wrapper
    return decorator


# Global instance
cache_service = CacheService()
