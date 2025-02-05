import logging
from datetime import timedelta

from httpx import AsyncClient

from srbusapi.caching.base_cache import BaseCache
from srbusapi.caching.caching_decorators import cache_data, cache_route
from srbusapi.client.base import BaseClient
from srbusapi.config import NisConfigBase

logger = logging.getLogger(__name__)


class NisClient(BaseClient):
    def __init__(self, client: AsyncClient = None, cache: BaseCache = None):
        """
        Initializes the NisClient with an optional HTTP client and cache.

        :param client: Instance of AsyncClient to make HTTP requests.
        :param cache: Optional cache instance for storing request results.
        """
        super().__init__(client, cache, NisConfigBase())

    @cache_data(expiration=timedelta(days=1))
    async def get_stations(self) -> dict:
        """
        Fetches the list of stations with extended city information.

        :return: Dictionary containing station data.
        """
        logger.info("Nis stations")
        endpoint = self.config.stations_endpoint
        params = {"action": "get_cities_extended"}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(seconds=15))
    async def get_arrivals(self, station_id) -> dict:
        """
        Fetches arrival information for a specific station.

        :param station_id: Unique identifier of the station.
        :return: Dictionary containing arrival data.
        """
        logger.info(f"Nis arrivals for station {station_id}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_announcement_data", "station_uid": station_id}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_route()
    async def get_route(self, actual_line_number) -> dict:
        """
        Fetches the route details for a specific line number.

        :param actual_line_number: Line number to fetch route data for.
        :return: Dictionary containing route data.
        """
        logger.info(f"Nis route for line {actual_line_number}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_line_route_data", "line_number": actual_line_number}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(days=1))
    async def get_route_version(self, actual_line_number) -> dict:
        """
        Fetches the route version details for a specific line number.

        :param actual_line_number: Line number to fetch route version data for.
        :return: Dictionary containing route version information.
        """
        logger.info(f"Nis route version for line {actual_line_number}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_line_route_version", "line_number": actual_line_number}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response
