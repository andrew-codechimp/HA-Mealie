"""Mealie API Client."""

from __future__ import annotations
from typing import Any

import aiohttp
from asyncio import timeout

from .const import LOGGER, API_URL


class MealieApiClient:
    """Mealie API Client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
    ) -> None:
        """Mealie API Client."""
        self._url = API_URL
        self._session = session
        self._username = username
        self._password = password

        self._connected = False
        self._error = ""

    async def connection_test(self) -> tuple:
        """Test connection."""
        await self.query("quota")

        return self._connected, self._error

    async def query(self, service: str, params: dict[str, Any] = None) -> any:
        """Get information from the API."""

        if params is None:
            params = {}

        error = False

        params["control_login"] = self._username
        params["control_password"] = self._password

        try:
            async with timeout(10):
                response = await self._session.request(
                    method="post",
                    url=f"{self._url}{service}",
                    data=params,
                )

                if response.status == 200:
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
                self._url,
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
