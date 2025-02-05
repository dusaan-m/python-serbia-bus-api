from datetime import timedelta


class BaseCache:
    """
    A base class for implementing caching backends. Provides interface methods that must
    be implemented by any specific cache subclasses.
    """

    async def get_data(self, key: str):
        """
        Retrieve the value associated with a given key from the cache.

        :param key: The key to look up in the cache.
        """
        raise NotImplementedError

    async def set_data(self, key: str, value, expiration: timedelta | None):
        """
        Store a value in the cache with an optional expiration time.

        :param key: The key under which the value will be stored.
        :param value: The value to be stored in the cache.
        :param expiration: An optional timedelta specifying the time until the value expires.
        """
        raise NotImplementedError
