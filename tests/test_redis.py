import os
import json
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, patch

from redis.exceptions import RedisError

from srbusapi.caching.redis_cache import RedisCache
from srbusapi.exceptions import CacheError, ConfigurationError


@pytest.fixture
def mock_env_vars():
    """Fixture to set and then clear Redis environment variables."""
    original_env = {
        "REDIS_HOST": os.getenv("REDIS_HOST"),
        "REDIS_PORT": os.getenv("REDIS_PORT"),
        "REDIS_USERNAME": os.getenv("REDIS_USERNAME"),
        "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD"),
    }

    # Set test environment variables
    os.environ["REDIS_HOST"] = "test-host"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_USERNAME"] = "test-user"
    os.environ["REDIS_PASSWORD"] = "test-pass"

    yield

    # Restore original environment variables
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


class TestRedisCache:
    @pytest.mark.asyncio
    async def test_init_from_env_vars(self, mock_env_vars):
        cache = RedisCache()

        assert cache.pool.connection_kwargs["host"] == "test-host"
        assert cache.pool.connection_kwargs["port"] == 6379
        assert cache.pool.connection_kwargs["username"] == "test-user"
        assert cache.pool.connection_kwargs["password"] == "test-pass"

    @pytest.mark.asyncio
    async def test_init_with_explicit_params(self):
        cache = RedisCache(
            host="explicit-host",
            port=1234,
            username="explicit-user",
            password="explicit-pass",
        )

        assert cache.pool.connection_kwargs["host"] == "explicit-host"
        assert cache.pool.connection_kwargs["port"] == 1234
        assert cache.pool.connection_kwargs["username"] == "explicit-user"
        assert cache.pool.connection_kwargs["password"] == "explicit-pass"

    def test_init_missing_host_and_port(self):
        # Clear environment variables
        with patch.dict(os.environ, {"REDIS_HOST": "", "REDIS_PORT": ""}):
            with pytest.raises(
                ConfigurationError, match="Redis host and port must be provided"
            ):
                RedisCache()

    @pytest.mark.asyncio
    async def test_get_data_successful(self):
        # Mock Redis client
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = json.dumps({"key": "value"})

        with patch("redis.asyncio.Redis", return_value=mock_redis_client):
            cache = RedisCache(host="test-host", port=6379)
            result = await cache.get_data("test-key")

            assert result == {"key": "value"}
            mock_redis_client.get.assert_awaited_once_with("test-key")

    @pytest.mark.asyncio
    async def test_get_data_cache_miss(self):
        # Mock Redis client to return None (cache miss)
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = None

        with patch("redis.asyncio.Redis", return_value=mock_redis_client):
            cache = RedisCache(host="test-host", port=6379)
            result = await cache.get_data("test-key")

            assert result is None
            mock_redis_client.get.assert_awaited_once_with("test-key")

    @pytest.mark.asyncio
    async def test_get_data_redis_error(self):
        # Mock Redis client to raise an error
        mock_redis_client = AsyncMock()
        mock_redis_client.get.side_effect = RedisError("Connection failed")

        with patch("redis.asyncio.Redis", return_value=mock_redis_client):
            cache = RedisCache(host="test-host", port=6379)

            with pytest.raises(CacheError, match="Failed to get data from Redis"):
                await cache.get_data("test-key")

    @pytest.mark.asyncio
    async def test_set_data_successful(self):
        # Mock Redis client
        mock_redis_client = AsyncMock()

        with patch("redis.asyncio.Redis", return_value=mock_redis_client):
            cache = RedisCache(host="test-host", port=6379)
            test_data = {"user": "test"}
            test_expiration = timedelta(minutes=10)

            await cache.set_data("test-key", test_data, test_expiration)

            mock_redis_client.set.assert_awaited_once_with(
                "test-key", json.dumps(test_data), ex=test_expiration
            )

    @pytest.mark.asyncio
    async def test_set_data_redis_error(self):
        # Mock Redis client to raise an error
        mock_redis_client = AsyncMock()
        mock_redis_client.set.side_effect = RedisError("Connection failed")

        with patch("redis.asyncio.Redis", return_value=mock_redis_client):
            cache = RedisCache(host="test-host", port=6379)
            test_data = {"user": "test"}
            test_expiration = timedelta(minutes=10)

            with pytest.raises(CacheError, match="Failed to set data in Redis"):
                await cache.set_data("test-key", test_data, test_expiration)
