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
        super().__init__(client, cache, NoviSadConfigBase())

    @cache_data(expiration=timedelta(days=1))
    async def get_stations(self) -> dict:
        logger.info("Novi Sad stations")
        endpoint = self.config.stations_endpoint
        params = {"action": "get_cities_extended"}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(seconds=15))
    async def get_arrivals(self, station_id) -> dict:
        logger.info(f"Novi Sad arrivals for station {station_id}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_announcement_data", "station_uid": station_id}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_route()
    async def get_route(self, actual_line_number) -> dict:
        logger.info(f"Novi Sad route for line {actual_line_number}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_line_route_data", "line_number": actual_line_number}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(days=1))
    async def get_route_version(self, actual_line_number) -> dict:
        logger.info(f"Novi Sad route version for line {actual_line_number}")
        endpoint = self.config.api_endpoint
        params = {"action": "get_line_route_version", "line_number": actual_line_number}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response
