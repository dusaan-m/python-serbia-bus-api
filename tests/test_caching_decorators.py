import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import timedelta

from srbusapi.caching.caching_decorators import (
    cache_data,
    generate_cache_key,
    cache_route,
)
from srbusapi.exceptions import CacheError


class MockCache:
    def __init__(self, get_data_return=None, set_data_raise_error=False):
        self.get_data = AsyncMock(return_value=get_data_return)
        self.set_data = AsyncMock()
        self.set_data_raise_error = set_data_raise_error

    async def get_data(self, key):
        if self.set_data_raise_error:
            raise CacheError("Simulated cache error")
        return await self.get_data(key)

    async def set_data(self, key, value, expiration):
        if self.set_data_raise_error:
            raise CacheError("Simulated cache error")
        await self.set_data(key, value, expiration)


class MockBaseClient:
    def __init__(self, cache=None, config_name="test_client"):
        self.cache = cache
        self.config = MagicMock()
        self.config.name = config_name
        self.get_route_version = AsyncMock()


class TestCacheDataDecorator:
    def test_decorator_requires_async_function(self):
        def sync_function():
            pass

        with pytest.raises(
            TypeError, match="The decorated function must be asynchronous."
        ):
            cache_data(timedelta(minutes=5))(sync_function)

    @pytest.mark.asyncio
    async def test_no_cache_client(self):
        return_data = "original_result"

        @cache_data(timedelta(minutes=5))
        async def mock_func(self):
            return return_data

        client = MockBaseClient(cache=None)
        result = await mock_func(client)
        assert result == return_data

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        cached_value = {"data": "cached_result"}
        mock_cache = MockCache(get_data_return=cached_value)
        client = MockBaseClient(cache=mock_cache)

        @cache_data(timedelta(minutes=5))
        async def mock_func(self, arg1, arg2):
            return {"data": "original_result"}

        result = await mock_func(client, "test1", "test2")

        expected_key = generate_cache_key(
            client.config.name, mock_func.__name__, "test1", "test2"
        )

        # Verify cache was checked
        mock_cache.get_data.assert_awaited_once_with(expected_key)

        # Verify original function was not called
        assert result == cached_value

    @pytest.mark.asyncio
    async def test_cache_miss_and_store(self):
        mock_cache = MockCache()
        client = MockBaseClient(cache=mock_cache)

        @cache_data(timedelta(minutes=5))
        async def mock_func(self, arg1, arg2):
            return {"data": "original_result"}

        result = await mock_func(client, "test1", "test2")

        # Verify result is correct
        assert result == {"data": "original_result"}

        # Verify cache was set
        expected_key = generate_cache_key(
            client.config.name, mock_func.__name__, "test1", "test2"
        )
        mock_cache.set_data.assert_awaited_once_with(
            expected_key, {"data": "original_result"}, timedelta(minutes=5)
        )

    @pytest.mark.asyncio
    async def test_cache_error_fallback(self):
        mock_cache = MockCache(set_data_raise_error=True)
        client = MockBaseClient(cache=mock_cache)

        @cache_data(timedelta(minutes=5))
        async def mock_func(self, arg1, arg2):
            return {"data": "original_result"}

        result = await mock_func(client, "test1", "test2")

        # Verify result is still returned
        assert result == {"data": "original_result"}

    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        mock_cache = MockCache()
        client = MockBaseClient(cache=mock_cache)

        @cache_data(timedelta(minutes=5))
        async def mock_func(self, arg1, arg2):
            return {"data": "original_result"}

        await mock_func(client, "test1", "test2")

        # Verify cache key is generated correctly
        expected_key = generate_cache_key(
            client.config.name, mock_func.__name__, "test1", "test2"
        )
        mock_cache.get_data.assert_awaited_once_with(expected_key)
        mock_cache.set_data.assert_awaited_once()

        # Verify the key used for setting matches the key used for getting
        assert (
            mock_cache.get_data.call_args[0][0] == mock_cache.set_data.call_args[0][0]
        )


class TestCacheRouteDecorator:
    def test_decorator_requires_async_function(self):
        def sync_function():
            pass

        with pytest.raises(
            TypeError, match="The decorated function must be asynchronous."
        ):
            cache_route(timedelta(days=15))(sync_function)

    @pytest.mark.asyncio
    async def test_no_cache_client(self):
        return_data = "original_result"

        @cache_route(timedelta(days=15))
        async def mock_func(self, route_id):
            return return_data

        client = MockBaseClient(cache=None)
        result = await mock_func(client, "route123")
        assert result == return_data

    @pytest.mark.asyncio
    async def test_cache_hit_same_version(self):
        cached_value = {"version": "v1", "data": {"route": "cached_result"}}
        mock_cache = MockCache(get_data_return=cached_value)
        client = MockBaseClient(cache=mock_cache)

        # Mock route version to match cached version
        client.get_route_version.return_value = "v1"

        @cache_route(timedelta(days=15))
        async def mock_func(self, route_id):
            return {"route": "original_result"}

        result = await mock_func(client, "route123")

        # Verify cache was checked
        expected_key = generate_cache_key(
            client.config.name, mock_func.__name__, "route123"
        )
        mock_cache.get_data.assert_awaited_once_with(expected_key)

        # Verify original function was not called
        assert result == {"route": "cached_result"}

        # Verify route version was checked
        client.get_route_version.assert_awaited_once_with("route123")

    @pytest.mark.asyncio
    async def test_cache_miss_different_version(self):
        cached_value = {"version": "v1", "data": {"route": "cached_result"}}
        mock_cache = MockCache(get_data_return=cached_value)
        client = MockBaseClient(cache=mock_cache)

        # Mock route version to be different from cached version
        client.get_route_version.return_value = "v2"

        @cache_route(timedelta(days=15))
        async def mock_func(self, route_id):
            return {"route": "original_result"}

        result = await mock_func(client, "route123")

        # Verify result is new result
        assert result == {"route": "original_result"}

        # Verify cache was updated with new version
        expected_key = generate_cache_key(
            client.config.name, mock_func.__name__, "route123"
        )
        mock_cache.set_data.assert_awaited_once_with(
            expected_key,
            {"version": "v2", "data": {"route": "original_result"}},
            timedelta(days=15),
        )

    @pytest.mark.asyncio
    async def test_cache_miss_no_cached_entry(self):
        mock_cache = MockCache(get_data_return=None)
        client = MockBaseClient(cache=mock_cache)

        # Mock route version
        client.get_route_version.return_value = "v1"

        @cache_route(timedelta(days=15))
        async def mock_func(self, route_id):
            return {"route": "original_result"}

        result = await mock_func(client, "route123")

        # Verify result is original result
        assert result == {"route": "original_result"}

        # Verify cache was set
        expected_key = generate_cache_key(
            client.config.name, mock_func.__name__, "route123"
        )
        mock_cache.set_data.assert_awaited_once_with(
            expected_key,
            {"version": "v1", "data": {"route": "original_result"}},
            timedelta(days=15),
        )

    @pytest.mark.asyncio
    async def test_cache_error_fallback(self):
        mock_cache = MockCache(set_data_raise_error=True)
        client = MockBaseClient(cache=mock_cache)

        # Mock route version
        client.get_route_version.return_value = "v1"

        @cache_route(timedelta(days=15))
        async def mock_func(self, route_id):
            return {"route": "original_result"}

        result = await mock_func(client, "route123")

        # Verify result is still returned
        assert result == {"route": "original_result"}
