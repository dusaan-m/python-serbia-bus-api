import logging
from datetime import timedelta
from time import time

from httpx import AsyncClient

from srbusapi.caching.base_cache import BaseCache
from srbusapi.caching.caching_decorators import cache_data, cache_route
from srbusapi.client.base import BaseClient
from srbusapi.config import BeogradConfigBase
from srbusapi.crypto import encrypt, decrypt

logger = logging.getLogger(__name__)


class BeogradClient(BaseClient):
    def __init__(self, client: AsyncClient = None, cache: BaseCache = None):
        """
        Initializes a BeogradClient instance.

        :param client: Async HTTP client for making requests.
        :param cache: Cache object for managing caching operations.
        """
        super().__init__(client, cache, BeogradConfigBase())

    @property
    def session_id(self):
        """
        Generates a session ID based on the current timestamp.

        :returns: A timestamp-based session ID as a string.
        """
        return f"A{round(time() * 1000)}"

    @cache_data(expiration=timedelta(days=1))
    async def get_stations(self) -> dict:
        """
        Retrieves a list of stations.

        :returns: A dictionary with station details.
        :raises Exception: If the request fails or response is invalid.
        """
        logger.info("Beograd stations")
        endpoint = self.config.stations_endpoint
        params = {"action": "get_cities_extended"}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(seconds=15))
    async def get_arrivals(self, station_id) -> dict:
        """
        Retrieves arrival data for a specific station.

        :param station_id: Unique ID of the station.
        :returns: A dictionary with arrival data.
        :raises Exception: If the request fails or decryption fails.
        """
        logger.info(f"Beograd arrivals for station {station_id}")
        key, iv = self.config.aes_arrivals.key, self.config.aes_arrivals.iv

        endpoint = self.config.api_endpoint

        base = {"station_uid": station_id, "session_id": self.session_id}

        data = {
            "action": "data_bulletin",
            "base": encrypt(base, key, iv).decode("utf-8"),
        }

        response = await self._request(method="POST", endpoint=endpoint, data=data)

        decrypted_response = decrypt(response, key, iv)

        return decrypted_response

    @cache_route()
    async def get_route(self, actual_line_number) -> dict:
        """
        Retrieves the route details for a specific line.

        :param actual_line_number: The number of the line to fetch the route for.
        :returns: A dictionary with route details.
        :raises Exception: If the request or decryption fails.
        """
        logger.info(f"Beograd route for line {actual_line_number}")
        key, iv = self.config.aes_route.key, self.config.aes_route.iv

        endpoint = self.config.api_endpoint

        base = {"line_number": actual_line_number, "session_id": self.session_id}

        data = {
            "action": "route_insight",
            "base": encrypt(base, key, iv).decode("utf-8"),
        }

        response = await self._request(method="POST", endpoint=endpoint, data=data)

        decrypt_response = decrypt(response, key, iv)

        return decrypt_response

    @cache_data(expiration=timedelta(days=1))
    async def get_route_version(self, actual_line_number) -> dict:
        """
        Retrieves the route version for a specific line.

        :param actual_line_number: The line number to get the version of.
        :returns: A dictionary with route version details.
        :raises Exception: If the request or decryption fails.
        """
        logger.info(f"Beograd route version for line {actual_line_number}")
        key, iv = self.config.aes_route_version.key, self.config.aes_route_version.iv

        endpoint = self.config.api_endpoint

        base = {"line_number": actual_line_number, "session_id": self.session_id}

        data = {
            "action": "line_route_revision",
            "base": encrypt(base, key, iv).decode("utf-8"),
        }

        response = await self._request(method="POST", endpoint=endpoint, data=data)

        decrypt_response = decrypt(response, key, iv)

        return decrypt_response

    @cache_data(expiration=timedelta(days=1))
    async def get_line_numbers(self, station_ids: list[str]) -> dict:
        """
        Retrieves line numbers for a list of stations.

        :param station_ids: List of station IDs.
        :returns: A dictionary with line numbers associated with the stations.
        :raises Exception: If the request or decryption fails.
        """
        logger.info(f"Beograd line numbers for stations {station_ids}")
        station_ids = ";".join(station_ids)
        key, iv = self.config.aes_line_number.key, self.config.aes_line_number.iv

        endpoint = self.config.api_endpoint

        base = {"station_uids": station_ids, "session_id": self.session_id}

        data = {
            "action": "line_number_getter",
            "base": encrypt(base, key, iv).decode("utf-8"),
        }

        response = await self._request(method="POST", endpoint=endpoint, data=data)

        decrypted_response = decrypt(response, key, iv)

        return decrypted_response
