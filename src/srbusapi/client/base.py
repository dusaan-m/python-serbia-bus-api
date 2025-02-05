import logging

from httpx import AsyncClient, HTTPStatusError

from srbusapi.caching.base_cache import BaseCache
from srbusapi.config import BaseCityConfig
from srbusapi.exceptions import APIError

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(
        self, client: AsyncClient = None, cache=None, config: BaseCityConfig = None
    ):
        self.client: AsyncClient = client if client is not None else AsyncClient()
        self.cache: BaseCache = cache
        self.config: BaseCityConfig = config

    @property
    def headers(self) -> dict:
        return {
            "User-Agent": "okhttp/4.10.0",
            "X-Api-Authentication": self.config.api_key,
        }

    async def _request(self, method: str, endpoint: str, **kwargs):
        url = self.config.url + endpoint
        logger.debug(f"{method} {url}")

        try:
            response = await self.client.request(
                method,
                url,
                headers=self.headers,
                **kwargs,
            )
            response.raise_for_status()

            return response.json() if method == "GET" else response.content
        except HTTPStatusError as e:
            raise APIError(f"API request failed: {str(e)}")

    async def get_stations(self):
        raise NotImplementedError

    async def get_arrivals(self, station_id: str) -> dict:
        raise NotImplementedError

    async def get_route(self, actual_line_number: str) -> dict:
        raise NotImplementedError

    async def get_route_version(self, actual_line_number: str) -> dict:
        raise NotImplementedError
