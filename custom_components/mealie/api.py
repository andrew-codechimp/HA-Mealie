"""Mealie API Client."""

import asyncio
import logging
import socket

import aiohttp
import async_timeout

TIMEOUT = 10

from .const import LOGGER

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class MealieApiClient:
    """API for Mealie."""

    def __init__(
        self, host: str, token: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._host = host
        self._token = token
        self._session = session

    def headers(self) -> dict:
        headers = HEADERS
        headers["Authorization"] = f"bearer {self._token}"
        return headers

    async def async_get_groups(self) -> dict:
        return await self.api_wrapper("get", "/api/groups/self", headers = self.headers)

    async def async_get_shopping_lists(self, group_id: str) -> dict:
        params = {"group_id": group_id}
        return await self.api_wrapper("get", "/api/groups/shopping/lists", data = params, headers = self.headers)

    async def async_get_shopping_list_items(self, group_id: str, shopping_list_id: str) -> dict:

        params = {"orderBy": "position", "orderDirection": "asc", "perPage": "1000"}
        params["group_id"] =  group_id
        params["queryFilter"] = f"shopping_list_id={shopping_list_id}"

        return await self.api_wrapper("get", "/api/groups/shopping/lists", data = params, headers = self.headers)

    async def api_wrapper(
        self, method: str, service: str, data: dict = {}, headers: dict = {}
    ) -> any:
        """Get information from the API."""

        error = False

        # try:
        #     async with timeout(10):
        #         if method == "get":
        #             response = await self._session.get(url, params=data, headers=headers)
        #             return await response.json()

        #         elif method == "put":
        #             await self._session.put(url, headers=headers, json=data)

        #         elif method == "post":
        #             await self._session.post(url, headers=headers, json=data)

        #         elif method == "delete":
        #             await self._session.delete(url, headers=headers, json=data)

        try:
            async with timeout(10):
                response = await self._session.request(
                    method=method,
                    url=f"{self._host}{service}",
                    data=data,
                    headers=headers
                )

                if response.status >= 200 and response.status < 300:
                    data = await response.json()
                    LOGGER.debug(
                        "%s query response: %s",
                        f"{self._url}{service}",
                        data,
                    )

                    if "error" in data:
                        error = True
                else:
                    error = True
        except Exception:  # pylint: disable=broad-exception-caught
            error = True

        if error:
            try:
                if data and "error" in data:
                    errorcode = data["error"]
                else:
                    errorcode = response.status
            except Exception:  # pylint: disable=broad-exception-caught
                errorcode = "no_connection"

            LOGGER.warning(
                "%s unable to fetch data %s (%s)",
                self._host,
                service,
                errorcode,
            )

            self._error = errorcode
            return None

        self._connected = True
        self._error = ""

        return data

    @property
    def error(self):
        """Return error."""
        return self._error
