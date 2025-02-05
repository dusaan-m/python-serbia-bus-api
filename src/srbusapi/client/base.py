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
        """
        Initialize the BaseClient.

        :param client: Optional async HTTP client. Defaults to None, creating a new AsyncClient instance.
        :param cache: Optional caching mechanism for API responses.
        :param config: Configuration object for city-specific API settings.
        """
        self.client: AsyncClient = client if client is not None else AsyncClient()
        self.cache: BaseCache = cache
        self.config: BaseCityConfig = config

    @property
    def headers(self) -> dict:
        """
        Generate headers for the API requests.

        :returns: A dictionary of HTTP headers used for authentication and user-agent.
        """
        return {
            "User-Agent": "okhttp/4.10.0",
            "X-Api-Authentication": self.config.api_key,
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Make an HTTP request to the API.

        :param method: HTTP method (e.g., 'GET', 'POST').
        :param endpoint: API endpoint to be appended to the base URL.
        :param kwargs: Additional request parameters (e.g., query params, JSON payload).
        :returns: Decoded JSON response for GET requests or raw content for others.
        :raises APIError: If the API response returns a non-2xx HTTP status.
        """
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

    async def get_stations(self) -> dict:
        """
        Retrieve station data from the API.

        :returns: A dictionary containing station details.
        :raises NotImplementedError: This method must be implemented in a subclass.
        """
        raise NotImplementedError

    async def get_arrivals(self, station_id: str) -> dict:
        """
        Retrieve arrival times for a specific station.

        :param station_id: Unique identifier for the station.
        :returns: A dictionary containing arrival times at the station.
        :raises NotImplementedError: This method must be implemented in a subclass.
        """
        raise NotImplementedError

    async def get_route(self, actual_line_number: str) -> dict:
        """
        Retrieve route details for a specific line number.

        :param actual_line_number: The unique identifier for the route's line number.
        :returns: A dictionary containing route information.
        :raises NotImplementedError: This method must be implemented in a subclass.
        """
        raise NotImplementedError

    async def get_route_version(self, actual_line_number: str) -> dict:
        """
        Retrieve the version details of a specific route.

        :param actual_line_number: The unique identifier for the route's line number.
        :returns: A dictionary containing route version information.
        :raises NotImplementedError: This method must be implemented in a subclass.
        """
        raise NotImplementedError
