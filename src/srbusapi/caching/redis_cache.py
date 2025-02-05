import json
import logging
import os
from datetime import timedelta
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from srbusapi.caching.base_cache import BaseCache
from srbusapi.exceptions import CacheError, ConfigurationError

logger = logging.getLogger(__name__)


class RedisCache(BaseCache):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        db: int = 0,
    ):
        host, port, username, password = self._from_env(host, port, username, password)

        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            username=username,
            password=password,
            db=db,
            decode_responses=True,
            retry_on_timeout=True,
            max_connections=10,
        )
        self.client: Redis = redis.Redis(connection_pool=self.pool)

    @staticmethod
    def _from_env(
        host: str = None, port: int = None, username: str = None, password: str = None
    ):
        host = host or os.getenv("REDIS_HOST")
        port = port or os.getenv("REDIS_PORT")
        username = username or os.getenv("REDIS_USERNAME")
        password = password or os.getenv("REDIS_PASSWORD")

        if not host or not port:
            raise ConfigurationError(
                "Redis host and port must be provided. "
                "Please provide them either as arguments or in environment variables. "
                "The environment variables are REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD"
            )

        return host, int(port), username, password

    async def _get(self, key: str) -> Optional[str]:
        try:
            return await self.client.get(key)
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {str(e)}")
            raise CacheError(f"Failed to get data from Redis: {str(e)}")

    async def _set(self, key: str, value: dict, ex: timedelta = None):
        try:
            await self.client.set(key, json.dumps(value), ex=ex)
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {str(e)}")
            raise CacheError(f"Failed to set data in Redis: {str(e)}")

    async def get_data(self, key):
        data = await self._get(key)
        return json.loads(data) if data else None

    async def set_data(self, key: str, value: dict, expiration):
        await self._set(key, value, ex=expiration)

    async def close(self):
        await self.pool.disconnect()
