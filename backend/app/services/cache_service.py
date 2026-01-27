"""
Cache service using Redis for hot data
"""

import json
from typing import Optional, Any, List
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.config import get_settings

settings = get_settings()


class CacheService:
    """Redis cache service for caching hot data"""

    def __init__(self):
        self.client: Optional["redis.Redis"] = None
        self.enabled = REDIS_AVAILABLE

        if self.enabled:
            try:
                # Parse redis_url to get connection params
                from urllib.parse import urlparse
                parsed = urlparse(settings.redis_url)

                self.client = redis.Redis(
                    host=parsed.hostname or settings.redis_host,
                    port=parsed.port or settings.redis_port,
                    db=int(parsed.path.lstrip('/') or settings.redis_db),
                    password=parsed.password or settings.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                # Test connection
                self.client.ping()
            except Exception as e:
                from app.core.logging import get_logger
                logger = get_logger("app.cache")
                logger.warning(f"Redis connection failed: {e}, caching disabled")
                self.enabled = False
                self.client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL in seconds"""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception:
            return False

    def delete_pattern(self, pattern: str) -> bool:
        """Delete keys matching pattern"""
        if not self.enabled or not self.client:
            return False

        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            return True
        except Exception:
            return False

    def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple values"""
        if not self.enabled or not self.client or not keys:
            return [None] * len(keys)

        try:
            values = self.client.mget(keys)
            return [json.loads(v) if v else None for v in values]
        except Exception:
            return [None] * len(keys)

    def mset(self, mapping: dict[str, Any], ttl: int = 300) -> bool:
        """Set multiple values"""
        if not self.enabled or not self.client or not mapping:
            return False

        try:
            pipe = self.client.pipeline()
            for key, value in mapping.items():
                pipe.setex(key, ttl, json.dumps(value))
            pipe.execute()
            return True
        except Exception:
            return False

    # Cache key generators
    @staticmethod
    def ticket_key(ticket_id: str) -> str:
        """Generate cache key for ticket"""
        return f"ticket:{ticket_id}"

    @staticmethod
    def ticket_list_key(hotel_id: str, status: str | None = None) -> str:
        """Generate cache key for ticket list"""
        if status:
            return f"tickets:{hotel_id}:{status}"
        return f"tickets:{hotel_id}"

    @staticmethod
    def conversation_key(conversation_id: str) -> str:
        """Generate cache key for conversation"""
        return f"conversation:{conversation_id}"

    @staticmethod
    def conversation_list_key(hotel_id: str) -> str:
        """Generate cache key for conversation list"""
        return f"conversations:{hotel_id}"

    @staticmethod
    def staff_key(staff_id: str) -> str:
        """Generate cache key for staff"""
        return f"staff:{staff_id}"

    @staticmethod
    def config_key(key: str) -> str:
        """Generate cache key for config"""
        return f"config:{key}"

    # Invalidate methods
    def invalidate_ticket(self, ticket_id: str) -> bool:
        """Invalidate ticket cache"""
        return self.delete(self.ticket_key(ticket_id))

    def invalidate_ticket_list(self, hotel_id: str, status: str | None = None) -> bool:
        """Invalidate ticket list cache"""
        return self.delete_pattern(f"tickets:{hotel_id}*")

    def invalidate_conversation(self, conversation_id: str) -> bool:
        """Invalidate conversation cache"""
        return self.delete(self.conversation_key(conversation_id))

    def invalidate_conversation_list(self, hotel_id: str) -> bool:
        """Invalidate conversation list cache"""
        return self.delete_pattern(f"conversations:{hotel_id}*")

    def invalidate_staff(self, staff_id: str) -> bool:
        """Invalidate staff cache"""
        return self.delete(self.staff_key(staff_id))

    def invalidate_config(self, key: str) -> bool:
        """Invalidate config cache"""
        return self.delete(self.config_key(key))


# Global cache service instance
cache_service = CacheService()
