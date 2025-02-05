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
    """
    A Redis-based caching system to store and retrieve data asynchronously, following BaseCache structure.
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        db: int = 0,
    ):
        """
        Initializes the RedisCache with optional connection parameters.

        :param host: Redis server host, optional if set in environment variables.
        :param port: Redis server port, optional if set in environment variables.
        :param username: Username for authenticated access, optional.
        :param password: Password for authenticated access, optional.
        :param db: Database index to connect to, defaults to 0.
        """
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
        """
        Retrieves Redis connection parameters from environment variables if not provided.

        :param host: Redis server host.
        :param port: Redis server port.
        :param username: Username for Redis authentication, if applicable.
        :param password: Password for Redis authentication, if applicable.
        :return: Tuple containing host, port, username, and password.
        """
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
        """
        Retrieves a value from the Redis cache for the provided key.

        :param key: The cache key to retrieve data for.
        :return: The cached data as a string, or None if not found.
        """
        try:
            return await self.client.get(key)
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {str(e)}")
            raise CacheError(f"Failed to get data from Redis: {str(e)}")

    async def _set(self, key: str, value: dict, ex: timedelta = None):
        """
        Stores a value in the Redis cache under the specified key.

        :param key: The key under which the value will be stored.
        :param value: The data to be stored, as a dictionary.
        :param ex: (Optional) Expiration time for the cached data.
        """
        try:
            await self.client.set(key, json.dumps(value), ex=ex)
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {str(e)}")
            raise CacheError(f"Failed to set data in Redis: {str(e)}")

    async def get_data(self, key):
        """
        Public method to retrieve structured data (deserialized) from the Redis cache.

        :param key: The key used to look up the data.
        :return: The data as a dictionary, or None if not found.
        """
        data = await self._get(key)
        return json.loads(data) if data else None

    async def set_data(self, key: str, value: dict, expiration):
        """
        Public method to store structured data (serialized) in Redis cache with an optional expiration.

        :param key: The key under which the value will be stored.
        :param value: The data to store, as a dictionary.
        :param expiration: Expiration time for the cached data.
        """
        await self._set(key, value, ex=expiration)

    async def close(self):
        """
        Closes the Redis connection pool, freeing up resources.
        """
        await self.pool.disconnect()
