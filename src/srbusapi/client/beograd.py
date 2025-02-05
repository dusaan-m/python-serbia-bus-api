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
        super().__init__(client, cache, BeogradConfigBase())

    @property
    def session_id(self):
        return f"A{round(time() * 1000)}"

    @cache_data(expiration=timedelta(days=1))
    async def get_stations(self) -> dict:
        logger.info("Beograd stations")
        endpoint = self.config.stations_endpoint
        params = {"action": "get_cities_extended"}

        response = await self._request(method="GET", endpoint=endpoint, params=params)

        return response

    @cache_data(expiration=timedelta(seconds=15))
    async def get_arrivals(self, station_id) -> dict:
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
