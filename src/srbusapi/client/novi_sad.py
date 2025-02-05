import logging
from datetime import timedelta

from httpx import AsyncClient

from srbusapi.caching.base_cache import BaseCache
from srbusapi.caching.caching_decorators import cache_data, cache_route
from srbusapi.client.base import BaseClient
from srbusapi.config import NoviSadConfigBase

logger = logging.getLogger(__name__)


class NoviSadClient(BaseClient):
    def __init__(self, client: AsyncClient = None, cache: BaseCache = None):
        """
        Initializes the NoviSadClient with an HTTP client and optional caching.

        :param client: An optional instance of AsyncClient for making HTTP requests.
        :param cache: An optional instance of BaseCache for caching responses.
        """
        super().__init__(client, cache, NoviSadConfigBase())

    @cache_data(expiration=timedelta(days=1))
    async def get_stations(self) -> dict:
        """
        Fetches a list of stations with extended city data.

        :returns: A dictionary containing station information.
        :raises httpx.HTTPError: If the request to the API fails.
        """
        logger.info("Novi Sad stations")
        endpoint = self.config.stations_endpoint
        params = {"action": "get_cities_extended"}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(seconds=15))
    async def get_arrivals(self, station_id) -> dict:
        """
        Fetches arrival data for a specific station.

        :param station_id: The unique identifier of the station.
        :returns: A dictionary containing arrival information.
        :raises httpx.HTTPError: If the request to the API fails.
        """
        logger.info(f"Novi Sad arrivals for station {station_id}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_announcement_data", "station_uid": station_id}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_route()
    async def get_route(self, actual_line_number) -> dict:
        """
        Fetches route data for a specific line number.

        :param actual_line_number: The number of the line to fetch route data for.
        :returns: A dictionary containing route data for the specified line.
        :raises httpx.HTTPError: If the request to the API fails.
        """
        logger.info(f"Novi Sad route for line {actual_line_number}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_line_route_data", "line_number": actual_line_number}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(days=1))
    async def get_route_version(self, actual_line_number) -> dict:
        """
        Fetches the route version information for a specific line.

        :param actual_line_number: The number of the line to fetch route version data for.
        :returns: A dictionary containing version data for the specified line route.
        :raises httpx.HTTPError: If the request to the API fails.
        """
        logger.info(f"Novi Sad route version for line {actual_line_number}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_line_route_version", "line_number": actual_line_number}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response
