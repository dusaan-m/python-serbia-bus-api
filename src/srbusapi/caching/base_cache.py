from datetime import timedelta


class BaseCache:
    """
    Base class defining a cache interface.

    This class provides an interface for caching implementations with methods
    to store and retrieve data, which should be overridden by subclasses.
    """

    async def get_data(self, key: str):
        """
        Retrieve data from the cache.

        Args:
            key (str): The unique key used to identify the cached data.
        """
        raise NotImplementedError

    async def set_data(self, key: str, value, expiration: timedelta | None):
        """
        Store data in the cache.

        Args:
            key (str): The unique key to identify the cached data.
            value (Any): The data to be cached.
            expiration (timedelta): The expiration time for the cached data.
        """
        raise NotImplementedError
