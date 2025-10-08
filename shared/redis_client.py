"""
Redis client for caching and state management
"""
import redis
import json
import os
from typing import Any, Optional


class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.client = redis.from_url(redis_url, decode_responses=True)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a value with optional TTL (seconds)"""
        serialized = json.dumps(value)
        if ttl:
            self.client.setex(key, ttl, serialized)
        else:
            self.client.set(key, serialized)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value"""
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def delete(self, key: str):
        """Delete a key"""
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0
    
    def set_hash(self, key: str, mapping: dict):
        """Set a hash"""
        serialized = {k: json.dumps(v) for k, v in mapping.items()}
        self.client.hset(key, mapping=serialized)
    
    def get_hash(self, key: str) -> Optional[dict]:
        """Get a hash"""
        data = self.client.hgetall(key)
        if data:
            return {k: json.loads(v) for k, v in data.items()}
        return None
    
    def ping(self) -> bool:
        """Check connection"""
        try:
            return self.client.ping()
        except:
            return False


# Global instance
redis_client = RedisClient()
