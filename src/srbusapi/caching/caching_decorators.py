import inspect
import logging
from datetime import timedelta
from functools import wraps
from typing import Callable

from srbusapi.client.base import BaseClient
from srbusapi.exceptions import CacheError

logger = logging.getLogger(__name__)


def generate_cache_key(city_name: str, key: str, *args):
    return ":".join([city_name, key, *[str(arg) for arg in args]])


def cache_data(expiration: timedelta):
    def decorator(func: Callable):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("The decorated function must be asynchronous.")

        @wraps(func)
        async def wrapper(self: BaseClient, *args, **kwargs):
            response_data = None
            try:
                if not hasattr(self, "cache") or self.cache is None:
                    return await func(self, *args, **kwargs)

                key = generate_cache_key(self.config.name, func.__name__, *args)

                cached_result = await self.cache.get_data(key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key {key}")
                    return cached_result

                response_data = await func(self, *args, **kwargs)

                await self.cache.set_data(key, response_data, expiration)

                return response_data
            except CacheError as e:
                logger.error(f"Cache error: {str(e)}")
                return (
                    await func(self, *args, **kwargs)
                    if response_data is None
                    else response_data
                )

        return wrapper

    return decorator


def cache_route(expiration: timedelta = timedelta(days=15)):
    def decorator(func: Callable):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("The decorated function must be asynchronous.")

        @wraps(func)
        async def wrapper(self: BaseClient, *args, **kwargs):
            try:
                if not hasattr(self, "cache") or self.cache is None:
                    return await func(self, *args, **kwargs)

                key = generate_cache_key(self.config.name, func.__name__, args[0])
                cache_entry = await self.cache.get_data(key)

                new_version = await self.get_route_version(args[0])
                if cache_entry is not None and cache_entry["version"] == new_version:
                    logger.debug(f"Cache hit for key {key}")
                    return cache_entry["data"]

                route_data = await func(self, *args, **kwargs)

                data_to_cache = {"version": new_version, "data": route_data}

                await self.cache.set_data(key, data_to_cache, expiration)

                return route_data
            except CacheError as e:
                logger.error(f"Cache error: {str(e)}")
                return await func(self, *args, **kwargs)

        return wrapper

    return decorator
